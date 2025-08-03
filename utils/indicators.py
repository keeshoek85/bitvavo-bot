import os
import pandas as pd
from utils.bitvavo_client import get_candles_df

def generate_signal(df):
    """
    Genereer trading signaal ('BUY', 'SELL', 'HOLD') o.b.v. RSI & MACD
    """
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Basis-strategie, uitbreidbaar:
    # BUY: RSI < 30 & MACD kruist boven signaallijn
    if last['rsi'] < 30 and prev['macd'] < prev['macd_signal'] and last['macd'] > last['macd_signal']:
        return 'BUY'
    # SELL: RSI > 70 & MACD kruist onder signaallijn
    if last['rsi'] > 70 and prev['macd'] > prev['macd_signal'] and last['macd'] < last['macd_signal']:
        return 'SELL'
    return 'HOLD'

def main():
    # Voorbeeld: analyseer een lijst coins
    coins = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR']
    interval = '1h'
    limit = 100

    results = []
    for coin in coins:
        try:
            df = get_candles_df(coin, interval, limit)
            df = add_all_indicators(df)
            signal = generate_signal(df)
            print(f"{coin}: {signal}")
            results.append({'coin': coin, 'signal': signal})
        except Exception as e:
            print(f"Fout bij {coin}: {e}")

    return results

if __name__ == "__main__":
    main()
