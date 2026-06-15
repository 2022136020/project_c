# Portfolio Tracker — 설치 가이드

## 요구 사항
| 항목 | 버전 |
|------|------|
| Flutter SDK | 3.29 이상 |
| Dart | 3.7 이상 |
| Android Studio / VS Code | 최신 권장 |
| Firebase CLI | 최신 권장 |

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/2022136020/project_c.git
cd project_c/portfolio-tracker
```

### 2. 패키지 설치
```bash
flutter pub get
```

### 3. 앱 실행 (개발 모드)
```bash
flutter run
```

### 4. APK 빌드 (Android 배포용)
```bash
flutter build apk --release
```

### 5. 웹 빌드 (Firebase Hosting 배포용)
```bash
flutter build web
firebase deploy --only hosting
```

## 참고 문서
- 개발 환경 전체 설정: `docs/setup.md`
- 빌드 & 배포 상세: `docs/deploy.md`
- README: `portfolio-tracker/README.md`

## GitHub
https://github.com/2022136020/project_c
