# Portfolio Tracker

> 되돌아보는 투자자가 앞으로 나아간다

주식·코인 포지션을 수동으로 기록하고, 수익률을 시각화하며, 복기를 통해 투자 실력을 키우는 Flutter 앱입니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 가상 계좌 관리 | 주식·코인 계좌 등록, 입출금 기록, 잔액 자동 계산 |
| 포지션 기록 | 진입가·수량·매수 근거·목표가·손절가 기록 |
| 수익률 계산 | 포지션 정리 시 수익률·실현 손익 자동 계산 |
| 복기 메모 | 정리된 포지션에 복기 메모 작성 |
| 시각화 | 수익률 막대 차트, 누적 손익 라인 차트 (기간 필터 포함) |
| 대시보드 | 총 잔액, 누적 손익, 승률, 최근 포지션 요약 |

---

## 빠른 시작

```bash
git clone https://github.com/[user]/portfolio-tracker.git
cd portfolio-tracker
flutter pub get
flutter run
```

자세한 설치 방법은 [docs/setup.md](docs/setup.md)를 참고하세요.

---

## 기술 스택

- **플랫폼**: Flutter (Android · iOS · Web)
- **인증 · DB**: Firebase Auth + Firestore
- **차트**: fl_chart

아키텍처 상세는 [docs/architecture.md](docs/architecture.md)를 참고하세요.

---

## 문서

| 문서 | 설명 |
|------|------|
| [docs/setup.md](docs/setup.md) | 환경 구축 및 실행 방법 |
| [docs/architecture.md](docs/architecture.md) | 시스템 설계 및 디렉토리 구조 |
| [docs/testing.md](docs/testing.md) | 테스트 체크리스트 |
| [.planning/](.planning/) | 기획 문서 (비전, PRD, WBS, 일정) |
| [.planning/decisions/](.planning/decisions/) | ADR (아키텍처 결정 기록) |

---

## 개발 일정

| 주차 | 내용 | 상태 |
|------|------|------|
| 10주차 | 기획·문서화 | ✅ |
| 11주차 | Firebase 연동, 인증 화면 | ✅ |
| 12주차 | 계좌 관리, 포지션 기록 | ✅ |
| 13주차 | 복기 메모, 차트 시각화 | ✅ |
| 14주차 | 대시보드, 기간 필터, 문서 완비 | ✅ |
| 15주차 | 최종 발표 | 예정 |
