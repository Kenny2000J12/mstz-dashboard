
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 下载数据
ticker = "MSTZ"
data = yf.download(ticker, period="7d", interval="15m")
data.dropna(inplace=True)

# 技术指标：布林带、RSI、成交量均值
data['EMA5'] = data['Close'].ewm(span=5).mean()
data['RSI'] = 100 - 100 / (1 + data['Close'].diff().apply(lambda x: max(x, 0)).ewm(span=14).mean() / data['Close'].diff().apply(lambda x: -min(x, 0)).ewm(span=14).mean())
data['BOLL_MID'] = data['Close'].rolling(20).mean()
data['BOLL_STD'] = data['Close'].rolling(20).std()
data['BOLL_UP'] = data['BOLL_MID'] + 2 * data['BOLL_STD']
data['BOLL_LOW'] = data['BOLL_MID'] - 2 * data['BOLL_STD']
data['VOL_MA'] = data['Volume'].rolling(20).mean()

# 策略信号
signals = []
profits = []
capital = 10000
capital_curve = []

for i in range(20, len(data)-20):
    row = data.iloc[i]
    next_row = data.iloc[i+1]
    low_buy = (row['Close'] < row['BOLL_LOW']) and (row['RSI'] < 30) and (row['Volume'] > row['VOL_MA'])

    if low_buy:
        entry = row['Close']
        exit = None
        for j in range(i+1, i+21):
            future = data.iloc[j]
            change = (future['Close'] - entry) / entry
            if change >= 0.035:
                exit = future['Close']
                profits.append(0.035)
                break
            elif change <= -0.025:
                exit = future['Close']
                profits.append(-0.025)
                break
        if not exit:
            closeout = data.iloc[i+20]['Close']
            change = (closeout - entry) / entry
            profits.append(change)
        signals.append((data.index[i], entry))

# 回测统计
returns = pd.Series(profits)
capital_curve = capital * (1 + returns).cumprod()
win_rate = len(returns[returns > 0]) / len(returns) if len(returns) > 0 else 0
max_drawdown = returns.min() if len(returns) > 0 else 0

# 图和HTML在后续生成
