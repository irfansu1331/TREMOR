# Amonia Monitoring System - Web Dashboard

Sistem monitoring real-time kadar amonia untuk toilet kampus dengan dashboard web yang menampilkan data dari sensor MQTT.

## 🎯 Fitur

- ✅ Dashboard real-time dengan grafik live
- ✅ Koneksi MQTT untuk menerima data sensor per 5 detik
- ✅ Penyimpanan data ke database
- ✅ Status indikator (Safe/Warning/Danger)
- ✅ AI Prediction untuk prediksi konsentrasi amonia
- ✅ Riwayat data dan statistik
- ✅ Dark mode support
- ✅ API endpoints untuk integrasi
- ✅ Admin panel untuk manage data

## 📋 Struktur Proyek

```
amonia_monitoring/
├── backend/                    # Django project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URLs configuration
│   ├── asgi.py
│   └── wsgi.py
├── monitoring/                # Django app
│   ├── static/
│   │   ├── css/style.css      # Dashboard CSS
│   │   └── js/
│   │       ├── mqtt-client.js # MQTT client
│   │       └── dashboard.js   # Dashboard logic
│   ├── templates/
│   │   └── monitoring/
│   │       └── dashboard.html # Dashboard HTML
│   ├── management/
│   │   └── commands/
│   │       └── start_mqtt.py  # MQTT service command
│   ├── models.py              # Database models
│   ├── views.py               # API views
│   ├── urls.py                # App URLs
│   ├── mqtt_service.py        # MQTT service
│   └── admin.py               # Admin configuration
├── manage.py
└── requirements.txt           # Python dependencies
```

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MQTT Settings

Edit `backend/settings.py` dan pastikan konfigurasi MQTT sesuai:

```python
MQTT_BROKER = '103.151.63.82'
MQTT_PORT = 8883
MQTT_TOPIC = 'proyek/mandiri'
MQTT_USERNAME = None  # Optional
MQTT_PASSWORD = None  # Optional
```

### 3. Migrate Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Buat Superuser (Optional, untuk admin panel)

```bash
python manage.py createsuperuser
```

### 5. Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

## ▶️ Menjalankan Aplikasi

### Development Mode

**Terminal 1 - Django Development Server:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - MQTT Service (Optional, auto-start saat Django siap):**
```bash
python manage.py start_mqtt
```

Akses dashboard di: `http://localhost:8000/`

### Production Mode

Gunakan gunicorn + nginx:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## 📡 MQTT Subscription

Dashboard secara otomatis subscribe ke:
- **Broker**: 103.151.63.82:8883 (WebSocket Secure)
- **Topic**: proyek/mandiri
- **Update Interval**: 5 detik (dari sensor)

### Format Data yang Diterima

**Format JSON (recommended):**
```json
{
  "value": 25.5,
  "ammonia": 25.5,
  "ppm": 25.5,
  "location": "Toilet Lab Kimia A",
  "timestamp": 1705335600000
}
```

**Format Plain Number:**
```
25.5
```

## 🌐 API Endpoints

### Get Latest Reading
```
GET /api/latest/
```

**Response:**
```json
{
  "value": 25.5,
  "location": "Toilet Lab Kimia A",
  "timestamp": "2024-01-15T14:30:00Z",
  "status": "warning",
  "source": "MQTT"
}
```

### Get History
```
GET /api/history/?hours=24&location=Toilet%20Lab%20Kimia%20A
```

### Get Statistics
```
GET /api/statistics/?hours=24
```

**Response:**
```json
{
  "average": 22.5,
  "maximum": 45.2,
  "minimum": 12.3,
  "total_readings": 288,
  "safe_readings": 250,
  "warning_readings": 32,
  "danger_readings": 6
}
```

### Get Device Status
```
GET /api/devices/
```

### Get Threshold Settings
```
GET /api/threshold/
```

### Save Reading (External)
```
POST /api/save-reading/
Content-Type: application/json

{
  "value": 25.5,
  "location": "Toilet Lab Kimia A",
  "source": "API"
}
```

## 🎨 Dashboard Features

### Main Dashboard Page
- Current ammonia concentration reading
- Real-time graph (20 latest readings)
- Daily trend chart
- System status indicator
- AI prediction for next hour
- Historical data table with filters
- Quick action buttons

### Other Pages (Accessible via Sidebar)
- **Locations**: Manage monitoring locations
- **Device Status**: Monitor sensor devices
- **AI Prediction**: Advanced analytics
- **Reports**: Generate reports
- **Threshold Settings**: Configure warning/danger levels
- **API Configuration**: Setup external integrations
- **Calibration**: Sensor calibration tools
- **User Management**: Manage system users
- **System Logs**: View system logs
- **Export Data**: Export readings
- **Documentation**: System documentation

## ⚙️ Configuration

### Threshold Settings (default)
- **Warning Level**: 25 ppm
- **Danger Level**: 50 ppm

Dapat diubah di Django Admin atau direct di database.

### Ambah Device di Admin

1. Buka `http://localhost:8000/admin/`
2. Login dengan superuser
3. Navigate ke "Sensor Devices"
4. Tambah device baru

## 🔧 Troubleshooting

### MQTT Connection Issues
```
ERROR: Failed to connect to MQTT broker
```
- Check MQTT broker address: `103.151.63.82:8883`
- Check topic: `proyek/mandiri`
- Check firewall/network connection
- Verify broker is running and accepting connections

### No Data Showing in Dashboard
- Check browser console (F12) untuk error messages
- Verify MQTT subscription in logs
- Check database untuk readings: `python manage.py shell`
  ```python
  from monitoring.models import SensorReading
  SensorReading.objects.all().count()
  ```

### Static Files Not Loading (CSS/JS)
```bash
python manage.py collectstatic --clear --noinput
```

## 📊 Database Schema

### SensorReading
- `ammonia_level` (Float): Kadar amonia dalam ppm
- `location` (String): Lokasi sensor
- `timestamp` (DateTime): Waktu pembacaan
- `status` (String): safe/warning/danger
- `source` (String): MQTT/API

### SensorDevice
- `name` (String): Nama device
- `location` (String): Lokasi device
- `device_id` (String): Unique identifier
- `is_active` (Boolean): Status aktif
- `last_online` (DateTime): Terakhir online

### ThresholdSetting
- `warning_level` (Float): Ambang warning
- `danger_level` (Float): Ambang danger
- `updated_at` (DateTime): Terakhir update

## 🔐 Security Notes

- Change Django `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Use SSL/TLS untuk MQTT connection
- Set proper `ALLOWED_HOSTS` dalam settings.py
- Implement authentication untuk API endpoints
- Use environment variables untuk sensitive data

## 📝 Logging

Log file tersimpan di console. Untuk file logging, configure di `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'monitoring.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

## 🤝 Support & Maintenance

- Monitor dashboard regularly untuk sensor issues
- Backup database secara berkala
- Update dependencies untuk security patches
- Check system logs untuk anomalies
- Perform sensor calibration regularly

## 📄 License

Project ini adalah bagian dari Tugas Akhir Kampus.

## 👥 Kontak

Untuk masalah atau pertanyaan, hubungi system administrator.
