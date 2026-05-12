# 인수인계 문서 (Handover Document)

> 작성일: 2026-05-12 | 작성자: seonghyeon | 모델: Claude Sonnet 4.6

---

## 개요

이 저장소(`project_c`)는 여러 개의 독립적인 프로젝트를 담은 모노레포입니다.
각 디렉터리는 별개의 프로젝트이며, 학습·실험·실용 목적이 혼재합니다.

`portfolio-tracker/`는 **수업 과제 프로젝트(Vibe Coding Project)**이며 평가 대상입니다.
나머지는 수업 중 실습하거나 별도로 개발한 프로젝트입니다.

---

## [최우선] 수업 과제: Vibe Coding Project

### 과목 개요

| 항목 | 내용 |
|------|------|
| 과목 | 앱 프로그래밍 응용 |
| 프로젝트명 | Vibe Coding Project |
| 형식 | AI Agent 기반 7세션 프로젝트 |
| 팀 구성 | 1인 (seonghyeon) |
| 대상 프로젝트 | `portfolio-tracker/` (Flutter 자산 포트폴리오 트래커) |

### 세션 일정 (9주차 ~ 15주차)

| 세션 | 주차 | 주제 | 핵심 산출물 | 상태 |
|------|------|------|------------|------|
| 1 | 9주차 | 오리엔테이션 | 팀 결정, 주제 선정 | ✅ 완료 |
| 2 | 10주차 | 기획 & 일정 수립 | `.planning/*`, WBS, 일정표, BONUS.md | 🔄 진행 중 |
| 3 | 11주차 | 설계 & 환경 구축 | `docs/architecture.md`, Hello World 실행 | ⬜ 미완료 |
| 4 | 12주차 | 구현 1 + 중간발표 | 동작하는 프로토타입 | ⬜ 미완료 |
| 5 | 13주차 | 구현 2 + 테스트 | 핵심 기능 완성 | ⬜ 미완료 |
| 6 | 14주차 | 마감 & 배포 & 발표 준비 | 배포 산출물, 문서, 앱 결과물 PPT | ⬜ 미완료 |
| 7 | 15주차 | 최종 발표 | 발표 자료, 회고 | ⬜ 미완료 |

### 평가 구조

**과제 점수 — 5점 (문서 단계별 가산)**

| 단계 | 조건 | 현재 |
|------|------|------|
| +1 | 기획서/요구사항 | ✅ 확보 (`00-vision.md`, `01-requirements.md`) |
| +2 | + WBS·일정 | ❌ 미확보 (`02-wbs.md`, `04-schedule.md` 없음) |
| +3 | + 아키텍처·ADR | ⬜ 미완료 |
| +4 | + setup·deploy·testing 문서 | ⬜ 미완료 |
| +5 | + AGENTS.md·README 완비 | ✅ AGENTS.md 있음, README 미완료 |

**발표 점수 — 30점**

| 항목 | 배점 | 비고 |
|------|------|------|
| 발표 체계성 | 10점 | 구조, 시간 관리 |
| 질의응답 | 8점 | 즉답성, 솔직함 |
| 개발자 기본 소양 | 12점 | 플랫폼 선택 이유, 구조, 빌드/배포/테스트 설명 |

> 개발자 소양 질문 예시: "Flutter를 선택한 이유는?", "앱 레이어 구조는?", "Firebase 설정은 처음부터 어떻게?", "테스트는 어떻게 작성하나?"

**가산점 — 최대 +6점**

| 항목 | 점수 | 현재 상태 | 증빙 필요 |
|------|------|-----------|----------|
| A. AI Agent/스킬/워크플로우 활용 | +1 | 🔄 준비 중 | Claude Code 사용 목록 + 절약 사례 1개 이상 |
| B. 본인만의 기법 (AUTHORING.md) | +2 | ✅ 파일 있음 | 말로 2~3분 설명 준비 필요 |
| C. LLM Wiki 암묵지 운영 | +1 | ⬜ 미완료 | 10개 이상 항목, 출처 명시 |
| D. AI Agent 리포트 발표 (10분+) | +2 | ⬜ 미완료 | 별도 시간 신청, 최근 6개월 내 주제 |

### 지금 당장 해야 할 일 (10주차 마감)

