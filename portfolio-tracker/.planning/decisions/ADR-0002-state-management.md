# ADR-0002: 상태 관리 방식 선택

- 상태: Accepted
- 날짜: 2026-05-19
- 결정자: Jooseonghyeon

## 배경

Flutter 앱에서 UI 상태와 데이터 흐름을 관리하는 방법을 결정해야 한다.
화면 간 공유 상태(계좌 목록, 포지션 목록)가 존재하며,
Firebase Firestore의 실시간 스트림을 효율적으로 처리해야 한다.

## 고려한 대안

### 대안 A: StatefulWidget + StreamBuilder (선택)
- 장점: 추가 패키지 불필요, 학습 곡선 없음, Firestore Stream과 자연스럽게 연동
- 단점: 화면이 많아지면 상태 공유가 번거로워질 수 있음

### 대안 B: Provider
- 장점: Flutter 공식 권장, 상태 공유 쉬움, 커뮤니티 자료 많음
- 단점: 보일러플레이트 코드 존재, 초급자에게 개념 이해 시간 필요

### 대안 C: Riverpod
- 장점: Provider 개선판, 컴파일 타임 안전성
- 단점: 학습 곡선이 Provider보다 가파름, 오버엔지니어링 가능성

### 대안 D: BLoC / Cubit
- 장점: 명확한 단방향 데이터 흐름, 테스트 용이
- 단점: 코드량이 많음, 소규모 프로젝트에는 과도한 구조

## 결정

**StatefulWidget + StreamBuilder**를 사용한다.

## 이유

- 1인 개발, 수업 기간 내 완성이 목표이므로 추가 학습 비용을 최소화
- Firestore의 `snapshots()` 스트림을 `StreamBuilder`로 직접 소비하면 별도 상태 관리 레이어 없이 실시간 UI 업데이트 가능
- 현재 앱의 화면 수(약 8개)와 공유 상태 복잡도가 Provider/Riverpod 도입을 정당화하기에 충분하지 않음

## 결과 (예상되는 영향)

긍정:
- 코드 단순, 빠른 구현 가능
- Firestore 스트림과 자연스럽게 연동

부정 / 제약:
- 화면 수가 15개 이상으로 늘어나거나 화면 간 복잡한 상태 공유가 필요해지면 Provider/Riverpod으로 마이그레이션 검토

## 후속 작업

- [ ] 화면 간 데이터 전달은 생성자 파라미터로 처리
- [ ] 복잡한 상태가 생기면 `StatefulWidget`을 `ConsumerWidget`(Riverpod)으로 교체 검토
