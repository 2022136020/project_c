# Architecture

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| UI | Flutter (Material 3) |
| 인증 | Firebase Auth (이메일/비밀번호 + Google) |
| 데이터 | Firebase Firestore |
| 상태 관리 | StatefulWidget + StreamBuilder (Phase 1) |

## 디렉터리 구조

```
lib/
├── main.dart                   # 앱 진입점, AuthWrapper (StreamBuilder)
├── firebase_options.dart       # FlutterFire 자동 생성
├── services/
│   └── auth_service.dart       # Firebase Auth 래퍼
└── screens/
    ├── auth/
    │   ├── login_screen.dart   # 이메일/Google 로그인
    │   └── signup_screen.dart  # 이메일 회원가입
    └── home_screen.dart        # 로그인 후 진입점 (대시보드 예정)
```

## 인증 흐름

```
앱 시작
  └─ Firebase.initializeApp()
       └─ StreamBuilder(authStateChanges)
            ├─ User != null → HomeScreen
            └─ User == null → LoginScreen
                  ├─ 이메일 로그인 → FirebaseAuth.signInWithEmailAndPassword
                  ├─ Google 로그인 → GoogleSignIn → FirebaseAuth.signInWithCredential
                  └─ 회원가입 → SignupScreen → FirebaseAuth.createUserWithEmailAndPassword
```

## 자동 로그인

`FirebaseAuth.instance.authStateChanges()` 스트림을 `main.dart`의 `StreamBuilder`가 구독한다.
앱 재실행 시 Firebase가 로컬 캐시에서 세션을 복원하면 자동으로 `HomeScreen`으로 진입한다.

## Firestore 데이터 모델 (예정)

```
users/{uid}/
  accounts/{accountId}       # 가상 계좌
  positions/{positionId}     # 포지션 기록
  transactions/{txId}        # 입출금 내역
```
