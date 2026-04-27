import yfinance as yf
import pandas as pd
import pandas_ta as ta
import finnhub
import json
import os
from datetime import datetime, timedelta
from tavily import TavilyClient

TICKERS = {
    "AAPL":  "aapl",
    "NVDA":  "nvda",
    "MSFT":  "msft",
    "META":  "meta",
    "GOOGL": "googl",
}

class AppleCrawler:
    def __init__(self, finnhub_key: str, tavily_key: str = None, data_dir: str = "data"):
        self.client = finnhub.Client(api_key=finnhub_key)
        self.tavily = TavilyClient(api_key=tavily_key) if tavily_key else None
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def crawl_all(self):
        end_date = datetime.today()
        start_date = end_date - timedelta(days=500)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        print(f"\n{'='*60}")
        print(f"  BẮT ĐẦU CÀO DỮ LIỆU  |  {start_str}  →  {end_str}")
        print(f"  Tổng số mã: {len(TICKERS)}")
        print(f"{'='*60}\n")

        combined_frames = {}

        for ticker, label in TICKERS.items():
            print(f"── [{label.upper()}] {ticker} ──")
            ticker_dir = os.path.join(self.data_dir, label)
            os.makedirs(ticker_dir, exist_ok=True)

            try:
                df = yf.download(
                    ticker, start=start_str, end=end_str,
                    interval="1d", auto_adjust=True, progress=False,
                )
            except Exception as e:
                print(f"Lỗi tải giá: {e}")
                df = pd.DataFrame()
            #================ yfinance =================
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df.ta.cores = 0
                try:
                    df.ta.rsi(append=True)
                    df.ta.macd(append=True)
                    df.ta.sma(length=20, append=True)
                    df.ta.sma(length=50, append=True)
                    df.ta.bbands(append=True)
                except Exception:
                    print(f"Một số chỉ báo bị bỏ qua cho {label}")

                df.index.name = "date"
                df.reset_index(inplace=True)
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

                out_path = os.path.join(ticker_dir, "tech.csv")
                df.to_csv(out_path, index=False)
                print(f"Đã lưu {len(df)} dòng → {out_path}")
                df_tmp = df.set_index("date")
                if "Close" in df_tmp.columns:
                    combined_frames[label] = df_tmp["Close"]
            else:
                print(f"Không có dữ liệu giá cho {ticker}")

            # ===================  finhub  ===================
            try:
                news = self.client.company_news(ticker, _from=start_str, to=end_str)
                metrics = self.client.company_basic_financials(ticker, "all")
                internal_data = {
                    "symbol": ticker,
                    "label": label,
                    "updated_at": end_str,
                    "news": [n["headline"] for n in news[:15]],
                    "financials": metrics.get("metric", {}),
                }

                out_path = os.path.join(ticker_dir, "internal.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(internal_data, f, indent=4, ensure_ascii=False)
                print(f"Đã lưu tin tức & tài chính → {out_path}")
            except Exception as e:
                print(f"Lỗi Finnhub ({ticker}): {e}")

            #================ tavily ===================
            if self.tavily:
                query = f"{ticker} stock analysis news {datetime.today().strftime('%Y')}"
                try:
                    response = self.tavily.search(
                        query=query, search_depth="advanced", max_results=10,
                    )
                    articles = []
                    for r in response.get("results", []):
                        articles.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "content": r.get("content", "")[:500],
                            "score": r.get("score", 0),
                        })
                    tavily_data = {
                        "symbol": ticker,
                        "query": query,
                        "searched_at": datetime.today().strftime("%Y-%m-%d %H:%M"),
                        "total_results": len(articles),
                        "articles": articles,
                    }
                    out_path = os.path.join(ticker_dir, "tavily_news.json")
                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(tavily_data, f, indent=4, ensure_ascii=False)
                    print(f"Đã lưu {len(articles)} bài báo Tavily → {out_path}")
                except Exception as e:
                    print(f"Lỗi Tavily ({ticker}): {e}")

            print()

        print(f"\n{'='*60}")
        print("  HOÀN TẤT CÔNG VIỆC CỦA CRAWLER")
        print(f"{'='*60}\n")