# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Layout

```
260317/
├── desktop_version/    # tkinter GUI 앱
│   ├── digit_recognition.py
│   ├── digit_model.keras       # 학습된 모델 (없으면 자동 학습)
│   └── 숫자인식_실행.bat
└── web_version/        # Flask 웹 서버
    ├── app.py
    ├── digit_model.keras
    ├── handwriting_model.keras  # 문자(A-Z) 포함 확장 모델
    ├── 웹서버_실행.bat
    ├── templates/index.html
    └── static/{css,js}
```

## Running

**Desktop (tkinter):**
```bash
cd 260317/desktop_version
pip install -r requirements.txt
python digit_recognition.py
```

**Web (Flask):**
```bash
cd 260317/web_version
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

Windows에서는 각 디렉터리의 `.bat` 파일을 더블클릭하면 패키지 설치 후 실행됩니다.

## Architecture

두 버전 모두 동일한 3계층 구조를 공유한다:

```
모델 계층: TensorFlow/Keras CNN (digit_model.keras / handwriting_model.keras)
     ↓
전처리 계층: preprocess() — PIL invert → getbbox 크롭 → 28×28 리사이즈
     ↓
표현 계층: tkinter GUI  또는  Flask REST API + HTML5 Canvas
```

**모델 생애주기 (공통)**
- 앱/서버 시작 시 백그라운드 스레드에서 `_load_or_train()` 실행.
- `.keras` 파일이 있으면 로드, 없으면 데이터셋 다운로드 후 학습·저장.
- Desktop: `self.after(0, ...)` 로 상태 메시지를 메인 스레드에 전달.
- Web: `threading.Lock` 싱글턴 + `/status` 폴링(3초 간격)으로 준비 여부 확인.

**CNN 구조 (digit_model — digits only)**
`Input(28,28)` → `Reshape(28,28,1)` → `Conv2D(32)` → `MaxPool` → `Conv2D(64)` → `MaxPool` → `Flatten` → `Dense(128, relu)` → `Dropout(0.3)` → `Dense(10, softmax)`

**CNN 구조 (handwriting_model — digits + A-Z, web only)**
`Input(28,28)` → `Reshape(28,28,1)` → `Conv2D(32)` → `MaxPool` → `Dropout(0.25)` → `Conv2D(64)` → `MaxPool` → `Dropout(0.25)` → `Flatten` → `Dense(512, relu)` → `Dropout(0.4)` → `Dense(36, softmax)`

**preprocess() 핵심 흐름**
1. 그레이스케일 변환
2. `ImageOps.invert` — 흰 배경·검정 글씨 → 검정 배경·흰 글씨(MNIST 형식)
3. `getbbox()` 크롭 → 20% 여백 추가 → 28×28 리사이즈 (LANCZOS)

## Web API

| 엔드포인트 | 메서드 | 요청 | 응답 |
|------------|--------|------|------|
| `/` | GET | — | HTML |
| `/predict` | POST | `{ "image": "data:image/png;base64,..." }` | `{ "prediction": int, "probabilities": [float×N] }` |
| `/status` | GET | — | `{ "ready": bool }` |

각 버전의 상세 문서는 해당 디렉터리의 `CLAUDE.md`를 참조하세요.

퀴즈 문제 교차 검증 가이드라인
모든 문제 작성 시 확인 사항
1. 정답이 하나뿐인가?- 다른 해석 가능 시 조건 명시 (예: 면적 기준, 2024년 기준)
2. 최상급 표현에 기준이 있는가?- '가장 큰', '최초의' 등 표현에 측정 기준 명시
3. 시간과 범위가 명확한가?- 변할 수 있는 정보는 시점 명시- 지리적, 분류적 범위 한정
4. 교차 검증했는가?- 의심스러운 정보는 2개 이상 출처 확인- 논란 있는 내용은 주류 학설 기준
