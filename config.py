# MetaTrader 5 Trading Bot Configuration

import os
from dotenv import load_dotenv

load_dotenv()

# MetaTrader 5 Connection Settings
MT5_LOGIN = int(os.getenv('MT5_LOGIN', 0))
MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
MT5_SERVER = os.getenv('MT5_SERVER', '')

# Trading Parameters
SYMBOL = 'EURUSD'
TIMEFRAME = 'M15'  # 15-minute timeframe
LOT_SIZE = 0.1
MAX_POSITIONS = 3
RISK_PERCENTAGE = 2.0  # 2% risk per trade

# AI Model Parameters
LOOKBACK_PERIOD = 100
FEATURE_WINDOW = 20
PREDICTION_THRESHOLD = 0.7

# MACD Parameters
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

# Volume Parameters
VOLUME_PERIOD = 20
VOLUME_THRESHOLD = 1.5

# Stop Loss and Take Profit
SL_POINTS = 50
TP_POINTS = 100

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_bot.log'