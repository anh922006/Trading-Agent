import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

TICKERS = {
    "AAPL":  "aapl",
    "^GSPC": "sp500",
    "^VIX":  "vix",
    "^IRX":  "fed_rate",
    "GOOGL": "googl",
    "MSFT":  "msft",
}

def fetch_all(days=500):
    end = datetime.today()
    start = end - timedelta(days=days)
    os.makedirs("data/lan", exist_ok=True)

    frames = {}
    for ticker, col_name in TICKERS.items():   # đổi "name" → "col_name"
        try:
            df = yf.download(ticker, start=start, end=end,
                             auto_adjust=True, progress=False)
            frames[col_name] = df["Close"].squeeze().rename(col_name)
            print(f"  OK {col_name}: {len(df)} rows")
        except Exception as e:
            print(f"  FAIL {ticker}: {e}")

    if not frames:
        print("Không tải được data nào — kiểm tra internet hoặc yfinance version")
        return

    combined = pd.concat(frames.values(), axis=1)
    combined.index.name = "date"
    combined.reset_index(inplace=True)
    combined["date"] = combined["date"].dt.strftime("%Y-%m-%d")

    combined.to_csv("data/lan/market_context.csv", index=False)
    print(f"\nDone! Saved: data/lan/market_context.csv")
    print(combined.tail(3).to_string(index=False))
    return combined

if __name__ == "__main__":
    fetch_all()