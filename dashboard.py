from flask import Flask, render_template_string, request
from utils.bitvavo_client import get_bitvavo_client, get_candles_df
from utils.indicators import add_all_indicators
from analyze_signals import generate_signal
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

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
    <h2>Saldo's</h2>
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
    <h2>Grafiek</h2>
    <form method="get" action="/">
        <label for="coin">Selecteer coin dicht bij trade signaal:</label>
        <select name="coin" id="coin" onchange="this.form.submit()">
            {% for c in relevant_coins %}
            <option value="{{ c }}" {% if c == selected_coin %}selected{% endif %}>{{ c }}</option>
            {% endfor %}
        </select>
    </form>
    <div style="margin-top:18px;">
        <img src="/chart/{{ selected_coin }}" alt="Grafiek" style="border:1px solid #ccc; max-width:95%;">
    </div>
    <p style="margin-top:30px;font-size:0.95em;color:#888;">Powered by Flask, v0.2</p>
</body>
</html>
"""

def get_relevant_coins():
    bv = get_bitvavo_client()
    markets = bv.markets({})
    eur_markets = [m['market'] for m in markets if m['market'].endswith('-EUR')]
    relevant = []
    for market in eur_markets:
        try:
            df = get_candles_df(market, interval="1h", limit=40)
            if df is None or df.empty or len(df) < 2:
                continue
            df = add_all_indicators(df)
            # Dicht bij tradegrens: RSI < 35 of RSI > 65
            if df['rsi'].iloc[-1] < 35 or df['rsi'].iloc[-1] > 65:
                relevant.append(market)
        except Exception:
            continue
    return relevant if relevant else ["BTC-EUR"]

@app.route("/", methods=["GET"])
def index():
    bv = get_bitvavo_client()
    balances = bv.balance({})
    show_balances = [b for b in balances if float(b['available']) > 0 or float(b['inOrder']) > 0]
    relevant_coins = get_relevant_coins()
    selected_coin = request.args.get("coin", relevant_coins[0])
    return render_template_string(
        DASHBOARD_HTML,
        balances=show_balances,
        relevant_coins=relevant_coins,
        selected_coin=selected_coin,
    )

@app.route("/chart/<market>")
def chart(market):
    df = get_candles_df(market, interval="1h", limit=50)
    if df is None or df.empty or len(df) < 2:
        return "Geen data", 404
    df = add_all_indicators(df)
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(df["timestamp"], df["close"], label="Close prijs", color='blue')

    # Signaal-markers in grafiek
    for i in range(1, len(df)):
        s = None
        try:
            s = generate_signal(df.iloc[i-1:i+1])  # geef 2 rijen voor signal check
        except Exception:
            continue
        if s == "BUY":
            ax.annotate('BUY', (df["timestamp"].iloc[i], df["close"].iloc[i]), color='green',
                        xytext=(0, 12), textcoords='offset points',
                        arrowprops=dict(facecolor='green', arrowstyle='->'))
        elif s == "SELL":
            ax.annotate('SELL', (df["timestamp"].iloc[i], df["close"].iloc[i]), color='red',
                        xytext=(0, -18), textcoords='offset points',
                        arrowprops=dict(facecolor='red', arrowstyle='->'))

    ax.set_title(f"{market} - Laatste 50 candles")
    ax.set_xlabel("Tijd")
    ax.set_ylabel("Prijs (EUR)")
    fig.autofmt_xdate()
    ax.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return app.response_class(buf.read(), mimetype='image/png')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
