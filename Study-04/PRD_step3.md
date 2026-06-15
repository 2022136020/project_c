# PRD Step 3 — 사용자 프로필 및 레시피 저장

## 개요

| 항목 | 내용 |
|------|------|
| 기능명 | 사용자 프로필 관리 및 레시피 저장소 |
| 담당 모델 | 없음 (AI 미사용, 데이터 관리 단계) |
| 우선순위 | P1 |
| 작성일 | 2026-04-12 |
| 선행 조건 | Step 1, Step 2 완료 |

사용자 계정 시스템을 구축하여 생성된 레시피를 저장·관리한다.
프로필에는 식이 선호 설정, 저장된 레시피, 사용 이력이 포함된다.

---

## 사용자 스토리

- **US-08** 사용자는 이메일 또는 소셜 로그인으로 계정을 만들 수 있다.
- **US-09** 사용자는 마음에 드는 레시피를 저장하고 나중에 다시 볼 수 있다.
- **US-10** 사용자는 자신의 식이 제한·선호 식재료를 프로필에 저장해 매번 설정하지 않아도 된다.
- **US-11** 사용자는 저장된 레시피를 검색하고 태그로 분류할 수 있다.
- **US-12** 사용자는 레시피에 개인 메모를 추가하거나 평점을 매길 수 있다.

---

## 기능 요구사항

### FR-10 계정 관리

#### 회원가입 / 로그인
- 이메일 + 비밀번호 방식
- 비밀번호 요구사항: 8자 이상, 영문+숫자 조합
- 로그인 상태 유지: JWT 토큰 (만료: 7일), 자동 갱신

#### 보안
- 비밀번호: bcrypt 해시 저장
- JWT 시크릿: 환경변수 관리
- HTTPS 전용 (배포 시)

### FR-11 사용자 프로필 설정

프로필 페이지에서 편집 가능한 항목:

| 항목 | 타입 | 설명 |
|------|------|------|
| 닉네임 | string | 최대 20자 |
| 기본 인원수 | integer | 1~6, Step 2 기본값으로 사용 |
| 식이 제한 | multiselect | 채식 / 글루텐프리 / 유제품 제외 / 견과류 제외 |
| 선호 요리 카테고리 | multiselect | 한식 / 중식 / 양식 / 일식 / 기타 |
| 알레르기 재료 | tag input | 자유 입력, Step 2 프롬프트에 자동 반영 |
| 조리 숙련도 | select | 초보 / 중급 / 고급 |

### FR-12 레시피 저장 및 관리

#### 저장
- Step 2 레시피 카드의 "저장하기" 클릭 시 DB에 저장
- 저장 시 자동 태그 부여: 주재료명, 요리 카테고리, 난이도

#### 저장된 레시피 목록
- 정렬 기준: 저장일 / 평점 / 요리 시간 / 가나다순
- 필터: 태그, 카테고리, 난이도, 조리 시간
- 검색: 레시피 제목 / 재료명 전문 검색

#### 레시피 상세 (저장된 것)
- 원본 레시피 내용 전체 표시
- 개인 메모 추가/편집 (textarea, 최대 500자)
- 평점 (별 1~5개)
- 저장 날짜, 사용한 재료 스냅샷
- 삭제 버튼 (확인 다이얼로그 포함)

### FR-13 사용 이력

- 최근 분석한 냉장고 이미지 썸네일 (최대 10개, 30일 보관)
- 최근 생성된 레시피 이력 (저장 여부 무관, 최대 20개)
- 이력 삭제 기능

### FR-14 데이터 내보내기 / 삭제

| 기능 | 설명 |
|------|------|
| 레시피 내보내기 | 저장된 레시피 전체를 JSON 또는 PDF로 다운로드 |
| 계정 삭제 | 모든 데이터 즉시 삭제, 30일 유예 없음 |

---

## 기술 요구사항

### 데이터베이스 스키마

```sql
-- 사용자
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,          -- bcrypt hash
    nickname    TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 프로필 설정
CREATE TABLE user_profiles (
    user_id         INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_servings INTEGER DEFAULT 2,
    dietary         TEXT DEFAULT '[]',  -- JSON array
    preferred_categories TEXT DEFAULT '[]',
    allergies       TEXT DEFAULT '[]',
    skill_level     TEXT DEFAULT '보통'
);

-- 저장된 레시피
CREATE TABLE saved_recipes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,          -- 레시피 전체 JSON
    tags        TEXT DEFAULT '[]',      -- JSON array
    memo        TEXT,
    rating      INTEGER CHECK(rating BETWEEN 1 AND 5),
    model_used  TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 분석 이력
CREATE TABLE analysis_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
    thumbnail_path  TEXT,
    ingredients     TEXT,               -- JSON array
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### API 엔드포인트

```
# 인증
POST   /api/auth/signup          회원가입
POST   /api/auth/login           로그인 → JWT 반환
POST   /api/auth/logout          토큰 무효화
GET    /api/auth/me              현재 사용자 정보

