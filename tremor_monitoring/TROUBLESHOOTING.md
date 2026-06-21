# ❌ Masalah: Data Tidak Keluar di Web

## ✅ Solusi Cepat (Copy-Paste)

### 1. Jalankan Setup Script Dulu
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
setup_and_verify.bat
```

Tunggu sampai selesai, Anda akan melihat:
```
[+] Database contains 0 sensor readings
[*] Once MQTT service receives data, it will appear here
```

### 2. Buka 2 Terminal Baru

**Terminal 1 - Daphne Server**
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
run_server.bat
```

Tunggu sampai Anda lihat:
```
[+] Listening on TCP address 127.0.0.1:8000
```

**Terminal 2 - MQTT Service**
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
run_mqtt.bat
```

Tunggu sampai Anda lihat:
```
[+] Connected to MQTT broker successfully
[+] Subscribed to topic: tremor/dht22
```

### 3. Buka Browser
```
http://localhost:8000
```

Login dengan username/password Anda.

## 🤔 Masih Tidak Ada Data?

Jika dashboard terbuka tapi tidak ada data sensor, kemungkinannya:

### Penyebab 1: Sensor Tidak Mengirim Data

**Cek MQTT Broker Connection:**

Buka Terminal 3 dan jalankan:
```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
call .venv\Scripts\activate.bat
python << PYTHON_SCRIPT
import paho.mqtt.client as mqtt
import time

print("[*] Testing MQTT Broker connection...")
print("[*] Broker: 192.168.18.233:1883")

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[+] Connected to MQTT Broker!")
        print("[*] Listening for messages on topic: tremor/dht22")
        client.subscribe('tremor/dht22')
    else:
        print(f"[-] Failed to connect. RC: {rc}")

def on_message(client, userdata, msg):
    print(f"[+] Received: {msg.payload.decode()}")

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect('192.168.18.233', 1883, 60)
    client.loop_start()
    
    print("[*] Waiting for messages (Ctrl+C to stop)...")
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n[*] Stopped")
    client.disconnect()
except Exception as e:
    print(f"[-] Error: {e}")
PYTHON_SCRIPT
```

Jika Anda lihat messages masuk, berarti sensor mengirim data ke MQTT. Jika tidak, sensor mungkin tidak aktif atau topik berbeda.

### Penyebab 2: MQTT Service Tidak Processing Data

**Check MQTT Service Console:**

Lihat Terminal 2 (MQTT Service). Seharusnya menampilkan:
```
[MQTT] Received message from tremor/dht22: {"temperature": 25.5, "humidity": 60.2}
[MQTT] Parsed JSON: temp=25.5°C, humidity=60.2%
[MQTT] Saved reading: 25.5°C, 60.2%
```

Jika tidak ada log, cek:
1. MQTT Broker IP yang benar: `192.168.18.233`
2. MQTT Topic yang benar: `tremor/dht22`
3. Koneksi network ke MQTT broker

### Penyebab 3: Database Tidak Menyimpan Data

**Manual Test - Publish ke MQTT:**

Jika Anda punya mosquitto client:

```bash
mosquitto_pub -h 192.168.18.233 -t tremor/dht22 -m "{\"temperature\": 25.5, \"humidity\": 60.2}"
```

Atau via Python:

```bash
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
call .venv\Scripts\activate.bat
python << PYTHON_SCRIPT
import paho.mqtt.client as mqtt
import json

print("[*] Publishing test data to MQTT...")

client = mqtt.Client()
client.connect('192.168.18.233', 1883, 60)

data = {
    "temperature": 25.5,
    "humidity": 60.2,
    "location": "Test"
}

result = client.publish('tremor/dht22', json.dumps(data))

if result.rc == 0:
    print("[+] Test data published successfully!")
    print(f"[+] Data: {data}")
else:
    print(f"[-] Failed to publish. RC: {result.rc}")

client.disconnect()
PYTHON_SCRIPT
```

Setelah menjalankan ini, cek Dashboard - seharusnya ada data baru muncul!

### Penyebab 4: WebSocket Tidak Connect

**Check Browser Console:**

Buka Browser Developer Tools (F12 → Console) dan lihat:

✅ **Jika berhasil:**
```
✅ WebSocket connected successfully
📊 WebSocket message received: real_time_update
```

❌ **Jika gagal:**
```
WebSocket connection failed
❌ WebSocket Closed
```

**Solusi:**
1. Pastikan Daphne (Terminal 1) berjalan
2. Refresh halaman browser
3. Check apakah port 8000 tidak di-block

## 🔍 Full Diagnostic Checklist

```bash
# 1. Check Python version
python --version

# 2. Check venv activated
echo %VIRTUAL_ENV%

# 3. Check Daphne installed
pip list | findstr daphne

# 4. Check database
cd "c:\Users\Rednox\Project TREMOR\tremor_monitoring"
python manage.py dbshell

# In SQLite shell:
# SELECT COUNT(*) FROM monitoring_sensorreading;
# .quit
```

## 📋 Checklist Sebelum Jalankan

- [ ] `setup_and_verify.bat` sudah dijalankan
- [ ] `run_server.bat` (Terminal 1) menunjukkan "Listening on TCP"
- [ ] `run_mqtt.bat` (Terminal 2) menunjukkan "Subscribed to topic"
- [ ] Browser bisa akses `http://localhost:8000`
- [ ] Browser Console menunjukkan "WebSocket connected"
- [ ] Sensor aktif & mengirim data ke MQTT

## 🎯 Expected Flow

```
Sensor → MQTT Broker → MQTT Service → Database ✓
                                    ↓
                              WebSocket Broadcast
                                    ↓
                              Browser Dashboard
                                    ↓
                           Real-Time Display ✓
```

---

**Status**: Troubleshooting
**Next Step**: Run `setup_and_verify.bat` 
**Help**: Check error messages di console
