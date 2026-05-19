# ADR-0003: 백엔드 선택

- 상태: Accepted
- 날짜: 2026-05-19
- 결정자: Jooseonghyeon

## 배경

포지션 기록, 계좌 데이터, 사용자 인증을 저장·관리할 백엔드가 필요하다.
기기가 바뀌어도 데이터가 유지되어야 하며,
1인 개발 환경에서 서버 직접 운영 없이 구현 가능해야 한다.

## 고려한 대안

### 대안 A: Firebase (Firestore + Auth) (선택)
- 장점: Flutter 공식 패키지 지원, 실시간 스트림, 서버리스, 무료 티어 충분, 인증 내장
- 단점: 구글 생태계 종속, 무료 티어 한도 존재, 복잡한 쿼리 제한

### 대안 B: Supabase (PostgreSQL + Auth)
- 장점: 오픈소스, SQL 사용 가능, 무료 티어 제공
- 단점: Flutter 패키지가 Firebase보다 성숙도 낮음, 설정 복잡

### 대안 C: 로컬 저장 (SQLite / Hive)
- 장점: 오프라인 완전 지원, 외부 의존성 없음
- 단점: 기기 간 데이터 공유 불가, 백업 없음

### 대안 D: 자체 REST API (Flask / FastAPI)
- 장점: 완전한 제어권
- 단점: 서버 운영 비용, 배포 복잡성, 1인 개발에서 과도한 범위

## 결정

**Firebase (Firestore + Firebase Auth)**를 사용한다.

## 이유

- Flutter FlutterFire 패키지(`firebase_core`, `firebase_auth`, `cloud_firestore`)가 공식 지원되고 안정적
- ADR-0001에서 선택한 Flutter와 가장 자연스럽게 연동되는 백엔드
- 실시간 스트림(`snapshots()`)으로 별도 폴링 없이 UI 실시간 갱신 가능
- Firestore 무료 티어(읽기 50,000회/일, 쓰기 20,000회/일)가 개인 투자 기록 앱에 충분
- 인증·데이터·파일 저장을 한 플랫폼으로 통합하여 관리 포인트 최소화

## 결과 (예상되는 영향)

긍정:
- 서버 운영 없이 인증 + 실시간 DB 즉시 사용
- 멀티 기기 동기화 자동 지원

부정 / 제약:
- Firebase 무료 티어 한도 초과 시 비용 발생 → 개발 중 테스트 데이터 최소화
- 복잡한 관계형 쿼리(JOIN 등)는 Firestore에서 직접 지원하지 않음 → 클라이언트에서 처리

## 후속 작업

- [x] `google-services.json` Android 등록 완료
- [x] `firebase_options.dart` 생성 완료
- [ ] Firestore 보안 규칙 설정 (사용자별 데이터 격리)
- [ ] Firebase Console에서 이메일/비밀번호 인증 활성화
