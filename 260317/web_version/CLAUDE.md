<!-- Created: 2026-03-17 -->
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

```bash
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

Windows 탐색기에서는 `웹서버_실행.bat` 더블클릭 (패키지 자동 설치 + 브라우저 자동 열기).

## Architecture

```
브라우저 (HTML Canvas + JS)
    │  POST /predict  { image: base64 PNG }
    ▼
Flask app.py
    ├── GET  /         → templates/index.html 렌더링
    ├── POST /predict  → preprocess() → model.predict() → JSON 응답
    └── GET  /status   → 모델 준비 여부 { ready: bool }
```

**모델 싱글턴 (`_model` 전역)**
- `get_model()`이 `threading.Lock`으로 보호된 싱글턴을 반환한다.
- 서버 시작 시 백그라운드 스레드로 미리 로드(`digit_model.keras` 있으면 로드, 없으면 학습·저장).
- `/status` 엔드포인트로 프론트엔드가 3초마다 준비 여부를 폴링한다.

**`preprocess()` — 데스크톱 버전과 동일한 로직**
1. PNG base64 → `PIL.Image`
2. 그레이스케일 변환 → `ImageOps.invert` (흰 배경·검정 글씨 → MNIST 형식)
3. `getbbox()` 크롭 → 20% 여백 → 28×28 리사이즈

**프론트엔드 (`static/js/main.js`)**
- `<canvas>` 위에 마우스/터치 이벤트로 직접 그린다 (`BRUSH_RADIUS = 12`).
- 인식 버튼 클릭 시 `canvas.toDataURL("image/png")`를 base64로 변환해 `/predict`에 POST.
- 응답의 `probabilities[10]`로 각 숫자별 확률 바를 업데이트한다.

## File Layout

```
web_version/
├── app.py                  # Flask 서버, 모델 관리, /predict 엔드포인트
├── templates/
│   └── index.html          # 단일 페이지 UI
└── static/
    ├── css/style.css       # 다크 테마 스타일
    └── js/main.js          # 캔버스 드로잉 + fetch API 통신
```

## API

| 엔드포인트 | 메서드 | 요청 | 응답 |
|------------|--------|------|------|
| `/` | GET | — | HTML |
| `/predict` | POST | `{ "image": "data:image/png;base64,..." }` | `{ "prediction": int, "probabilities": [float×10] }` |
| `/status` | GET | — | `{ "ready": bool }` |
