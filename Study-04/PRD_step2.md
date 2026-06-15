# PRD Step 2 — 레시피 생성

## 개요

| 항목 | 내용 |
|------|------|
| 기능명 | 재료 기반 레시피 추천 및 생성 |
| 담당 모델 | `qwen/qwen3.6-plus:free` (OpenRouter) |
| 우선순위 | P0 |
| 작성일 | 2026-04-12 |
| 선행 조건 | Step 1에서 재료 목록 JSON이 전달되어야 함 |

Step 1에서 추출한 재료 목록을 입력받아 Qwen 모델로 맞춤형 레시피를 생성한다.
사용자가 선호 조건(인원수, 요리 시간, 식이 제한)을 설정하면 최적화된 레시피를 제안한다.

> **참고:** `qwen/qwen3.6-plus:free`가 OpenRouter에서 deprecated된 경우,
> 동일 벤더의 사용 가능한 최신 free 모델로 대체한다.
> 교체 후 이 문서의 모델 ID를 업데이트한다.

---

## 사용자 스토리

- **US-04** 사용자는 인식된 재료를 바탕으로 만들 수 있는 레시피 목록을 받아볼 수 있다.
- **US-05** 사용자는 인원수, 조리 시간, 식이 제한을 설정해 레시피를 필터링할 수 있다.
- **US-06** 사용자는 레시피별 상세 조리법(단계별)을 확인할 수 있다.
- **US-07** 사용자는 마음에 드는 레시피를 저장 목록에 추가할 수 있다(Step 3 연계).

---

## 기능 요구사항

### FR-05 레시피 생성 옵션 설정
레시피 생성 전 사용자가 선택할 수 있는 옵션:

| 옵션 | 입력 방식 | 기본값 |
|------|-----------|--------|
| 추천 레시피 수 | 1 / 2 / 3 선택 | 2 |
| 인원수 | 1~6명 슬라이더 | 2명 |
| 최대 조리 시간 | 15 / 30 / 60 / 제한 없음 | 30분 |
| 식이 제한 | 없음 / 채식 / 글루텐프리 / 유제품 제외 | 없음 |
| 난이도 | 쉬움 / 보통 / 어려움 | 보통 |

### FR-06 레시피 생성 요청
- 재료 목록 + 사용자 옵션을 결합하여 Qwen 모델에 전송
- 사용 모델: `qwen/qwen3.6-plus:free`
- 시스템 프롬프트 (서버 고정):
  ```
  You are a professional chef and recipe creator.
  Based on the given ingredients, suggest Korean home-cooking recipes.
  Return a JSON array. Each recipe must include:
    - title (string, Korean)
    - description (string, 2 sentences max)
    - difficulty (쉬움/보통/어려움)
    - cook_time (minutes, integer)
    - servings (integer)
    - ingredients (array: {name, amount, note?})
    - steps (array of strings, numbered instructions)
    - tips (array of strings, optional cooking tips)
    - missing_ingredients (array: ingredients not in the fridge but needed)
  ```
- 응답 형식: JSON 배열 (파싱 실패 시 마크다운 원문으로 폴백)

### FR-07 레시피 결과 표시
- 레시피 카드 목록 (제목, 설명, 조리 시간, 난이도 배지)
- 카드 클릭 시 상세 모달/섹션 확장:
  - 필요 재료 목록 (보유 재료 강조 표시, 없는 재료는 빨간색)
  - 단계별 조리법 (번호 리스트)
  - 조리 팁
- "저장하기" 버튼 (로그인 상태일 때 활성화, Step 3 연계)
- "다시 생성하기" 버튼 — 같은 재료로 새 레시피 재요청

### FR-08 없는 재료 안내
- 레시피에 필요하지만 냉장고에 없는 재료를 별도 섹션으로 표시
- "쇼핑 목록에 추가" 버튼 (클립보드 복사 또는 Step 3 저장)

### FR-09 오류 처리

