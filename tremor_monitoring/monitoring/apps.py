from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    name = 'monitoring'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Amonia Monitoring System'
    
    def ready(self):
        """Initialize MQTT service when Django starts"""
        try:
            from .mqtt_service import start_mqtt_service
            import logging
            logger = logging.getLogger(__name__)
            
            # Start MQTT service
            if start_mqtt_service():
                logger.info("MQTT service started successfully")
            else:
                logger.warning("Failed to start MQTT service")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error starting MQTT service: {str(e)}")

