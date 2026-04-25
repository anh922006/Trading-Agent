import yfinance as yf
import pandas as pd
import pandas_ta as ta
import finnhub
import json
import os

class AppleCrawler:
    def __init__(self, finnhub_key):
        self.client = finnhub.Client(api_key=finnhub_key)
        if not os.path.exists('data'):
            os.makedirs('data')

    def crawl_all(self, symbol="AAPL"):
        print(f"--- Đang cào dữ liệu nội tại cho {symbol} ---")
        
        # 1. Cào giá qua yfinance
        df = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
        
        if not df.empty:
            # SỬA LỖI MULTIINDEX Ở ĐÂY:
            # yfinance mới trả về 2 tầng tiêu đề, ta đưa về 1 tầng để pandas_ta hiểu được
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.ta.cores = 0 
            
            try:
                print("Đang tính toán các chỉ báo...")
                # Tính các chỉ số cơ bản trước để đảm bảo có dữ liệu
                df.ta.rsi(append=True)
                df.ta.macd(append=True)
                # Sau đó thử chạy strategy All
                df.ta.strategy("All") 
            except Exception as e:
                print(f"Lưu ý: Một số chỉ báo không tính được, nhưng các chỉ số chính đã sẵn sàng.")

            df.to_csv(f'data/{symbol}_tech.csv')
        else:
            print("Lỗi: Không tải được dữ liệu từ yfinance.")

        # 2. Cào tin tức báo chí và chỉ số tài chính qua Finnhub
        try:
            news = self.client.company_news(symbol, _from='2026-03-01', to='2026-04-25')
            metrics = self.client.company_basic_financials(symbol, 'all')
            
            internal_data = {
                "news": [n['headline'] for n in news[:15]], 
                "financials": metrics.get('metric', {})
            }
            with open(f'data/{symbol}_internal.json', 'w', encoding='utf-8') as f:
                json.dump(internal_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi gọi Finnhub: {e}")
            
        print(f"--- Hoàn tất! Dữ liệu đã nằm trong thư mục 'data' ---")