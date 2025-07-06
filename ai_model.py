# AI Model for Trading Signals

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import logging

class TradingAI:
    """AI model za trgovanje koji koristi MACD i Volume indikatore"""
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        
        # Inicijalizuj model
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
        
        self.logger = logging.getLogger(__name__)
    
    def prepare_features(self, price_data, macd_data, volume_data, lookback=20):
        """
        Priprema feature-e za AI model
        
        Args:
            price_data: Dictionary sa OHLCV podacima
            macd_data: MACD indikatori
            volume_data: Volume indikatori
            lookback: Broj prethodnih perioda za analizu
        
        Returns:
            numpy array: Feature matrix
        """
        features = []
        
        if not all([price_data, macd_data, volume_data]):
            return np.array([])
        
        # Price features
        close_prices = price_data['close']
        high_prices = price_data['high']
        low_prices = price_data['low']
        
        if len(close_prices) < lookback:
            return np.array([])
        
        # MACD features
        macd_line = macd_data['macd_line']
        signal_line = macd_data['signal_line']
        fast_ema = macd_data['fast_ema']
        slow_ema = macd_data['slow_ema']
        
        # Volume features
        volume_ratio = volume_data['volume_ratio']
        volume_strength = volume_data['volume_strength']
        pvt = volume_data['price_volume_trend']
        
        for i in range(lookback, len(close_prices)):
            feature_vector = []
            
            # Price movement features (poslednji lookback period)
            recent_closes = close_prices[i-lookback:i]
            recent_highs = high_prices[i-lookback:i]
            recent_lows = low_prices[i-lookback:i]
            
            # 1. Price trend features
            price_change_pct = (recent_closes[-1] - recent_closes[0]) / recent_closes[0] * 100
            volatility = np.std(recent_closes) / np.mean(recent_closes) * 100
            
            feature_vector.extend([price_change_pct, volatility])
            
            # 2. MACD features
            current_macd = macd_line[i] if i < len(macd_line) else 0
            current_signal = signal_line[i] if i < len(signal_line) else 0
            prev_macd = macd_line[i-1] if i-1 < len(macd_line) else 0
            prev_signal = signal_line[i-1] if i-1 < len(signal_line) else 0
            
            macd_divergence = current_macd - current_signal
            macd_momentum = (current_macd - prev_macd) if prev_macd != 0 else 0
            signal_momentum = (current_signal - prev_signal) if prev_signal != 0 else 0
            
            # MACD crossover signals
            bullish_crossover = 1 if current_macd > current_signal and prev_macd <= prev_signal else 0
            bearish_crossover = 1 if current_macd < current_signal and prev_macd >= prev_signal else 0
            
            feature_vector.extend([
                macd_divergence, macd_momentum, signal_momentum,
                bullish_crossover, bearish_crossover
            ])
            
            # 3. EMA trend features
            current_fast = fast_ema[i] if i < len(fast_ema) else 0
            current_slow = slow_ema[i] if i < len(slow_ema) else 0
            ema_spread = (current_fast - current_slow) / current_slow * 100 if current_slow != 0 else 0
            
            feature_vector.append(ema_spread)
            
            # 4. Volume features
            current_vol_ratio = volume_ratio[i] if i < len(volume_ratio) else 1
            current_vol_strength = volume_strength[i] if i < len(volume_strength) else 0
            current_pvt = pvt[i] if i < len(pvt) else 0
            
            # Volume trend (poslednih 5 perioda)
            recent_vol_ratios = volume_ratio[max(0, i-5):i] if i-5 >= 0 else volume_ratio[:i]
            vol_trend = np.mean(recent_vol_ratios) if len(recent_vol_ratios) > 0 else 1
            
            feature_vector.extend([
                current_vol_ratio, current_vol_strength, current_pvt, vol_trend
            ])
            
            # 5. Combined momentum features
            price_volume_momentum = price_change_pct * current_vol_ratio
            macd_volume_confirmation = macd_divergence * current_vol_strength
            
            feature_vector.extend([price_volume_momentum, macd_volume_confirmation])
            
            features.append(feature_vector)
        
        # Definiši nazive feature-a
        self.feature_names = [
            'price_change_pct', 'volatility',
            'macd_divergence', 'macd_momentum', 'signal_momentum',
            'bullish_crossover', 'bearish_crossover',
            'ema_spread',
            'volume_ratio', 'volume_strength', 'pvt', 'volume_trend',
            'price_volume_momentum', 'macd_volume_confirmation'
        ]
        
        return np.array(features)
    
    def create_labels(self, price_data, lookback=20, future_periods=5):
        """
        Kreira labele za training (buy=1, sell=-1, hold=0)
        
        Args:
            price_data: Dictionary sa price podacima
            lookback: Broj perioda za feature računanje
            future_periods: Broj perioda u budućnost za label određivanje
        
        Returns:
            numpy array: Labeli
        """
        close_prices = price_data['close']
        labels = []
        
        for i in range(lookback, len(close_prices) - future_periods):
            current_price = close_prices[i]
            future_price = close_prices[i + future_periods]
            
            price_change_pct = (future_price - current_price) / current_price * 100
            
            # Definiši threshold-e za buy/sell signale
            buy_threshold = 0.5  # 0.5% profit
            sell_threshold = -0.5  # 0.5% loss
            
            if price_change_pct > buy_threshold:
                labels.append(1)  # Buy signal
            elif price_change_pct < sell_threshold:
                labels.append(-1)  # Sell signal
            else:
                labels.append(0)  # Hold
        
        return np.array(labels)
    
    def train(self, price_data, macd_data, volume_data, test_size=0.2):
        """
        Trenira AI model
        
        Args:
            price_data: Price podaci
            macd_data: MACD indikatori
            volume_data: Volume indikatori
            test_size: Procenat podataka za testing
        
        Returns:
            dict: Rezultati treniranja
        """
        try:
            # Pripremi features i labels
            features = self.prepare_features(price_data, macd_data, volume_data)
            labels = self.create_labels(price_data)
            
            if len(features) == 0 or len(labels) == 0:
                raise ValueError("Nema dovoljno podataka za treniranje")
            
            # Skrati arrays da budu iste dužine
            min_length = min(len(features), len(labels))
            features = features[:min_length]
            labels = labels[:min_length]
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features_scaled, labels, test_size=test_size, random_state=42, stratify=labels
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            
            self.is_trained = True
            
            results = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            self.logger.info(f"Model treniran - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Greška pri treniranju modela: {e}")
            return None
    
    def predict_signal(self, price_data, macd_data, volume_data):
        """
        Predviđa trading signal
        
        Returns:
            dict: signal, confidence, probabilities
        """
        if not self.is_trained:
            return {'signal': 0, 'confidence': 0.0, 'probabilities': []}
        
        try:
            # Pripremi features za poslednji period
            features = self.prepare_features(price_data, macd_data, volume_data)
            
            if len(features) == 0:
                return {'signal': 0, 'confidence': 0.0, 'probabilities': []}
            
            # Uzmi poslednji feature vector
            last_features = features[-1].reshape(1, -1)
            last_features_scaled = self.scaler.transform(last_features)
            
            # Predvidi signal
            signal = self.model.predict(last_features_scaled)[0]
            
            # Uzmi probabilities
            probabilities = self.model.predict_proba(last_features_scaled)[0]
            confidence = max(probabilities)
            
            return {
                'signal': int(signal),
                'confidence': float(confidence),
                'probabilities': probabilities.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Greška pri predviđanju: {e}")
            return {'signal': 0, 'confidence': 0.0, 'probabilities': []}
    
    def save_model(self, filepath):
        """Sačuva model na disk"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'model_type': self.model_type
            }
            joblib.dump(model_data, filepath)
            self.logger.info(f"Model sačuvan u {filepath}")
    
    def load_model(self, filepath):
        """Učita model sa diska"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_type = model_data['model_type']
            self.is_trained = True
            self.logger.info(f"Model učitan iz {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Greška pri učitavanju modela: {e}")
            return False