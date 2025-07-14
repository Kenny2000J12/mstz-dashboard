import yfinance as yf
import pandas as pd
import json

def calculate_indicators(df):
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    df["Upper"] = df["Close"].rolling(20).mean() + 2 * df["Close"].rolling(20).std()
    df["Lower"] = df["Close"].rolling(20).mean() - 2 * df["Close"].rolling(20).std()
    return df

def generate_signal(df):
    last = df.iloc[-1]
    signal = "持有"
    advice = "观察中"

    if last["MACD"] > last["Signal"] and last["RSI"] < 70 and last["Close"] > last["EMA12"]:
        signal = "买入"
        advice = "可加仓"
    elif last["MACD"] < last["Signal"] and last["RSI"] > 30 and last["Close"] < last["EMA12"]:
        signal = "卖出"
        advice = "可减仓"

    return signal, advice

result = {}
ticker = "MSTZ"
intervals = {"2m": "signal_2m", "15m": "signal_15m", "30m": "signal_30m"}

for interval, key in intervals.items():
    data = yf.download(ticker, period="2d", interval=interval)
    if data.empty:
        result[key] = {"信号": "无数据", "建议": "等待数据加载"}
    else:
        data = calculate_indicators(data)
        signal, advice = generate_signal(data)
        result[key] = {"信号": signal, "建议": advice}

with open("trade_signals.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

    
