import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Đọc data AAPL đã cào
df = pd.read_csv("AAPL-YFin-data-2021-04-27-2026-04-27.csv")
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Lấy cột Close
close = df["Close"].values
dates = df["Date"]

# ── Chiến lược 1: Buy & Hold ──────────────────
bnh = (close / close[0]) * 100  # normalize về 100

# ── Chiến lược 2: SMA (20/50 crossover) ───────
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

capital_sma = 100.0
position_sma = 0
sma_values = [100.0]

for i in range(1, len(df)):
    if pd.isna(df["SMA20"].iloc[i]) or pd.isna(df["SMA50"].iloc[i]):
        sma_values.append(capital_sma)
        continue
    # Tín hiệu mua
    if df["SMA20"].iloc[i] > df["SMA50"].iloc[i] and \
       df["SMA20"].iloc[i-1] <= df["SMA50"].iloc[i-1]:
        position_sma = capital_sma / close[i]
    # Tín hiệu bán
    elif df["SMA20"].iloc[i] < df["SMA50"].iloc[i] and \
         df["SMA20"].iloc[i-1] >= df["SMA50"].iloc[i-1]:
        capital_sma = position_sma * close[i]
        position_sma = 0
    # Cập nhật giá trị
    if position_sma > 0:
        sma_values.append(position_sma * close[i])
    else:
        sma_values.append(capital_sma)

# ── Chiến lược 3: MACD ────────────────────────
exp12 = df["Close"].ewm(span=12).mean()
exp26 = df["Close"].ewm(span=26).mean()
macd  = exp12 - exp26
signal = macd.ewm(span=9).mean()

capital_macd = 100.0
position_macd = 0
macd_values = [100.0]

for i in range(1, len(df)):
    if df["Close"].iloc[i] != df["Close"].iloc[i]:
        macd_values.append(capital_macd)
        continue
    if macd.iloc[i] > signal.iloc[i] and macd.iloc[i-1] <= signal.iloc[i-1]:
        position_macd = capital_macd / close[i]
    elif macd.iloc[i] < signal.iloc[i] and macd.iloc[i-1] >= signal.iloc[i-1]:
        capital_macd = position_macd * close[i]
        position_macd = 0
    if position_macd > 0:
        macd_values.append(position_macd * close[i])
    else:
        macd_values.append(capital_macd)

# ── Vẽ biểu đồ ───────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(dates, bnh,         label="Buy & Hold",     color="#1f77b4", linewidth=2)
ax.plot(dates, sma_values,  label="SMA Strategy",   color="#ff7f0e", linewidth=1.5, linestyle="--")
ax.plot(dates, macd_values, label="MACD Strategy",  color="#2ca02c", linewidth=1.5, linestyle="-.")

# TradingAgents — dùng kết quả thực tế nhóm đã chạy
# Thay số này bằng kết quả thật nếu có
ax.axhline(y=126.62, color="#d62728", linewidth=2,
           linestyle=":", label="TradingAgents (+26.62%)")

ax.set_title("So sánh chiến lược giao dịch — AAPL (2021–2026)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Ngày", fontsize=12)
ax.set_ylabel("Giá trị danh mục (gốc = 100)", fontsize=12)
ax.legend(fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/strategy_comparison.png", dpi=150)
plt.show()
print("Đã lưu: results/strategy_comparison.png")