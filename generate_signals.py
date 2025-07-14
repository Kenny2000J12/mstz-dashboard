import yfinance as yf
import pandas as pd
import json
import os
import datetime

# ========== 指标计算函数 ==========
def calculate_indicators(data):
    # 均线
    data["EMA12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA26"] = data["Close"].ewm(span=26, adjust=False).mean()
    
    # MACD
    data["MACD"] = data["EMA12"] - data["EMA26"]
    data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

    # RSI
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # 布林带
    ma = data["Close"].rolling(window=20).mean()
    std = data["Close"].rolling(window=20).std()
    data["Upper"] = ma + 2 * std
    data["Lower"] = ma - 2 * std

    return data

# ========== 信号生成函数 ==========
def generate_signal(data):
    last = data.iloc[-1]

    macd = last["MACD"]
    signal_line = last["Signal"]
    rsi = last["RSI"]
    close = last["Close"]
    ema12 = last["EMA12"]
    upper = last["Upper"]
    lower = last["Lower"]

    if (macd > signal_line) and (rsi < 70) and (close > ema12) and (close < upper):
        return "BUY", "考虑加仓"
    elif (macd < signal_line) and (rsi > 30) and (close < ema12) and (close > lower):
        return "SELL", "建议减仓"
    else:
        return "HOLD", "保持观望"

# ========== 主函数：多周期 ==========
def main():
    ticker = "MSTZ"
    intervals = {
        "2m": "signals_2m.json",
        "15m": "signals_15m.json",
        "30m": "signals_30m.json"
    }

    for interval, filename in intervals.items():
        data = yf.download(ticker, period="2d", interval=interval)
        if data.empty:
            continue
        data.dropna(inplace=True)
        data = calculate_indicators(data)
        signal, advice = generate_signal(data)

        result = {
            "symbol": ticker,
            "interval": interval,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "signal": signal,
            "advice": advice
        }

        with open(filename, "w") as f:
            json.dump(result, f, indent=4)

if __name__ == "__main__":
    main()

