# Setup

> 새 사람이 이 문서만 보고 5분 안에 실행할 수 있어야 합니다.

## 1. 사전 요구

| 도구 | 버전 | 확인 명령 |
|------|------|-----------|
| Flutter | 3.x 이상 | `flutter --version` |
| Dart | SDK ^3.8.0 | `dart --version` |
| Git | 2.40+ | `git --version` |
| Android Studio | 최신 | (에뮬레이터 사용 시 필요) |

### 설치 방법

#### Windows
```powershell
# Flutter SDK 설치 (공식 문서 권장)
# https://docs.flutter.dev/get-started/install/windows

# 개발자 모드 활성화 (Flutter 플러그인 심볼릭 링크 필요)
start ms-settings:developers
```

#### macOS
```bash
brew install --cask flutter
```

#### Linux
```bash
sudo snap install flutter --classic
```

---

## 2. 클론

```bash
git clone https://github.com/[user]/portfolio-tracker.git
cd portfolio-tracker
```

---

## 3. 의존성 설치

```bash
flutter pub get
```

---

## 4. Firebase 설정

이 앱은 Firebase를 백엔드로 사용합니다. 아래 파일이 이미 포함되어 있습니다:
- `android/app/google-services.json` — Android Firebase 설정
- `lib/firebase_options.dart` — FlutterFire 자동 생성 파일

> **새로 Firebase 프로젝트를 연결할 경우:**
> ```bash
> npm install -g firebase-tools
> dart pub global activate flutterfire_cli
> firebase login
> flutterfire configure
> ```

---

## 5. 첫 실행

### Android 기기 (권장)
```bash
# USB 디버깅을 켠 Android 기기 연결 후
flutter run
```

### Android 에뮬레이터
```bash
# Android Studio에서 AVD 생성 후
flutter emulators --launch [emulator-id]
flutter run
```

### 웹 (Firebase 웹 앱 등록 후)
```bash
flutter run -d chrome
```

**성공 시:** 로그인 화면이 표시됩니다.

---

## 6. Firebase 콘솔 설정 (최초 1회)

1. [Firebase Console](https://console.firebase.google.com) → `portfolio-tracker-d3939` 프로젝트
2. Authentication → Sign-in method → **이메일/비밀번호** 활성화
3. Firestore Database → 규칙 탭에서 인증된 사용자만 본인 데이터 접근 허용:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

---

## 7. 자주 묻는 문제

### Q1. `flutter pub get` 중 "symlink support" 오류
→ Windows에서 개발자 모드가 꺼져 있습니다. `start ms-settings:developers` 실행 후 활성화.

### Q2. "Firebase App named '[DEFAULT]' already exists" 오류
→ `main.dart`의 `Firebase.initializeApp()`이 중복 호출됩니다. `WidgetsFlutterBinding.ensureInitialized()`가 `main()`에서 한 번만 실행되는지 확인.

### Q3. Android 빌드 중 Gradle 동기화 실패
→ `android/app/build.gradle`의 `minSdkVersion`이 23 이상인지 확인. Firebase Auth는 API 23+ 필요.

### Q4. Google Sign-In 오류 (`PlatformException: sign_in_failed`)
→ Firebase Console에 SHA-1 지문이 등록되지 않았습니다. (현재 버전은 이메일 로그인만 지원)

### Q5. `flutter run` 후 "No devices found"
→ `flutter devices`로 연결된 기기 확인. USB 디버깅이 켜진 기기가 없으면 에뮬레이터 실행 필요.
