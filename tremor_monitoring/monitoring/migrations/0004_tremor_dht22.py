# Generated migration for TREMOR DHT22 Temperature & Humidity Monitoring
# From Ammonia Monitoring to Temperature & Humidity Monitoring

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_systemlog'),
    ]

    operations = [
        # Update SensorReading model
        migrations.RemoveField(
            model_name='sensorreading',
            name='ammonia_level',
        ),
        migrations.RemoveField(
            model_name='sensorreading',
            name='status',
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='temperature',
            field=models.FloatField(default=0, help_text='Suhu dalam Celsius (°C)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='humidity',
            field=models.FloatField(default=0, help_text='Kelembaban dalam Persen (%)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='temp_status',
            field=models.CharField(choices=[('normal', 'Normal'), ('warning', 'Warning'), ('danger', 'Danger')], default='normal', max_length=20),
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='humidity_status',
            field=models.CharField(choices=[('normal', 'Normal'), ('warning', 'Warning'), ('danger', 'Danger')], default='normal', max_length=20),
        ),
        
        # Update default location
        migrations.AlterField(
            model_name='sensorreading',
            name='location',
            field=models.CharField(default='Ruangan Monitoring', max_length=100),
        ),
        
        # Update ThresholdSetting model
        migrations.RemoveField(
            model_name='thresholdsetting',
            name='warning_level',
        ),
        migrations.RemoveField(
            model_name='thresholdsetting',
            name='danger_level',
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='temp_warning_low',
            field=models.FloatField(default=15),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='temp_warning_high',
            field=models.FloatField(default=30),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='temp_danger_low',
            field=models.FloatField(default=10),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='temp_danger_high',
            field=models.FloatField(default=35),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='humidity_warning_low',
            field=models.FloatField(default=30),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='humidity_warning_high',
            field=models.FloatField(default=75),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='humidity_danger_low',
            field=models.FloatField(default=20),
        ),
        migrations.AddField(
            model_name='thresholdsetting',
            name='humidity_danger_high',
            field=models.FloatField(default=85),
        ),
    ]
