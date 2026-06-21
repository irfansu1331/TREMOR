#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views untuk monitoring DHT22 (Temperature & Humidity) - TREMOR Project
"""
import json
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import logging

from .models import SensorReading, SensorDevice, ThresholdSetting, SystemLog, CalibrationSetting
from .mqtt_service import get_mqtt_service

logger = logging.getLogger(__name__)


# ==================== Authentication ====================

def login_view(request):
    """Login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'monitoring/login.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """Render dashboard HTML"""
    context = {
        'page_title': 'TREMOR - Temperature & Humidity Monitoring'
    }
    return render(request, 'monitoring/dashboard.html', context)


# ==================== API Endpoints - Temperature & Humidity ====================

@require_http_methods(["GET"])
@login_required(login_url='login')
def api_latest_reading(request):
    """Get latest sensor reading (DHT22 - Temperature & Humidity)"""
    try:
        latest = SensorReading.objects.latest('timestamp')
        return JsonResponse({
            'temperature': latest.temperature,
            'humidity': latest.humidity,
            'temp_status': latest.temp_status,
            'humidity_status': latest.humidity_status,
            'location': latest.location,
            'timestamp': latest.timestamp.isoformat(),
            'source': latest.source
        })
    except SensorReading.DoesNotExist:
        return JsonResponse({'error': 'No readings available'}, status=404)


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_readings_history(request):
    """Get sensor readings history (Temperature & Humidity)"""
    hours = int(request.GET.get('hours', 24))
    limit = int(request.GET.get('limit', 100))
    
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
    
    return JsonResponse(data, safe=False)


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_statistics(request):
    """Get statistics for sensor readings (Temperature & Humidity)"""
    hours = int(request.GET.get('hours', 24))
    start_time = timezone.now() - timedelta(hours=hours)
    
    readings = SensorReading.objects.filter(timestamp__gte=start_time)
    
    if not readings.exists():
        return JsonResponse({'error': 'No data available'}, status=404)
    
    temps = list(readings.values_list('temperature', flat=True))
    humidities = list(readings.values_list('humidity', flat=True))
    
    temp_stats = {
        'avg_temp': sum(temps) / len(temps) if temps else 0,
        'max_temp': max(temps) if temps else 0,
        'min_temp': min(temps) if temps else 0,
    }
    
    humidity_stats = {
        'avg_humidity': sum(humidities) / len(humidities) if humidities else 0,
        'max_humidity': max(humidities) if humidities else 0,
        'min_humidity': min(humidities) if humidities else 0,
    }
    
    total_count = readings.count()
    query = readings
    
    normal_temp_count = query.filter(temp_status='normal').count()
    warning_temp_count = query.filter(temp_status='warning').count()
    danger_temp_count = query.filter(temp_status='danger').count()
    
    normal_hum_count = query.filter(humidity_status='normal').count()
    warning_hum_count = query.filter(humidity_status='warning').count()
    danger_hum_count = query.filter(humidity_status='danger').count()
    
    try:
        threshold = ThresholdSetting.objects.latest('updated_at')
    except ThresholdSetting.DoesNotExist:
        threshold = ThresholdSetting.objects.create()
    
    return JsonResponse({
        'temperature': {
            'average': round(temp_stats['avg_temp'], 2),
            'maximum': round(temp_stats['max_temp'], 2),
            'minimum': round(temp_stats['min_temp'], 2),
        },
        'humidity': {
            'average': round(humidity_stats['avg_humidity'], 2),
            'maximum': round(humidity_stats['max_humidity'], 2),
            'minimum': round(humidity_stats['min_humidity'], 2),
        },
        'total_readings': total_count,
        'temperature_status': {
            'normal': normal_temp_count,
            'warning': warning_temp_count,
            'danger': danger_temp_count
        },
        'humidity_status': {
            'normal': normal_hum_count,
            'warning': warning_hum_count,
            'danger': danger_hum_count
        },
        'thresholds': {
            'temperature': {
                'warning_low': threshold.temp_warning_low,
                'warning_high': threshold.temp_warning_high,
                'danger_low': threshold.temp_danger_low,
                'danger_high': threshold.temp_danger_high,
            },
            'humidity': {
                'warning_low': threshold.humidity_warning_low,
                'warning_high': threshold.humidity_warning_high,
                'danger_low': threshold.humidity_danger_low,
                'danger_high': threshold.humidity_danger_high,
            }
        }
    })


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_device_status(request):
    """Get all devices status"""
    devices = SensorDevice.objects.all().values(
        'name', 'location', 'device_id', 'is_active', 'last_online'
    )
    return JsonResponse(list(devices), safe=False)


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_threshold(request):
    """Get current threshold settings"""
    try:
        threshold = ThresholdSetting.objects.latest('updated_at')
    except ThresholdSetting.DoesNotExist:
        threshold = ThresholdSetting.objects.create()
    
    return JsonResponse({
        'temperature': {
            'warning_low': threshold.temp_warning_low,
            'warning_high': threshold.temp_warning_high,
            'danger_low': threshold.temp_danger_low,
            'danger_high': threshold.temp_danger_high,
        },
        'humidity': {
            'warning_low': threshold.humidity_warning_low,
            'warning_high': threshold.humidity_warning_high,
            'danger_low': threshold.humidity_danger_low,
            'danger_high': threshold.humidity_danger_high,
        }
    })


