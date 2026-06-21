# TREMOR Real-Time Monitoring - WebSocket Setup

## Installation Complete! 🎉

Kami telah mengimplementasikan real-time WebSocket support untuk dashboard TREMOR monitoring. Berikut adalah langkah-langkah untuk menjalankan aplikasi dengan dukungan WebSocket.

## Persyaratan

Pastikan telah menginstall paket-paket berikut:
- Django Channels
- Django Channels Redis
- Daphne (ASGI server)
- Paho MQTT

```bash
pip install channels channels-redis daphne paho-mqtt
```

## Cara Menjalankan

### Opsi 1: Menggunakan Daphne (Recommended untuk Production & Real-time Data)

Daphne adalah ASGI server yang mendukung WebSocket. Gunakan ini untuk mendapatkan real-time updates:

```bash
cd tremor_monitoring
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

Atau dengan binding ke localhost saja:

```bash
daphne -b localhost -p 8000 backend.asgi:application
```

### Opsi 2: Menggunakan Django Development Server (Fallback only)

Jika Daphne tidak tersedia, gunakan development server Django (hanya WebSocket tidak akan bekerja, fallback ke polling):

```bash
cd tremor_monitoring
python manage.py runserver
```

## Menjalankan MQTT Service

Di terminal lain, jalankan MQTT service untuk menerima data dari sensor:

```bash
cd tremor_monitoring/monitoring
python mqtt_service.py
```

Atau gunakan management command:

```bash
cd tremor_monitoring
python manage.py start_mqtt
```

## Testing WebSocket Connection

Buka browser dan akses dashboard di:
- http://localhost:8000

Periksa browser console (F12 > Console) untuk melihat:
1. "WebSocket connected successfully" - berarti WebSocket berhasil terhubung
2. "WebSocket message received" - data real-time diterima
3. "pollSensorData()" - fallback ke polling jika WebSocket gagal

## Features Real-Time

✅ **Real-time Sensor Data**: Data suhu dan kelembaban ditampilkan secara live
✅ **Automatic Reconnection**: WebSocket akan otomatis reconnect jika terputus
✅ **Fallback to Polling**: Jika WebSocket tidak tersedia, sistem fallback ke polling API setiap 3 detik
✅ **Historical Data**: Saat connect, sistem otomatis meminta data historis 24 jam terakhir

## Troubleshooting

### WebSocket tidak connect
1. Pastikan menggunakan Daphne bukan Django development server
2. Check browser console untuk error messages
3. Verify CORS/firewall settings
4. Cek URL WebSocket di console: seharusnya `ws://localhost:8000/ws/sensor/`

### Data tidak realtime (tetap polling)
1. Check apakah ada error di WebSocket connection
2. Verify MQTT service berjalan dan menerima data dari sensor
3. Check Redis connection jika production (default: localhost:6379)

### MQTT tidak terkoneksi ke sensor
1. Verify alamat broker MQTT di settings.py: `MQTT_BROKER = '192.168.18.233'`
2. Check port MQTT: `MQTT_PORT = 1883`
3. Verify sensor publish ke topic: `tremor/dht22`

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DHT22 Sensor                              │
└────────────────┬────────────────────────────────────────────────┘
                 │ (MQTT Publish)
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                    MQTT Broker (192.168.18.233:1883)            │
└────────────────┬────────────────────────────────────────────────┘
                 │
         ┌───────┴──────────────────┐
         │                          │
    ┌────▼────────────────┐   ┌────▼──────────────────┐
    │ MQTT Service        │   │ WebSocket Consumer    │
    │ (process_sensor)    │   │ (Channel Layer)       │
    └────┬────────────────┘   │                       │
         │                    └────────┬──────────────┘
         │ Save to Database            │
    ┌────▼────────────────────────────┐ broadcast
    │ SensorReading Model             │◄──────────────┐
    │ (Temperature & Humidity)        │              │
    └────────┬──────────────────────┬─┘              │
             │                      │                │
      ┌──────▼────────┐    ┌────────▼──────────┐    │
      │ API Endpoint  │    │ WebSocket Handler │    │
      │ /api/latest/  │    │ /ws/sensor/       │────┘
      └───────┬────────┘    └────────┬──────────┘
              │                      │
              │      ┌───────────────┘
              │      │
         ┌────▼──────▼──────────────┐
         │   Dashboard Frontend     │
         │   (dashboard.js)         │
         │ - Real-time Updates      │
         │ - Charts & Graphs        │
         │ - Status Indicators      │
         └──────────────────────────┘
```

## Performance

- **Real-time Latency**: ~100-500ms (WebSocket)
- **Polling Latency**: 3 seconds (fallback)
- **Data Points per Second**: 1 (sensor update rate)
- **Historical Data**: Up to 24 hours retained

## Production Deployment

Untuk production, gunakan:
1. **Daphne** sebagai ASGI server
2. **Redis** untuk Channel Layer (bukan in-memory)
3. **Supervisor** atau **systemd** untuk auto-restart
4. **Nginx** sebagai reverse proxy dengan WebSocket support

Contoh Nginx config untuk WebSocket:
```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

**Version**: 1.0
**Last Updated**: 2026-06-20
