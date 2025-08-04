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

def generate_scalping_signal(df):
    """
    Geeft 'BUY', 'SELL' of 'HOLD' op basis van EMA cross + RSI.
    - BUY: EMA9 kruist boven EMA21, RSI14 > 45
    - SELL: EMA9 kruist onder EMA21, RSI14 < 55
    """
    if len(df) < 2:
        return 'HOLD'
    prev = df.iloc[-2]
    last = df.iloc[-1]
    # EMA cross UP en RSI voldoende hoog
    if prev['ema9'] < prev['ema21'] and last['ema9'] > last['ema21'] and last['rsi14'] > 45:
        return 'BUY'
    # EMA cross DOWN of RSI laag
    if prev['ema9'] > prev['ema21'] and last['ema9'] < last['ema21']:
        return 'SELL'
    if last['rsi14'] < 55:
        return 'SELL'
    return 'HOLD'


# Testmain (optioneel)
if __name__ == "__main__":
    print("Gebruik dit bestand als module in je trader of voor losse signal-checks.")
