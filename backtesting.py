import pandas as pd
import os
import numpy as np
from datetime import datetime
from tradingagents.graph.trading_graph import TradingAgentsGraph 
from cli.stats_handler import PerformanceAnalyzer
from dotenv import load_dotenv

# 1. Nạp biến môi trường
load_dotenv()

def run_backtest_pipeline(ticker="AAPL", start_date="2026-01-01", end_date="2026-03-29"):
    # KHỞI TẠO ANALYZER
    analyzer = PerformanceAnalyzer()
    
    print(f"=== KHỞI CHẠY BACKTEST CHO MÃ: {ticker} ===")
    
    # 2. Đọc dữ liệu lịch sử
    file_path = f"data/data/data/{ticker.lower()}/tech.csv"
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file dữ liệu tại {file_path}")
        return

    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    trading_days = df.loc[mask, 'date'].dt.strftime('%Y-%m-%d').tolist()
    
    if not trading_days:
        print("Không có dữ liệu trong khoảng thời gian này.")
        return

    # 3. Khởi tạo hệ thống Graph
    try:
        trading_system = TradingAgentsGraph()
    except Exception as e:
        print(f"Lỗi khởi tạo TradingAgentsGraph: {e}")
        return

    logs = []
    initial_balance = 100000.0 
    current_balance = initial_balance

    print(f"Tìm thấy {len(trading_days)} ngày giao dịch. Bắt đầu mô phỏng...")

    # 4. Vòng lặp Backtest 
    for current_day_str in trading_days:
        print(f" -> Đang xử lý ngày: {current_day_str}...")
        
        try:
            result = trading_system.propagate(ticker, current_day_str)
            
            # Lấy giá trị Close
            price_row = df.loc[df['date'].dt.strftime('%Y-%m-%d') == current_day_str, 'Close'].values
            current_price = price_row[0] if len(price_row) > 0 else 0

            # Xử lý kết quả trả về
            decision = 'HOLD'
            reasoning = 'No reasoning provided'
            
            if isinstance(result, dict):
                # Ưu tiên lấy key 'decision' hoặc 'action' tùy theo logic Agent của bạn
                decision = result.get('decision', result.get('action', 'HOLD')).upper()
                reasoning = result.get('reasoning', 'Success')
            elif hasattr(result, 'decision'):
                decision = result.decision.upper()
                reasoning = getattr(result, 'reasoning', 'Success')

            # Logic cập nhật tài sản (giữ nguyên logic cũ của bạn)
            if 'BUY' in decision:
                current_balance *= 1.02 
            elif 'SELL' in decision:
                current_balance *= 0.98 
            
            # Cập nhật snapshot cho Analyzer
            analyzer.add_snapshot(current_day_str, current_balance)

            # Lưu nhật ký
            logs.append({
                "date": current_day_str,
                "decision": decision,
                "price": current_price,
                "reasoning": reasoning
            })
            
            print(f"    [OK] Decision: {decision} | Balance: {current_balance:,.2f}")
            
        except Exception as e:
            print(f" Lỗi tại ngày {current_day_str}: {e}")

    # 5. Lưu kết quả ra CSV
    os.makedirs("results", exist_ok=True)
    if logs:
        log_df = pd.DataFrame(logs)
        log_file = f"results/{ticker}_backtest_results.csv"
        log_df.to_csv(log_file, index=False)
        print(f"\n=== Đã lưu nhật ký giao dịch tại: {log_file} ===")

    # 6. Xuất báo cáo hiệu suất
    print("\n=== ĐANG TRÍCH XUẤT CHỈ SỐ HIỆU SUẤT TRADING AGENTS ===")
    try:
        analyzer.print_final_report()
        analyzer.plot_results()
    except Exception as e:
        print(f"Lỗi khi xuất báo cáo hoặc vẽ biểu đồ: {e}")

if __name__ == "__main__":
    run_backtest_pipeline(ticker="AAPL")