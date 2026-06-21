@echo off
REM Complete Setup Script for TREMOR Real-Time Monitoring
REM This script will setup and verify everything is working

cd /d "%~dp0"

echo.
echo ====================================================
echo   TREMOR Setup & Verification Script
echo ====================================================
echo.

echo [*] Step 1: Activating virtual environment...
call .venv\Scripts\activate.bat

echo [*] Step 2: Installing all dependencies...
pip install -q django channels channels-redis daphne paho-mqtt 2>nul

echo [*] Step 3: Running database migrations...
python manage.py migrate --noinput

echo [*] Step 4: Checking database...
python << PYTHON_SCRIPT
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from monitoring.models import SensorReading
count = SensorReading.objects.count()
print(f"[+] Database contains {count} sensor readings")

if count == 0:
    print("[!] No sensor data in database yet")
    print("[*] Once MQTT service receives data, it will appear here")
PYTHON_SCRIPT

echo.
echo [*] Step 5: Setup complete!
echo.
echo Next Steps:
echo ============
echo.
echo Terminal 1 - Start Daphne WebSocket Server:
echo   run_server.bat
echo.
echo Terminal 2 - Start MQTT Service:
echo   run_mqtt.bat
echo.
echo Terminal 3 - Optional: Test MQTT (if mosquitto installed):
echo   mosquitto_pub -h 192.168.18.233 -t tremor/dht22 -m "{"temperature": 25.5, "humidity": 60.2}"
echo.
echo Then open browser:
echo   http://localhost:8000
echo.
echo ====================================================
echo.

pause