# 프로필
GET    /api/profile              프로필 조회
PUT    /api/profile              프로필 수정

# 레시피
GET    /api/recipes              저장된 레시피 목록 (페이지네이션, 필터)
POST   /api/recipes              레시피 저장
GET    /api/recipes/{id}         레시피 상세
PUT    /api/recipes/{id}         메모/평점 수정
DELETE /api/recipes/{id}         레시피 삭제
GET    /api/recipes/export       전체 내보내기 (JSON)

# 이력
GET    /api/history              분석 이력 조회
DELETE /api/history/{id}         이력 삭제
```

#### 인증이 필요한 엔드포인트
모든 `/api/recipes/*`, `/api/profile`, `/api/history/*` — `Authorization: Bearer <JWT>` 헤더 필수

### 서버 구성
- **DB:** SQLite (개발) → PostgreSQL (프로덕션)
- **ORM:** SQLAlchemy (Flask-SQLAlchemy)
- **인증:** Flask-JWT-Extended
- **비밀번호 해시:** Flask-Bcrypt
- **추가 패키지:** `flask-sqlalchemy`, `flask-jwt-extended`, `flask-bcrypt`

### 프론트엔드
- **프로필 페이지:** `/profile` — 설정 폼, 저장된 레시피 탭, 이력 탭
- **네비게이션:** 헤더에 로그인/프로필 아이콘 — 인증 상태에 따라 전환
- **인증 상태 관리:** JWT를 `localStorage`에 저장, 모든 API 요청 헤더에 자동 삽입
- **페이지네이션:** 레시피 목록 무한 스크롤 (20개씩)

---

## UI 흐름

```
[헤더 네비게이션]
  - 비로그인: [로그인] [회원가입]
  - 로그인: 닉네임 + 프로필 아이콘 드롭다운
              ├─ 내 레시피 모음
              ├─ 프로필 설정
              └─ 로그아웃

[프로필 페이지 /profile]
  ├─ [프로필 설정] 탭
  │    - 닉네임, 인원수, 식이 제한, 알레르기 등 편집
  │    - [저장] 버튼
  │
  ├─ [저장된 레시피] 탭
  │    - 검색바 + 필터(카테고리/난이도/평점)
  │    - 레시피 카드 그리드
  │    - 카드 클릭 → 상세 모달
  │         ├─ 조리법 전체
  │         ├─ 메모 편집
  │         ├─ 별점
  │         └─ [삭제]
  │
  └─ [분석 이력] 탭
       - 썸네일 + 인식된 재료 요약
       - [다시 레시피 생성] 버튼 (해당 재료로 Step 2 재진입)
       - [이력 삭제] 버튼
```

---

## 완료 기준 (Definition of Done)

- [ ] 회원가입 → 로그인 → 로그아웃 플로우가 정상 작동한다.
- [ ] 프로필 설정이 저장되고 다음 Step 2 요청 시 자동 반영된다.
- [ ] 레시피 저장, 메모 추가, 평점, 삭제가 정상 작동한다.
- [ ] 저장된 레시피를 제목/재료명으로 검색할 수 있다.
- [ ] JWT 만료 시 자동 갱신 또는 재로그인 안내가 표시된다.
- [ ] 레시피 JSON 내보내기가 정상 다운로드된다.
- [ ] 계정 삭제 시 연관 데이터가 모두 삭제된다.

---

## 의존성 및 제약

- Step 1, Step 2 API가 모두 구현된 상태에서 통합
- 비로그인 사용자도 Step 1~2는 사용 가능 (저장만 제한)
- SQLite는 개발/테스트 전용 — 다중 사용자 프로덕션 환경에서는 PostgreSQL 전환 필요
- 이미지 썸네일은 서버 로컬 파일시스템에 저장 (프로덕션 시 S3 등 오브젝트 스토리지 고려)
- GDPR/개인정보보호법 준수: 사용자 데이터 수집 최소화, 삭제 요청 즉시 처리
