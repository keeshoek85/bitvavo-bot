import pandas as pd

def add_sma(df, period=14, column='close', out_col=None):
    if out_col is None:
        out_col = f'sma_{period}'
    df[out_col] = df[column].rolling(window=period, min_periods=1).mean()
    return df

def add_ema(df, period=14, column='close', out_col=None):
    if out_col is None:
        out_col = f'ema_{period}'
    df[out_col] = df[column].ewm(span=period, adjust=False).mean()
    return df

def add_rsi(df, period=14, column='close', out_col='rsi'):
    delta = df[column].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(window=period, min_periods=1).mean()
    ma_down = down.rolling(window=period, min_periods=1).mean()
    rs = ma_up / (ma_down + 1e-10)
    df[out_col] = 100 - (100 / (1 + rs))
    return df

def add_macd(df, fast=12, slow=26, signal=9, column='close'):
    df['ema_fast'] = df[column].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df[column].ewm(span=slow, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    return df

def add_all_indicators(df, close_col='close'):
    df = add_sma(df, period=14, column=close_col)
    df = add_ema(df, period=12, column=close_col)
    df = add_ema(df, period=26, column=close_col)
    df = add_rsi(df, period=14, column=close_col)
    df = add_macd(df, column=close_col)
    return df
