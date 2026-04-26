import json
import os
import pandas as pd
from datetime import datetime, timedelta
import finnhub
from groq import Groq

class NewsAgent:
    def __init__(self, finnhub_key, groq_key):
        self.finnhub_client = finnhub.Client(api_key=finnhub_key)
        self.groq_client = Groq(api_key=groq_key)

    def analyze(self, symbol):
        # Đọc news từ JSON của crawler
        json_file = f"data/{symbol}_internal.json"
        headlines = []
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                internal = json.load(f)
            headlines = internal.get('news', [])
        else:
            end = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            try:
                news = self.finnhub_client.company_news(symbol, _from=start, to=end)
                headlines = [n.get('headline', '') for n in news[:15]]
            except Exception:
                headlines = []

        # Đọc macro data từ TV1
        macro_ctx = {}
        market_file = "data/lan/market_context.csv"
        if os.path.exists(market_file):
            df_mkt = pd.read_csv(market_file)
            last = df_mkt.iloc[-1]
            if 'vix' in df_mkt.columns:
                vix = float(last['vix'])
                macro_ctx['VIX'] = round(vix, 2)
                macro_ctx['VIX_signal'] = (
                    "Thị trường sợ hãi cao " if vix > 30
                    else "Biến động trung bình " if vix > 20
                    else "Thị trường bình tĩnh "
                )
            if 'fed_rate' in df_mkt.columns:
                fed = float(last['fed_rate'])
                macro_ctx['Fed_Rate'] = round(fed, 2)
                macro_ctx['Fed_signal'] = (
                    "Lãi suất cao, áp lực cổ phiếu tăng trưởng" if fed > 4
                    else "Lãi suất trung bình" if fed > 2
                    else "Lãi suất thấp, hỗ trợ cổ phiếu"
                )

        news_list = "\n".join([f"- {h}" for h in headlines])
        macro_text = f"""
VIX Index: {macro_ctx.get('VIX', 'N/A')} → {macro_ctx.get('VIX_signal', 'N/A')}
Fed Rate: {macro_ctx.get('Fed_Rate', 'N/A')}% → {macro_ctx.get('Fed_signal', 'N/A')}
""" if macro_ctx else "Macro data không khả dụng"

        prompt = f"""You are a professional news and macroeconomic analyst at a top-tier investment firm.
Analyze the following recent news headlines for {symbol} and macroeconomic indicators:

=== RECENT NEWS ({len(headlines)} articles) ===
{news_list}

=== MACRO ECONOMIC INDICATORS ===
{macro_text}

Write a comprehensive news analysis report in Vietnamese with these sections:
### Tổng Quan Môi Trường Vĩ Mô
### Phân Tích Tin Tức Công Ty
### Các Sự Kiện Nổi Bật Ảnh Hưởng Đến Thị Trường
### Chỉ Số VIX và Lãi Suất Fed
### Tác Động Đến {symbol}
### Kết Luận

Analyze like a Wall Street macro expert. Connect news events to potential stock price impact.
"""

        print(f"    [News] Đang phân tích với LLM...")
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )

        report_text = response.choices[0].message.content

        return {
            "agent": "News Analyst",
            "symbol": symbol,
            "total_news": len(headlines),
            "macro_context": macro_ctx,
            "report": report_text,
            "conclusion": f"{len(headlines)} tin gần đây | VIX={macro_ctx.get('VIX','N/A')} ({macro_ctx.get('VIX_signal','N/A')}) | Fed={macro_ctx.get('Fed_Rate','N/A')}%"
        }

