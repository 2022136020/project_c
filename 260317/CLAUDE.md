# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# 패키지 설치
pip install -r requirements.txt

# 실행
python digit_recognition.py
```

Windows 탐색기에서는 `숫자인식_실행.bat` 더블클릭으로 실행 (패키지 자동 설치 포함).

## Architecture

단일 파일(`digit_recognition.py`) 구조로, 세 개의 계층이 순차적으로 의존한다.

```
train_and_save_model / load_model   ← TensorFlow/Keras, MNIST
        ↓
    preprocess()                    ← PIL 이미지 → (1,28,28) numpy 배열
        ↓
  DigitRecognizerApp (tkinter)      ← GUI, 캔버스 드로잉, 결과 표시
```

**모델 학습 흐름**
- 앱 시작 시 `_load_or_train()`이 백그라운드 스레드에서 실행된다.
- `digit_model.keras`가 있으면 로드, 없으면 MNIST를 다운로드해 CNN을 학습 후 저장한다.
- 학습된 모델 파일은 스크립트와 같은 디렉터리에 저장된다.

**이미지 전처리 (`preprocess`)**
- 캔버스는 흰 배경에 검정 글씨로 그려진다.
- MNIST는 검정 배경에 흰 글씨이므로, `ImageOps.invert`로 반전한다.
- 글씨 영역을 `getbbox()`로 크롭 → 여백 추가 → 28×28 리사이즈 순으로 정규화한다.

**드로잉 동기화**
- tkinter Canvas(`_canvas`)와 PIL `_pil_image`를 동시에 업데이트한다.
- Canvas는 화면 표시용, PIL 이미지는 실제 예측 입력으로 사용된다.
- `_clear()` 시 두 객체를 모두 초기화해야 한다.

## Key Constants

| 상수 | 위치 | 설명 |
|------|------|------|
| `MODEL_PATH` | 모듈 최상단 | 모델 저장 경로 |
| `CANVAS_SIZE` | `DigitRecognizerApp` | 캔버스 픽셀 크기 (기본 280) |
| `BRUSH_RADIUS` | `DigitRecognizerApp` | 브러시 반지름 (기본 12) |

## CNN 모델 구조

Conv2D(32) → MaxPool → Conv2D(64) → MaxPool → Flatten → Dense(128) → Dropout(0.3) → Dense(10, softmax)

입력: `(batch, 28, 28)` — `Reshape` 레이어가 내부에서 `(batch, 28, 28, 1)`로 변환한다.