@require_http_methods(["GET"])
@csrf_exempt
@login_required(login_url='login')
def api_sensor_status(request):
    """Get sensor connection status based on MQTT message frequency and last reading"""
    try:
        latest = SensorReading.objects.latest('timestamp')
        now = timezone.now()
        time_diff = (now - latest.timestamp).total_seconds()
        
        is_connected = time_diff < 30  # Consider offline if no data for 30 seconds
        
        return JsonResponse({
            'is_connected': is_connected,
            'last_reading': latest.timestamp.isoformat(),
            'seconds_since_last_reading': int(time_diff),
            'location': latest.location
        })
    except SensorReading.DoesNotExist:
        return JsonResponse({
            'is_connected': False,
            'error': 'No readings available'
        }, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_save_threshold(request):
    """Save threshold settings"""
    try:
        data = json.loads(request.body)
        
        threshold, created = ThresholdSetting.objects.get_or_create(pk=1)
        
        # Update temperature thresholds
        if 'temperature' in data:
            temp_data = data['temperature']
            threshold.temp_warning_low = float(temp_data.get('warning_low', threshold.temp_warning_low))
            threshold.temp_warning_high = float(temp_data.get('warning_high', threshold.temp_warning_high))
            threshold.temp_danger_low = float(temp_data.get('danger_low', threshold.temp_danger_low))
            threshold.temp_danger_high = float(temp_data.get('danger_high', threshold.temp_danger_high))
        
        # Update humidity thresholds
        if 'humidity' in data:
            hum_data = data['humidity']
            threshold.humidity_warning_low = float(hum_data.get('warning_low', threshold.humidity_warning_low))
            threshold.humidity_warning_high = float(hum_data.get('warning_high', threshold.humidity_warning_high))
            threshold.humidity_danger_low = float(hum_data.get('danger_low', threshold.humidity_danger_low))
            threshold.humidity_danger_high = float(hum_data.get('danger_high', threshold.humidity_danger_high))
        
        threshold.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Threshold settings saved',
            'data': {
                'temperature': {
                    'warning_low': threshold.temp_warning_low,
                    'warning_high': threshold.temp_warning_high,
                    'danger_low': threshold.temp_danger_low,
                    'danger_high': threshold.temp_danger_high,
                },
                'humidity': {
                    'warning_low': threshold.humidity_warning_low,
                    'warning_high': threshold.humidity_warning_high,
                    'danger_low': threshold.humidity_danger_low,
                    'danger_high': threshold.humidity_danger_high,
                }
            }
        })
    except Exception as e:
        logger.error(f"Error saving threshold: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_save_reading(request):
    """Save sensor reading manually"""
    try:
        data = json.loads(request.body)
        
        reading = SensorReading(
            temperature=float(data.get('temperature', 0)),
            humidity=float(data.get('humidity', 0)),
            location=data.get('location', 'Ruangan Monitoring'),
            source=data.get('source', 'API'),
        )
        reading.save()
        
        return JsonResponse({'success': True, 'id': reading.id})
    except Exception as e:
        logger.error(f"Error saving reading: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_mqtt_config(request):
    """Get MQTT configuration"""
    return JsonResponse({
        'broker': settings.MQTT_BROKER,
        'port': settings.MQTT_PORT,
        'topic': settings.MQTT_TOPIC,
    })


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_polling_config(request):
    """Get polling configuration"""
    return JsonResponse({
        'enabled': True,
        'interval': 5000  # milliseconds
    })


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_calibration_status(request):
    """Get calibration status"""
    try:
        cal = CalibrationSetting.objects.latest('updated_at')
        return JsonResponse({
            'is_calibrated': cal.is_calibrated,
            'zero_point': cal.zero_point,
            'offset': cal.offset,
            'last_calibration': cal.updated_at.isoformat()
        })
    except CalibrationSetting.DoesNotExist:
        return JsonResponse({'is_calibrated': False})


@require_http_methods(["POST"])
@csrf_exempt
def api_set_zero_point(request):
    """Set calibration zero point"""
    try:
        cal, created = CalibrationSetting.objects.get_or_create(pk=1)
        latest = SensorReading.objects.latest('timestamp')
        cal.zero_point = latest.temperature
        cal.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_set_offset(request):
    """Set calibration offset"""
    try:
        data = json.loads(request.body)
        cal, created = CalibrationSetting.objects.get_or_create(pk=1)
        cal.offset = float(data.get('offset', 0))
        cal.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_reset_calibration(request):
    """Reset calibration"""
    try:
        cal, created = CalibrationSetting.objects.get_or_create(pk=1)
        cal.is_calibrated = False
        cal.zero_point = 0
        cal.offset = 0
        cal.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_export_data(request):
    """Export sensor data as CSV"""
    import csv
    from django.http import HttpResponse
    
    hours = int(request.GET.get('hours', 24))
    start_time = timezone.now() - timedelta(hours=hours)
    
    readings = SensorReading.objects.filter(timestamp__gte=start_time).order_by('timestamp')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tremor_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)', 'Temp Status', 'Hum Status', 'Location'])
    
    for reading in readings:
        writer.writerow([
            reading.timestamp,
            reading.temperature,
            reading.humidity,
            reading.temp_status,
            reading.humidity_status,
            reading.location
        ])
    
    return response


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_system_logs(request):
    """Get system logs"""
    limit = int(request.GET.get('limit', 50))
    logs = SystemLog.objects.all().order_by('-timestamp')[:limit]
    
    data = [{
        'timestamp': log.timestamp.isoformat(),
        'level': log.level,
        'message': log.message,
        'source': log.source
    } for log in reversed(list(logs))]
    
    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
@csrf_exempt
def api_log_event(request):
    """Log an event"""
    try:
        data = json.loads(request.body)
        log = SystemLog(
            level=data.get('level', 'INFO'),
            message=data.get('message', ''),
            source=data.get('source', 'API')
        )
        log.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_documentation(request):
    """API documentation"""
    return JsonResponse({
        'title': 'TREMOR API Documentation',
        'version': '1.0',
        'endpoints': {
            'api/latest/': 'Get latest sensor reading',
            'api/history/': 'Get sensor readings history',
            'api/statistics/': 'Get statistics',
            'api/threshold/': 'Get threshold settings',
            'api/save-threshold/': 'Save threshold settings',
        }
    })


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_ai_prediction(request):
    """AI prediction endpoint (placeholder)"""
    return JsonResponse({'message': 'AI prediction feature coming soon'})


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_anomaly_detection(request):
    """Anomaly detection endpoint (placeholder)"""
    return JsonResponse({'message': 'Anomaly detection feature coming soon'})


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_pattern_analysis(request):
    """Pattern analysis endpoint (placeholder)"""
    return JsonResponse({'message': 'Pattern analysis feature coming soon'})


@require_http_methods(["GET"])
@login_required(login_url='login')
def api_analytics_summary(request):
    """Get comprehensive analytics summary"""
    try:
        time_period = request.GET.get('period', '24h')
        
        if time_period == '7d':
            hours = 168
        elif time_period == '30d':
            hours = 720
        else:
            hours = 24
        
        start_time = timezone.now() - timedelta(hours=hours)
        readings = SensorReading.objects.filter(timestamp__gte=start_time)
        
        if not readings.exists():
            return JsonResponse({
                'success': False,
                'error': 'Insufficient data'
            }, status=400)
        
        temps = list(readings.values_list('temperature', flat=True))
        humidities = list(readings.values_list('humidity', flat=True))
        
        return JsonResponse({
            'success': True,
            'period': time_period,
            'data_points': readings.count(),
            'temperature': {
                'average': round(sum(temps) / len(temps), 2) if temps else 0,
                'max': round(max(temps), 2) if temps else 0,
                'min': round(min(temps), 2) if temps else 0,
            },
            'humidity': {
                'average': round(sum(humidities) / len(humidities), 2) if humidities else 0,
                'max': round(max(humidities), 2) if humidities else 0,
                'min': round(min(humidities), 2) if humidities else 0,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
