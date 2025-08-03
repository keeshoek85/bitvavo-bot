from flask import Flask, render_template_string, request
import sqlite3
import matplotlib.pyplot as plt
import io
import time
from utils.bitvavo_client import get_bitvavo_client

app = Flask(__name__)

DB_PATH = "trades.db"

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bitvavo Bot Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #fafbfc;}
        table { border-collapse: collapse; min-width: 400px;}
        th, td { border: 1px solid #ccc; padding: 6px 12px; }
        th { background: #eee; }
    </style>
</head>
<body>
    <h1>Bitvavo Bot Dashboard</h1>
    <h2>Saldo's (live)</h2>
    <table>
        <tr>
            <th>Coin</th>
            <th>Beschikbaar</th>
            <th>In Order</th>
        </tr>
        {% for bal in balances %}
        <tr>
            <td>{{ bal['symbol'] }}</td>
            <td>{{ bal['available'] }}</td>
            <td>{{ bal['inOrder'] }}</td>
        </tr>
        {% endfor %}
    </table>
    <h2>Dropdown: coins dicht bij trade-signaal</h2>
    <form method="get" action="/">
        <label for="coin">Coin:</label>
        <select name="coin" id="coin" onchange="this.form.submit()">
            {% for c in relevant_coins %}
            <option value="{{ c }}" {% if c == selected_coin %}selected{% endif %}>{{ c }}</option>
            {% endfor %}
        </select>
    </form>
    <div style="margin-top:18px;">
        <img src="/chart/{{ selected_coin }}" alt="Grafiek" style="border:1px solid #ccc; max-width:95%;">
    </div>
    <p style="margin-top:30px;font-size:0.95em;color:#888;">Powered by Flask + SQLite, v0.4</p>
</body>
</html>
"""

def get_db_conn():
    return sqlite3.connect(DB_PATH, timeout=30)

def get_live_balances():
    try:
        bv = get_bitvavo_client()
        balances = bv.balance({})
        # Toon alleen coins met non-zero saldo of inOrder
        return [b for b in balances if float(b['available']) > 0 or float(b['inOrder']) > 0]
    except Exception:
        return []

def get_relevant_coins():
    coins = set()
    with get_db_conn() as conn:
        c = conn.cursor()
        # Pak alleen de laatste candle per coin
        c.execute("""
        SELECT coin, rsi FROM signals WHERE id IN (
            SELECT MAX(id) FROM signals GROUP BY coin
        )
        """)
        for coin, rsi in c.fetchall():
            if rsi is not None and (rsi < 35 or rsi > 65):
                coins.add(coin)
    return sorted(list(coins)) if coins else ["BTC-EUR"]

@app.route("/", methods=["GET"])
def index():
    relevant_coins = get_relevant_coins()
    selected_coin = request.args.get("coin", relevant_coins[0])
    balances = get_live_balances()
    return render_template_string(
        DASHBOARD_HTML,
        relevant_coins=relevant_coins,
        selected_coin=selected_coin,
        balances=balances
    )

@app.route("/chart/<market>")
def chart(market):
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT timestamp, close FROM candles
            WHERE coin=? ORDER BY timestamp DESC LIMIT 50
        """, (market,))
        rows = c.fetchall()
        if not rows:
            return "Geen data", 404
        data = sorted([(int(ts), float(close)) for ts, close in rows])
        timestamps, closes = zip(*data)
        # Pak de signalen op deze timestamps
        c.execute("""
            SELECT timestamp, signal FROM signals
            WHERE coin=? AND timestamp IN ({})
        """.format(",".join("?"*len(timestamps))), (market, *timestamps))
        signal_map = {int(ts): sig for ts, sig in c.fetchall()}

    plt.figure(figsize=(7, 3))
    plt.plot([time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) for ts in timestamps], closes, label="Close prijs", color='blue')
    for idx, ts in enumerate(timestamps):
        sig = signal_map.get(ts)
        if sig == "BUY":
            plt.annotate('BUY', (idx, closes[idx]), color='green', xytext=(0, 12), textcoords='offset points',
                         arrowprops=dict(facecolor='green', arrowstyle='->'))
        elif sig == "SELL":
            plt.annotate('SELL', (idx, closes[idx]), color='red', xytext=(0, -18), textcoords='offset points',
                         arrowprops=dict(facecolor='red', arrowstyle='->'))

    plt.title(f"{market} - Laatste 50 candles (DB)")
    plt.xlabel("Tijd")
    plt.ylabel("Prijs (EUR)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return app.response_class(buf.read(), mimetype='image/png')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
