# ADR-0001: 모바일 프레임워크 선택

- 상태: Accepted
- 날짜: 2026-05-12
- 결정자: Jooseonghyeon

## 배경

portfolio-tracker는 Android / iOS 모두를 지원해야 하는 모바일 앱이다.
개발 인원이 1인이므로 두 플랫폼을 각각 네이티브로 개발하는 것은 현실적으로 불가능하다.
크로스플랫폼 프레임워크 중 하나를 선택해야 한다.

## 고려한 대안

### 대안 A: Flutter (Dart)
- 장점: 단일 코드베이스로 Android / iOS 동시 지원, 위젯 렌더링 엔진 자체 보유로 플랫폼 간 UI 일관성 높음, Firebase 공식 지원 패키지 풍부, 성능이 React Native보다 안정적
- 단점: Dart 언어 별도 학습 필요, JavaScript 생태계 활용 불가

### 대안 B: React Native (JavaScript)
- 장점: JavaScript / TypeScript 사용 가능, 웹 개발 경험 재활용 가능, 커뮤니티 큼
- 단점: 네이티브 브릿지 구조로 성능 이슈 발생 가능, 플랫폼별 UI 차이 관리 필요, 의존성 충돌 잦음

### 대안 C: Android Native (Kotlin)
- 장점: 최적의 Android 성능, Jetpack 생태계 활용
- 단점: iOS 미지원, 1인 개발에서 단일 플랫폼만 커버

## 결정

**Flutter**를 선택한다.

## 이유

- 1인 개발에서 Android / iOS를 동시에 커버할 수 있는 유일한 현실적 선택
- Firebase와의 공식 연동 패키지(`firebase_core`, `firebase_auth`, `cloud_firestore`)가 잘 관리되고 있어 백엔드 연동 부담이 낮음
- 차트 라이브러리(`fl_chart` 등) 등 이 프로젝트에 필요한 패키지가 충분히 존재
- 수업 과목이 "앱 프로그래밍 응용"으로 모바일 앱 결과물이 평가 기준에 부합

## 결과 (예상되는 영향)

긍정:
- 코드 한 벌로 Android / iOS 동시 제출 가능
- Firebase 연동 공식 패키지로 인증·DB 구현 속도 향상

부정 / 제약:
- Dart 문법 학습 곡선 존재 (11주차 초반 시간 투자 필요)
- 빌드 환경 설정 (Android Studio, 에뮬레이터) 초기 세팅 시간 필요 → 위험 목록 #7 참조

## 후속 작업

- [ ] Flutter SDK 설치 확인 (`flutter doctor`)
- [ ] Android Studio 에뮬레이터 정상 동작 확인
- [ ] `flutter pub get` 후 Hello World 빌드 성공 확인
