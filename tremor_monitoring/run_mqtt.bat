@echo off
REM Script untuk menjalankan MQTT Service dengan proper venv activation

cd /d "%~dp0"

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [*] Installing paho-mqtt if not present...
pip install paho-mqtt --quiet

echo.
echo [+] Starting MQTT Service...
echo [+] Listening to MQTT Broker: 192.168.18.233:1883
echo [+] Topic: tremor/dht22
echo.
echo [!] Press Ctrl+C to stop
echo.

python manage.py start_mqtt

pause
