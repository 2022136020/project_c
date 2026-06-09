# Deploy

## Android APK 빌드

### 사전 요구

- Flutter SDK 3.x 이상 설치
- Java 17 이상 (Android Gradle 빌드에 필요)
- `flutter doctor` 에서 Android toolchain 항목에 경고 없음 확인

### 릴리즈 APK 빌드

```bash
cd portfolio-tracker
flutter build apk --release
```

빌드 완료 후 APK 위치:

```
build/app/outputs/flutter-apk/app-release.apk
```

### 기기 직접 설치

```bash
# USB 디버깅 켠 Android 기기 연결 후
flutter install
```

또는 APK 파일을 기기에 복사 후 파일 관리자에서 직접 설치 (설정 → 알 수 없는 앱 허용 필요).

---

## Firebase 배포 (웹 버전)

### 사전 요구

```bash
npm install -g firebase-tools
firebase login
```

### 웹 빌드 + 배포

```bash
flutter build web
firebase deploy --only hosting
```

배포 완료 후 Firebase Console에서 제공하는 URL로 접근 가능.

---

## Firebase 프로젝트 연결 확인

현재 연결된 Firebase 프로젝트: `portfolio-tracker-d3939`

새로 연결하거나 변경이 필요한 경우:

```bash
dart pub global activate flutterfire_cli
flutterfire configure
```

---

## 주의 사항

- `google-services.json` 파일은 `android/app/` 에 있어야 Android 빌드가 된다.
- 릴리즈 APK는 서명(keystore)이 없으면 Google Play 등록 불가. 개인 테스트 설치는 서명 없이도 가능.
- iOS 빌드는 macOS + Xcode 환경 필요 — 현재 미지원.