1. ❌ `.planning/02-wbs.md` 생성 — WBS 작업 분해 구조 (과제 +2점 조건)
2. ❌ `.planning/04-schedule.md` 생성 — 10~15주차 6주 일정표 (과제 +2점 조건)
3. ❌ `BONUS.md` 생성 — 신청할 가산점 항목(A/B/C/D) + 증빙 정리
4. ❌ 위 3개 파일 GitHub push

### 이후 순서별 해야 할 일

| 우선순위 | 항목 | 목표 주차 |
|----------|------|-----------|
| 1 | `02-wbs.md`, `04-schedule.md`, `BONUS.md` 작성 + push | 10주차 |
| 2 | Firebase 프로젝트 생성 + `google-services.json` 발급 | 11주차 |
| 3 | Firebase Auth 연동 (이메일/Google 로그인) | 11주차 |
| 4 | `docs/architecture.md` 작성 (과제 +3점 조건) | 11주차 |
| 5 | Hello World Flutter 앱 실행 확인 | 11주차 |
| 6 | 계좌 관리 + 포지션 기록 기능 구현 | 12~13주차 |
| 7 | setup/deploy/testing 문서 작성 (과제 +4점 조건) | 14주차 |
| 8 | README 완비 (과제 +5점 조건) | 14주차 |
| 9 | 가산점 A: Claude Code 활용 사례 정리 → BONUS.md 반영 | 수시 |
| 10 | 가산점 C: LLM Wiki 10개 이상 항목 작성 | 수시 |

### 기획 결정 사항 (2026-05-12 기준)

| 항목 | 결정 내용 |
|------|-----------|
| 비전 (현재) | "되돌아보는 투자자가 앞으로 나아간다" |
| 비전 (소비 기능 추가 시) | "매일의 소비와 투자가 쌓여 내일의 나를 만든다" |
| 소비 내역 관리 | 보류 — 실계좌 연동 불가, 현실적 대안 없음 |
| 가상 계좌 | 채택 — 실제 계좌 유사 기능을 수동 관리 |
| 커뮤니티 게시판 | 제외 — 핵심 가치와 거리 있음 |
| 실시간 시세·API 연동 | 제외 — 구현 불가 |

### 핵심 참고 파일

| 파일 | 내용 |
|------|------|
| `portfolio-tracker/.planning/00-vision.md` | 비전 · 문제 정의 · 사용자 시나리오 · 범위 결정 |
| `portfolio-tracker/.planning/01-requirements.md` | MoSCoW 요구사항 (최신) |
| `portfolio-tracker/.planning/02-wbs.md` | WBS 작업 분해 구조 |
| `portfolio-tracker/.planning/04-schedule.md` | 6주 일정표 (11~15주차) |
| `portfolio-tracker/.planning/05-risks.md` | 위험 식별 및 대응 (7개) |
| `portfolio-tracker/BONUS.md` | 가산점 신청 항목 및 증빙 |
| `portfolio-tracker/.planning/02-prd.md` | 상세 기능 명세 (PRD, 구버전 참고용) |
| `portfolio-tracker/AGENTS.md` | AI Agent 운영 규칙 |
| `portfolio-tracker/AUTHORING.Jooseonghyeon.v0.1.0.md` | 가산점 B 증빙 파일 |
| `Downloads/9주차/resources/03-bonus-points.md` | 가산점 상세 가이드 |

---

## 전체 프로젝트 목록

| 디렉터리 | 프로젝트명 | 기술 스택 | 상태 |
|----------|-----------|-----------|------|
| `260317/` | 손글씨 숫자 인식기 | Python, TensorFlow, tkinter, Flask | ✅ 완료 |
| `Study-03/` | 상식 퀴즈 게임 | HTML/CSS/Vanilla JS | ✅ 완료 |
| `Study-04/` | AI 냉장고 레시피 생성기 | Python, Flask, OpenRouter API | 🔄 진행 중 |
| `exam/` | 시험지 PDF 정리 도구 | Python, Flask, Claude API | ✅ 완료 |
| `pdf_quiz_app/` | PDF 퀴즈 앱 | Node.js (Express), MCP Server | 🔄 진행 중 |
| `portfolio-tracker/` | 자산 포트폴리오 트래커 (**과제**) | Flutter, Firebase | 🔄 진행 중 |

---

## 프로젝트별 요약

