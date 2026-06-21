#!/bin/bash
# Complete startup script for TREMOR Monitoring with Real-Time WebSocket

echo ""
echo "===================================================="
echo "  TREMOR Real-Time Monitoring System - Complete"
echo "===================================================="
echo ""

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "[!] Virtual environment not found!"
    echo "[*] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source .venv/bin/activate || . .venv/Scripts/activate

# Install/update dependencies
echo "[*] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || \
pip install channels channels-redis daphne paho-mqtt django

# Run migrations
echo "[*] Running database migrations..."
python manage.py migrate

# Collect static files
echo "[*] Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "===================================================="
echo "  Ready to Start Services"
echo "===================================================="
echo ""
echo "Option 1: Start both Daphne and MQTT (Recommended)"
echo "  Run in two terminals:"
echo "  Terminal 1: python manage.py runserver_with_mqtt"
echo "  Terminal 2: daphne -b localhost -p 8000 backend.asgi:application"
echo ""
echo "Option 2: Start Daphne only (WebSocket with fallback polling)"
echo "  daphne -b localhost -p 8000 backend.asgi:application"
echo ""
echo "Option 3: Start MQTT service only"
echo "  python manage.py start_mqtt"
echo ""
echo "Dashboard URL: http://localhost:8000"
echo ""
