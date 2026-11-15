"""Huấn luyện mô hình trên tập huấn luyện và đo trên tập kiểm định.

Tập kiểm thử không được đọc ở đây (docs/02-yeu-cau-va-danh-gia.md, mục 5).

Chạy trong Ubuntu:
    source ~/vnhw/env.sh
    python train.py --name m1_base --model m1 --epochs 50
"""
import argparse
import json
import math
import os
import random
import subprocess
import time

import numpy as np
import tensorflow as tf
import keras

import data as D
from metrics import error_rates
from model import CONFIGS, build


def parse():
    home = os.path.expanduser("~/vnhw")
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--model", default="m1", choices=sorted(CONFIGS))
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--lr-min", type=float, default=1e-5)
    p.add_argument("--dropout", type=float, default=0.5)
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--height", type=int, default=64)
    p.add_argument("--no-crop", action="store_true")
    p.add_argument("--no-augment", action="store_true")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--limit", type=int, default=0, help="Chỉ dùng N dòng đầu, để chạy thử mã")
    p.add_argument("--overfit", type=int, default=0, help="Học thuộc N dòng đầu, đo trên chính các dòng đó")
    p.add_argument("--max-ink", type=int, default=0, help="Giới hạn chiều cao phần nét sau khi co, 0 là không giới hạn")
    p.add_argument("--rerender", type=float, nargs="*", default=[], help="Các độ dày nét dùng để vẽ lại ảnh huấn luyện")
    p.add_argument("--intensity-low", type=float, default=1.0, help="Hệ số độ đậm nhỏ nhất khi tăng cường, 1 là không đổi")
    p.add_argument("--intensity-high", type=float, default=1.0, help="Hệ số độ đậm lớn nhất khi tăng cường, giá trị vượt 1 làm nét đậm và sắc hơn")
    p.add_argument("--elastic", type=float, default=0.0, help="Biên độ biến dạng đàn hồi, tính bằng điểm ảnh, 0 là không dùng")
    p.add_argument("--lines", default=f"{home}/data/lines")
    p.add_argument("--splits", default=f"{home}/data/splits")
    p.add_argument("--runs", default=f"{home}/runs")
    return p.parse_args()


ELASTIC_STEP = 12  # Khoảng cách giữa các nút của trường dịch chuyển thô, tính bằng điểm ảnh


