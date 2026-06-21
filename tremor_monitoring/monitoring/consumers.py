"""
WebSocket consumers untuk real-time sensor data streaming
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import timedelta

from .models import SensorReading, SensorDevice, ThresholdSetting

logger = logging.getLogger(__name__)


class SensorDataConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer untuk streaming data sensor real-time
    Clients connect to ws://localhost:8000/ws/sensor/
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'sensor_data'
        self.room_group_name = f'sensor_{self.room_name}'
        self.user = self.scope['user']
        
        # Add this connection to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial data (latest reading)
        latest_data = await self.get_latest_sensor_data()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'data': latest_data,
            'timestamp': timezone.now().isoformat()
        }))
        
        logger.info(f"WebSocket connection established for user: {self.user}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove this connection from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for user: {self.user}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            command = data.get('command', '')
            
            if command == 'get_history':
                # Send historical data
                hours = int(data.get('hours', 24))
                limit = int(data.get('limit', 100))
                history = await self.get_sensor_history(hours, limit)
                
                await self.send(text_data=json.dumps({
                    'type': 'history_data',
                    'data': history,
                    'timestamp': timezone.now().isoformat()
                }))
            
            elif command == 'get_latest':
                # Send latest data
                latest = await self.get_latest_sensor_data()
                await self.send(text_data=json.dumps({
                    'type': 'latest_data',
                    'data': latest,
                    'timestamp': timezone.now().isoformat()
                }))
            
            elif command == 'ping':
                # Response to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
        
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    # Handler untuk message yang dikirim dari channel layer
    async def sensor_data_update(self, event):
        """Handle sensor data updates from channel layer"""
        await self.send(text_data=json.dumps(event['data']))
    
    # Helper methods
    @sync_to_async
    def get_latest_sensor_data(self):
        """Get latest sensor reading dari database"""
        try:
            latest = SensorReading.objects.latest('timestamp')
            return {
                'id': latest.id,
                'temperature': latest.temperature,
                'humidity': latest.humidity,
                'temp_status': latest.temp_status,
                'humidity_status': latest.humidity_status,
                'location': latest.location,
                'timestamp': latest.timestamp.isoformat(),
                'source': latest.source
            }
        except SensorReading.DoesNotExist:
            return None
    
    @sync_to_async
    def get_sensor_history(self, hours=24, limit=100):
        """Get historical sensor data"""
        start_time = timezone.now() - timedelta(hours=hours)
        readings = SensorReading.objects.filter(
            timestamp__gte=start_time
        ).order_by('-timestamp')[:limit]
        
        data = [{
            'id': r.id,
            'temperature': r.temperature,
            'humidity': r.humidity,
            'temp_status': r.temp_status,
            'humidity_status': r.humidity_status,
            'location': r.location,
            'timestamp': r.timestamp.isoformat(),
            'source': r.source
        } for r in reversed(list(readings))]
        
        return data


def broadcast_sensor_data(sensor_data):
    """
    Function untuk broadcast sensor data ke semua connected WebSocket clients
    Call ini dari MQTT service ketika ada data baru
    
    Usage:
        from monitoring.consumers import broadcast_sensor_data
        broadcast_sensor_data({
            'temperature': 25.5,
            'humidity': 60.2,
            'temp_status': 'normal',
            'humidity_status': 'normal',
            'location': 'Ruangan Monitoring',
            'timestamp': datetime.now().isoformat(),
            'source': 'MQTT'
        })
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    
    # Prepare message to send to all connected clients
    message = {
        'type': 'sensor_data_update',
        'data': {
            'type': 'real_time_update',
            'data': sensor_data,
            'timestamp': timezone.now().isoformat()
        }
    }
    
    # Send to all clients in the sensor_data group
    async_to_sync(channel_layer.group_send)(
        'sensor_sensor_data',
        message
    )
