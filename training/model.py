"""Các mô hình M0, M1 và bản M1 lớn theo docs/01-mo-ta-de-tai.md, mục 7.3."""
import keras
from keras import layers as L

# Số bộ lọc của bốn khối tích chập, số chiều sau lớp kết nối đầy đủ, số ô LSTM mỗi chiều (0 là không có BiLSTM).
CONFIGS = {
    "m0": dict(filters=(32, 64, 128, 128), dense=128, lstm=0),
    "m1": dict(filters=(32, 64, 128, 128), dense=128, lstm=128),
    "m1l": dict(filters=(48, 96, 192, 192), dense=192, lstm=192),
}
POOLS = ((2, 2), (2, 1), (2, 1), (2, 1))


def build(name, width, height, num_classes, dropout=0.5):
    """Đầu vào (height, width, 1). Đầu ra (width / 2 bước, num_classes)."""
    if name not in CONFIGS:
        raise ValueError(name)
    c = CONFIGS[name]
    inputs = keras.Input((height, width, 1))
    x = inputs
    for filters, pool in zip(c["filters"], POOLS):
        x = L.Conv2D(filters, 3, padding="same", use_bias=False)(x)
        x = L.BatchNormalization()(x)
        x = L.ReLU()(x)
        x = L.MaxPool2D(pool)(x)
    # (height / 16, width / 2, kênh) đổi thành (width / 2 bước, height / 16 nhân kênh đặc trưng)
    steps, features = width // 2, (height // 16) * c["filters"][-1]
    x = L.Permute((2, 1, 3))(x)
    x = L.Reshape((steps, features))(x)
    x = L.Dense(c["dense"], activation="relu")(x)
    if c["lstm"]:
        for _ in range(2):
            x = L.Bidirectional(L.LSTM(c["lstm"], return_sequences=True))(x)
            x = L.Dropout(dropout)(x)
    outputs = L.Dense(num_classes, activation="softmax", name="softmax")(x)
    return keras.Model(inputs, outputs, name=name)
