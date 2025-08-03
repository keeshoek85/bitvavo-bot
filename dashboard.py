import io
import base64
import matplotlib.pyplot as plt
from utils.bitvavo_client import get_candles_df
from utils.indicators import add_all_indicators
from flask import Flask, render_template_string
from utils.bitvavo_client import get_bitvavo_client

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
    <p style="margin-top:30px;font-size:0.95em;color:#888;">Powered by Flask, v0.1</p>
    <h2>Grafiek (BTC-EUR)</h2>
    <div>
    <img src="/chart/BTC-EUR" alt="BTC-EUR chart" style="border:1px solid #ccc; max-width:95%;">
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    bv = get_bitvavo_client()
    balances = bv.balance({})
    # Toon alleen coins met non-zero saldo of inOrder
    show_balances = [b for b in balances if float(b['available']) > 0 or float(b['inOrder']) > 0]
    return render_template_string(DASHBOARD_HTML, balances=show_balances)

@app.route("/chart/<market>")
def chart(market):
    df = get_candles_df(market, interval="1h", limit=50)
    if df is None or df.empty:
        return "Geen data", 404
    df = add_all_indicators(df)
    plt.figure(figsize=(7, 3))
    plt.plot(df["timestamp"], df["close"], label="Close prijs")
    plt.title(f"{market} - Laatste 50 candles")
    plt.xlabel("Tijd")
    plt.ylabel("Prijs (EUR)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf8")
    return f'<img src="data:image/png;base64,{img_base64}">'


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