| 상황 | 처리 방법 |
|------|-----------|
| API 429 Rate Limit | 남은 대기 시간 카운트다운 표시 후 자동 재시도 |
| 모델 Deprecated | 서버에서 대체 모델로 폴백, 사용 모델명 응답에 포함 |
| JSON 파싱 실패 | 마크다운 형식으로 원문 표시 |
| 재료 0개 | "재료를 1개 이상 선택해 주세요" 안내 |

---

## 기술 요구사항

### 백엔드 (`/api/recipe`)
```
POST /api/recipe
Content-Type: application/json

Request
  {
    "ingredients": [
      { "name": "당근", "quantity": "2개", "category": "채소" },
      ...
    ],
    "options": {
      "count": 2,
      "servings": 2,
      "max_time": 30,
      "dietary": "none",
      "difficulty": "보통"
    }
  }

Response 200
  {
    "recipes": [
      {
        "title": "당근 볶음밥",
        "description": "...",
        "difficulty": "쉬움",
        "cook_time": 20,
        "servings": 2,
        "ingredients": [...],
        "steps": ["1. ...", "2. ..."],
        "tips": ["..."],
        "missing_ingredients": ["계란"]
      }
    ],
    "model_used": "qwen/qwen3.6-plus:free"
  }

Response 429
  { "error": "rate_limit", "retry_after": 60 }
```

### 서버 구성
- 엔드포인트: `/api/recipe` (Step 1의 Flask 앱에 추가)
- 프롬프트 조합: 재료 JSON + 옵션을 템플릿 문자열로 합성
- 모델 폴백 로직:
  ```python
  RECIPE_MODELS = [
      "qwen/qwen3.6-plus:free",
      "qwen/qwen3-coder:free",          # 1차 폴백
      "google/gemma-3-4b-it:free",      # 2차 폴백
  ]
  ```
- 응답 캐시: 동일 재료+옵션 조합은 10분간 서버 메모리 캐시 (중복 API 호출 방지)

### 프론트엔드
- 옵션 설정 폼 → 제출 시 재료 목록과 함께 `/api/recipe` POST
- 로딩 상태: "레시피를 생성하는 중..." + 예상 대기 시간 표시
- 레시피 카드: CSS 그리드, 반응형

---

## UI 흐름

```
[Step 1 결과 화면 → "레시피 생성하기" 클릭]
        │
        ▼
  [레시피 옵션 설정]
    - 인원수 / 조리 시간 / 식이 제한 / 난이도
    - [생성하기] 버튼
        │
        ▼ 생성 중
  [로딩 상태 (예상 10~30초)]
        │
        ▼ 완료
  [레시피 카드 목록]
    - 카드: 제목, 설명, 시간, 난이도 배지
    - 클릭 → 상세 펼치기
        ├─ 재료 목록 (보유/미보유 구분)
        ├─ 단계별 조리법
        ├─ 조리 팁
        └─ [저장하기] [다시 생성하기]
```

---

## 완료 기준 (Definition of Done)

- [ ] 재료 목록과 옵션을 입력하면 60초 이내에 레시피가 표시된다.
- [ ] 레시피에 제목, 재료, 단계별 조리법이 모두 포함된다.
- [ ] 없는 재료와 보유 재료가 시각적으로 구분된다.
- [ ] 모델이 deprecated일 때 폴백 모델로 자동 전환된다.
- [ ] 같은 재료 조합 재요청 시 캐시로 즉시 응답한다.
- [ ] "저장하기" 클릭 시 Step 3의 프로필로 레시피가 전달된다.

---

## 의존성 및 제약

- Step 1 완료 필수 (재료 목록 JSON 형식 준수)
- `qwen/qwen3.6-plus:free` deprecated 확인 — 서버에서 폴백 처리
- OpenRouter free tier 특성상 응답에 10~30초 소요 가능 — 로딩 UI 필수
- Step 3(사용자 프로필)이 없어도 레시피 조회는 가능해야 함 (저장만 제한)
