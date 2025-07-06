# Technical Indicators for MT5 Trading Bot

import numpy as np
import pandas as pd
import talib

class TechnicalIndicators:
    """Klasa za izračunavanje tehničkih indikatora"""
    
    def __init__(self):
        pass
    
    def calculate_macd_lines(self, close_prices, fast_period=12, slow_period=26, signal_period=9):
        """
        Izračunava MACD linije (ne histogram) - EMA fast i EMA slow linije
        
        Args:
            close_prices: Array zatvorenih cena
            fast_period: Period za brzu EMA
            slow_period: Period za sporu EMA
            signal_period: Period za signal liniju
        
        Returns:
            dict: Sadrži fast_ema, slow_ema, macd_line, signal_line
        """
        if len(close_prices) < slow_period:
            return None
            
        # Izračunaj EMA linije koje čine MACD
        fast_ema = talib.EMA(close_prices, timeperiod=fast_period)
        slow_ema = talib.EMA(close_prices, timeperiod=slow_period)
        
        # MACD linija je razlika između brze i spore EMA
        macd_line = fast_ema - slow_ema
        
        # Signal linija je EMA od MACD linije
        signal_line = talib.EMA(macd_line, timeperiod=signal_period)
        
        return {
            'fast_ema': fast_ema,
            'slow_ema': slow_ema,
            'macd_line': macd_line,
            'signal_line': signal_line
        }
    
    def calculate_volume_indicator(self, volume_data, price_data, period=20):
        """
        Izračunava Volume indikator sa trendom
        
        Args:
            volume_data: Array volume podataka
            price_data: Array cena (close)
            period: Period za izračunavanje proseka
        
        Returns:
            dict: Volume indikatori
        """
        if len(volume_data) < period:
            return None
            
        # Volume Moving Average
        volume_ma = talib.SMA(volume_data, timeperiod=period)
        
        # Volume Ratio (trenutni vs prosečni)
        volume_ratio = volume_data / volume_ma
        
        # Price Volume Trend
        price_change = np.diff(price_data, prepend=price_data[0])
        pvt = np.cumsum((price_change / price_data[:-1]) * volume_data[1:])
        pvt = np.insert(pvt, 0, 0)  # Dodaj početnu vrednost
        
        # Volume Price Confirmation
        volume_strength = np.where(
            (volume_ratio > 1.2) & (np.abs(price_change) > np.std(price_change)),
            1,  # Jaka potvrda
            np.where(
                (volume_ratio > 1.0),
                0.5,  # Umerena potvrda
                0  # Slaba potvrda
            )
        )
        
        return {
            'volume_ma': volume_ma,
            'volume_ratio': volume_ratio,
            'price_volume_trend': pvt,
            'volume_strength': volume_strength
        }
    
    def get_entry_signal_strength(self, macd_data, volume_data):
        """
        Procenjuje snagu signala za ulazak na osnovu MACD i Volume
        
        Returns:
            float: Vrednost između 0 i 1 (šansa za dobar ulazak)
        """
        if not macd_data or not volume_data:
            return 0.0
            
        # MACD signal strength
        macd_line = macd_data['macd_line']
        signal_line = macd_data['signal_line']
        fast_ema = macd_data['fast_ema']
        slow_ema = macd_data['slow_ema']
        
        # Trenutne vrednosti (poslednje)
        current_macd = macd_line[-1] if len(macd_line) > 0 else 0
        current_signal = signal_line[-1] if len(signal_line) > 0 else 0
        current_fast = fast_ema[-1] if len(fast_ema) > 0 else 0
        current_slow = slow_ema[-1] if len(slow_ema) > 0 else 0
        
        # Prethodne vrednosti
        prev_macd = macd_line[-2] if len(macd_line) > 1 else 0
        prev_signal = signal_line[-2] if len(signal_line) > 1 else 0
        
        macd_strength = 0.0
        
        # Bullish crossover (MACD prelazi signal odozdo)
        if current_macd > current_signal and prev_macd <= prev_signal:
            macd_strength += 0.4
            
        # Bearish crossover (MACD prelazi signal odozgo)
        elif current_macd < current_signal and prev_macd >= prev_signal:
            macd_strength += 0.4
            
        # Trend confirmation (fast EMA vs slow EMA)
        if current_fast > current_slow:
            macd_strength += 0.3  # Bullish trend
        elif current_fast < current_slow:
            macd_strength += 0.3  # Bearish trend
            
        # Volume confirmation
        volume_strength = volume_data['volume_strength'][-1] if len(volume_data['volume_strength']) > 0 else 0
        volume_ratio = volume_data['volume_ratio'][-1] if len(volume_data['volume_ratio']) > 0 else 1
        
        # Kombinovana snaga signala
        combined_strength = (macd_strength * 0.6) + (volume_strength * 0.4)
        
        # Bonus za visok volume
        if volume_ratio > 1.5:
            combined_strength *= 1.2
            
        return min(combined_strength, 1.0)
    
    def get_exit_signal(self, macd_data, volume_data, position_type='buy'):
        """
        Određuje kada i gde izaći iz pozicije
        
        Args:
            position_type: 'buy' ili 'sell'
        
        Returns:
            dict: exit_signal (True/False), exit_reason, confidence
        """
        if not macd_data or not volume_data:
            return {'exit_signal': False, 'exit_reason': 'No data', 'confidence': 0.0}
            
        macd_line = macd_data['macd_line']
        signal_line = macd_data['signal_line']
        
        current_macd = macd_line[-1] if len(macd_line) > 0 else 0
        current_signal = signal_line[-1] if len(signal_line) > 0 else 0
        prev_macd = macd_line[-2] if len(macd_line) > 1 else 0
        prev_signal = signal_line[-2] if len(signal_line) > 1 else 0
        
        volume_strength = volume_data['volume_strength'][-1] if len(volume_data['volume_strength']) > 0 else 0
        
        exit_signal = False
        exit_reason = ""
        confidence = 0.0
        
        if position_type.lower() == 'buy':
            # Exit signali za BUY poziciju
            if current_macd < current_signal and prev_macd >= prev_signal:
                exit_signal = True
                exit_reason = "MACD bearish crossover"
                confidence = 0.8
                
        elif position_type.lower() == 'sell':
            # Exit signali za SELL poziciju
            if current_macd > current_signal and prev_macd <= prev_signal:
                exit_signal = True
                exit_reason = "MACD bullish crossover"
                confidence = 0.8
        
        # Povećaj confidence ako je volume potvrda
        if exit_signal and volume_strength > 0.5:
            confidence = min(confidence + 0.2, 1.0)
            
        return {
            'exit_signal': exit_signal,
            'exit_reason': exit_reason,
            'confidence': confidence
        }