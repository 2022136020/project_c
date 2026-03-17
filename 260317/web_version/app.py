# Created: 2026-03-17
import os
import io
import base64
import threading

import numpy as np
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageOps

app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "digit_model.keras")

_model = None
_model_lock = threading.Lock()

# ── 모델 관리 ─────────────────────────────────────────────────────────────

def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = _load_or_train()
    return _model


def _load_or_train():
    import tensorflow as tf
    if os.path.exists(MODEL_PATH):
        print("[모델] 저장된 모델 로드 중...")
        return tf.keras.models.load_model(MODEL_PATH)

    print("[모델] MNIST 학습 시작...")
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test  = x_test.astype("float32")  / 255.0

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(28, 28)),
        tf.keras.layers.Reshape((28, 28, 1)),
        tf.keras.layers.Conv2D(32, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(optimizer="adam",
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    model.fit(x_train, y_train, epochs=5, batch_size=128, verbose=1,
              validation_data=(x_test, y_test))
    acc = model.evaluate(x_test, y_test, verbose=0)[1]
    print(f"[모델] 학습 완료 — 정확도: {acc*100:.1f}%")
    model.save(MODEL_PATH)
    return model


# ── 이미지 전처리 ──────────────────────────────────────────────────────────

def preprocess(pil_image: Image.Image) -> np.ndarray:
    """PIL 이미지 → (1, 28, 28) float32 배열 (MNIST 형식)"""
    img = pil_image.convert("L")
    img = ImageOps.invert(img)           # 흰 배경 → 검정, 글씨 → 흰색
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        pad = max(img.size) // 5
        img = ImageOps.expand(img, border=pad, fill=0)
    img = img.resize((28, 28), Image.LANCZOS)
    arr = np.array(img).astype("float32") / 255.0
    return arr[np.newaxis, ...]          # (1, 28, 28)


# ── 라우트 ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    요청: JSON { "image": "<base64 PNG>" }
    응답: JSON { "prediction": int, "probabilities": [float × 10] }
    """
    data = request.get_json(force=True)
    image_b64 = data.get("image", "")

    # base64 → PIL
    if "," in image_b64:          # data:image/png;base64,<data>
        image_b64 = image_b64.split(",", 1)[1]
    img_bytes = base64.b64decode(image_b64)
    pil_img   = Image.open(io.BytesIO(img_bytes))

    arr   = preprocess(pil_img)
    model = get_model()
    probs = model.predict(arr, verbose=0)[0].tolist()
    pred  = int(np.argmax(probs))

    return jsonify({"prediction": pred, "probabilities": probs})


@app.route("/status")
def status():
    """모델 준비 여부 확인용 엔드포인트"""
    ready = os.path.exists(MODEL_PATH) or _model is not None
    return jsonify({"ready": ready})


# ── 진입점 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 서버 시작 전 모델 미리 로드
    threading.Thread(target=get_model, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
