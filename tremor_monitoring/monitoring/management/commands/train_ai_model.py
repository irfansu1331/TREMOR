"""
Django management command untuk training AI models
Usage: python manage.py train_ai_model
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from monitoring.models import SensorReading
from monitoring.ai_models import ai_models
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    

class Command(BaseCommand):
    help = 'Train AI models menggunakan historical sensor data'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Starting AI Model Training...\n'))
        
        # Get 30 days of historical data
        thirty_days_ago = timezone.now() - timedelta(days=30)
        readings = SensorReading.objects.filter(
            timestamp__gte=thirty_days_ago
        ).order_by('timestamp').values_list('ammonia_level', 'timestamp')
        
        if len(readings) < 100:
            self.stdout.write(self.style.WARNING(
                f'⚠️  Only {len(readings)} readings available. Need at least 100 for training.\n'
            ))
            return
        
        ppm_values = [float(r[0]) for r in readings]
        timestamps = [r[1] for r in readings]
        
        self.stdout.write(f'✓ Loaded {len(ppm_values)} readings for training')
        
        # Train Anomaly Detector
        try:
            self._train_anomaly_detector(ppm_values)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Anomaly Detector training failed: {e}'))
        
        # Train Pattern Analysis (K-Means)
        try:
            self._train_pattern_analysis(timestamps, ppm_values)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Pattern Analysis training failed: {e}'))
        
        # Train LSTM Forecast Model
        try:
            self._train_lstm_forecast(ppm_values)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ LSTM training failed: {e}'))
        
        # Save models
        ai_models.save_models()
        
        self.stdout.write(self.style.SUCCESS('\n✅ AI Model Training Completed!'))
    
    def _train_anomaly_detector(self, ppm_values):
        """Train Isolation Forest untuk anomaly detection"""
        if not SKLEARN_AVAILABLE:
            self.stdout.write(self.style.WARNING('⚠️  Scikit-learn not available, skipping anomaly detection'))
            return
        
        self.stdout.write('\n📊 Training Anomaly Detector (Isolation Forest)...')
        
        # Prepare features
        data = np.array(ppm_values).reshape(-1, 1)
        
        # Train Isolation Forest
        iso_forest = IsolationForest(
            contamination=0.05,  # 5% anomalies
            random_state=42,
            n_estimators=100
        )
        iso_forest.fit(data)
        
        ai_models.anomaly_detector = iso_forest
        
        self.stdout.write(self.style.SUCCESS('  ✓ Anomaly Detector trained'))
    
    def _train_pattern_analysis(self, timestamps, ppm_values):
        """Train pattern analysis untuk daily patterns"""
        if not SKLEARN_AVAILABLE:
            self.stdout.write(self.style.WARNING('⚠️  Scikit-learn not available, skipping pattern analysis'))
            return
        
        self.stdout.write('\n📈 Training Pattern Analysis...')
        
        # Extract hourly patterns
        hourly_features = []
        for timestamp, value in zip(timestamps, ppm_values):
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            hourly_features.append([hour, day_of_week, float(value)])
        
        hourly_features = np.array(hourly_features)
        
        # Normalize
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(hourly_features)
        
        # K-Means clustering untuk 3 clusters (low, medium, high activity)
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(features_scaled)
        
        ai_models.kmeans_model = kmeans
        ai_models.scaler = scaler
        
        # Store cluster centers
        ai_models.pattern_centers = {
            'centers': kmeans.cluster_centers_.tolist(),
            'labels': kmeans.labels_.tolist()
        }
        
        self.stdout.write(self.style.SUCCESS('  ✓ Pattern Analysis trained'))
    
    def _train_lstm_forecast(self, ppm_values):
        """Train LSTM untuk forecasting - Optional (requires TensorFlow)"""
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
            from sklearn.preprocessing import MinMaxScaler
        except ImportError:
            self.stdout.write(self.style.WARNING('⚠️  TensorFlow not available, skipping LSTM training'))
            return
        
        self.stdout.write('\n🧠 Training LSTM Forecast Model...')
        
        # Prepare data
        data = np.array(ppm_values).reshape(-1, 1)
        
        lstm_scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = lstm_scaler.fit_transform(data)
        
        # Create sequences
        lookback = 12  # Use 12 steps (1 hour if 5-min intervals)
        generator = TimeseriesGenerator(
            scaled_data, scaled_data,
            length=lookback, batch_size=32
        )
        
        # Build model
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(lookback, 1)),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train
        model.fit(generator, epochs=10, verbose=0)
        
        ai_models.lstm_model = model
        ai_models.scaler = lstm_scaler
        
        self.stdout.write(self.style.SUCCESS('  ✓ LSTM Forecast Model trained'))
