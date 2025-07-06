#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MetaTrader 5 AI Trading Bot
Koristi MACD i Volume indikatore sa AI modelom za trgovanje

Autor: AI Trading Bot
Datum: 2024
"""

import sys
import time
import signal
import argparse
from mt5_trader import MT5Trader

def signal_handler(signum, frame):
    """Handler za graceful shutdown"""
    print("\nZaustavlja se trading bot...")
    if 'trader' in globals():
        trader.stop_trading()
        trader.disconnect_mt5()
    sys.exit(0)

def main():
    """Glavna funkcija"""
    
    parser = argparse.ArgumentParser(description='MetaTrader 5 AI Trading Bot')
    parser.add_argument('--mode', choices=['trade', 'train', 'test'], default='trade',
                       help='Mod rada: trade (trading), train (samo treniranje), test (test mode)')
    parser.add_argument('--days', type=int, default=30,
                       help='Broj dana za treniranje AI modela (default: 30)')
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("    MetaTrader 5 AI Trading Bot")
    print("    MACD + Volume + AI Model")
    print("=" * 60)
    print()
    
    # Kreiraj trader instancu
    global trader
    trader = MT5Trader()
    
    if args.mode == 'train':
        # Samo treniranje modela
        print("🤖 Treniranje AI modela...")
        if trader.connect_mt5():
            success = trader.train_ai_model(days=args.days)
            if success:
                print("✅ AI model uspešno treniran!")
            else:
                print("❌ Greška pri treniranju AI modela")
            trader.disconnect_mt5()
        else:
            print("❌ Greška pri povezivanju sa MT5")
        return
    
    elif args.mode == 'test':
        # Test mode - analiza bez stvarnog trgovanja
        print("🔍 Test mode - analiza bez trgovanja...")
        if trader.connect_mt5():
            # Dobij podatke i analiziraj
            market_data = trader.get_market_data()
            if market_data:
                macd_data, volume_data = trader.calculate_indicators()
                if macd_data and volume_data:
                    # Prikazi analizu
                    entry_analysis = trader.analyze_entry_opportunity(macd_data, volume_data)
                    print(f"📊 Analiza trenutne situacije:")
                    print(f"   • Entry Strength: {entry_analysis['entry_strength']:.2f}")
                    print(f"   • Basic Strength: {entry_analysis['basic_strength']:.2f}")
                    print(f"   • AI Signal: {entry_analysis['ai_signal']}")
                    print(f"   • AI Confidence: {entry_analysis['ai_confidence']:.2f}")
                    print(f"   • Preporuka: {entry_analysis['recommendation']}")
                    
                    # Prikazi MACD podatke
                    print(f"\n📈 MACD indikatori:")
                    print(f"   • MACD Line: {macd_data['macd_line'][-1]:.5f}")
                    print(f"   • Signal Line: {macd_data['signal_line'][-1]:.5f}")
                    print(f"   • Fast EMA: {macd_data['fast_ema'][-1]:.5f}")
                    print(f"   • Slow EMA: {macd_data['slow_ema'][-1]:.5f}")
                    
                    # Prikazi Volume podatke
                    print(f"\n📊 Volume indikatori:")
                    print(f"   • Volume Ratio: {volume_data['volume_ratio'][-1]:.2f}")
                    print(f"   • Volume Strength: {volume_data['volume_strength'][-1]:.2f}")
                else:
                    print("❌ Greška pri računanju indikatora")
            else:
                print("❌ Greška pri dobijanju market podataka")
            trader.disconnect_mt5()
        else:
            print("❌ Greška pri povezivanju sa MT5")
        return
    
    else:
        # Trading mode
        print("🚀 Pokretanje AI Trading Bot-a...")
        
        # Proveraj konfiguraciju
        from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
        if not MT5_LOGIN or not MT5_PASSWORD or not MT5_SERVER:
            print("⚠️  UPOZORENJE: MT5 credentials nisu konfigurisani!")
            print("   Kreirajte .env fajl sa vašim MT5 podacima.")
            print("   Pogledajte .env.example za primer.")
            
        # Prikaži početne informacije
        print("📋 Konfiguracija:")
        print(f"   • Symbol: {trader.indicators.__dict__.get('symbol', 'EURUSD')}")
        print(f"   • Timeframe: 15 minuta")
        print(f"   • AI Model: Random Forest")
        print(f"   • MACD: Koristi MA linije (ne histogram)")
        print(f"   • Volume: Volume strength + trend")
        print()
        
        # Pokreni trgovanje
        if trader.start_trading():
            print("✅ Trading bot uspešno pokrenut!")
            print("\n📊 Status:")
            
            try:
                while True:
                    status = trader.get_status()
                    print(f"\r🔄 Povezan: {status['connected']} | "
                          f"Trading: {status['trading']} | "
                          f"Balance: ${status['balance']:.2f} | "
                          f"Pozicije: {status['positions']} | "
                          f"AI: {'✅' if status['ai_trained'] else '❌'}", end="")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Zaustavljanje bot-a...")
                trader.stop_trading()
                trader.disconnect_mt5()
                print("✅ Bot zaustavljen!")
        else:
            print("❌ Greška pri pokretanju trading bot-a")

if __name__ == "__main__":
    main()