def elastic(x, amplitude):
    """Biến dạng đàn hồi: mỗi điểm ảnh lấy giá trị tại vị trí dịch đi theo một trường dịch chuyển trơn ngẫu nhiên."""
    n = tf.shape(x)[0]
    h, w = x.shape[1], x.shape[2]
    coarse = tf.random.uniform([n, h // ELASTIC_STEP + 2, w // ELASTIC_STEP + 2, 2], -1.0, 1.0)
    field = tf.image.resize(coarse, [h, w], method="bicubic") * amplitude
    yy, xx = tf.meshgrid(tf.range(h, dtype=tf.float32), tf.range(w, dtype=tf.float32), indexing="ij")
    sy, sx = yy[None] + field[..., 0], xx[None] + field[..., 1]
    y0, x0 = tf.floor(sy), tf.floor(sx)
    wy, wx = sy - y0, sx - x0
    y0, x0 = tf.cast(y0, tf.int32), tf.cast(x0, tf.int32)
    image = x[..., 0]
    batch = tf.broadcast_to(tf.range(n)[:, None, None], tf.shape(y0))

    def at(yi, xi):
        inside = (yi >= 0) & (yi < h) & (xi >= 0) & (xi < w)
        idx = tf.stack([batch, tf.clip_by_value(yi, 0, h - 1), tf.clip_by_value(xi, 0, w - 1)], axis=-1)
        return tf.where(inside, tf.gather_nd(image, idx), 0.0)

    out = (at(y0, x0) * (1 - wy) * (1 - wx) + at(y0, x0 + 1) * (1 - wy) * wx
           + at(y0 + 1, x0) * wy * (1 - wx) + at(y0 + 1, x0 + 1) * wy * wx)
    return out[..., None]


def augment(x, intensity_low=1.0, intensity_high=1.0, elastic_amplitude=0.0):
    """Tăng cường theo 03, mục 3.4: co giãn, nghiêng, biến dạng đàn hồi, dày mỏng nét, độ đậm. x có giá trị 0 đến 1."""
    if elastic_amplitude:
        x = elastic(x, elastic_amplitude)
    n = tf.shape(x)[0]
    h, w = float(x.shape[1]), float(x.shape[2])
    # sx không vượt 1,02 để nét không rơi khỏi khung trong khi nhãn vẫn còn đủ ký tự.
    sx = tf.random.uniform([n], 0.88, 1.02)
    sy = tf.random.uniform([n], 0.85, 1.15)
    shear = tf.random.uniform([n], -0.25, 0.25)
    dy = tf.random.uniform([n], -3.0, 3.0)
    # Biến đổi ngược: tọa độ ảnh ra về tọa độ ảnh vào, giữ tâm của khung.
    a0, a1 = 1.0 / sx, shear
    b1 = 1.0 / sy
    a2 = w / 2.0 * (1.0 - a0) - a1 * h / 2.0
    b2 = h / 2.0 * (1.0 - b1) - dy
    zeros = tf.zeros([n])
    matrix = tf.stack([a0, a1, a2, zeros, b1, b2, zeros, zeros], axis=1)
    x = tf.raw_ops.ImageProjectiveTransformV3(
        images=x, transforms=matrix, output_shape=tf.constant([int(h), int(w)]),
        fill_value=0.0, interpolation="BILINEAR", fill_mode="CONSTANT")
    x.set_shape([None, int(h), int(w), 1])
    alpha = tf.reshape(tf.random.uniform([n], -0.5, 1.0), [-1, 1, 1, 1])
    dilated = tf.nn.max_pool2d(x, 3, 1, "SAME")
    eroded = -tf.nn.max_pool2d(-x, 3, 1, "SAME")
    thick = x + tf.maximum(alpha, 0.0) * (dilated - x) + tf.maximum(-alpha, 0.0) * (eroded - x)
    if intensity_low != 1.0 or intensity_high != 1.0:
        thick = thick * tf.reshape(tf.random.uniform([n], intensity_low, intensity_high), [-1, 1, 1, 1])
    return tf.clip_by_value(thick, 0.0, 1.0)


def pad(encoded):
    length = max(map(len, encoded))
    out = np.zeros((len(encoded), length), np.int32)
    for i, e in enumerate(encoded):
        out[i, : len(e)] = e
    return out, np.array([[len(e)] for e in encoded], np.int32)


def main():
    a = parse()
    random.seed(a.seed); np.random.seed(a.seed); tf.random.set_seed(a.seed)
    out_dir = os.path.join(a.runs, a.name)
    os.makedirs(out_dir, exist_ok=True)

    train_stems = D.read_split(f"{a.splits}/train.ln")
    val_stems = D.read_split(f"{a.splits}/val.ln")
    if a.limit:
        train_stems, val_stems = train_stems[: a.limit], val_stems[: a.limit]
    if a.overfit:
        # Phép học thuộc của Cổng 1: đo trên chính các dòng đã học, không tăng cường.
        train_stems = train_stems[: a.overfit]
        val_stems = list(train_stems)
        a.no_augment, a.dropout = True, 0.0
    train_labels = [D.read_label(a.lines, s) for s in train_stems]
    val_labels = [D.read_label(a.lines, s) for s in val_stems]
    charset = D.Charset.from_labels(train_labels + val_labels)
    charset.save(os.path.join(out_dir, "charset.json"))

    t0 = time.time()
    crop = not a.no_crop
    train_x = D.load_images(a.lines, train_stems, a.width, a.height, crop, a.max_ink)
    val_x = D.load_images(a.lines, val_stems, a.width, a.height, crop, a.max_ink)
    pool = train_x[:, None]
    if a.rerender:
        # Mỗi dòng có thêm các bản vẽ lại bằng bộ vẽ của ứng dụng, mỗi epoch chọn ngẫu nhiên một bản.
        import rerender

        pool = np.concatenate([pool, rerender.render_all(a.lines, train_stems, a.width, a.height, a.rerender, cap=a.max_ink)], axis=1)
    print(f"images {pool.shape} {val_x.shape} in {time.time() - t0:.1f}s, chars {len(charset.chars)}", flush=True)
    train_y = [charset.encode(t) for t in train_labels]

    model = build(a.model, a.width, a.height, charset.num_classes, a.dropout)
    print("params", model.count_params(), "output", model.output_shape, flush=True)
    steps_per_epoch = len(train_x) // a.batch
    schedule = keras.optimizers.schedules.CosineDecay(a.lr, steps_per_epoch * a.epochs, alpha=a.lr_min / a.lr)
    optimizer = keras.optimizers.Adam(schedule, global_clipnorm=5.0)
    use_augment = not a.no_augment

    @tf.function(reduce_retracing=True, input_signature=[
        tf.TensorSpec([None, a.height, a.width], tf.uint8), tf.TensorSpec([None, None], tf.int32),
        tf.TensorSpec([None, 1], tf.int32)])
    def train_step(images, labels, label_lengths):
        x = tf.cast(images[..., None], tf.float32) / 255.0
        if use_augment:
            x = augment(x, a.intensity_low, a.intensity_high, a.elastic)
        with tf.GradientTape() as tape:
            p = model(x, training=True)
            t = tf.fill([tf.shape(p)[0], 1], tf.shape(p)[1])
            loss = tf.reduce_mean(tf.keras.backend.ctc_batch_cost(labels, p, t, label_lengths))
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply(grads, model.trainable_variables)
        return loss

    @tf.function(reduce_retracing=True, input_signature=[tf.TensorSpec([None, a.height, a.width], tf.uint8)])
    def predict_step(images):
        x = tf.cast(images[..., None], tf.float32) / 255.0
        return tf.argmax(model(x, training=False), axis=-1)

    def evaluate(images, labels, keep=None):
        predictions = []
        for i in range(0, len(images), 64):
            for row in predict_step(tf.constant(images[i : i + 64])).numpy():
                predictions.append(charset.decode_greedy(row.tolist()))
        cer1, cer2 = error_rates(labels, predictions)
        wer1, wer2 = error_rates(labels, predictions, "word")
        return dict(cer_total=cer1, cer_line=cer2, wer_total=wer1, wer_line=wer2), predictions

    config = vars(a) | dict(train_lines=len(train_x), val_lines=len(val_x), num_chars=len(charset.chars),
                            params=model.count_params(), tensorflow=tf.__version__, keras=keras.__version__)
    json.dump(config, open(os.path.join(out_dir, "config.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    log = open(os.path.join(out_dir, "log.jsonl"), "a", encoding="utf8")

    best = dict(cer_line=math.inf)
    for epoch in range(1, a.epochs + 1):
        started = time.time()
        order = np.random.permutation(len(train_x))
        losses = []
        for i in range(steps_per_epoch):
            idx = order[i * a.batch : (i + 1) * a.batch]
            y, yl = pad([train_y[j] for j in idx])
            batch = pool[idx, np.random.randint(pool.shape[1], size=len(idx))]
            losses.append(float(train_step(tf.constant(batch), tf.constant(y), tf.constant(yl))))
        train_s = time.time() - started
        scores, predictions = evaluate(val_x, val_labels)
        row = dict(epoch=epoch, loss=float(np.mean(losses)), train_s=round(train_s, 1),
                   total_s=round(time.time() - started, 1), **{k: round(v, 5) for k, v in scores.items()})
        if not math.isfinite(row["loss"]):
            print("loss is not finite, stopping", flush=True)
            break
        print(json.dumps(row), flush=True)
        log.write(json.dumps(row) + "\n"); log.flush()
        if scores["cer_line"] < best["cer_line"]:
            best = dict(epoch=epoch, **scores)
            model.save(os.path.join(out_dir, "best.keras"))
            with open(os.path.join(out_dir, "val_predictions.txt"), "w", encoding="utf8") as f:
                for t, p in zip(val_labels, predictions):
                    f.write(t + "\n" + p + "\n\n")
    json.dump(best, open(os.path.join(out_dir, "best.json"), "w", encoding="utf8"), indent=1)
    print("BEST", json.dumps(best), flush=True)


if __name__ == "__main__":
    main()
