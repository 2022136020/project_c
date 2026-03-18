# Created: 2026-03-17 | Updated: 2026-03-17 (MNIST 숫자 + 폰트 생성 영문자, 외부 다운로드 없음)
import os, io, base64, threading, random
import numpy as np
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont, ImageOps

app = Flask(__name__)

MODEL_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "handwriting_model.keras")
LABELS      = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # 36 클래스
NUM_CLASSES = len(LABELS)

_model      = None
_model_lock = threading.Lock()

# ── 영문자 이미지 합성 ────────────────────────────────────────────────────

_FONT_PATHS = [
    "C:/Windows/Fonts/arial.ttf",   "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/times.ttf",   "C:/Windows/Fonts/timesbd.ttf",
    "C:/Windows/Fonts/cour.ttf",    "C:/Windows/Fonts/courbd.ttf",
    "C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/georgiab.ttf",
]

def _build_fonts():
    fonts = []
    for fp in _FONT_PATHS:
        if os.path.exists(fp):
            for sz in [16, 18, 20, 22, 24]:
                try:    fonts.append(ImageFont.truetype(fp, sz))
                except: pass
    return fonts or [ImageFont.load_default()]

def _make_char_img(char, font):
    """28×28 흰 글씨 / 검정 배경 이미지 반환 (numpy float32 0~1)."""
    canvas = Image.new("L", (56, 56), 0)
    draw   = ImageDraw.Draw(canvas)
    bb = draw.textbbox((0, 0), char, font=font)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    draw.text(((56-w)//2 - bb[0], (56-h)//2 - bb[1]), char, fill=255, font=font)

    angle = random.uniform(-22, 22)
    canvas = canvas.rotate(angle, resample=Image.BILINEAR)
    new_sz = random.randint(36, 52)
    canvas = canvas.resize((new_sz, new_sz), Image.LANCZOS)

    bg  = Image.new("L", (56, 56), 0)
    off = ((56-new_sz)//2 + random.randint(-4, 4),
           (56-new_sz)//2 + random.randint(-4, 4))
    bg.paste(canvas, off)
    arr = np.array(bg.resize((28, 28), Image.LANCZOS), dtype=np.float32)
    arr = np.clip(arr + np.random.normal(0, 10, arr.shape), 0, 255) / 255.0
    return arr

def _generate_letter_data(n_per_class, log_fn=None):
    fonts  = _build_fonts()
    images, labels = [], []
    chars  = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for li, ch in enumerate(chars):
        if log_fn: log_fn(f"영문자 생성 중: {ch} ({li+1}/26)")
        for _ in range(n_per_class):
            images.append(_make_char_img(ch, random.choice(fonts)))
            labels.append(li + 10)   # A=10, B=11, ..., Z=35
    return np.array(images, np.float32), np.array(labels, np.int64)

# ── 모델 관리 ─────────────────────────────────────────────────────────────

def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = _load_or_train()
    return _model

def _load_or_train(log_fn=None):
    import tensorflow as tf

    if os.path.exists(MODEL_PATH):
        print("[모델] 저장된 모델 로드 중...")
        return tf.keras.models.load_model(MODEL_PATH)

    def log(m):
        print(m)
        if log_fn: log_fn(m)

    # ── 데이터 준비 ──────────────────────────────────────────────────
    log("MNIST 데이터 로드 중...")
    (xd_tr, yd_tr), (xd_te, yd_te) = tf.keras.datasets.mnist.load_data()
    xd_tr = xd_tr.astype(np.float32) / 255.0
    xd_te = xd_te.astype(np.float32) / 255.0

    log("영문자 학습 데이터 생성 중 (A-Z, 약 1분)...")
    xl_tr, yl_tr = _generate_letter_data(n_per_class=2200)
    xl_te, yl_te = _generate_letter_data(n_per_class=350)

    x_tr = np.concatenate([xd_tr, xl_tr])
    y_tr = np.concatenate([yd_tr, yl_tr])
    x_te = np.concatenate([xd_te, xl_te])
    y_te = np.concatenate([yd_te, yl_te])

    idx  = np.random.permutation(len(x_tr))
    x_tr, y_tr = x_tr[idx], y_tr[idx]

    # ── 모델 정의 ────────────────────────────────────────────────────
    log("모델 학습 중...")
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(28, 28)),
        tf.keras.layers.Reshape((28, 28, 1)),
        tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
        tf.keras.layers.Conv2D(32, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
        tf.keras.layers.Conv2D(64, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(NUM_CLASSES, activation="softmax"),
    ])
    model.compile(optimizer="adam",
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    model.fit(x_tr, y_tr, epochs=12, batch_size=256, verbose=1,
              validation_data=(x_te, y_te))

    acc = model.evaluate(x_te, y_te, verbose=0)[1]
    log(f"학습 완료 - 정확도: {acc*100:.1f}%")
    model.save(MODEL_PATH)
    return model

# ── 이미지 전처리 ──────────────────────────────────────────────────────────

def preprocess(pil_image: Image.Image) -> np.ndarray:
    img  = pil_image.convert("L")
    img  = ImageOps.invert(img)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        pad = max(img.size) // 5
        img = ImageOps.expand(img, border=pad, fill=0)
    img = img.resize((28, 28), Image.LANCZOS)
    return np.array(img, dtype=np.float32)[np.newaxis, ...] / 255.0

# ── 라우트 ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    b64  = data.get("image", "")
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    pil  = Image.open(io.BytesIO(base64.b64decode(b64)))

    arr   = preprocess(pil)
    probs = get_model().predict(arr, verbose=0)[0]
    top5  = [{"char": LABELS[i], "prob": float(probs[i])}
             for i in np.argsort(probs)[::-1][:5]]
    return jsonify({"prediction": LABELS[int(np.argmax(probs))], "top5": top5})

@app.route("/status")
def status():
    ready = os.path.exists(MODEL_PATH) or _model is not None
    return jsonify({"ready": ready})

if __name__ == "__main__":
    threading.Thread(target=get_model, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
