@echo off
REM Script untuk menjalankan TREMOR Monitoring dengan WebSocket support (Daphne)
REM Gunakan script ini untuk development dengan real-time WebSocket updates

echo.
echo ====================================================
echo   TREMOR Real-Time Monitoring - Daphne Server
echo ====================================================
echo.

cd /d "%~dp0"

echo [*] Checking Python environment...
python --version

echo.
echo [*] Migrating database...
python manage.py migrate

echo.
echo [*] Collecting static files...
python manage.py collectstatic --noinput

echo.
echo [+] Starting Daphne server on localhost:8000
echo [+] WebSocket URL: ws://localhost:8000/ws/sensor/
echo [+] Dashboard URL: http://localhost:8000
echo.
echo [!] Press Ctrl+C to stop the server
echo.

REM Run Daphne server
daphne -b localhost -p 8000 -v 2 backend.asgi:application

pause
