@echo off
REM Script untuk menjalankan MQTT Service untuk TREMOR Monitoring
REM Service ini menerima data dari sensor DHT22 dan menyimpan ke database

echo.
echo ====================================================
echo   TREMOR MQTT Service
echo ====================================================
echo.

cd /d "%~dp0"

echo [*] Checking Python environment...
python --version

echo.
echo [*] Starting MQTT Service...
echo [*] Listening to MQTT Broker: 192.168.18.233:1883
echo [*] Topic: tremor/dht22
echo.
echo [!] Press Ctrl+C to stop the service
echo.

REM Try to run as management command first
python manage.py start_mqtt

REM If command doesn't exist, run the MQTT service directly
if %errorlevel% neq 0 (
    echo [!] Management command not found, running MQTT service directly...
    cd monitoring
    python mqtt_service.py
)

pause
