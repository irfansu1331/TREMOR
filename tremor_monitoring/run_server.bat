@echo off
REM Script untuk menjalankan Daphne Server dengan proper venv activation
REM This is the correct way to run with virtual environment

cd /d "%~dp0"

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [*] Installing daphne if not present...
pip install daphne --quiet

echo [*] Running migrations...
python manage.py migrate

echo.
echo [+] Starting Daphne server on localhost:8000
echo [+] WebSocket URL: ws://localhost:8000/ws/sensor/
echo [+] Dashboard URL: http://localhost:8000
echo.
echo [!] Press Ctrl+C to stop
echo.

daphne -b localhost -p 8000 backend.asgi:application

pause
