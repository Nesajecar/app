# MetaTrader 5 Trading Bot with AI

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from threading import Thread, Event
import json

from config import *
from indicators import TechnicalIndicators
from ai_model import TradingAI

class MT5Trader:
    """Glavni trading bot koji se povezuje na MT5 i trguje sa AI"""
    
    def __init__(self):
        self.is_connected = False
        self.is_trading = False
        self.stop_event = Event()
        
        # Inicijalizuj komponente
        self.indicators = TechnicalIndicators()
        self.ai_model = TradingAI(model_type='random_forest')
        
        # Trading state
        self.positions = []
        self.balance = 0.0
        self.equity = 0.0
        
        # Data storage
        self.price_history = {
            'time': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []
        }
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_mt5(self):
        """Povezuje se na MetaTrader 5"""
        try:
            if not mt5.initialize():
                self.logger.error("MT5 initialization failed")
                return False
            
            # Login sa credentials
            if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
                login_result = mt5.login(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
                if not login_result:
                    self.logger.error(f"MT5 login failed: {mt5.last_error()}")
                    return False
            
            # Proveri konekciju
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.error("Failed to get account info")
                return False
            
            self.balance = account_info.balance
            self.equity = account_info.equity
            
            self.is_connected = True
            self.logger.info(f"Connected to MT5 - Balance: {self.balance}, Equity: {self.equity}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect_mt5(self):
        """Prekida konekciju sa MT5"""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            self.logger.info("Disconnected from MT5")
    
    def get_market_data(self, symbol=SYMBOL, timeframe=TIMEFRAME, count=LOOKBACK_PERIOD):
        """Dobija market podatke sa MT5"""
        try:
            # Konvertuj timeframe string u MT5 konstancu
            tf_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_M15)
            
            # Dobij rates
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                self.logger.error(f"Failed to get market data for {symbol}")
                return None
            
            # Konvertuj u DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Update internal history
            self.price_history = {
                'time': df['time'].values,
                'open': df['open'].values,
                'high': df['high'].values,
                'low': df['low'].values,
                'close': df['close'].values,
                'volume': df['tick_volume'].values.astype(float)
            }
            
            return self.price_history
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return None
    
    def calculate_indicators(self):
        """Izračunava sve potrebne indikatore"""
        try:
            if not self.price_history['close'].any():
                return None, None
            
            close_prices = self.price_history['close']
            volume_data = self.price_history['volume']
            
            # MACD
            macd_data = self.indicators.calculate_macd_lines(
                close_prices, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD
            )
            
            # Volume indicators
            volume_indicators = self.indicators.calculate_volume_indicator(
                volume_data, close_prices, VOLUME_PERIOD
            )
            
            return macd_data, volume_indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return None, None
    
    def analyze_entry_opportunity(self, macd_data, volume_data):
        """Analizira šanse za ulazak u poziciju"""
        try:
            # Osnovni signal strength iz indikatora
            basic_strength = self.indicators.get_entry_signal_strength(macd_data, volume_data)
            
            # AI prediction
            ai_prediction = self.ai_model.predict_signal(self.price_history, macd_data, volume_data)
            
            # Kombinuj basic i AI signale
            combined_strength = (basic_strength * 0.4) + (ai_prediction['confidence'] * 0.6)
            
            signal_info = {
                'entry_strength': combined_strength,
                'basic_strength': basic_strength,
                'ai_signal': ai_prediction['signal'],
                'ai_confidence': ai_prediction['confidence'],
                'recommendation': self._get_entry_recommendation(combined_strength, ai_prediction)
            }
            
            return signal_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing entry opportunity: {e}")
            return None
    
    def _get_entry_recommendation(self, combined_strength, ai_prediction):
        """Dobija preporuku za ulazak"""
        if combined_strength < PREDICTION_THRESHOLD:
            return "WAIT"
        
        ai_signal = ai_prediction['signal']
        
        if ai_signal == 1 and combined_strength > PREDICTION_THRESHOLD:
            return "BUY"
        elif ai_signal == -1 and combined_strength > PREDICTION_THRESHOLD:
            return "SELL"
        else:
            return "WAIT"
    
    def check_exit_signals(self, macd_data, volume_data):
        """Proverava exit signale za postojeće pozicije"""
        exit_signals = []
        
        for position in self.positions:
            position_type = 'buy' if position['type'] == mt5.ORDER_TYPE_BUY else 'sell'
            
            # Basic exit signal
            basic_exit = self.indicators.get_exit_signal(macd_data, volume_data, position_type)
            
            # AI exit prediction
            ai_prediction = self.ai_model.predict_signal(self.price_history, macd_data, volume_data)
            
            # Kombinuj signale
            should_exit = basic_exit['exit_signal']
            confidence = basic_exit['confidence']
            
            # AI potvrda
            if ai_prediction['signal'] != 0:
                # Ako AI predviđa suprotan signal od pozicije
                if (position_type == 'buy' and ai_prediction['signal'] == -1) or \
                   (position_type == 'sell' and ai_prediction['signal'] == 1):
                    should_exit = True
                    confidence = max(confidence, ai_prediction['confidence'])
            
            if should_exit and confidence > 0.6:
                exit_signals.append({
                    'ticket': position['ticket'],
                    'reason': basic_exit['exit_reason'],
                    'confidence': confidence
                })
        
        return exit_signals
    
    def place_order(self, action, symbol=SYMBOL, lot=LOT_SIZE):
        """Postavlja nalog na MT5"""
        try:
            # Dobij trenutnu cenu
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"Symbol {symbol} not found")
                return None
            
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    self.logger.error(f"Failed to select symbol {symbol}")
                    return None
            
            point = symbol_info.point
            
            if action == "BUY":
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
                sl = price - SL_POINTS * point
                tp = price + TP_POINTS * point
                
            elif action == "SELL":
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
                sl = price + SL_POINTS * point
                tp = price - TP_POINTS * point
            else:
                return None
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 234000,
                "comment": "AI Trading Bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Order failed: {result.retcode}")
                return None
            
            self.logger.info(f"{action} order executed - Ticket: {result.order}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None
    
    def close_position(self, ticket):
        """Zatvara poziciju"""
        try:
            positions = mt5.positions_get(ticket=ticket)
            if len(positions) == 0:
                return False
            
            position = positions[0]
            
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "AI Bot Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Close position failed: {result.retcode}")
                return False
            
            self.logger.info(f"Position {ticket} closed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            return False
    
    def update_positions(self):
        """Ažurira listu otvorenih pozicija"""
        try:
            positions = mt5.positions_get(symbol=SYMBOL)
            self.positions = []
            
            if positions:
                for pos in positions:
                    self.positions.append({
                        'ticket': pos.ticket,
                        'type': pos.type,
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'profit': pos.profit,
                        'symbol': pos.symbol
                    })
            
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
    
    def train_ai_model(self, days=30):
        """Trenira AI model sa istorijskim podacima"""
        try:
            self.logger.info("Počinje treniranje AI modela...")
            
            # Dobij istorijske podatke
            count = days * 24 * 4  # 15-min candles
            historical_data = self.get_market_data(count=count)
            
            if not historical_data:
                self.logger.error("Nema istorijskih podataka za treniranje")
                return False
            
            # Izračunaj indikatore
            close_prices = historical_data['close']
            volume_data = historical_data['volume']
            
            macd_data = self.indicators.calculate_macd_lines(close_prices)
            volume_indicators = self.indicators.calculate_volume_indicator(volume_data, close_prices)
            
            if not macd_data or not volume_indicators:
                self.logger.error("Greška pri računanju indikatora")
                return False
            
            # Treniraj model
            results = self.ai_model.train(historical_data, macd_data, volume_indicators)
            
            if results:
                self.logger.info(f"AI model treniran uspešno - Accuracy: {results['accuracy']:.3f}")
                # Sačuvaj model
                self.ai_model.save_model('trading_model.joblib')
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Greška pri treniranju AI modela: {e}")
            return False
    
    def trading_loop(self):
        """Glavna trading petlja"""
        self.logger.info("Pokretanje trading petlje...")
        
        while not self.stop_event.is_set():
            try:
                # Dobij najnovije podatke
                market_data = self.get_market_data()
                if not market_data:
                    time.sleep(10)
                    continue
                
                # Izračunaj indikatore
                macd_data, volume_data = self.calculate_indicators()
                if not macd_data or not volume_data:
                    time.sleep(10)
                    continue
                
                # Ažuriraj pozicije
                self.update_positions()
                
                # Proanaliziraj prilike za ulazak
                entry_analysis = self.analyze_entry_opportunity(macd_data, volume_data)
                
                if entry_analysis:
                    self.logger.info(f"Entry Analysis - Strength: {entry_analysis['entry_strength']:.2f}, "
                                   f"Recommendation: {entry_analysis['recommendation']}")
                    
                    # Trading logika
                    if len(self.positions) < MAX_POSITIONS:
                        if entry_analysis['recommendation'] in ['BUY', 'SELL']:
                            if entry_analysis['entry_strength'] > PREDICTION_THRESHOLD:
                                self.place_order(entry_analysis['recommendation'])
                
                # Provjeri exit signale
                if self.positions:
                    exit_signals = self.check_exit_signals(macd_data, volume_data)
                    for exit_signal in exit_signals:
                        self.logger.info(f"Exit signal za poziciju {exit_signal['ticket']}: {exit_signal['reason']}")
                        self.close_position(exit_signal['ticket'])
                
                # Sačekaj pre sledeće iteracije
                time.sleep(60)  # 1 minut
                
            except Exception as e:
                self.logger.error(f"Greška u trading petlji: {e}")
                time.sleep(30)
    
    def start_trading(self):
        """Pokretanje trading bota"""
        if not self.is_connected:
            if not self.connect_mt5():
                return False
        
        # Učitaj postojeći model ili treniraj novi
        if not self.ai_model.load_model('trading_model.joblib'):
            self.logger.info("Postojeći model nije pronađen, treniram novi...")
            if not self.train_ai_model():
                self.logger.error("Neuspešno treniranje modela")
                return False
        
        self.is_trading = True
        self.stop_event.clear()
        
        # Pokreni trading u posebnom thread-u
        trading_thread = Thread(target=self.trading_loop)
        trading_thread.daemon = True
        trading_thread.start()
        
        self.logger.info("Trading bot pokrenut!")
        return True
    
    def stop_trading(self):
        """Zaustavljanje trading bota"""
        self.is_trading = False
        self.stop_event.set()
        self.logger.info("Trading bot zaustavljen!")
    
    def get_status(self):
        """Vraća status bota"""
        account_info = mt5.account_info()
        return {
            'connected': self.is_connected,
            'trading': self.is_trading,
            'balance': account_info.balance if account_info else 0,
            'equity': account_info.equity if account_info else 0,
            'positions': len(self.positions),
            'ai_trained': self.ai_model.is_trained
        }