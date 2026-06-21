"""
AI Models untuk Amonia Monitoring System
- LSTM untuk forecasting PPM 1 jam ke depan
- Isolation Forest untuk anomaly detection
- K-Means clustering untuk pattern analysis
- Statistical analysis untuk trend
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
import os
from pathlib import Path
import json

try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# Model paths
MODEL_DIR = Path(__file__).parent / 'models'
MODEL_DIR.mkdir(exist_ok=True)

LSTM_MODEL_PATH = MODEL_DIR / 'lstm_forecaster.keras'
SCALER_PATH = MODEL_DIR / 'scaler.pkl'
ANOMALY_MODEL_PATH = MODEL_DIR / 'anomaly_detector.pkl'
KMEANS_MODEL_PATH = MODEL_DIR / 'pattern_kmeans.pkl'
PATTERN_CENTERS_PATH = MODEL_DIR / 'pattern_centers.json'


class AmmoniAIModels:
    """Kumpulan model AI untuk analisis data amonia"""
    
    def __init__(self):
        self.lstm_model = None
        self.scaler = None
        self.anomaly_detector = None
        self.kmeans_model = None
        self.pattern_centers = None
        self.load_models()
    
    # ==================== MODEL LOADING ====================
    
    def load_models(self):
        """Load semua trained models"""
        try:
            if TENSORFLOW_AVAILABLE and os.path.exists(LSTM_MODEL_PATH):
                self.lstm_model = load_model(LSTM_MODEL_PATH)
        except Exception as e:
            print(f"Failed to load LSTM model: {e}")
        
        try:
            if os.path.exists(SCALER_PATH):
                with open(SCALER_PATH, 'rb') as f:
                    self.scaler = pickle.load(f)
        except Exception as e:
            print(f"Failed to load scaler: {e}")
        
        try:
            if SKLEARN_AVAILABLE and os.path.exists(ANOMALY_MODEL_PATH):
                with open(ANOMALY_MODEL_PATH, 'rb') as f:
                    self.anomaly_detector = pickle.load(f)
        except Exception as e:
            print(f"Failed to load anomaly detector: {e}")
        
        try:
            if SKLEARN_AVAILABLE and os.path.exists(KMEANS_MODEL_PATH):
                with open(KMEANS_MODEL_PATH, 'rb') as f:
                    self.kmeans_model = pickle.load(f)
        except Exception as e:
            print(f"Failed to load K-Means model: {e}")
        
        try:
            if os.path.exists(PATTERN_CENTERS_PATH):
                with open(PATTERN_CENTERS_PATH, 'r') as f:
                    self.pattern_centers = json.load(f)
        except Exception as e:
            print(f"Failed to load pattern centers: {e}")
    
    # ==================== FORECASTING (LSTM) ====================
    
    def forecast_ppm_lstm(self, recent_data, hours=1):
        """
        FORECASTING AMMONIA LEVELS (LSTM Neural Network)
        =================================================
        Memprediksi konsentrasi ammonia di masa depan menggunakan teknologi 
        LSTM (Long Short-Term Memory) - jaringan neural yang dapat mempelajari 
        pola temporal dari data sensor.
        
        BAGAIMANA CARA KERJANYA:
        - Menganalisis data konsentrasi ammonia dari 12 jam terakhir
        - Mengenali pola dan tren dari data historis
        - Memprediksi nilai ammonia untuk 30 menit ke depan
        - Memberikan confidence score berdasarkan stabilitas data
        - Menentukan trend (meningkat/menurun/stabil)
        
        KEGUNAAN:
        - Antisipasi awal jika ammonia akan meningkat berbahaya
        - Memberikan waktu untuk tindakan pencegahan
        - Membantu optimasi sistem ventilasi
        
        Args:
            recent_data: List of recent PPM values (last 24 hours)
            hours: Jumlah jam untuk forecast (default 0.5 = 30 menit)
        
        Returns:
            Dict berisi: predicted_ppm, confidence (%), trend, model_type
        """
        if not TENSORFLOW_AVAILABLE or self.lstm_model is None:
            return self.forecast_ppm_simple(recent_data, hours)
        
        try:
            # Prepare data
            data = np.array(recent_data).reshape(-1, 1)
            
            if self.scaler is not None:
                data_scaled = self.scaler.transform(data)
            else:
                # Simple normalization
                data_scaled = (data - np.mean(data)) / (np.std(data) + 1e-8)
            
            # Use last 12 values for prediction
            sequence = data_scaled[-12:] if len(data_scaled) >= 12 else data_scaled
            sequence = sequence.reshape(1, len(sequence), 1)
            
            # Predict
            predictions = []
            current_sequence = sequence.copy()
            
            for _ in range(hours):
                pred = self.lstm_model.predict(current_sequence, verbose=0)
                predictions.append(pred[0, 0])
                
                # Update sequence for next prediction
                current_sequence = np.append(current_sequence[0, 1:, :], 
                                            pred.reshape(1, 1), axis=0)
                current_sequence = current_sequence.reshape(1, len(current_sequence), 1)
            
            # Inverse scale
            if self.scaler is not None:
                predictions_original = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
            else:
                predictions_original = predictions * (np.std(data) + 1e-8) + np.mean(data)
            
            next_value = float(predictions_original[-1][0])
            
            # Calculate confidence (0-100%)
            recent_std = np.std(recent_data[-12:]) if len(recent_data) >= 12 else np.std(recent_data)
            confidence = max(0, min(100, 100 - (recent_std / (np.mean(recent_data) + 1e-8)) * 100))
            
            # Determine trend
            if len(recent_data) >= 3:
                recent_trend = (recent_data[-1] - recent_data[-3]) / 3
                trend = "Meningkat" if recent_trend > 5 else "Menurun" if recent_trend < -5 else "Stabil"
            else:
                trend = "Stabil"
            
            return {
                'success': True,
                'predicted_ppm': round(next_value, 2),
                'confidence': round(confidence, 1),
                'trend': trend,
                'model_type': 'LSTM',
                'hours_ahead': hours
            }
        
        except Exception as e:
            print(f"LSTM forecast error: {e}")
            return self.forecast_ppm_simple(recent_data, hours)
    
    def forecast_ppm_simple(self, recent_data, hours=1):
        """
        BACKUP FORECASTING (Simple Moving Average)
        ===========================================
        Metode fallback ketika model LSTM tidak tersedia.
        Menggunakan teknik moving average sederhana untuk prediksi.
        
        BAGAIMANA CARA KERJANYA:
        - Menghitung rata-rata 3 jam terakhir (trend pendek)
        - Menghitung rata-rata 12 jam terakhir (trend panjang)
        - Membandingkan kedua trend untuk memprediksi arah perubahan
        - Less sophisticated dibanding LSTM tapi tetap akurat
        
        Args:
            recent_data: List of recent PPM values
            hours: Jumlah jam untuk forecast
        
        Returns:
            Dict dengan predicted_ppm, confidence, trend
        """
        if len(recent_data) == 0:
            return {
                'success': False,
                'error': 'No data available'
            }
        
        # Calculate simple moving average
        ma_short = np.mean(recent_data[-3:])
        ma_long = np.mean(recent_data[-12:]) if len(recent_data) >= 12 else np.mean(recent_data)
        
        # Trend
        if ma_short > ma_long:
            predicted = ma_short + (ma_short - ma_long) * 0.5
            trend = "Meningkat"
        elif ma_short < ma_long:
            predicted = ma_short - (ma_long - ma_short) * 0.5
            trend = "Menurun"
        else:
            predicted = ma_short
            trend = "Stabil"
        
        # Confidence sederhana
        recent_std = np.std(recent_data[-12:]) if len(recent_data) >= 12 else np.std(recent_data)
        confidence = max(0, min(100, 100 - (recent_std / (np.mean(recent_data) + 1e-8)) * 100))
        
        return {
            'success': True,
            'predicted_ppm': round(max(0, predicted), 2),
            'confidence': round(confidence, 1),
            'trend': trend,
            'model_type': 'Simple Moving Average',
            'hours_ahead': hours
        }
    
    # ==================== ANOMALY DETECTION ====================
    
    def detect_anomaly(self, current_value, recent_data, window=24):
        """
        ANOMALY DETECTION - Deteksi Pembacaan Abnormal
        ===============================================
        Mengidentifikasi jika pembacaan sensor saat ini tidak normal atau 
        menyimpang dari pola biasanya menggunakan teknik statistik advanced.
        
        BAGAIMANA CARA KERJANYA:
        - Membandingkan pembacaan saat ini dengan riwayat 24 jam
        - Menggunakan Isolation Forest (AI method) atau Z-Score (statistical)
        - Mendeteksi nilai yang terlalu tinggi atau terlalu rendah
        - Memberikan confidence score untuk anomali
        
        KEMUNGKINAN ANOMALI:
        - Sensor rusak/error kalibrasi
        - Lonjakan ammonia mendadak (emergency)
        - Sensor tidak terkoneksi dengan baik
        
        KEGUNAAN:
        - Alert real-time jika ada pembacaan tidak normal
        - Validasi data sebelum analisis lebih lanjut
        - Identifikasi masalah hardware sensor
        
        Args:
            current_value: Current PPM reading
            recent_data: List of recent PPM values
            window: Window size untuk analysis (24 jam)
        
        Returns:
            Dict berisi: is_anomaly, confidence (%), reason, method
        """
        if len(recent_data) < 3:
            return {
                'is_anomaly': False,
                'confidence': 0,
                'reason': 'Insufficient data'
            }
        
        # Method 1: Isolation Forest (jika available)
        if SKLEARN_AVAILABLE and self.anomaly_detector is not None:
            try:
                data_window = np.array(recent_data[-window:]).reshape(-1, 1)
                current_point = np.array([[current_value]])
                
                combined_data = np.vstack([data_window, current_point])
                predictions = self.anomaly_detector.predict(combined_data)
                
                is_anomaly = predictions[-1] == -1  # -1 for anomaly, 1 for normal
                confidence = 85
                
                return {
                    'is_anomaly': is_anomaly,
                    'confidence': confidence,
                    'method': 'Isolation Forest',
                    'reason': 'Sensor reading deviation detected' if is_anomaly else 'Normal operation'
                }
            except Exception as e:
                print(f"Isolation Forest error: {e}")
        
        # Method 2: Statistical Z-score
        recent_mean = np.mean(recent_data[-window:])
        recent_std = np.std(recent_data[-window:])
        
        if recent_std < 1:  # Avoid division issues
            z_score = 0
        else:
            z_score = abs((current_value - recent_mean) / recent_std)
        
        # Threshold: 3 sigma = 99.7% confidence
        is_anomaly = z_score > 3
        confidence = min(100, (z_score / 3) * 100) if z_score > 0 else 0
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': round(confidence, 1),
            'method': 'Statistical Z-Score',
            'z_score': round(z_score, 2),
            'reason': f'Z-score {z_score:.2f} exceeds threshold' if is_anomaly else 'Normal operation'
        }
    
    # ==================== PATTERN ANALYSIS ====================
    
    def analyze_daily_pattern(self, data_with_time):
        """
        DAILY PATTERN ANALYSIS - Analisis Pola Harian
        ==============================================
        Menganalisis konsentrasi ammonia per jam untuk menemukan kapan 
        ammonia biasanya tinggi dan rendah selama sehari.
        
        BAGAIMANA CARA KERJANYA:
        - Mengelompokkan data berdasarkan jam (00:00-23:59)
        - Menghitung rata-rata, min, max untuk setiap jam
        - Mengidentifikasi 3 jam dengan konsentrasi tertinggi
        - Mengidentifikasi 3 jam dengan konsentrasi terendah
        
        INFORMASI YANG DIBERIKAN:
        - Peak Hours: Jam-jam ketika ammonia paling banyak (mungkin saat produksi tinggi)
        - Low Hours: Jam-jam ketika ammonia paling sedikit (mungkin saat operasional rendah)
        - Hourly Stats: Detail lengkap (rata-rata, std dev) untuk setiap jam
        
        KEGUNAAN:
        - Mengoptimalkan jadwal maintenance
        - Menyesuaikan sistem ventilasi berdasarkan waktu
        - Prediksi beban kerja operasional per jam
        - Identifikasi waktu kritis dengan ammonia tinggi
        
        Args:
            data_with_time: List of tuples [(timestamp, ppm_value), ...]
        
        Returns:
            Dict berisi: hourly_stats, peak_hours, low_hours, overall_avg
        """
        if len(data_with_time) < 24:
            return {
                'success': False,
                'error': 'Insufficient data (need 24+ hours)'
            }
        
        try:
            # Group by hour
            hourly_data = {}
            for timestamp, value in data_with_time:
                hour = timestamp.hour
                if hour not in hourly_data:
                    hourly_data[hour] = []
                hourly_data[hour].append(value)
            
            # Calculate statistics per hour
            hourly_stats = {}
            for hour in range(24):
                if hour in hourly_data:
                    values = hourly_data[hour]
                    hourly_stats[hour] = {
                        'avg': round(np.mean(values), 2),
                        'min': round(np.min(values), 2),
                        'max': round(np.max(values), 2),
                        'std': round(np.std(values), 2),
                        'count': len(values)
                    }
                else:
                    hourly_stats[hour] = {
                        'avg': 0, 'min': 0, 'max': 0, 'std': 0, 'count': 0
                    }
            
            # Find peak hours
            peak_hours = sorted(hourly_stats.items(), 
                              key=lambda x: x[1]['avg'], 
                              reverse=True)[:3]
            
            # Find low hours
            low_hours = sorted(hourly_stats.items(), 
                             key=lambda x: x[1]['avg'])[:3]
            
            return {
                'success': True,
                'hourly_stats': hourly_stats,
                'peak_hours': [{'hour': h[0], 'avg_ppm': h[1]['avg']} for h in peak_hours],
                'low_hours': [{'hour': h[0], 'avg_ppm': h[1]['avg']} for h in low_hours],
                'overall_avg': round(np.mean([v['avg'] for v in hourly_stats.values()]), 2)
            }
        
        except Exception as e:
            print(f"Pattern analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== STATISTICAL ANALYSIS ====================
    
    def analyze_trend(self, recent_data, time_period='24h'):
        """
        TREND ANALYSIS - Analisis Tren Konsentrasi Ammonia
        ===================================================
        Menganalisis perubahan konsentrasi ammonia dari waktu ke waktu
        untuk menentukan apakah ammonia meningkat, menurun, atau stabil.
        
        BAGAIMANA CARA KERJANYA:
        - Membagi data menjadi 2 periode (awal dan akhir)
        - Menghitung rata-rata masing-masing periode
        - Membandingkan untuk menentukan trend direction
        - Menghitung persentase perubahan
        - Menghitung berbagai statistik (min, max, percentile, std dev)
        
        STATISTIK YANG DIBERIKAN:
        - Current: Pembacaan terakhir
        - Average: Rata-rata dalam periode
        - Min/Max: Nilai terendah dan tertinggi
        - Std Dev: Variabilitas data
        - Percentile 25/50/75: Distribusi data
        - Trend Direction: Meningkat/Menurun/Stabil dengan % perubahan
        
        KEGUNAAN:
        - Monitoring apakah situasi membaik atau memburuk
        - Evaluasi efektivitas sistem kontrol
        - Laporan tren untuk management/regulasi
        - Identifikasi pattern jangka panjang
        
        Args:
            recent_data: List of PPM values
            time_period: '24h', '7d', '30d' untuk konteks
        
        Returns:
            Dict berisi: current, average, min, max, std_dev, trend_direction, change_percent
        """
        if len(recent_data) < 2:
            return {'error': 'Insufficient data'}
        
        try:
            data = np.array(recent_data)
            
            # Calculate statistics
            stats = {
                'current': float(data[-1]),
                'average': round(float(np.mean(data)), 2),
                'min': round(float(np.min(data)), 2),
                'max': round(float(np.max(data)), 2),
                'std_dev': round(float(np.std(data)), 2),
                'percentile_25': round(float(np.percentile(data, 25)), 2),
                'percentile_50': round(float(np.percentile(data, 50)), 2),
                'percentile_75': round(float(np.percentile(data, 75)), 2),
            }
            
            # Trend direction
            if len(data) >= 2:
                recent_avg = np.mean(data[-len(data)//2:])
                older_avg = np.mean(data[:len(data)//2])
                
                change_percent = ((recent_avg - older_avg) / (older_avg + 1e-8)) * 100
                
                if abs(change_percent) < 5:
                    trend_direction = 'Stabil'
                elif change_percent > 0:
                    trend_direction = f'Meningkat +{change_percent:.1f}%'
                else:
                    trend_direction = f'Menurun {change_percent:.1f}%'
                
                stats['trend_direction'] = trend_direction
                stats['change_percent'] = round(change_percent, 1)
            
            # Time period info
            stats['time_period'] = time_period
            stats['data_points'] = len(data)
            
            return stats
        
        except Exception as e:
            print(f"Trend analysis error: {e}")
            return {'error': str(e)}
    
    # ==================== TRAINING ====================
    
    def save_models(self):
        """Save semua trained models"""
        try:
            if self.lstm_model is not None:
                # Save using native Keras format
                self.lstm_model.save(str(LSTM_MODEL_PATH), save_format='keras')
                print('  ✓ LSTM model saved')
            
            if self.scaler is not None:
                with open(SCALER_PATH, 'wb') as f:
                    pickle.dump(self.scaler, f)
            
            if self.anomaly_detector is not None:
                with open(ANOMALY_MODEL_PATH, 'wb') as f:
                    pickle.dump(self.anomaly_detector, f)
            
            if self.kmeans_model is not None:
                with open(KMEANS_MODEL_PATH, 'wb') as f:
                    pickle.dump(self.kmeans_model, f)
            
            if self.pattern_centers is not None:
                with open(PATTERN_CENTERS_PATH, 'w') as f:
                    json.dump(self.pattern_centers, f)
            
            print("✅ All models saved successfully")
        except Exception as e:
            print(f"❌ Error saving models: {e}")


# Global instance
ai_models = AmmoniAIModels()
