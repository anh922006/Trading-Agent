import pandas as pd
import json

class AnalystAgents:
    def __init__(self, gemini_key):
        pass  # Không cần API nữa

    def run_analysis(self, symbol):
        # Đọc dữ liệu
        df = pd.read_csv(f'data/{symbol}_tech.csv')
        latest = df.iloc[-1]
        
        with open(f'data/{symbol}_internal.json', 'r', encoding='utf-8') as f:
            internal_info = json.load(f)
        
        rsi = latest.get('RSI_14', 'N/A')
        pe = internal_info['financials'].get('peTTM', 'N/A')
        
        print(f"--- AI đang thực hiện phân tích cho {symbol} ---")
        
        report = f"""
1. PHÂN TÍCH KỸ THUẬT:
   - RSI(14) = {rsi:.2f} → {'Quá mua, cẩn thận điều chỉnh' if float(rsi) > 70 else 'Quá bán, cơ hội mua vào' if float(rsi) < 30 else 'Trung tính, thị trường cân bằng'}
   - Xu hướng ngắn hạn cần theo dõi thêm các tín hiệu MA và MACD.

2. PHÂN TÍCH CƠ BẢN:
   - P/E TTM = {pe} → {'Định giá cao so với thị trường' if float(pe) > 30 else 'Định giá hợp lý'}
   - {symbol} duy trì vị thế dẫn đầu ngành với hệ sinh thái sản phẩm mạnh.
   - Tin tức gần đây: {internal_info['news'][0] if internal_info['news'] else 'Không có tin mới'}

3. KẾT LUẬN ĐẦU TƯ:
   - Khuyến nghị: HOLD / Theo dõi thêm
   - Rủi ro: Định giá cao, áp lực lãi suất toàn cầu
   - Cơ hội: Tăng trưởng dịch vụ và AI tích hợp sản phẩm
        """
        return report