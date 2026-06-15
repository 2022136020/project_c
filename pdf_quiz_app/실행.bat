@echo off
chcp 65001 >nul
cd /d "%~dp0web_app"

if not exist node_modules (
    echo npm 패키지 설치 중...
    call npm install
    echo.
)

echo 서버 시작 중... http://localhost:3000
echo 브라우저에서 http://localhost:3000 을 열어주세요.
echo 종료하려면 이 창을 닫으세요.
echo.
node server.js
pause
