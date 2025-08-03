import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "trades.db")

def get_conn():
    return sqlite3.connect(DB_PATH, timeout=30)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS candles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            open REAL, high REAL, low REAL, close REAL, volume REAL,
            UNIQUE(coin, timestamp)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            signal TEXT NOT NULL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            UNIQUE(coin, timestamp)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            trade_type TEXT NOT NULL,
            price REAL,
            amount REAL,
            orderid TEXT
        )
        """)
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database en tabellen aangemaakt!")
