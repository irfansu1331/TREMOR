from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/latest/', views.api_latest_reading, name='api-latest'),
    path('api/history/', views.api_readings_history, name='api-history'),
    path('api/statistics/', views.api_statistics, name='api-stats'),
    path('api/devices/', views.api_device_status, name='api-devices'),
    path('api/threshold/', views.api_threshold, name='api-threshold'),
    path('api/sensor-status/', views.api_sensor_status, name='api-sensor-status'),
    path('api/save-threshold/', views.api_save_threshold, name='api-save-threshold'),
    path('api/save-reading/', views.api_save_reading, name='api-save-reading'),
    path('api/mqtt-config/', views.api_mqtt_config, name='api-mqtt-config'),
    path('api/polling-config/', views.api_polling_config, name='api-polling-config'),
    path('api/calibration-status/', views.api_calibration_status, name='api-calibration-status'),
    path('api/set-zero-point/', views.api_set_zero_point, name='api-set-zero-point'),
    path('api/set-offset/', views.api_set_offset, name='api-set-offset'),
    path('api/reset-calibration/', views.api_reset_calibration, name='api-reset-calibration'),
    path('api/export-data/', views.api_export_data, name='api-export-data'),
    path('api/system-logs/', views.api_system_logs, name='api-api-logs'),
    path('api/log-event/', views.api_log_event, name='api-log-event'),
    path('api/documentation/', views.api_documentation, name='api-documentation'),
    
    # AI & Analytics endpoints
    path('api/ai-prediction/', views.api_ai_prediction, name='api-ai-prediction'),
    path('api/anomaly-detection/', views.api_anomaly_detection, name='api-anomaly-detection'),
    path('api/pattern-analysis/', views.api_pattern_analysis, name='api-pattern-analysis'),
    path('api/analytics-summary/', views.api_analytics_summary, name='api-analytics-summary'),
]


