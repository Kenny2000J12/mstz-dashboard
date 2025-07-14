import yfinance as yf
import pandas as pd
import json

def calculate_indicators(df):
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    df["Upper"] = df["Close"].rolling(window=20).mean() + 2 * df["Close"].rolling(window=20).std()
    df["Lower"] = df["Close"].rolling(window=20).mean() - 2 * df["Close"].rolling(window=20).std()
    return df

def generate_signal(df):
    last = df.iloc[-1]  # 取最后一行

    if (last["MACD"] > last["Signal"]) and (last["RSI"] < 70) and (last["Close"] > last["EMA12"]):
        return "BUY", "加仓或建仓"
    elif (last["MACD"] < last["Signal"]) and (last["RSI"] > 30) and (last["Close"] < last["EMA12"]):
        return "SELL", "减仓或止盈"
    else:
        return "HOLD", "继续持有"

def main():
    ticker = "MSTZ"
    intervals = ["2m", "15m", "30m"]
    all_signals = {}

    for interval in intervals:
        data = yf.download(ticker, period="2d", interval=interval)
        if data.empty:
            all_signals[interval] = {"signal": "NO DATA", "advice": "无数据"}
            continue
        data.dropna(inplace=True)
        data = calculate_indicators(data)
        signal, advice = generate_signal(data)
        all_signals[interval] = {
            "signal": signal,
            "advice": advice,
            "last_price": round(data.iloc[-1]["Close"], 2),
        }

    with open("trade_signals.json", "w") as f:
        json.dump(all_signals, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

