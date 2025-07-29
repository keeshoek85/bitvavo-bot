import pandas as pd
import os
import json
from python_bitvavo_api.bitvavo import Bitvavo

# Vind het pad naar config/config.json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")

def load_api_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configbestand niet gevonden: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    for key in ["APIKEY", "APISECRET"]:
        if key not in config or not config[key]:
            raise ValueError(f"'{key}' ontbreekt in config/config.json")
    return config

def get_bitvavo_client():
    config = load_api_config()
    return Bitvavo({
        'APIKEY': config['APIKEY'],
        'APISECRET': config['APISECRET'],
        # Optioneel: pas timeout, restUrl, wsUrl, etc. aan indien gewenst
    })

def get_candles_df(market, interval="1h", limit=500):
    """
    Haal candles op voor een coin en geef als Pandas DataFrame terug.
    :param market: bv. 'BTC-EUR'
    :param interval: bv. '1h', '15m', '1d'
    :param limit: maximaal aantal candles (max 1000 per Bitvavo API-call)
    """
    bv = get_bitvavo_client()
    candles = bv.candles(market, interval, {'limit': limit})
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(candles, columns=cols)
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Voor direct testen van deze module
if __name__ == "__main__":
    bv = get_bitvavo_client()
    balances = bv.balance({})
    print(json.dumps(balances, indent=2))
    df = get_candles_df("BTC-EUR", "1h", 50)
    print(df.tail())
