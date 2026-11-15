"""Chuyển mô hình đã huấn luyện sang .tflite và đo trên một phần tập kiểm định.

Chạy trong Ubuntu, không cần GPU:
    source ~/vnhw/env.sh
    CUDA_VISIBLE_DEVICES=-1 python export_tflite.py --run ~/vnhw/runs/m1_base
"""
import argparse
import json
import os
import statistics
import time

import numpy as np
import tensorflow as tf
import keras
import tf_keras

import data as D
from metrics import error_rates
from model import CONFIGS, POOLS


def legacy_copy(model, name, height, width, num_classes):
    """Dựng lại mô hình bằng tf_keras theo cùng cấu hình trong model.py và chép trọng số.

    LSTM của Keras 3 chuyển sang LiteRT thành vòng lặp có biến và không chạy được.
    LSTM của tf_keras chuyển thành toán tử UNIDIRECTIONAL_SEQUENCE_LSTM gốc.
    """
    c = CONFIGS[name]
    L = tf_keras.layers
    inputs = tf_keras.Input((height, width, 1), batch_size=1)
    x = inputs
    for filters, pool in zip(c["filters"], POOLS):
        x = L.Conv2D(filters, 3, padding="same", use_bias=False)(x)
        x = L.BatchNormalization()(x)
        x = L.ReLU()(x)
        x = L.MaxPool2D(pool)(x)
    x = L.Permute((2, 1, 3))(x)
    x = L.Reshape((width // 2, (height // 16) * c["filters"][-1]))(x)
    x = L.Dense(c["dense"], activation="relu")(x)
    if c["lstm"]:
        for _ in range(2):
            x = L.Bidirectional(L.LSTM(c["lstm"], return_sequences=True))(x)
    outputs = L.Dense(num_classes, activation="softmax")(x)
    legacy = tf_keras.Model(inputs, outputs)
    source = [l for l in model.layers if l.weights]
    target = [l for l in legacy.layers if l.weights]
    if len(source) != len(target):
        raise ValueError("layer count differs")
    for s, t in zip(source, target):
        t.set_weights(s.get_weights())
    return legacy


def convert(legacy, mode):
    converter = tf.lite.TFLiteConverter.from_keras_model(legacy)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    if mode != "float":
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    if mode == "float16":
        converter.target_spec.supported_types = [tf.float16]
    return converter.convert()


def op_names(blob):
    interpreter = tf.lite.Interpreter(model_content=blob)
    interpreter.allocate_tensors()
    return sorted({d["op_name"] for d in interpreter._get_ops_details()})


def run(blob, images, charset):
    interpreter = tf.lite.Interpreter(model_content=blob, num_threads=4)
    interpreter.allocate_tensors()
    in_detail, out_detail = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    texts, times = [], []
    for image in images:
        interpreter.set_tensor(in_detail["index"], image[None, ..., None].astype(np.float32) / 255.0)
        # LSTM của LiteRT giữ trạng thái giữa các lần chạy, phải đặt lại trước mỗi dòng.
        interpreter.reset_all_variables()
        started = time.perf_counter()
        interpreter.invoke()
        times.append((time.perf_counter() - started) * 1000)
        texts.append(charset.decode_greedy(interpreter.get_tensor(out_detail["index"])[0].argmax(-1).tolist()))
    return texts, times


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--samples", type=int, default=200)
    p.add_argument("--data", default=os.path.expanduser("~/vnhw/data"))
    a = p.parse_args()

    config = json.load(open(os.path.join(a.run, "config.json"), encoding="utf8"))
    width, height, crop = config["width"], config["height"], not config["no_crop"]
    charset = D.Charset(json.load(open(os.path.join(a.run, "charset.json"), encoding="utf8")))
    model = keras.models.load_model(os.path.join(a.run, "best.keras"))

    stems = D.read_split(f"{a.data}/splits/val.ln")[:: max(1, 1229 // a.samples)][: a.samples]
    labels = [D.read_label(f"{a.data}/lines", s) for s in stems]
    images = D.load_images(f"{a.data}/lines", stems, width, height, crop, config.get("max_ink", 0))

    keras_texts = []
    for i in range(0, len(images), 32):
        out = model(images[i : i + 32][..., None].astype(np.float32) / 255.0, training=False).numpy().argmax(-1)
        keras_texts += [charset.decode_greedy(r.tolist()) for r in out]
    report = dict(samples=len(images), keras_cer_line=round(error_rates(labels, keras_texts)[1], 5))

    legacy = legacy_copy(model, config["model"], height, width, charset.num_classes)
    for name in ("float", "float16", "dynamic_range"):
        blob = convert(legacy, name)
        path = os.path.join(a.run, f"m_{name}.tflite")
        open(path, "wb").write(blob)
        texts, times = run(blob, images, charset)
        report[name] = dict(size_MB=round(len(blob) / 1e6, 3), cer_line=round(error_rates(labels, texts)[1], 5),
                            ms_median_pc=round(statistics.median(times), 1), same_as_keras=sum(x == y for x, y in zip(texts, keras_texts)),
                            ops=op_names(blob))
    print(json.dumps(report, indent=1))
    json.dump(report, open(os.path.join(a.run, "tflite_report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
