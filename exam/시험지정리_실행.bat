@echo off
cd /d "%~dp0"
echo 패키지 설치 중...
py -m pip install -r requirements.txt -q
echo.
echo ※ ANTHROPIC_API_KEY 환경 변수가 설정되어 있어야 합니다.
echo.
echo 서버 시작: http://localhost:5002
start "" "http://localhost:5002"
py app.py
pause
