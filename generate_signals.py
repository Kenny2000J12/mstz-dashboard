import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def fetch_data(ticker, interval):
    data = yf.download(ticker, period="2d", interval=interval)
    data.dropna(inplace=True)
    return data

def calculate_indicators(data):
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['STD20'] = data['Close'].rolling(window=20).std()
    data['Upper'] = data['MA20'] + 2 * data['STD20']
    data['Lower'] = data['MA20'] - 2 * data['STD20']
    return data

def generate_signal(data):
    last = data.iloc[-1]
    signal = "Hold"
    advice = "Wait"
    if (last["MACD"] > last["Signal"]) and (last["RSI"] < 70) and (last["Close"] > last["EMA12"]):
        signal = "Buy"
        advice = "Add position"
    elif (last["MACD"] < last["Signal"]) and (last["RSI"] > 30) and (last["Close"] < last["EMA12"]):
        signal = "Sell"
        advice = "Reduce position"
    return signal, advice

def main():
    ticker = "MSTZ"
    intervals = {"2m": "2m", "15m": "15m", "30m": "30m"}
    signals = {}

    for label, interval in intervals.items():
        data = fetch_data(ticker, interval)
        data = calculate_indicators(data)
        signal, advice = generate_signal(data)
        signals[label] = {
            "signal": signal,
            "advice": advice,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    with open("trade_signals.json", "w") as f:
        json.dump(signals, f, indent=2)

if __name__ == "__main__":
    main()

    
