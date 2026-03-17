:: Created: 2026-03-17
@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ──────────────────────────────────────────
echo  손글씨 숫자 인식기 (데스크톱)
echo ──────────────────────────────────────────

python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo  https://www.python.org 에서 Python 3.10 이상을 설치하세요.
    pause
    exit /b 1
)

python -c "import tensorflow" > nul 2>&1
if errorlevel 1 (
    echo 필요한 패키지를 설치합니다. 잠시 기다려 주세요...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [오류] 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
)

python digit_recognition.py
if errorlevel 1 (
    echo.
    echo [오류] 프로그램 실행 중 문제가 발생했습니다.
    pause
)
