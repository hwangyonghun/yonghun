@echo off
echo [VeritasGuard AI] 가상 환경 생성 중... (잠시만 기다려주세요)
python -m venv venv

echo [VeritasGuard AI] pip 업그레이드 중...
venv\Scripts\python -m pip install --upgrade pip

echo [VeritasGuard AI] 필수 라이브러리 설치 중... (TensorFlow 설치로 인해 시간이 소요될 수 있습니다)
venv\Scripts\pip install -r requirements.txt

echo.
echo [VeritasGuard AI] 설치가 완료되었습니다!
echo 'start.bat'를 실행하여 서버를 시작하세요.
pause
