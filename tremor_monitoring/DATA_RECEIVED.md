# ✅ DATA SUDAH MASUK! Sekarang Jalankan Server

Bagus! Sensor Anda sudah mengirim data. Kami sudah terima:

```
Temperature: 29.1°C (Normal)
Humidity: 92.4% (Danger - too high)
```

## 🚀 Cara Menampilkan di Dashboard

### Langkah 1: Buka Terminal PowerShell Baru

```powershell
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
```

### Langkah 2: Jalankan Daphne Server

```powershell
daphne -b localhost -p 8000 backend.asgi:application
```

**Tunggu sampai melihat:**
```
Listening on TCP address 127.0.0.1:8000
```

### Langkah 3: Buka Browser

```
http://localhost:8000
```

Login dengan username/password Anda.

## ✨ Sekarang Data Muncul Real-Time!

Dashboard akan menampilkan:
- 🌡️ **Temperature**: 29.1°C
- 💧 **Humidity**: 92.4%
- ⚠️ **Status**: Temperature Normal, Humidity Danger

Data akan **update otomatis** saat sensor mengirim data baru (melalui WebSocket real-time)!

## 🔍 Check WebSocket Connection

Buka Browser Console (F12 → Console tab) dan lihat:

✅ **Harus ada:**
```
✅ WebSocket connected successfully
📊 WebSocket message received: real_time_update
🌡️ Temp: 29.1°C, 💧 Humidity: 92.4%
```

## 📊 Apa yang Sedang Terjadi?

```
Sensor ESP32 (29.1°C, 92.4%)
    ↓
MQTT Broker (active - data diterima!)
    ↓
MQTT Service (active - data tersimpan!)
    ↓
Database (✅ DATA ADA)
    ↓
Daphne Server (jalankan sekarang!)
    ↓
WebSocket Broadcast
    ↓
Dashboard (real-time display)
```

## ⚡ Quick Command

Untuk menjalankan semuanya, buka Terminal PowerShell di folder `tremor_monitoring`:

```powershell
# Terminal 1 - WebSocket Server
daphne -b localhost -p 8000 backend.asgi:application

# Terminal 2 - (MQTT sudah berjalan, tidak perlu)

# Browser
Start-Process http://localhost:8000
```

---

**Status**: ✅ Data diterima dan tersimpan
**Next**: Jalankan Daphne server
**Result**: Real-time dashboard akan muncul
