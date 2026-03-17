# Created: 2026-03-17 (desktop_version으로 이동)
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import os
import sys
import threading

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "digit_model.keras")

# ── 모델 학습 / 로드 ─────────────────────────────────────────────────────────

def train_and_save_model(log_callback=None):
    import tensorflow as tf

    def log(msg):
        if log_callback:
            log_callback(msg)

    log("MNIST 데이터셋 다운로드 중...")
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test  = x_test.astype("float32")  / 255.0

    log("모델 학습 중 (약 30초)...")
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
    model.fit(x_train, y_train, epochs=5,
              batch_size=128, verbose=0,
              validation_data=(x_test, y_test))

    acc = model.evaluate(x_test, y_test, verbose=0)[1]
    log(f"학습 완료! 정확도: {acc*100:.1f}%")
    model.save(MODEL_PATH)
    return model


def load_model():
    import tensorflow as tf
    return tf.keras.models.load_model(MODEL_PATH)


# ── 이미지 전처리 ──────────────────────────────────────────────────────────

def preprocess(pil_image: Image.Image) -> np.ndarray:
    """PIL 이미지 → (1, 28, 28) float32 배열 (MNIST 형식)"""
    img = pil_image.convert("L")
    img = ImageOps.invert(img)                # 흰 배경 → 검정, 검정 글씨 → 흰색
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        pad = max(img.size) // 5
        img = ImageOps.expand(img, border=pad, fill=0)
    img = img.resize((28, 28), Image.LANCZOS)
    arr = np.array(img).astype("float32") / 255.0
    return arr[np.newaxis, ...]               # (1, 28, 28)


# ── GUI ───────────────────────────────────────────────────────────────────

class DigitRecognizerApp(tk.Tk):
    CANVAS_SIZE = 280
    BRUSH_RADIUS = 12

    def __init__(self):
        super().__init__()
        self.title("손글씨 숫자 인식기")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.model = None
        self._pil_image = Image.new("RGB", (self.CANVAS_SIZE, self.CANVAS_SIZE), "white")
        self._draw      = ImageDraw.Draw(self._pil_image)

        self._build_ui()
        self._load_or_train()

    def _build_ui(self):
        PAD = 16
        BG  = "#1e1e2e"
        FG  = "#cdd6f4"
        ACC = "#89b4fa"

        tk.Label(self, text="손글씨 숫자 인식기",
                 font=("맑은 고딕", 16, "bold"),
                 bg=BG, fg=ACC).pack(pady=(PAD, 4))

        self._status_var = tk.StringVar(value="모델을 불러오는 중...")
        tk.Label(self, textvariable=self._status_var,
                 font=("맑은 고딕", 10),
                 bg=BG, fg=FG).pack(pady=(0, 8))

        frame = tk.Frame(self, bg=ACC, padx=2, pady=2)
        frame.pack(padx=PAD)

        self._canvas = tk.Canvas(frame,
                                 width=self.CANVAS_SIZE,
                                 height=self.CANVAS_SIZE,
                                 bg="white", cursor="crosshair",
                                 highlightthickness=0)
        self._canvas.pack()
        self._canvas.bind("<B1-Motion>",       self._on_draw)
        self._canvas.bind("<ButtonPress-1>",   self._on_draw)
        self._canvas.bind("<ButtonRelease-1>", lambda e: None)

        self._result_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self._result_var,
                 font=("맑은 고딕", 48, "bold"),
                 bg=BG, fg=ACC, width=3).pack(pady=(12, 0))

        self._prob_frame = tk.Frame(self, bg=BG)
        self._prob_frame.pack(padx=PAD, pady=(4, 0), fill="x")
        self._prob_bars   = []
        self._prob_labels = []
        for i in range(10):
            row = tk.Frame(self._prob_frame, bg=BG)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=str(i), width=2,
                     font=("맑은 고딕", 9), bg=BG, fg=FG).pack(side="left")
            bar = ttk.Progressbar(row, length=220, maximum=100, mode="determinate")
            bar.pack(side="left", padx=4)
            lbl = tk.Label(row, text="", width=6,
                           font=("맑은 고딕", 9), bg=BG, fg=FG)
            lbl.pack(side="left")
            self._prob_bars.append(bar)
            self._prob_labels.append(lbl)

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=PAD)

        tk.Button(btn_frame, text="인식",
                  command=self._predict,
                  font=("맑은 고딕", 11, "bold"),
                  bg=ACC, fg="#1e1e2e",
                  activebackground="#74c7ec",
                  relief="flat", padx=20, pady=6,
                  cursor="hand2").pack(side="left", padx=8)

        tk.Button(btn_frame, text="지우기",
                  command=self._clear,
                  font=("맑은 고딕", 11),
                  bg="#313244", fg=FG,
                  activebackground="#45475a",
                  relief="flat", padx=20, pady=6,
                  cursor="hand2").pack(side="left", padx=8)

    def _load_or_train(self):
        def worker():
            try:
                if os.path.exists(MODEL_PATH):
                    self._set_status("저장된 모델 불러오는 중...")
                    self.model = load_model()
                    self._set_status("준비 완료! 숫자를 그리고 [인식] 버튼을 누르세요.")
                else:
                    self._set_status("첫 실행: 모델 학습 중 (인터넷 필요)...")
                    self.model = train_and_save_model(log_callback=self._set_status)
                    self._set_status("준비 완료! 숫자를 그리고 [인식] 버튼을 누르세요.")
            except Exception as e:
                self._set_status(f"오류: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _set_status(self, msg: str):
        self.after(0, lambda: self._status_var.set(msg))

    def _on_draw(self, event):
        r = self.BRUSH_RADIUS
        x, y = event.x, event.y
        self._canvas.create_oval(x-r, y-r, x+r, y+r,
                                 fill="black", outline="black")
        self._draw.ellipse([x-r, y-r, x+r, y+r], fill="black")

    def _clear(self):
        self._canvas.delete("all")
        self._pil_image = Image.new("RGB", (self.CANVAS_SIZE, self.CANVAS_SIZE), "white")
        self._draw      = ImageDraw.Draw(self._pil_image)
        self._result_var.set("")
        for bar, lbl in zip(self._prob_bars, self._prob_labels):
            bar["value"] = 0
            lbl.config(text="")

    def _predict(self):
        if self.model is None:
            messagebox.showwarning("잠깐", "모델을 아직 준비 중입니다. 잠시 기다려 주세요.")
            return

        arr   = preprocess(self._pil_image)
        probs = self.model.predict(arr, verbose=0)[0]
        pred  = int(np.argmax(probs))

        self._result_var.set(str(pred))
        for i, (bar, lbl) in enumerate(zip(self._prob_bars, self._prob_labels)):
            pct = float(probs[i]) * 100
            bar["value"] = pct
            lbl.config(text=f"{pct:.1f}%")


if __name__ == "__main__":
    app = DigitRecognizerApp()
    app.mainloop()
