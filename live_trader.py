import time
from utils.bitvavo_client import get_bitvavo_client, get_candles_df
from db import insert_candle, insert_signal, insert_trade
from utils.indicators import add_scalping_indicators
from analyze_signals import generate_scalping_signal

# Instellingen
TRADE_AMOUNT_EUR = 10.00   # Vast bedrag per trade
MIN_EUR_AVAILABLE = 15.00  # Altijd minstens dit bedrag overhouden
INTERVAL = '1h'
CANDLE_LIMIT = 100

def get_available_eur(bitvavo):
    for bal in bitvavo.balance({}):
        if bal['symbol'] == 'EUR':
            return float(bal['available'])
    return 0.0

def get_all_eur_markets(bitvavo):
    markets = bitvavo.markets({})
    eur_markets = [m['market'] for m in markets if m['market'].endswith('-EUR')]
    return eur_markets

def main():
    bitvavo = get_bitvavo_client()
    eur_avail = get_available_eur(bitvavo)
    print(f"EUR beschikbaar: {eur_avail}")

    # Alle EUR-markten automatisch ophalen
    all_markets = get_all_eur_markets(bitvavo)
    print(f"Aantal verhandelbare coins: {len(all_markets)}")

    for market in all_markets:
        try:
            df = get_candles_df(market, INTERVAL, CANDLE_LIMIT)
            if df is None or df.empty or len(df) < 22:  # Minimaal 21 candles voor EMA
                print(f"{market}: GEEN of te weinig DATA (wordt overgeslagen)")
                continue
            df = add_scalping_indicators(df)
            signal = generate_scalping_signal(df)

            # Log alle candles
            for _, row in df.iterrows():
                insert_candle(market, row)

            signal = generate_signal(df)
            insert_signal(
                market,
                int(df['timestamp'].iloc[-1].timestamp()),
                signal,
                float(df['rsi'].iloc[-1]),
                float(df['macd'].iloc[-1]),
                float(df['macd_signal'].iloc[-1]),
            )

            symbol = market.split('-')[0]
            bal = [b for b in bitvavo.balance({}) if b['symbol'] == symbol]
            coin_avail = float(bal[0]['available']) if bal else 0.0

            print(f"{market}: Signaal = {signal} | Coin beschikbaar: {coin_avail}")

            if signal == 'BUY':
                if eur_avail >= (TRADE_AMOUNT_EUR + MIN_EUR_AVAILABLE):
                    buy_amount = TRADE_AMOUNT_EUR / df['close'].iloc[-1]
                    resp = bitvavo.order(market, 'buy', 'market', {'amount': f"{buy_amount:.6f}"})
                    print(f"BUY {market}: Order geplaatst: {resp}")
                    eur_avail -= TRADE_AMOUNT_EUR
                    insert_trade(
                        market,
                        int(time.time()),
                        'BUY',
                        float(resp.get('price', 0)),
                        float(resp.get('amount', 0)),
                        resp.get('orderId', '')
                    )
                else:
                    print(f"Niet genoeg EUR om {market} te kopen.")
            elif signal == 'SELL':
                if coin_avail > 0:
                    resp = bitvavo.order(market, 'sell', 'market', {'amount': f"{coin_avail:.6f}"})
                    print(f"SELL {market}: Order geplaatst: {resp}")
                    insert_trade(
                        market,
                        int(time.time()),
                        'SELL',
                        float(resp.get('price', 0)),
                        float(resp.get('amount', 0)),
                        resp.get('orderId', '')
                    )
                else:
                    print(f"Niets te verkopen voor {market}.")
            else:
                print(f"Houd {market}: Geen actie.")

        except Exception as e:
            print(f"Fout bij {market}: {e}")

if __name__ == "__main__":
    main()