### 1. 손글씨 숫자 인식기 (`260317/`)
- **목적**: 캔버스에 손으로 쓴 숫자(0-9) 및 알파벳(A-Z)을 CNN으로 인식
- **두 가지 버전**: tkinter GUI (`desktop_version/`) + Flask 웹서버 (`web_version/`)
- **모델**: MNIST 기반 CNN, `.keras` 파일로 저장. 파일 없으면 앱 시작 시 자동 학습
- **실행**: 각 디렉터리의 `.bat` 파일 더블클릭 (Windows)
- **상세 문서**: `260317/CLAUDE.md`, 루트 `CLAUDE.md`

### 2. 상식 퀴즈 게임 (`Study-03/`)
- **목적**: 한국사·과학·지리·일반상식 4개 카테고리, 총 40문제 4지선다 퀴즈
- **기술**: 순수 HTML/CSS/JS 단일 파일 앱 (`index.html`)
- **실행**: `python -m http.server 8080` 후 브라우저 접속 (fetch 때문에 로컬 서버 필요)
- **문제 데이터**: `questions.json` (카테고리별 10문제씩)
- **순위**: `localStorage`에 저장
- **상세 문서**: `Study-03/PRD.md`, `Study-03/CLAUDE.md`

### 3. AI 냉장고 레시피 생성기 (`Study-04/`)
- **목적**: 냉장고 사진 업로드 → 재료 인식 → 레시피 추천 (3단계 파이프라인)
- **기술**: Flask 백엔드, OpenRouter API (`google/gemma-3-27b-it:free`)
- **환경변수**: `.env`에 `OPENROUTER_API_KEY` 필요 (`.env.example` 참조)
- **현재 구현**: Step 1 (이미지 → 재료 인식) 완료. Step 2, 3 미완료
- **상세 문서**: `Study-04/PRD_step1.md`, `PRD_step2.md`, `PRD_step3.md`

### 4. 시험지 PDF 정리 도구 (`exam/`)
- **목적**: 시험지 이미지를 업로드하면 Claude API로 내용을 추출하여 PDF로 변환
- **기술**: Flask 웹서버, Claude API (Anthropic), ReportLab (PDF 생성)
- **실행**: `시험지정리_실행.bat` 또는 `python app.py` → `http://localhost:5002`
- **제한**: 최대 5페이지, 결과 PDF는 30분 후 자동 삭제
- **API**: POST `/process` (이미지 업로드 + API 키) → GET `/download/<id>`

### 5. PDF 퀴즈 앱 (`pdf_quiz_app/`)
- **목적**: PDF 문서에서 퀴즈를 자동 생성하고 MCP 서버로 제공
- **구성**: `mcp_server/` (MCP 프로토콜 서버) + `web_app/` (Node.js Express 웹앱)
- **환경변수**: `web_app/.env`에 API 키 필요
- **실행**: `실행.bat`

### 6. 자산 포트폴리오 트래커 (`portfolio-tracker/`) — 수업 과제
- **목적**: 주식·코인 포지션 기록, 수익률 계산, 자산 시각화
- **기술**: Flutter (Android/iOS 크로스플랫폼), Firebase (Auth + Firestore)
- **현재 상태**: Flutter 프로젝트 초기 세팅 완료. 기획 문서 일부 작성됨
- **상세**: 위 [최우선] 섹션 참조

---

## 공통 환경 설정

```bash
# Python 프로젝트
pip install -r requirements.txt

# Node.js 프로젝트
npm install

# Flutter 프로젝트
flutter pub get
flutter run
```

---

## 저장소 구조

```
project_c/
├── HANDOVER.md          ← 이 파일 (인수인계 문서)
├── PROGRESS.md          ← 전체 진행 현황
├── CLAUDE.md            ← Claude Code 지침
├── 260317/              ← 손글씨 숫자 인식기
├── Study-03/            ← 상식 퀴즈 게임
├── Study-04/            ← AI 냉장고 레시피 생성기
├── exam/                ← 시험지 PDF 정리 도구
├── pdf_quiz_app/        ← PDF 퀴즈 앱
└── portfolio-tracker/   ← 자산 포트폴리오 트래커 (수업 과제)
```

---

## 주의사항

- `.env` 파일은 `.gitignore`에 포함되어 저장소에 없음 — 각 `.env.example` 참고
- `portfolio-tracker`의 Firebase 설정 파일(`google-services.json`)은 별도 발급 필요
- 모델 파일(`.keras`)은 없으면 앱 시작 시 자동 학습 (인터넷 연결 필요)
