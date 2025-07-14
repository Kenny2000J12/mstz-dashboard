# generate_signals.py
import yfinance as yf
import pandas as pd
import json
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def get_data(interval):
    data = yf.download("MSTZ", period="2d", interval=interval)
    data.dropna(inplace=True)
    return data

def generate_signal(df):
    df = df.copy()
    df['EMA12'] = EMAIndicator(close=df["Close"], window=12).ema_indicator()
    df['RSI'] = RSIIndicator(close=df["Close"], window=14).rsi()
    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()
    boll = BollingerBands(close=df['Close'])
    df['BB_upper'] = boll.bollinger_hband()
    df['BB_lower'] = boll.bollinger_lband()

    last = df.iloc[-1]
    if (last['MACD'] > last['Signal']) and (last['RSI'] < 70) and (last['Close'] > last['EMA12']) and (last['Close'] < last['BB_upper']):
        return "BUY", "Consider adding position"
    elif (last['MACD'] < last['Signal']) and (last['RSI'] > 30) and (last['Close'] < last['EMA12']) and (last['Close'] > last['BB_lower']):
        return "SELL", "Consider reducing position"
    else:
        return "HOLD", "No action"

def main():
    result = {}
    for interval in ["2m", "15m", "30m"]:
        try:
            df = get_data(interval)
            signal, advice = generate_signal(df)
            result[interval] = {"signal": signal, "advice": advice}
        except Exception as e:
            result[interval] = {"signal": "ERROR", "advice": str(e)}

    with open("trade_signals.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
