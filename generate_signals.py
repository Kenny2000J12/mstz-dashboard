
import yfinance as yf
import pandas as pd
import ta
import json
from datetime import datetime

TICKER = "MSTZ"
INTERVALS = {
    "2m": "2d",
    "15m": "10d",
    "30m": "30d"
}

def fetch_data(interval, period):
    df = yf.download(TICKER, interval=interval, period=period)
    df.dropna(inplace=True)
    return df

def compute_indicators(df):
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20).ema_indicator()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(df['Close'])
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    signal = "HOLD"
    position = "Neutral"

    if latest['RSI'] < 30 and latest['Close'] < latest['BB_lower'] and latest['MACD'] > 0:
        signal = "BUY"
        position = "Add"
    elif latest['RSI'] > 70 and latest['Close'] > latest['BB_upper'] and latest['MACD'] < 0:
        signal = "SELL"
        position = "Reduce"

    return {
        "time": latest.name.strftime("%Y-%m-%d %H:%M"),
        "close": round(latest['Close'], 2),
        "signal": signal,
        "position": position
    }

all_signals = {}
for interval, period in INTERVALS.items():
    df = fetch_data(interval, period)
    df = compute_indicators(df)
    signal = generate_signal(df)
    all_signals[interval] = signal

with open("trade_signals.json", "w") as f:
    json.dump(all_signals, f, indent=2)

print("Signals updated.")
    