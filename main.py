
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ========== 获取数据 ==========
ticker = "MSTZ"
data = yf.download(ticker, period="7d", interval="15m")
data.dropna(inplace=True)

# ========== 技术指标计算 ==========
data['EMA5'] = data['Close'].ewm(span=5).mean()
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.ewm(span=14).mean()
avg_loss = loss.ewm(span=14).mean()
rs = avg_gain / avg_loss
data['RSI'] = 100 - 100 / (1 + rs)
data['BOLL_MID'] = data['Close'].rolling(20).mean()
data['BOLL_STD'] = data['Close'].rolling(20).std()
data['BOLL_UP'] = data['BOLL_MID'] + 2 * data['BOLL_STD']
data['BOLL_LOW'] = data['BOLL_MID'] - 2 * data['BOLL_STD']
data['VOL_MA'] = data['Volume'].rolling(20).mean()

# ========== 策略逻辑 ==========
signals = []
profits = []
capital = 10000
FEE = 0.001

for i in range(20, len(data) - 21):
    row = data.iloc[i]
    if row['Close'] < row['BOLL_LOW'] and row['RSI'] < 30 and row['Volume'] > row['VOL_MA']:
        entry = row['Close']
        time = data.index[i]
        for j in range(i + 1, i + 21):
            if j >= len(data): break
            future = data.iloc[j]
            change = (future['Close'] - entry) / entry
            if change >= 0.035:
                profits.append(0.035 - 2 * FEE)
                signals.append((time, entry, "止盈"))
                break
            elif change <= -0.025:
                profits.append(-0.025 - 2 * FEE)
                signals.append((time, entry, "止损"))
                break
        else:
            closeout = data.iloc[i + 20]['Close']
            change = (closeout - entry) / entry
            profits.append(change - 2 * FEE)
            signals.append((time, entry, "时间止出"))

# ========== 输出 ==========
returns = pd.Series(profits)
capital_curve = capital * (1 + returns).cumprod()
plt.figure(figsize=(10, 4))
plt.plot(capital_curve, color="orange")
plt.title("低吸高抛策略资金曲线")
plt.xlabel("交易次数")
plt.ylabel("资金")
plt.tight_layout()
plt.savefig("strategy_chart_lowsell.png")

# HTML 输出
latest = data.iloc[-1]
suggestion = "尝试低吸" if latest['Close'] < latest['BOLL_LOW'] and latest['RSI'] < 30 else "观望"
html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>MSTZ 策略</title></head><body>
<h2>当前建议：{suggestion}</h2>
<p>当前价格：{latest['Close']:.2f}</p>
<p>RSI：{latest['RSI']:.1f}</p>
<img src='strategy_chart_lowsell.png' width='800'>
<p>更新于：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<a href='trade_signals.csv' download>下载交易信号</a>
</body></html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# 导出信号
pd.DataFrame(signals, columns=["时间", "买入价", "结果"]).to_csv("trade_signals.csv", index=False, encoding="utf-8-sig")
