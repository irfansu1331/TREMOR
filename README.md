<img width="1919" height="984" alt="Screenshot 2026-06-22 004327" src="https://github.com/user-attachments/assets/e0d48102-d93f-48b3-938a-47e0bb2c74f2" />


# Project TREMOR

Sistem monitoring suhu dan kelembaban ruangan berbasis ESP32, MQTT, Zabbix, dan Web Dashboard.

## Fitur

- Monitoring suhu real-time
- Monitoring kelembaban real-time
- MQTT Communication
- Integrasi Zabbix
- Notifikasi Telegram
- Dashboard Web

## Teknologi

- ESP32
- DHT22
- MQTT (Mosquitto)
- Python
- Zabbix
- PostgreSQL
- Django

## Arsitektur Sistem

ESP32 → MQTT Broker → Python Subscriber → Zabbix → Telegram

## Instalasi

### Clone Repository

```bash
git clone https://github.com/username/project-tremor.git
cd project-tremor
```

### Install Dependency

```bash
pip install -r requirements.txt
django
paho-mqtt
```

## Konfigurasi MQTT

```python
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
```

## Menjalankan Script web

```bash
python manage.py start_mqtt
```
## Menjalankan Script zabbix di servrr

```bash
python3 mqtttozabbix.py
```


## Struktur Folder

```text
Project TREMOR/
│
├── mqtt_zabbix.py
├── esp32/
├── dashboard/
├── docs/
├── requirements.txt
└── README.md
```

## Author

Irfansupnl

Politeknik Negeri Lampung
