# Created: 2026-03-17 | Updated: 2026-03-17 (MNIST 숫자 + 폰트 생성 영문자, 외부 다운로드 없음)
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, threading, random

MODEL_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "handwriting_model.keras")
LABELS      = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # 36 클래스
NUM_CLASSES = len(LABELS)
TOP_N       = 5

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
    canvas = Image.new("L", (56, 56), 0)
    draw   = ImageDraw.Draw(canvas)
    bb = draw.textbbox((0, 0), char, font=font)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    draw.text(((56-w)//2 - bb[0], (56-h)//2 - bb[1]), char, fill=255, font=font)
    canvas = canvas.rotate(random.uniform(-22, 22), resample=Image.BILINEAR)
    new_sz = random.randint(36, 52)
    canvas = canvas.resize((new_sz, new_sz), Image.LANCZOS)
    bg = Image.new("L", (56, 56), 0)
    bg.paste(canvas, ((56-new_sz)//2 + random.randint(-4,4),
                       (56-new_sz)//2 + random.randint(-4,4)))
    arr = np.array(bg.resize((28, 28), Image.LANCZOS), dtype=np.float32)
    return np.clip(arr + np.random.normal(0, 10, arr.shape), 0, 255) / 255.0

def _generate_letter_data(n_per_class, log_fn=None):
    fonts = _build_fonts()
    images, labels = [], []
    for li, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        if log_fn: log_fn(f"영문자 생성 중: {ch} ({li+1}/26)")
        for _ in range(n_per_class):
            images.append(_make_char_img(ch, random.choice(fonts)))
            labels.append(li + 10)
    return np.array(images, np.float32), np.array(labels, np.int64)

# ── 모델 학습 / 로드 ─────────────────────────────────────────────────────────

def train_and_save_model(log_callback=None):
    import tensorflow as tf

    def log(m):
        if log_callback: log_callback(m)

    log("MNIST 데이터 로드 중...")
    (xd_tr, yd_tr), (xd_te, yd_te) = tf.keras.datasets.mnist.load_data()
    xd_tr = xd_tr.astype(np.float32) / 255.0
    xd_te = xd_te.astype(np.float32) / 255.0

    log("영문자 학습 데이터 생성 중 (A-Z, 약 1분)...")
    xl_tr, yl_tr = _generate_letter_data(n_per_class=2200, log_fn=log)
    xl_te, yl_te = _generate_letter_data(n_per_class=350)

    x_tr = np.concatenate([xd_tr, xl_tr])
    y_tr = np.concatenate([yd_tr, yl_tr])
    x_te = np.concatenate([xd_te, xl_te])
    y_te = np.concatenate([yd_te, yl_te])

    idx  = np.random.permutation(len(x_tr))
    x_tr, y_tr = x_tr[idx], y_tr[idx]

    log(f"모델 학습 중 ({NUM_CLASSES}개 클래스)...")
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
    model.fit(x_tr, y_tr, epochs=12, batch_size=256, verbose=0,
              validation_data=(x_te, y_te))

    acc = model.evaluate(x_te, y_te, verbose=0)[1]
    log(f"학습 완료! 정확도: {acc*100:.1f}%")
    model.save(MODEL_PATH)
    return model

def load_model():
    import tensorflow as tf
    return tf.keras.models.load_model(MODEL_PATH)

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

# ── GUI ───────────────────────────────────────────────────────────────────

class HandwritingRecognizerApp(tk.Tk):
    CANVAS_SIZE  = 420
    BRUSH_RADIUS = 14

    def __init__(self):
        super().__init__()
        self.title("손글씨 인식기")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self.model = None
        self._pil_image = Image.new("RGB", (self.CANVAS_SIZE, self.CANVAS_SIZE), "white")
        self._draw      = ImageDraw.Draw(self._pil_image)
        self._build_ui()
        self._load_or_train()

    def _build_ui(self):
        BG, FG, ACC = "#1e1e2e", "#cdd6f4", "#89b4fa"
        PAD = 16

        tk.Label(self, text="손글씨 인식기",
                 font=("맑은 고딕", 16, "bold"), bg=BG, fg=ACC).pack(pady=(PAD, 4))

        self._status_var = tk.StringVar(value="모델을 불러오는 중...")
        tk.Label(self, textvariable=self._status_var,
                 font=("맑은 고딕", 9), bg=BG, fg=FG).pack(pady=(0, 8))

        frame = tk.Frame(self, bg=ACC, padx=2, pady=2)
        frame.pack(padx=PAD)
        self._canvas = tk.Canvas(frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE,
                                 bg="white", cursor="crosshair", highlightthickness=0)
        self._canvas.pack()
        self._canvas.bind("<B1-Motion>",     self._on_draw)
        self._canvas.bind("<ButtonPress-1>", self._on_draw)

        self._result_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self._result_var,
                 font=("맑은 고딕", 56, "bold"), bg=BG, fg=ACC, width=3).pack(pady=(12, 0))

        tk.Label(self, text="상위 5개 후보",
                 font=("맑은 고딕", 9), bg=BG, fg="#6c7086").pack()

        self._prob_frame = tk.Frame(self, bg=BG)
        self._prob_frame.pack(padx=PAD, pady=(4, 0), fill="x")
        self._prob_bars, self._prob_labels, self._prob_chars = [], [], []
        for _ in range(TOP_N):
            row = tk.Frame(self._prob_frame, bg=BG)
            row.pack(fill="x", pady=2)
            cl = tk.Label(row, text="", width=3, font=("맑은 고딕", 10, "bold"), bg=BG, fg=ACC)
            cl.pack(side="left")
            bar = ttk.Progressbar(row, length=300, maximum=100, mode="determinate")
            bar.pack(side="left", padx=4)
            pl = tk.Label(row, text="", width=6, font=("맑은 고딕", 9), bg=BG, fg=FG)
            pl.pack(side="left")
            self._prob_chars.append(cl)
            self._prob_bars.append(bar)
            self._prob_labels.append(pl)

        btn = tk.Frame(self, bg=BG)
        btn.pack(pady=PAD)
        tk.Button(btn, text="인식", command=self._predict,
                  font=("맑은 고딕", 11, "bold"), bg=ACC, fg="#1e1e2e",
                  activebackground="#74c7ec", relief="flat", padx=20, pady=6,
                  cursor="hand2").pack(side="left", padx=8)
        tk.Button(btn, text="지우기", command=self._clear,
                  font=("맑은 고딕", 11), bg="#313244", fg=FG,
                  activebackground="#45475a", relief="flat", padx=20, pady=6,
                  cursor="hand2").pack(side="left", padx=8)

    def _load_or_train(self):
        def worker():
            try:
                if os.path.exists(MODEL_PATH):
                    self._set_status("저장된 모델 불러오는 중...")
                    self.model = load_model()
                    self._set_status("준비 완료! 숫자(0-9) 또는 영문 대문자(A-Z)를 그리세요.")
                else:
                    self._set_status("첫 실행: 데이터 생성 및 학습 중 (약 3~5분)...")
                    self.model = train_and_save_model(log_callback=self._set_status)
                    self._set_status("준비 완료! 숫자(0-9) 또는 영문 대문자(A-Z)를 그리세요.")
            except Exception as e:
                self._set_status(f"오류: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _set_status(self, msg):
        self.after(0, lambda: self._status_var.set(msg))

    def _on_draw(self, event):
        r = self.BRUSH_RADIUS
        x, y = event.x, event.y
        self._canvas.create_oval(x-r, y-r, x+r, y+r, fill="black", outline="black")
        self._draw.ellipse([x-r, y-r, x+r, y+r], fill="black")

    def _clear(self):
        self._canvas.delete("all")
        self._pil_image = Image.new("RGB", (self.CANVAS_SIZE, self.CANVAS_SIZE), "white")
        self._draw      = ImageDraw.Draw(self._pil_image)
        self._result_var.set("")
        for c, b, l in zip(self._prob_chars, self._prob_bars, self._prob_labels):
            c.config(text=""); b["value"] = 0; l.config(text="")

    def _predict(self):
        if self.model is None:
            messagebox.showwarning("잠깐", "모델을 아직 준비 중입니다.")
            return
        arr   = preprocess(self._pil_image)
        probs = self.model.predict(arr, verbose=0)[0]
        top   = np.argsort(probs)[::-1][:TOP_N]
        self._result_var.set(LABELS[top[0]])
        for i, idx in enumerate(top):
            pct = float(probs[idx]) * 100
            self._prob_chars[i].config(text=LABELS[idx])
            self._prob_bars[i]["value"] = pct
            self._prob_labels[i].config(text=f"{pct:.1f}%")

if __name__ == "__main__":
    app = HandwritingRecognizerApp()
    app.mainloop()
