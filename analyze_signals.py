def generate_signal(df):
    """
    Genereer trading signaal ('BUY', 'SELL', 'HOLD') o.b.v. RSI & MACD
    """
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # BUY: RSI < 30 & MACD kruist boven signaallijn
    if last['rsi'] < 30 and prev['macd'] < prev['macd_signal'] and last['macd'] > last['macd_signal']:
        return 'BUY'
    # SELL: RSI > 70 & MACD kruist onder signaallijn
    if last['rsi'] > 70 and prev['macd'] > prev['macd_signal'] and last['macd'] < last['macd_signal']:
        return 'SELL'
    return 'HOLD'

# Testmain (optioneel)
if __name__ == "__main__":
    print("Gebruik dit bestand als module in je trader of voor losse signal-checks.")
