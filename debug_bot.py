#!/usr/bin/env python3
# Debug script za testiranje MT5 AI Trading Bot komponenti

import sys
import numpy as np
from mt5_trader import MT5Trader
from indicators import TechnicalIndicators
from ai_model import TradingAI

def test_indicators():
    """Test funkcionalnosti indikatora"""
    print("🔧 Testiranje indikatora...")
    
    # Kreiraj dummy podatke
    np.random.seed(42)
    close_prices = np.cumsum(np.random.randn(100) * 0.01) + 1.1000
    volume_data = np.random.randint(1000, 10000, 100).astype(float)
    
    indicators = TechnicalIndicators()
    
    # Test MACD
    print("📈 MACD test:")
    macd_data = indicators.calculate_macd_lines(close_prices)
    if macd_data:
        print(f"   ✅ MACD izračunat uspešno")
        print(f"   • Fast EMA poslednja vrednost: {macd_data['fast_ema'][-1]:.5f}")
        print(f"   • Slow EMA poslednja vrednost: {macd_data['slow_ema'][-1]:.5f}")
        print(f"   • MACD Line: {macd_data['macd_line'][-1]:.5f}")
        print(f"   • Signal Line: {macd_data['signal_line'][-1]:.5f}")
    else:
        print("   ❌ MACD računanje neuspešno")
    
    # Test Volume
    print("\n📊 Volume test:")
    volume_indicators = indicators.calculate_volume_indicator(volume_data, close_prices)
    if volume_indicators:
        print(f"   ✅ Volume indikatori izračunati uspešno")
        print(f"   • Volume Ratio: {volume_indicators['volume_ratio'][-1]:.2f}")
        print(f"   • Volume Strength: {volume_indicators['volume_strength'][-1]:.2f}")
    else:
        print("   ❌ Volume računanje neuspešno")
    
    # Test Entry Signal
    if macd_data and volume_indicators:
        print("\n🎯 Entry Signal test:")
        entry_strength = indicators.get_entry_signal_strength(macd_data, volume_indicators)
        print(f"   • Entry Strength: {entry_strength:.2f}")
        
        # Test Exit Signal
        print("\n🚪 Exit Signal test:")
        exit_signal = indicators.get_exit_signal(macd_data, volume_indicators, 'buy')
        print(f"   • Should Exit: {exit_signal['exit_signal']}")
        print(f"   • Exit Reason: {exit_signal['exit_reason']}")
        print(f"   • Confidence: {exit_signal['confidence']:.2f}")

def test_ai_model():
    """Test funkcionalnosti AI modela"""
    print("\n🤖 Testiranje AI modela...")
    
    # Kreiraj dummy podatke
    np.random.seed(42)
    price_data = {
        'open': np.cumsum(np.random.randn(200) * 0.01) + 1.1000,
        'high': np.cumsum(np.random.randn(200) * 0.01) + 1.1020,
        'low': np.cumsum(np.random.randn(200) * 0.01) + 1.0980,
        'close': np.cumsum(np.random.randn(200) * 0.01) + 1.1000,
        'volume': np.random.randint(1000, 10000, 200).astype(float)
    }
    
    indicators = TechnicalIndicators()
    ai_model = TradingAI()
    
    # Izračunaj indikatore
    close_prices = price_data['close']
    volume_data = price_data['volume']
    
    macd_data = indicators.calculate_macd_lines(close_prices)
    volume_indicators = indicators.calculate_volume_indicator(volume_data, close_prices)
    
    if macd_data and volume_indicators:
        print("📊 Priprema features...")
        features = ai_model.prepare_features(price_data, macd_data, volume_indicators)
        print(f"   ✅ Features pripremljeni: {features.shape if len(features) > 0 else 'Prazno'}")
        
        if len(features) > 0:
            print("🏷️ Kreiranje labels...")
            labels = ai_model.create_labels(price_data)
            print(f"   ✅ Labels kreirani: {labels.shape if len(labels) > 0 else 'Prazno'}")
            
            if len(labels) > 50:  # Dovoljno podataka za treniranje
                print("🎓 Treniranje modela...")
                results = ai_model.train(price_data, macd_data, volume_indicators)
                if results:
                    print(f"   ✅ Model treniran uspešno!")
                    print(f"   • Accuracy: {results['accuracy']:.3f}")
                    print(f"   • Precision: {results['precision']:.3f}")
                    print(f"   • Recall: {results['recall']:.3f}")
                    
                    # Test prediction
                    print("🔮 Test predviđanja...")
                    prediction = ai_model.predict_signal(price_data, macd_data, volume_indicators)
                    print(f"   • Signal: {prediction['signal']}")
                    print(f"   • Confidence: {prediction['confidence']:.3f}")
                else:
                    print("   ❌ Treniranje neuspešno")
            else:
                print("   ⚠️ Nedovoljno podataka za treniranje")
    else:
        print("   ❌ Greška pri računanju indikatora")

def test_mt5_connection():
    """Test MT5 konekcije (bez trading operacija)"""
    print("\n🔌 Testiranje MT5 konekcije...")
    
    trader = MT5Trader()
    
    if trader.connect_mt5():
        print("   ✅ MT5 konekcija uspešna")
        
        # Test dobijanja podataka
        print("📈 Test dobijanja market podataka...")
        market_data = trader.get_market_data(count=50)
        if market_data:
            print(f"   ✅ Market podaci dobijeni: {len(market_data['close'])} candles")
            print(f"   • Poslednja cena: {market_data['close'][-1]:.5f}")
            print(f"   • Poslednji volume: {market_data['volume'][-1]:.0f}")
            
            # Test indikatora
            print("🧮 Test računanja indikatora...")
            macd_data, volume_data = trader.calculate_indicators()
            if macd_data and volume_data:
                print("   ✅ Indikatori izračunati uspešno")
                
                # Test analiza
                print("🎯 Test analize entry prilika...")
                entry_analysis = trader.analyze_entry_opportunity(macd_data, volume_data)
                if entry_analysis:
                    print("   ✅ Entry analiza uspešna")
                    print(f"   • Entry Strength: {entry_analysis['entry_strength']:.2f}")
                    print(f"   • Preporuka: {entry_analysis['recommendation']}")
                else:
                    print("   ❌ Entry analiza neuspešna")
            else:
                print("   ❌ Indikatori računanje neuspešno")
        else:
            print("   ❌ Greška pri dobijanju market podataka")
        
        trader.disconnect_mt5()
    else:
        print("   ❌ MT5 konekcija neuspešna")
        print("   💡 Proverite da li je MT5 terminal otvoren i .env konfigurisan")

def main():
    """Glavna debug funkcija"""
    print("=" * 60)
    print("    MT5 AI Trading Bot - Debug Mode")
    print("=" * 60)
    
    try:
        # Test komponenti
        test_indicators()
        test_ai_model()
        test_mt5_connection()
        
        print("\n" + "=" * 60)
        print("✅ Debug testovi završeni!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ Debug prekinut od korisnika")
    except Exception as e:
        print(f"\n❌ Greška tokom debug-a: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()