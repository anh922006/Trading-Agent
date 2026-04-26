import pandas as pd
import os
from groq import Groq
 
class TechnicalAgent:
    def __init__(self, groq_key):
        self.groq_client = Groq(api_key=groq_key)
 
    def analyze(self, symbol):
        csv_file = f"data/{symbol}_tech.csv"
        if not os.path.exists(csv_file):
            return {"agent": "Technical Analyst", "symbol": symbol, "error": f"Không tìm thấy {csv_file}"}
 
        df = pd.read_csv(csv_file)
 
        # Tìm cột RSI và MACD
        rsi_col = next((c for c in df.columns if 'RSI' in c.upper()), None)
        macd_col = next((c for c in df.columns if c.upper().startswith('MACD') and 'SIGNAL' not in c.upper() and 'HIST' not in c.upper()), None)
        macd_sig_col = next((c for c in df.columns if 'MACDS' in c.upper() or ('MACD' in c.upper() and 'SIGNAL' in c.upper())), None)
 
        latest = df.iloc[-1]
        price = float(latest.get('Close', 0))
 
        rsi = float(latest[rsi_col]) if rsi_col and pd.notna(latest[rsi_col]) else None
        macd = float(latest[macd_col]) if macd_col and pd.notna(latest[macd_col]) else None
        macd_sig = float(latest[macd_sig_col]) if macd_sig_col and pd.notna(latest[macd_sig_col]) else None
 
        # Bollinger Bands
        close_series = df['Close'].dropna()
        sma20 = close_series.rolling(20).mean().iloc[-1]
        std20 = close_series.rolling(20).std().iloc[-1]
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20
 
        # Tín hiệu
        rsi_signal = "Quá mua " if rsi and rsi > 70 else "Quá bán " if rsi and rsi < 30 else "Trung tính "
        macd_signal = "Tăng " if macd and macd_sig and macd > macd_sig else "Giảm "
        bb_signal = "Giá trên dải trên" if price > bb_upper else "Giá dưới dải dưới" if price < bb_lower else "Giá trong dải Bollinger"
 
        # Format an toàn
        rsi_str = f"{rsi:.2f}" if rsi is not None else "N/A"
        macd_str = f"{macd:.4f}" if macd is not None else "N/A"
        macd_sig_str = f"{macd_sig:.4f}" if macd_sig is not None else "N/A"
 
        # Lấy 5 ngày gần nhất
        recent = df.tail(5)[['date', 'Close']].to_string(index=False) if 'date' in df.columns else "N/A"
 
        raw_data = (
            f"Symbol: {symbol}\n"
            f"Current Price: ${price:.2f}\n\n"
            f"=== MOMENTUM INDICATORS ===\n"
            f"RSI(14): {rsi_str} → {rsi_signal}\n\n"
            f"=== TREND INDICATORS ===\n"
            f"MACD: {macd_str}\n"
            f"MACD Signal Line: {macd_sig_str}\n"
            f"MACD Direction: {macd_signal}\n\n"
            f"=== VOLATILITY INDICATORS ===\n"
            f"Bollinger Band Upper: ${bb_upper:.2f}\n"
            f"Bollinger Band Lower: ${bb_lower:.2f}\n"
            f"Bollinger Band Mid (SMA20): ${sma20:.2f}\n"
            f"Current Position: {bb_signal}\n\n"
            f"=== RECENT PRICE ACTION (5 days) ===\n"
            f"{recent}\n"
        )
 
        prompt = (
            f"You are a professional technical analyst at a top-tier investment firm on Wall Street.\n"
            f"Based on the following technical indicator data for {symbol}, write a comprehensive technical analysis report in Vietnamese.\n\n"
            f"{raw_data}\n\n"
            f"Your report MUST include these sections with headers:\n"
            f"### Chỉ Số Động Lượng (Momentum)\n"
            f"### Chỉ Số Xu Hướng (Trend)\n"
            f"### Chỉ Số Biến Động (Volatility - Bollinger Bands)\n"
            f"### Hành Động Giá Gần Đây\n"
            f"### Tổng Hợp Tín Hiệu\n"
            f"### Kết Luận và Khuyến Nghị\n\n"
            f"Interpret each indicator professionally, explain what it means for traders, and give specific entry/exit guidance.\n"
            f"Include a summary table of all signals at the end.\n"
        )
 
        print("    [Technical] Đang phân tích với LLM...")
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
 
        report_text = response.choices[0].message.content
 
        return {
            "agent": "Technical Analyst",
            "symbol": symbol,
            "indicators": {
                "Current Price": round(price, 2),
                "RSI(14)": rsi_str,
                "MACD": macd_str,
                "BB Upper": round(bb_upper, 2),
                "BB Lower": round(bb_lower, 2),
            },
            "signals": {
                "RSI": rsi_signal,
                "MACD": macd_signal,
                "Bollinger": bb_signal,
            },
            "report": report_text,
            "conclusion": f"RSI={rsi_str} ({rsi_signal}) | MACD {macd_signal} | {bb_signal}"
        }