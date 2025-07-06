# MetaTrader 5 AI Trading Bot

Automatski trading bot koji koristi MACD i Volume indikatore sa AI modelom za trgovanje na MetaTrader 5 platformi.

## 🎯 Karakteristike

- **MACD Indikator**: Koristi MA linije (fast i slow EMA) umesto histograma
- **Volume Indikator**: Analizira volume strength i trend
- **AI Model**: Random Forest model za poboljšanje trading signala
- **Entry Analyzer**: Procenjuje šanse za dobar ulazak (0-1)
- **Exit Manager**: Automatski exit signali na osnovu indikatora i AI
- **Risk Management**: Stop Loss i Take Profit automatski

## 📊 Kako funkcioniše

### 1. Entry Signali (Šanse za ulazak)
Bot analizira:
- **MACD crossover**: Kada MACD linija prelazi signal liniju
- **EMA trend**: Odnos između fast i slow EMA
- **Volume potvrda**: Povećan volume kod price movement-a
- **AI prediction**: Machine learning model procenjuje buduće kretanje

**Rezultat**: Ocena 0-1 koja predstavlja šansu za dobar ulazak

### 2. Exit Signali (Kada i gde izaći)
Bot prati:
- **MACD reversal**: Suprotan crossover od entry signala
- **Volume weakness**: Slabljenje volume podrške
- **AI confirmation**: AI predviđa suprotan trend
- **Stop Loss/Take Profit**: Automatska zaštita

## 🛠 Instalacija

### 1. Klonirajte repozitorijum
```bash
git clone <repo-url>
cd mt5-ai-trading-bot
```

### 2. Instalirajte Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurirajte MT5 credentials
```bash
cp .env.example .env
```

Editujte `.env` fajl sa vašim MT5 podacima:
```
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=MetaQuotes-Demo
```

### 4. Instalirajte MetaTrader 5
- Preuzmite i instalirajte MT5 terminal
- Kreirajte demo ili live račun
- Uverite se da je MT5 otvoren i prijavljen

## 🚀 Korišćenje

### Pokretanje trading bota
```bash
python main.py
```

### Test mode (analiza bez trgovanja)
```bash
python main.py --mode test
```

### Samo treniranje AI modela
```bash
python main.py --mode train --days 60
```

### Debug mode (testiranje komponenti)
```bash
python debug_bot.py
```
Testira sve komponente bota bez povezivanja sa stvarnim trgovanjem.

## ⚙️ Konfiguracija

Editujte `config.py` za prilagođavanje:

```python
# Trading parametri
SYMBOL = 'EURUSD'           # Par za trgovanje
TIMEFRAME = 'M15'           # 15-min candlesticks
LOT_SIZE = 0.1              # Veličina pozicije
MAX_POSITIONS = 3           # Maksimalno otvorenih pozicija

# MACD parametri
MACD_FAST_PERIOD = 12       # Brza EMA
MACD_SLOW_PERIOD = 26       # Spora EMA
MACD_SIGNAL_PERIOD = 9      # Signal linija

# Risk management
SL_POINTS = 50              # Stop Loss u points
TP_POINTS = 100             # Take Profit u points
RISK_PERCENTAGE = 2.0       # 2% rizika po trade-u

# AI parametri
PREDICTION_THRESHOLD = 0.7  # Minimalna confidence za trade
```

## 📈 Indikatori

### MACD (Moving Average Convergence Divergence)
- **Fast EMA**: 12-period exponential moving average
- **Slow EMA**: 26-period exponential moving average
- **MACD Line**: Fast EMA - Slow EMA
- **Signal Line**: 9-period EMA od MACD linije

### Volume Indikator
- **Volume Ratio**: Trenutni volume vs prosečni volume
- **Volume Strength**: Kombinacija volume-a i price movement-a
- **Price Volume Trend**: Trend na osnovu volume i cena

### AI Model Features
- Price movement i volatility
- MACD divergence i momentum
- EMA spread i trend
- Volume confirmation
- Combined momentum indikatori

## 🔒 Sigurnost

### ⚠️ VAŽNE NAPOMENE:
1. **UVEK testirajte na demo računu prvo!**
2. Nikad ne riskirajte novac koji ne možete da izgubite
3. Bot je alat - ne garantuje profit
4. Pratite performance i prilagođavajte parametre

### Preporučene sigurnosne mere:
- Koristite demo račun za početno testiranje
- Postavite konzervativne lot size-ove
- Redovno pratite bot performance
- Imajte plan za manual override

## 📊 Monitoring i Logovanje

Bot kreira detaljne logove u `trading_bot.log`:
- Sve trading odluke i razloge
- Entry/exit signale i confidence nivoe
- Greške i upozorenja
- Performance statistike

### Real-time status
Bot prikazuje live status tokom rada:
```
🔄 Povezan: True | Trading: True | Balance: $10000.00 | Pozicije: 2 | AI: ✅
```

## 🔧 Troubleshooting

### Uobičajeni problemi:

**MT5 connection failed**
- Proverite da li je MT5 terminal otvoren i prijavljen
- Verificirajte credentials u .env fajlu
- Proverite internet konekciju

**No market data**
- Uverite se da je simbol dostupan u MT5
- Proverite da li je market otvoren
- Proverite timeframe settings

**AI model training failed**
- Potrebno je više istorijskih podataka
- Proverite da li su svi paketi instalirani
- Povećajte broj dana za treniranje

## 📁 Struktura fajlova

```
mt5-ai-trading-bot/
├── main.py              # Glavni fajl za pokretanje
├── mt5_trader.py        # Glavna trader klasa
├── indicators.py        # MACD i Volume indikatori
├── ai_model.py          # AI/ML model za trgovanje
├── config.py           # Konfiguracija i parametri
├── debug_bot.py        # Debug script za testiranje
├── requirements.txt    # Python dependencies
├── .env.example       # Template za MT5 credentials
├── README.md          # Ova dokumentacija
└── trading_bot.log    # Log fajl (kreira se automatski)
```

## 📚 Dodatne informacije

### MT5 Python API
- [Dokumentacija](https://www.mql5.com/en/docs/integration/python_metatrader5)
- [Primeri](https://www.mql5.com/en/docs/integration/python_metatrader5/mt5copyratesfrom_py)

### MACD Indikator
- [TA-Lib dokumentacija](https://ta-lib.org/)
- [MACD strategije](https://www.investopedia.com/terms/m/macd.asp)

## 📄 Licenca

Ovaj projekat je kreiran za obrazovne svrhe. Koristite na sopstvenu odgovornost.

## ⚠️ Disclaimer

Trading finansijskih instrumenata nosi visok rizik i može rezultovati gubitkom vašeg kapitala. Nikad ne investirajte novac koji ne možete da izgubite. Ovaj bot je alat za pomoć u trgovanju, ali ne garantuje profit. Uvek konsultujte sa finansijskim savetnicima pre donošenja investicionih odluka.