# PRD Step 1 — 냉장고 이미지 인식

## 개요

| 항목 | 내용 |
|------|------|
| 기능명 | 냉장고 이미지 업로드 및 재료 인식 |
| 담당 모델 | `google/gemma-3-27b-it:free` (OpenRouter) |
| 우선순위 | P0 (기반 기능) |
| 작성일 | 2026-04-12 |

사용자가 냉장고 사진을 업로드하면, Gemma 비전 모델이 이미지를 분석해 재료 목록을 추출한다.
이 결과는 Step 2의 레시피 생성 입력값으로 전달된다.

---

## 사용자 스토리

- **US-01** 사용자는 냉장고 사진을 업로드해서 현재 보유한 재료를 자동으로 파악할 수 있다.
- **US-02** 사용자는 인식된 재료 목록을 확인하고 수동으로 추가·삭제할 수 있다.
- **US-03** 사용자는 인식 결과를 기반으로 다음 단계(레시피 생성)로 진행할 수 있다.

---

## 기능 요구사항

### FR-01 이미지 업로드
- 드래그 앤 드롭 및 파일 선택 버튼 모두 지원
- 허용 형식: `image/jpeg`, `image/png`, `image/webp`
- 최대 파일 크기: 10 MB
- 업로드 즉시 미리보기 표시

### FR-02 이미지 분석 요청
- 업로드된 이미지를 Base64로 인코딩하여 OpenRouter API에 전송
- 사용 모델: `google/gemma-3-27b-it:free`
- 시스템 프롬프트 (서버 고정):
  ```
  You are a kitchen assistant. Analyze the fridge image and list all visible food ingredients.
  Return a JSON array of objects with keys: name (Korean), quantity (estimated), category (채소/육류/유제품/조미료/기타).
  Example: [{"name":"당근","quantity":"2개","category":"채소"}, ...]
  ```
- 응답 형식: JSON 배열 (파싱 실패 시 원문 텍스트로 폴백)

### FR-03 재료 목록 표시 및 편집
- 인식된 재료를 카테고리별로 그룹화하여 카드 형태로 표시
- 각 재료 항목에 삭제(X) 버튼 제공
- 재료 직접 추가 입력 필드 (이름 + 수량)
- "레시피 생성하기" 버튼 — 최소 1개 이상의 재료가 있을 때 활성화

### FR-04 오류 처리
| 상황 | 처리 방법 |
|------|-----------|
| 이미지 크기 초과 | 업로드 전 클라이언트 검증 후 안내 메시지 |
| API 429 Rate Limit | "잠시 후 다시 시도해 주세요" 메시지 + 재시도 버튼 |
| API 응답 JSON 파싱 실패 | 원문을 그대로 표시하고 수동 입력 유도 |
| 네트워크 오류 | 재시도 버튼 노출 |

---

## 기술 요구사항

### 백엔드 (`/api/analyze`)
```
POST /api/analyze
Content-Type: multipart/form-data

Request
  - image: File

Response 200
  {
    "ingredients": [
      { "name": "당근", "quantity": "2개", "category": "채소" },
      ...
    ],
    "raw_text": "...",   // JSON 파싱 실패 시 사용
    "model": "google/gemma-3-27b-it:free"
  }

Response 429
  { "error": "rate_limit", "retry_after": 60 }

Response 500
  { "error": "analysis_failed", "message": "..." }
```

### 서버 구성
- **프레임워크:** Flask
- **이미지 처리:** Pillow — 업로드 이미지를 최대 1024px로 리사이즈 후 Base64 인코딩
- **API 호출:** `requests` 라이브러리, timeout=60s
- **환경변수:** `OPENROUTER_API_KEY` (.env)

### 프론트엔드
- **구조:** 단일 HTML 파일 + Vanilla JS (Alpine.js 또는 순수 JS)
- **업로드 영역:** 드래그 앤 드롭 + `<input type="file">`
- **로딩 상태:** 스피너 + "재료를 인식하는 중..." 메시지
- **상태 관리:** 업로드됨 → 분석 중 → 결과 표시 → 편집 완료

---

## UI 흐름

```
[홈 화면]
  └─ 이미지 업로드 영역 (드래그 앤 드롭 / 파일 선택)
        │
        ▼ 업로드 완료
  [이미지 미리보기 + "분석하기" 버튼]
        │
        ▼ 분석 중
  [로딩 스피너]
        │
        ▼ 분석 완료
  [재료 목록 카드 (카테고리별)]
    - 각 항목: 이름, 수량, 삭제 버튼
    - 재료 추가 입력 필드
    - [레시피 생성하기 →] 버튼
```

---

## 완료 기준 (Definition of Done)

- [ ] 이미지 업로드 후 30초 이내에 재료 목록이 표시된다.
- [ ] 인식된 재료가 카테고리별로 정렬되어 표시된다.
- [ ] 재료 추가·삭제가 즉시 반영된다.
- [ ] 429 오류 시 사용자에게 안내 메시지가 표시된다.
- [ ] "레시피 생성하기" 클릭 시 재료 목록이 Step 2로 전달된다.

---

## 의존성 및 제약

- OpenRouter free tier: 분당 요청 제한 존재 — 연속 요청 방지 UI 필요
- `google/gemma-3-27b-it:free` 비전 지원 확인 완료 (`text+image->text`)
- Step 2(레시피 생성)는 이 단계의 재료 목록 JSON을 입력으로 받음
