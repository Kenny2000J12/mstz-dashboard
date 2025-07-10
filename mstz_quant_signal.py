
import json, random
signal = random.choice(["买入", "卖出", "持有", "观望"])
with open("trade_signals.json", "w", encoding="utf-8") as f:
    json.dump({"signal": signal}, f, ensure_ascii=False)
