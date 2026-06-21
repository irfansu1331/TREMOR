from django.db import models

# Create your models here.

class SensorReading(models.Model):
    """Model untuk menyimpan pembacaan sensor DHT22 (Suhu dan Kelembaban)"""
    temperature = models.FloatField(help_text="Suhu dalam Celsius (°C)")
    humidity = models.FloatField(help_text="Kelembaban dalam Persen (%)")
    location = models.CharField(max_length=100, default="Ruangan Monitoring")
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="MQTT", choices=[('MQTT', 'MQTT'), ('API', 'API')])
    temp_status = models.CharField(max_length=20, default="normal", choices=[
        ('normal', 'Normal'),
        ('warning', 'Warning'),
        ('danger', 'Danger')
    ])
    humidity_status = models.CharField(max_length=20, default="normal", choices=[
        ('normal', 'Normal'),
        ('warning', 'Warning'),
        ('danger', 'Danger')
    ])
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['location', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.location}: {self.temperature}°C, {self.humidity}% @ {self.timestamp}"


class SensorDevice(models.Model):
    """Model untuk sensor devices"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    device_id = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    last_reading = models.DateTimeField(null=True, blank=True)
    last_online = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.location})"


class ThresholdSetting(models.Model):
    """Model untuk konfigurasi ambang batas
    Temperature:
    - Normal: 18-27°C
    - Warning: 15-18°C atau 27-30°C
    - Danger: <15°C atau >30°C
    
    Humidity:
    - Normal: 40-60%
    - Warning: 30-40% atau 60-75%
    - Danger: <30% atau >75%
    """
    # Temperature thresholds (dalam Celsius)
    temp_warning_low = models.FloatField(default=15)   # Di bawah ini warning
    temp_warning_high = models.FloatField(default=30)  # Di atas ini warning
    temp_danger_low = models.FloatField(default=10)    # Di bawah ini danger
    temp_danger_high = models.FloatField(default=35)   # Di atas ini danger
    
    # Humidity thresholds (dalam Persen)
    humidity_warning_low = models.FloatField(default=30)   # Di bawah ini warning
    humidity_warning_high = models.FloatField(default=75)  # Di atas ini warning
    humidity_danger_low = models.FloatField(default=20)    # Di bawah ini danger
    humidity_danger_high = models.FloatField(default=85)   # Di atas ini danger
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Temp: {self.temp_warning_low}-{self.temp_warning_high}°C, Hum: {self.humidity_warning_low}-{self.humidity_warning_high}%"


class CalibrationSetting(models.Model):
    """Model untuk konfigurasi kalibrasi sensor"""
    zero_point = models.FloatField(default=0, help_text="Zero point calibration value")
    offset = models.FloatField(default=0, help_text="Offset adjustment untuk koreksi pembacaan")
    last_calibration = models.DateTimeField(null=True, blank=True, help_text="Kapan terakhir dikalibrasi")
    calibration_notes = models.TextField(blank=True, help_text="Catatan kalibrasi")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Calibration: Zero={self.zero_point}, Offset={self.offset}"


class SystemLog(models.Model):
    """Model untuk mencatat semua aktivitas sistem"""
    EVENT_TYPES = [
        ('MQTT_CONNECT', 'MQTT Connected'),
        ('MQTT_DISCONNECT', 'MQTT Disconnected'),
        ('SENSOR_ONLINE', 'Sensor Online'),
        ('SENSOR_OFFLINE', 'Sensor Offline'),
        ('THRESHOLD_CHANGED', 'Threshold Changed'),
        ('CALIBRATION_PERFORMED', 'Calibration Performed'),
        ('DATA_EXPORTED', 'Data Exported'),
        ('SYSTEM_ERROR', 'System Error'),
        ('SYSTEM_INFO', 'System Information'),
    ]
    
    SEVERITY_LEVELS = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='INFO')
    description = models.TextField()
    details = models.JSONField(null=True, blank=True, help_text="Additional JSON data")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
        ]
    
    def __str__(self):
        return f"[{self.severity}] {self.event_type}: {self.description}"
