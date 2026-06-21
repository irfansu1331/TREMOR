from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = 'Start MQTT service for sensor data collection'

    def handle(self, *args, **options):
        from monitoring.mqtt_service import get_mqtt_service
        
        self.stdout.write(self.style.SUCCESS('Starting MQTT service...'))
        
        service = get_mqtt_service()
        
        try:
            if service.connect():
                self.stdout.write(self.style.SUCCESS('MQTT service connected successfully!'))
                self.stdout.write(f"Broker: {service.broker}:{service.port}")
                self.stdout.write(f"Topic: {service.topic}")
                
                # Keep service running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stdout.write(self.style.WARNING('\nShutting down MQTT service...'))
                    service.disconnect()
                    self.stdout.write(self.style.SUCCESS('MQTT service stopped.'))
            else:
                self.stdout.write(self.style.ERROR('Failed to connect MQTT service'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
