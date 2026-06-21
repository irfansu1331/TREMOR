from django.contrib import admin
from .models import SensorReading, SensorDevice, ThresholdSetting


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('temperature', 'humidity', 'temp_status', 'humidity_status', 'location', 'timestamp', 'source')
    list_filter = ('temp_status', 'humidity_status', 'location', 'source', 'timestamp')
    search_fields = ('location',)
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return True


@admin.register(SensorDevice)
class SensorDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'device_id', 'is_active', 'last_online')
    list_filter = ('is_active', 'location')
    search_fields = ('name', 'location', 'device_id')
    readonly_fields = ('last_online',)


@admin.register(ThresholdSetting)
class ThresholdSettingAdmin(admin.ModelAdmin):
    list_display = ('temp_warning_low', 'temp_warning_high', 'temp_danger_low', 'temp_danger_high', 
                    'humidity_warning_low', 'humidity_warning_high', 'humidity_danger_low', 'humidity_danger_high', 'updated_at')
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Allow only one threshold setting
        return not ThresholdSetting.objects.exists()

