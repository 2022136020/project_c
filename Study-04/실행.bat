@echo off
chcp 65001 > nul
echo.
echo  ╔══════════════════════════════════════╗
echo  ║   냉장고 재료 인식 & 레시피 추천 앱  ║
echo  ╚══════════════════════════════════════╝
echo.
echo  패키지 확인 중...
py -m pip install -q -r step1\requirements.txt

echo.
echo  서버 시작 중... (http://localhost:5001)
echo  종료하려면 Ctrl+C 를 누르세요.
echo.
cd step1
start "" http://localhost:5001
py app.py
