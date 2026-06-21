# 🚀 QUICK START - TREMOR Real-Time Dashboard

## ⏱️ 5 Menit Setup

Follow langkah-langkah ini untuk mendapatkan dashboard real-time running!

### Step 1: Navigate ke Project (1 menit)
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
```

### Step 2: Install Dependencies (2 menit)
```bash
pip install channels channels-redis daphne paho-mqtt
```

✅ Tunggu sampai selesai. Anda akan melihat:
```
Successfully installed channels-4.3.2 daphne asgiref-3.11.1 ...
```

### Step 3: Prepare Database (1 menit)
```bash
python manage.py migrate
```

✅ Database siap!

### Step 4: START THE MAGIC! (1 menit)

**Buka 2 Terminal sekaligus:**

#### Terminal 1 - Daphne WebSocket Server
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
daphne -b localhost -p 8000 backend.asgi:application
```

Anda akan melihat:
```
2026-06-20 14:30:00,000 - daphne.server - INFO - Listening on TCP address 127.0.0.1:8000
```

#### Terminal 2 - MQTT Service  
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
python manage.py start_mqtt
```

Anda akan melihat:
```
[*] Starting MQTT service...
[+] Connected to MQTT broker successfully
[+] Subscribed to topic: tremor/dht22
```

### Step 5: Open Dashboard
Buka browser dan akses:
```
http://localhost:8000
```

Login dengan credentials Anda.

## ✅ Dashboard Sekarang REAL-TIME!

Buka **F12 Console** (Browser Developer Tools) dan Anda akan melihat:
```
✅ WebSocket connected successfully
📊 WebSocket message received: real_time_update
```

## 🎯 Apa yang Terjadi

1. **Browser** → Connects ke WebSocket `ws://localhost:8000/ws/sensor/`
2. **MQTT Service** → Receives data dari sensor
3. **Backend** → Saves ke database & broadcasts via WebSocket
4. **Dashboard** → Shows data INSTANTLY ⚡

## 🐛 Troubleshooting

### Problem: "WebSocket connection failed"
**Solution**: Pastikan Daphne (Terminal 1) berjalan dengan baik

### Problem: "No data showing"
**Solution**: Pastikan MQTT Service (Terminal 2) connected dan sensor aktif

### Problem: "Module not found"
**Solution**: Run `pip install channels channels-redis daphne paho-mqtt` lagi

## 📊 Testing WebSocket

Copy-paste ini ke Browser Console (F12):

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/sensor/');

ws.onopen = () => {
    console.log('✅ WebSocket Connected!');
    // Request latest data
    ws.send(JSON.stringify({command: 'get_latest'}));
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log('📊 Real-time update:', msg);
    if (msg.data && msg.data.temperature) {
        console.log(`🌡️ Temp: ${msg.data.temperature}°C, 💧 Humidity: ${msg.data.humidity}%`);
    }
};

ws.onerror = (error) => console.error('❌ WebSocket Error:', error);
ws.onclose = () => console.log('⚠️ WebSocket Closed');
```

Anda akan melihat output seperti:
```
✅ WebSocket Connected!
📊 Real-time update: {type: "initial_data", data: {...}}
🌡️ Temp: 25.5°C, 💧 Humidity: 60.2%
```

## 📚 Dokumentasi

Untuk informasi lebih lanjut, baca:

1. **REALTIME_SETUP.md** - Setup & troubleshooting lengkap
2. **REALTIME_GUIDE.md** - Dokumentasi teknis mendalam
3. **IMPLEMENTATION_CHECKLIST.md** - Verification checklist
4. **IMPLEMENTATION_SUMMARY.md** - Overview lengkap

Semua file ada di folder `tremor_monitoring/`

## 🔄 Data Flow Visualization

```
┌─────────────┐
│ DHT22       │
│ Sensor      │
└──────┬──────┘
       │ 25.5°C, 60.2%
       │ (MQTT)
       ▼
┌──────────────────┐
│ MQTT Broker      │
│ 192.168.18.233   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ MQTT Service     │
│ (Receiving)      │
└──────┬───────────┘
       │
       ├─► Database ──┐
       │              │
       └─► WebSocket  │
           Broadcast  │
                      │
                      ▼
           ┌────────────────┐
           │ All Connected  │
           │ Browsers       │
           │ (Instant!)     │
           └────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Real-Time       │
         │ Dashboard       │
         │ Updates         │
         └─────────────────┘
```

## 💡 Pro Tips

1. **Monitor Data Flow**
   - Lihat Terminal MQTT Service untuk log real-time
   - Lihat Browser Console untuk WebSocket messages

2. **Test Manually**
   - Publish test message ke MQTT:
     ```bash
     mosquitto_pub -h 192.168.18.233 -t tremor/dht22 -m '{"temperature": 28.5, "humidity": 65}'
     ```
   - Dashboard akan update instantly! ⚡

3. **Performance**
   - Real-time latency: ~100-500ms
   - Polling fallback: ~3 detik
   - Auto-reconnect: otomatis
   
4. **Production Tips**
   - Install Redis untuk scalability
   - Use Nginx sebagai reverse proxy
   - Enable HTTPS/WSS
   - Use supervisor untuk process management

## ✨ Features

✅ Real-time sensor data via WebSocket
✅ Automatic reconnection
✅ Polling fallback
✅ Historical data loading
✅ Live charts & graphs
✅ Real-time status indicators
✅ Secure authentication
✅ Production ready

## 🎉 Done!

Sekarang dashboard Anda menampilkan data sensor **REAL-TIME**! 

Enjoy live monitoring! 🚀

---

## Emergency Troubleshooting

### Step 1: Check Ports
```bash
# Check if port 8000 is available
netstat -ano | findstr :8000
```

### Step 2: Kill Old Processes
```bash
# Kill old daphne process if any
taskkill /PID [PID] /F
```

### Step 3: Clear Cache
```bash
# Clear browser cache (Ctrl+Shift+Delete)
# Or use private/incognito mode
```

### Step 4: Reset Database (if needed)
```bash
python manage.py migrate zero monitoring
python manage.py migrate
```

---

**Setup Time**: ~5 minutes
**Status**: Ready to Run ✅
**Next Step**: Open http://localhost:8000 🚀
