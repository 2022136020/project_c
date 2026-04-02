# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

상식 퀴즈 게임 — 한국사, 과학, 지리, 일반상식 4개 카테고리, 카테고리별 10문제 × 4 = 총 40문제의 4지선다 웹 퀴즈 게임.

## 파일 구조

```
Study-03/
├── PRD.md              # 제품 요구사항 문서 (기능·데이터 명세 원본)
├── prompts.md          # Claude Code용 3단계 구현 프롬프트
├── questions.json      # 퀴즈 문제 데이터 (40문제, 생성 후 추가됨)
├── index.html          # 퀴즈 게임 단일 파일 앱 (생성 후 추가됨)
└── .claude/
    └── commands/
        └── quiz-validate.md  # /quiz-validate 슬래시 커맨드
```

## 개발 순서

`prompts.md`의 3단계 프롬프트를 순서대로 실행한다.

1. **1단계**: `questions.json` 생성 → `/quiz-validate`로 검증
2. **2단계**: `index.html` 구현 (순수 HTML/CSS/JS 단일 파일)
3. **3단계**: 기능·UI 검증 후 `README.md` 작성

## 실행 방법

`questions.json`을 fetch로 로드하므로 로컬 서버가 필요하다.

```bash
# Python 3
python -m http.server 8080
# 이후 브라우저에서 http://localhost:8080 접속
```

## 아키텍처

단일 파일(`index.html`) 안에서 화면 전환을 JS로 처리한다.

```
[시작 화면] → [문제 화면] → [피드백] → [결과 화면] → [순위표]
                               ↑ 즉시 표시 (클릭 후 0.3초 이내)
```

- **데이터**: `questions.json` fetch → 메모리 로드 → 카테고리별 셔플
- **상태 관리**: JS 전역 변수 (currentIndex, score, answers)
- **순위 저장**: `localStorage` (브라우저 종료 후에도 유지)

## 문제 데이터 명세 (`questions.json`)

```json
{
  "id": "KH-001",
  "category": "한국사",
  "question": "문제 내용",
  "choices": ["보기1", "보기2", "보기3", "보기4"],
  "answer": 0,
  "explanation": "정답 해설"
}
```

카테고리 코드: `KH`(한국사) · `SC`(과학) · `GE`(지리) · `GK`(일반상식)

## 퀴즈 문제 교차 검증 가이드라인

문제 작성 및 수정 시 아래 4가지를 반드시 확인한다.

1. **정답 유일성** — 다른 해석으로 정답이 달라지면 조건을 명시한다 (예: 면적 기준, 2024년 기준).
2. **최상급 표현 기준** — `가장`, `최초`, `최대`, `최소` 등에는 측정 기준과 시점을 명시한다.
3. **시점·범위 명확성** — 변할 수 있는 정보에는 시점을, 지리·분류 정보에는 범위를 한정한다.
4. **교차 검증** — 의심스러운 사실은 2개 이상 출처 확인, 논란 있는 내용은 주류 학설 기준.

## /quiz-validate 커맨드

`.claude/commands/quiz-validate.md`에 정의된 슬래시 커맨드.

- `/quiz-validate` — 전체 문제 검증
- `/quiz-validate 한국사` — 해당 카테고리만 검증

모호한 표현(`가장`, `최초`, `최대` 등) 탐지 후 기준 명시 방향을 제안한다.
