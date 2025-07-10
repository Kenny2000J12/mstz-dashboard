import yfinance as yf
import pandas as pd
import json

symbol = "MSTR"
intervals = {
    "2m": {"interval": "2m", "period": "1d"},
    "15m": {"interval": "15m", "period": "5d"},
    "30m": {"interval": "30m", "period": "5d"},
}

def compute_indicators(df):
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['MB'] = df['Close'].rolling(20).mean()
    df['UB'] = df['MB'] + 2 * df['Close'].rolling(20).std()
    df['LB'] = df['MB'] - 2 * df['Close'].rolling(20).std()
    return df

def get_signal(df):
    last = df.iloc[-1]
    if last['MACD'] > last['Signal_Line'] and last['RSI'] < 70 and last['Close'] > last['EMA26']:
        return "买入"
    elif last['MACD'] < last['Signal_Line'] and last['RSI'] > 30 and last['Close'] < last['EMA26']:
        return "卖出"
    if last['RSI'] > 80:
        return "卖出"
    elif last['RSI'] < 20:
        return "买入"
    return "持有"

signals = {}
for key, cfg in intervals.items():
    df = yf.download(symbol, interval=cfg["interval"], period=cfg["period"])
    df.dropna(inplace=True)
    if len(df) > 50:
        df = compute_indicators(df)
        signals[key] = get_signal(df)
    else:
        signals[key] = "数据不足"

with open("trade_signals.json", "w", encoding="utf-8") as f:
    json.dump(signals, f, ensure_ascii=False)
