import yfinance as yf
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 设置股票代码和时间范围
TICKER = "MSTZ"
INTERVAL = "2m"
PERIOD = "1d"

# 下载2分钟K线数据
data = yf.download(TICKER, interval=INTERVAL, period=PERIOD)
data.dropna(inplace=True)

# 计算技术指标
data['EMA5'] = data['Close'].ewm(span=5, adjust=False).mean()
data['EMA13'] = data['Close'].ewm(span=13, adjust=False).mean()
data['RSI'] = pd.Series(dtype='float64')
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

# 判断策略信号
def generate_signals(df):
    df['Signal'] = ''
    for i in range(1, len(df)):
        if df['EMA5'][i] > df['EMA13'][i] and df['RSI'][i] > 50:
            df.at[i, 'Signal'] = 'BUY'
        elif df['EMA5'][i] < df['EMA13'][i] and df['RSI'][i] < 50:
            df.at[i, 'Signal'] = 'SELL'
        else:
            df.at[i, 'Signal'] = 'HOLD'
    return df

data = generate_signals(data)

# 保存为Excel
filename = f"mstz_2min_monitor_20250710_0217.xlsx"
data.to_excel(filename)

print(f"已生成监控文件: {filename}")
