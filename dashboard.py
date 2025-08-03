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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
