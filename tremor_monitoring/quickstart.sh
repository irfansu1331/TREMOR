#!/bin/bash
# Quick Start Script untuk Amonia Monitoring System

echo "================================"
echo "Amonia Monitoring System - Quick Start"
echo "================================"
echo ""

# Check Python
echo "1. Checking Python installation..."
python --version || { echo "Python not found!"; exit 1; }

# Create virtual environment
echo "2. Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "3. Activating virtual environment..."
if [ "$OSTYPE" == "msys" ] || [ "$OSTYPE" == "cygwin" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "4. Installing dependencies..."
pip install -q -r requirements.txt

# Run migrations
echo "5. Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "6. Collecting static files..."
python manage.py collectstatic --clear --noinput

# Create superuser prompt
echo ""
echo "7. Create superuser for admin panel?"
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Activate venv:"
if [ "$OSTYPE" == "msys" ] || [ "$OSTYPE" == "cygwin" ]; then
    echo "     venv\\Scripts\\activate"
else
    echo "     source venv/bin/activate"
fi
echo "  2. Run development server:"
echo "     python manage.py runserver 0.0.0.0:8000"
echo "  3. In another terminal, start MQTT service:"
echo "     python manage.py start_mqtt"
echo ""
echo "Access dashboard: http://localhost:8000/"
echo "Access admin: http://localhost:8000/admin/"
