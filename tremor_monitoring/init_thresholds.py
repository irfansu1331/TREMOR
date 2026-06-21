#!/usr/bin/env python
# Initialize default thresholds
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from monitoring.models import ThresholdSetting

if not ThresholdSetting.objects.exists():
    ThresholdSetting.objects.create(
        temp_warning_low=15,
        temp_warning_high=30,
        temp_danger_low=10,
        temp_danger_high=35,
        humidity_warning_low=30,
        humidity_warning_high=75,
        humidity_danger_low=20,
        humidity_danger_high=85
    )
    print("✓ Default thresholds created successfully!")
else:
    print("✓ Thresholds already exist")
