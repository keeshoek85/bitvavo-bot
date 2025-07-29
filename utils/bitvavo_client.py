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

# Voor direct testen van deze module
if __name__ == "__main__":
    bv = get_bitvavo_client()
    balances = bv.balance({})
    print(json.dumps(balances, indent=2))
