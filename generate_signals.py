import yfinance as yf
import pandas as pd
import json

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


def generate_signal(df):
    # 技术指标
    ema12 = EMAIndicator(close=df["Close"], window=12).ema_indicator()
    ema26 = EMAIndicator(close=df["Close"], window=26).ema_indicator()
    rsi = RSIIndicator(close=df["Close"], window=14).rsi()
    macd = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
    bb = BollingerBands(close=df["Close"], window=20, window_dev=2)

    df["EMA12"] = ema12
    df["EMA26"] = ema26
    df["RSI"] = rsi
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()
    df["Upper"] = bb.bollinger_hband()
    df["Lower"] = bb.bollinger_lband()

    df.dropna(inplace=True)

    last = df.iloc[-1]
    close = last["Close"]

    signal = "Hold"
    advice = "No action"

    if (
        (last["MACD"] > last["Signal"])
        and (last["RSI"] < 70)
        and (close > last["EMA12"])
        and (close < last["Upper"])
    ):
        signal = "Buy"
        advice = "Consider increasing position"
    elif (
        (last["MACD"] < last["Signal"])
        and (last["RSI"] > 30)
        and (close < last["EMA12"])
        and (close > last["Lower"])
    ):
        signal = "Sell"
        advice = "Consider reducing position"

    return signal, advice


def main():
    ticker = "MSTZ"
    interval = "2m"
    data = yf.download(ticker, period="2d", interval=interval)
    data.dropna(inplace=True)

    signal, advice = generate_signal(data)

    output = {
        "symbol": ticker,
        "interval": interval,
        "signal": signal,
        "advice": advice,
    }

    with open("trade_signal.json", "w") as f:
        json.dump(output, f, indent=4)


if __name__ == "__main__":
    main()


