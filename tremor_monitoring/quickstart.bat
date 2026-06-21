@echo off
REM Quick Start Script untuk Amonia Monitoring System (Windows)

echo ================================
echo Amonia Monitoring System - Quick Start
echo ================================
echo.

REM Check Python
echo 1. Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found!
    exit /b 1
)

REM Create virtual environment
echo 2. Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 3. Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 4. Installing dependencies...
pip install -q -r requirements.txt

REM Run migrations
echo 5. Running database migrations...
python manage.py migrate --noinput

REM Collect static files
echo 6. Collecting static files...
python manage.py collectstatic --clear --noinput

REM Create superuser prompt
echo.
echo 7. Create superuser for admin panel?
set /p create_user="Do you want to create a superuser? (y/n) "
if /i "%create_user%"=="y" (
    python manage.py createsuperuser
)

echo.
echo ✅ Setup complete!
echo.
echo To start the application:
echo  1. Activate venv:
echo     venv\Scripts\activate
echo  2. Run development server:
echo     python manage.py runserver 0.0.0.0:8000
echo  3. In another terminal, start MQTT service:
echo     python manage.py start_mqtt
echo.
echo Access dashboard: http://localhost:8000/
echo Access admin: http://localhost:8000/admin/
echo.
pause
