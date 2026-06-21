"""
MQTT Service untuk menerima data dari sensor dan menyimpan ke database
"""
import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from monitoring.models import SensorReading, ThresholdSetting

logger = logging.getLogger(__name__)


class MQTTService:
    """Service untuk handle MQTT connections dan data"""
    
    def __init__(self):
        self.broker = settings.MQTT_BROKER
        self.port = settings.MQTT_PORT
        self.topic = settings.MQTT_TOPIC
        self.username = settings.MQTT_USERNAME
        self.password = settings.MQTT_PASSWORD
        self.client = None
        self.is_connected = False
        self.last_message_time = None  # Track when last message was received
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback saat terhubung ke broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.is_connected = True
            # Subscribe to topic
            client.subscribe(self.topic)
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker. RC: {rc}")
            self.is_connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback saat disconnect"""
        if rc != 0:
            logger.warning(f"Unexpected disconnection. RC: {rc}")
        self.is_connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback saat menerima message"""
        self.last_message_time = timezone.now()  # Record when message arrives
        try:
            payload = msg.payload.decode('utf-8')
            print(f"[MQTT] Received message from {msg.topic}: {payload}")
            logger.info(f"Received message: {payload}")
            
            # Parse message
            self.process_sensor_data(payload)
        except Exception as e:
            print(f"[MQTT ERROR] {str(e)}")
            logger.error(f"Error processing MQTT message: {str(e)}")
    
    def process_sensor_data(self, payload):
        """Process sensor data dari MQTT untuk DHT22"""
        try:
            # Try to parse as JSON
            try:
                data = json.loads(payload)
                # Handle DHT22 format: {"temperature": 28.5, "humidity": 65.2}
                # atau {"temp": 28.5, "hum": 65.2}
                temperature = float(data.get('temperature', data.get('temp', 0)))
                humidity = float(data.get('humidity', data.get('hum', 0)))
                location = data.get('location', 'Ruangan Monitoring')
                print(f"[MQTT] Parsed JSON: temp={temperature}°C, humidity={humidity}%")
            except (json.JSONDecodeError, TypeError, ValueError):
                # If not JSON, log error
                print(f"[MQTT ERROR] Invalid JSON format: {payload}")
                logger.error(f"Invalid JSON format: {payload}")
                return
            
            # Validate values
            if not (0 <= temperature <= 50) or not (0 <= humidity <= 100):
                print(f"[MQTT ERROR] Invalid sensor values: temp={temperature}, hum={humidity}")
                logger.error(f"Invalid sensor values: temp={temperature}, hum={humidity}")
                return
            
            # Get threshold settings
            try:
                threshold = ThresholdSetting.objects.latest('updated_at')
            except ThresholdSetting.DoesNotExist:
                threshold = ThresholdSetting.objects.create()
            
            # Determine status untuk temperature
            temp_status = self.determine_temp_status(temperature, threshold)
            
            # Determine status untuk humidity
            humidity_status = self.determine_humidity_status(humidity, threshold)
            
            # Save to database
            reading = SensorReading(
                temperature=temperature,
                humidity=humidity,
                location=location,
                temp_status=temp_status,
                humidity_status=humidity_status,
                source='MQTT'
            )
            reading.save()
            
            log_msg = f"Saved reading: {temperature}°C, {humidity}% from {location} (Temp: {temp_status}, Humidity: {humidity_status})"
            print(f"[MQTT] {log_msg}")
            logger.info(log_msg)
            
        except ValueError as e:
            print(f"[MQTT ERROR VALUE] {payload} - {str(e)}")
            logger.error(f"Invalid sensor value: {payload} - {str(e)}")
        except Exception as e:
            print(f"[MQTT ERROR SAVE] {str(e)}")
            logger.error(f"Error saving sensor data: {str(e)}")
    
    @staticmethod
    def determine_temp_status(temperature, threshold):
        """Determine temperature status based on value dan threshold
        Normal: warning_low <= temp <= warning_high
        Warning: (danger_low <= temp < warning_low) atau (warning_high < temp <= danger_high)
        Danger: temp < danger_low atau temp > danger_high
        """
        if temperature < threshold.temp_danger_low or temperature > threshold.temp_danger_high:
            return 'danger'
        elif temperature < threshold.temp_warning_low or temperature > threshold.temp_warning_high:
            return 'warning'
        return 'normal'
    
    @staticmethod
    def determine_humidity_status(humidity, threshold):
        """Determine humidity status based on value dan threshold
        Normal: warning_low <= hum <= warning_high
        Warning: (danger_low <= hum < warning_low) atau (warning_high < hum <= danger_high)
        Danger: hum < danger_low atau hum > danger_high
        """
        if humidity < threshold.humidity_danger_low or humidity > threshold.humidity_danger_high:
            return 'danger'
        elif humidity < threshold.humidity_warning_low or humidity > threshold.humidity_warning_high:
            return 'warning'
        return 'normal'
    
    @staticmethod
    def determine_status(value, warning_level=350, danger_level=400):
        """Determine status based on value dan threshold (Legacy - for compatibility)
        Safe: < 350 ppm
        Warning: 350-400 ppm (Sedang/Sedikit Bau)
        Danger: > 400 ppm (Bahaya)
        """
        if value >= danger_level:
            return 'danger'
        elif value >= warning_level:
            return 'warning'
        return 'safe'
    
    def connect(self):
        """Connect ke MQTT broker"""
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            # Set username/password jika ada
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            logger.info(f"Connecting to MQTT broker: {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect dari MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
    
    def publish(self, topic, payload):
        """Publish message ke MQTT topic"""
        if self.client and self.is_connected:
            self.client.publish(topic, payload)
            logger.info(f"Published to {topic}: {payload}")
        else:
            logger.warning("MQTT client not connected")
    
    def get_mqtt_health(self):
        """Get MQTT connection health status
        Returns: {is_receiving: bool, seconds_since_last_message: float, is_connected: bool}
        """
        result = {
            'is_connected': self.is_connected,
            'is_receiving': False,
            'seconds_since_last_message': None,
            'last_message_time': self.last_message_time
        }
        
        if self.last_message_time:
            seconds_since = (timezone.now() - self.last_message_time).total_seconds()
            result['seconds_since_last_message'] = seconds_since
            result['is_receiving'] = seconds_since < 20  # Consider receiving if got message within 20 sec
        
        return result


# Global MQTT service instance
mqtt_service = None


def get_mqtt_service():
    """Get atau create MQTT service instance"""
    global mqtt_service
    if mqtt_service is None:
        mqtt_service = MQTTService()
    return mqtt_service


def start_mqtt_service():
    """Start MQTT service"""
    service = get_mqtt_service()
    return service.connect()


def stop_mqtt_service():
    """Stop MQTT service"""
    global mqtt_service
    if mqtt_service:
        mqtt_service.disconnect()
        mqtt_service = None
