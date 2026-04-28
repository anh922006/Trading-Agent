import pandas as pd
import os
from datetime import datetime
# Import các thành phần từ dự án của bạn
from tradingagents.graph.trading_graph import TradingAgentGraph 
from cli.stats_handler import PerformanceAnalyzer

def run_backtest_pipeline(ticker="AAPL", start_date="2026-01-01", end_date="2026-03-29"):
    print(f"=== KHỞI CHẠY BACKTEST CHO MÃ: {ticker} ===")
    
    # 1. Đọc dữ liệu lịch sử từ cấu hình thư mục của bạn
    # Đường dẫn khớp với ảnh bạn gửi: data/data/data/aapl/tech.csv
    file_path = f"data/data/data/{ticker.lower()}/tech.csv"
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file dữ liệu tại {file_path}")
        return

    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Lọc danh sách các ngày giao dịch (Trading Days) [cite: 340, 342]
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    trading_days = df.loc[mask, 'date'].dt.strftime('%Y-%m-%d').tolist()
    
    # 2. Khởi tạo hệ thống Đa tác tử (Multi-Agent Graph) [cite: 14, 148]
    trading_system = TradingGraph()
    logs = []

    print(f"Tìm thấy {len(trading_days)} ngày giao dịch. Bắt đầu mô phỏng...")

    # 3. Vòng lặp Backtest [cite: 343, 344]
    for current_date in trading_days:
        print(f" -> Đang xử lý ngày: {current_date}...")
        
        try:
            # Chạy Pipeline Agentic [cite: 104, 107, 258]
            # Lưu ý: TradingGraph sẽ tự gọi các Analyst, Researcher, Trader...
            result = trading_system.run(ticker=ticker, date=current_date)
            
            # Lưu nhật ký để tính toán hiệu suất
            logs.append({
                "date": current_date,
                "decision": result.get('decision', 'HOLD'),
                "price": df.loc[df['date'] == current_date, 'Close'].values[0],
                "reasoning": result.get('reasoning', '')
            })
        except Exception as e:
            print(f" Lỗi tại ngày {current_date}: {e}")

    # 4. Lưu kết quả giao dịch
    os.makedirs("results", exist_ok=True)
    log_df = pd.DataFrame(logs)
    log_file = f"results/{ticker}_backtest_results.csv"
    log_df.to_csv(log_file, index=False)
    print(f"=== Đã lưu nhật ký giao dịch tại: {log_file} ===")

    # 5. Gọi Stats Handler để xuất bảng so sánh (Cho Slide 23 & 24) [cite: 346, 394, 396]
    print("\n=== ĐANG TRÍCH XUẤT CHỈ SỐ HIỆU SUẤT (TABLE 1) ===")
    analyzer = PerformanceAnalyzer(log_file)
    analyzer.calculate_metrics() # Tính CR%, AR%, Sharpe, MDD [cite: 346, 591]
    analyzer.plot_results()      # Vẽ biểu đồ P&L Curve [cite: 422, 428]

if __name__ == "__main__":
    # Bạn có thể đổi ticker thành 'NVDA', 'META' tùy ý [cite: 340, 348]
    run_backtest_pipeline(ticker="AAPL")