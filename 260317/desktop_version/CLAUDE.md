<!-- Created: 2026-03-17 -->
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

```bash
pip install -r requirements.txt
python digit_recognition.py
```

Windows 탐색기에서는 `숫자인식_실행.bat` 더블클릭 (패키지 자동 설치 포함).

## Architecture

단일 파일(`digit_recognition.py`) 안에 세 계층이 순서대로 의존한다.

```
train_and_save_model / load_model   ← TensorFlow/Keras + MNIST
        ↓
    preprocess()                    ← PIL 이미지 → (1,28,28) numpy 배열
        ↓
  DigitRecognizerApp (tkinter.Tk)   ← GUI, 드로잉, 결과 표시
```

**모델 생애주기**
- 앱 시작 시 `_load_or_train()`이 백그라운드 스레드에서 실행된다.
- `digit_model.keras`가 스크립트와 같은 디렉터리에 있으면 로드, 없으면 MNIST 다운로드 후 학습·저장.
- 학습 중 상태 메시지는 `self.after(0, ...)` 로 메인 스레드에 전달한다 (`_set_status`).

**드로잉 이중 버퍼**
- tkinter `Canvas`(화면 표시)와 PIL `Image`(예측 입력)를 항상 동시에 업데이트한다.
- `_clear()` 시 두 객체를 모두 새로 생성해야 일관성이 유지된다.

**`preprocess()` 핵심 흐름**
1. `ImageOps.invert` — 흰 배경·검정 글씨 → MNIST 형식(검정 배경·흰 글씨)으로 반전
2. `getbbox()` 크롭 → 20% 여백 추가 → 28×28 리사이즈

## Key Constants

| 상수 | 설명 |
|------|------|
| `MODEL_PATH` | 모델 저장 경로 (스크립트 디렉터리 기준) |
| `CANVAS_SIZE = 280` | 캔버스 픽셀 크기 |
| `BRUSH_RADIUS = 12` | 브러시 반지름 |

## CNN 구조

`Input(28,28)` → `Reshape(28,28,1)` → `Conv2D(32)` → `MaxPool` → `Conv2D(64)` → `MaxPool` → `Flatten` → `Dense(128, relu)` → `Dropout(0.3)` → `Dense(10, softmax)`
