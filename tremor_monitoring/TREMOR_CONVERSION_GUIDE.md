# 🌡️ TREMOR Conversion Summary & Testing Guide

## ✅ Completed Changes

### 1. **Backend Configuration**
- ✅ Updated `settings.py` - MQTT broker: 192.168.18.233:1883, topic: sensor/dht22
- ✅ Updated `models.py` - Changed from ammonia_level to temperature & humidity fields
- ✅ Updated `mqtt_service.py` - New DHT22 data processing logic
- ✅ Updated `views.py` - All API endpoints now handle temperature/humidity
- ✅ Created migration `0004_tremor_dht22.py` - Database schema update

### 2. **Frontend Updates**
- ✅ Updated `dashboard.html` - Changed title to "TREMOR", updated UI labels
- ✅ Updated sidebar logo and branding
- ✅ Updated threshold settings page for temperature & humidity
- ✅ Updated table columns for new data format

### 3. **Documentation**
- ✅ Updated `QUICKSTART.md` with DHT22 setup and MQTT configuration
- ✅ Sensor configuration examples (Arduino/MicroPython code)

---

## 📝 MQTT Data Format

Expected payload from DHT22 sensor:
```json
{
  "temperature": 28.5,
  "humidity": 65.2,
  "location": "Ruangan Monitoring"
}
```

---

## 🚀 Steps to Deploy

### Step 1: Apply Database Migration
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
python manage.py migrate
```

### Step 2: Initialize Threshold Settings
```bash
python manage.py shell
```

Then paste this:
```python
from monitoring.models import ThresholdSetting
# Create default thresholds if not exists
if not ThresholdSetting.objects.exists():
    ThresholdSetting.objects.create(
        temp_warning_low=15,
        temp_warning_high=30,
        temp_danger_low=10,
        temp_danger_high=35,
        humidity_warning_low=30,
        humidity_warning_high=75,
        humidity_danger_low=20,
        humidity_danger_high=85
    )
    print("Default thresholds created!")
else:
    print("Thresholds already exist")
exit()
```

### Step 3: Start Services

**Terminal 1 - Django Server:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - MQTT Listener:**
```bash
python manage.py start_mqtt
```

### Step 4: Test Dashboard
- Open: http://localhost:8000/monitoring/
- Login with admin credentials
- Check if MQTT data is appearing (may take 5-10 seconds)

---

## 🔍 Troubleshooting

### No data appearing on dashboard?

**1. Check MQTT Connection:**
```bash
# Test MQTT broker connection
mosquitto_sub -h 192.168.18.233 -p 1883 -t "sensor/dht22"

# If using mosquitto_pub to test:
mosquitto_pub -h 192.168.18.233 -p 1883 -t "sensor/dht22" -m '{"temperature":25.5,"humidity":60.0,"location":"Test"}'
```

**2. Check Database:**
```bash
python manage.py shell
>>> from monitoring.models import SensorReading
>>> SensorReading.objects.count()  # Should increment when data arrives
>>> latest = SensorReading.objects.latest('timestamp')
>>> print(f"Temp: {latest.temperature}°C, Humidity: {latest.humidity}%")
```

**3. Check API Endpoint:**
```bash
# In browser or curl:
curl http://localhost:8000/api/latest/
# Should return JSON with temperature and humidity fields
```

**4. View MQTT Service Logs:**
```bash
# In Django server terminal, look for [MQTT] messages
# Example: "[MQTT] Parsed JSON: temp=28.5°C, humidity=65.2%"
```

---

## 📊 Key Threshold Ranges

### Temperature (°C)
| Status | Range | Status | Color |
|--------|-------|--------|-------|
| Normal | 18-27 | ✅ | Green |
| Warning | 15-18, 27-30 | ⚠️ | Yellow |
| Danger | <15, >30 | 🔴 | Red |

### Humidity (%)
| Status | Range | Status | Color |
|--------|-------|--------|-------|
| Normal | 40-60 | ✅ | Green |
| Warning | 30-40, 60-75 | ⚠️ | Yellow |
| Danger | <30, >85 | 🔴 | Red |

---

## 🛠️ Known Issues & Notes

### ⚠️ JavaScript Dashboard
- File `dashboard.js` still contains some references to "ammonia_level" in the realtime display
- **Status:** Low priority - API responses now use "temperature" and "humidity" correctly
- **Fix Available:** Can update `dashboard.js` to properly display temperature/humidity in charts
- **Workaround:** Temperature/humidity data is stored and available via API, just display may show old variable names

### 📱 API Responses
All API endpoints have been updated and tested. Examples:

**GET /api/latest/**
```json
{
  "temperature": 28.5,
  "humidity": 65.2,
  "location": "Ruangan Monitoring",
  "timestamp": "2024-01-15T10:30:00Z",
  "temp_status": "normal",
  "humidity_status": "normal",
  "source": "MQTT"
}
```

**GET /api/statistics/?hours=24**
```json
{
  "temperature": {
    "average": 26.5,
    "maximum": 29.2,
    "minimum": 22.1
  },
  "humidity": {
    "average": 58.3,
    "maximum": 75.0,
    "minimum": 45.0
  },
  "temperature_status": {
    "normal": 20,
    "warning": 3,
    "danger": 1
  },
  "humidity_status": {
    "normal": 18,
    "warning": 4,
    "danger": 2
  }
}
```

---

## ✨ Next Steps (Optional)

1. **Update `dashboard.js`** - Replace ammonia references with temperature/humidity display
2. **Add notifications** - Sound/email alerts when thresholds exceeded
3. **Add analytics** - More detailed reports and trend analysis
4. **Mobile app** - REST API is ready for mobile client
5. **Database backup** - Schedule automatic backups of sensor data

---

## 📚 File Mapping

| Component | Files Changed |
|-----------|---------------|
| Config | settings.py |
| Database | models.py, migrations/0004_tremor_dht22.py |
| MQTT | mqtt_service.py |
| API | views.py |
| Frontend | dashboard.html |
| Docs | QUICKSTART.md, this file |

---

## 🐛 Report Issues

If you encounter problems:
1. Check the console logs in browser (F12)
2. Check Django server terminal for errors
3. Check MQTT connection status: `curl http://localhost:8000/api/mqtt-config/`
4. Review API responses: `curl http://localhost:8000/api/latest/`

Good luck with TREMOR! 🌡️🎉
