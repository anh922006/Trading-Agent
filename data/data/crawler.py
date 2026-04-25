import yfinance as yf
import pandas as pd
import pandas_ta as ta
import finnhub
import json
import os
from datetime import datetime, timedelta

class AppleCrawler:
    def __init__(self, finnhub_key):
        self.client = finnhub.Client(api_key=finnhub_key)
        if not os.path.exists('data'):
            os.makedirs('data')

    def crawl_all(self, symbol="AAPL"):
        # 1. THIẾT LẬP THỜI GIAN (LẤY 500 NGÀY)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=500)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"--- Đang cào dữ liệu cho {symbol} từ {start_str} đến {end_str} ---")
        
        # 2. CÀO GIÁ QUA YFINANCE
        df = yf.download(symbol, start=start_str, end=end_str, interval="1d", auto_adjust=True)
        
        if not df.empty:
            # Sửa lỗi MultiIndex (Tiêu đề 2 tầng của yfinance mới)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Ép pandas nhận diện TA và tính toán chỉ báo
            df.ta.cores = 0 
            try:
                print("Đang tính toán các chỉ báo kỹ thuật...")
                df.ta.rsi(append=True)
                df.ta.macd(append=True)
                df.ta.strategy("All") 
            except Exception:
                print("Lưu ý: Một số chỉ báo phức tạp bị bỏ qua, các chỉ số chính đã sẵn sàng.")

            # CHỈNH SỬA CỘT NGÀY THÁNG CHO RÕ RÀNG
            df.index.name = "date"
            df.reset_index(inplace=True)
            # Chuyển định dạng ngày sang Năm-Tháng-Ngày cho dễ đọc
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

            # Lưu vào CSV
            df.to_csv(f'data/{symbol}_tech.csv', index=False)
            print(f"✅ Đã lưu dữ liệu kỹ thuật vào data/{symbol}_tech.csv")
        else:
            print("❌ Lỗi: Không tải được dữ liệu từ yfinance.")

        # 3. CÀO TIN TỨC VÀ CHỈ SỐ TÀI CHÍNH QUA FINNHUB
        try:
            # Lấy tin tức trong khoảng thời gian tương ứng
            news = self.client.company_news(symbol, _from=start_str, to=end_str)
            metrics = self.client.company_basic_financials(symbol, 'all')
            
            internal_data = {
                "symbol": symbol,
                "update_at": end_str,
                "news": [n['headline'] for n in news[:15]], # Lấy 15 tin mới nhất
                "financials": metrics.get('metric', {})
            }
            
            with open(f'data/{symbol}_internal.json', 'w', encoding='utf-8') as f:
                json.dump(internal_data, f, indent=4, ensure_ascii=False)
            print(f"✅ Đã lưu dữ liệu nội tại vào data/{symbol}_internal.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi gọi Finnhub: {e}")
            
        print(f"--- HOÀN TẤT CÔNG VIỆC CỦA ANALYST AGENT ---")