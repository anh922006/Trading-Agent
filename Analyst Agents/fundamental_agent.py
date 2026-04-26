import yfinance as yf
import pandas as pd
import os
from groq import Groq

class FundamentalAgent:
    def __init__(self, groq_key):
        self.client = Groq(api_key=groq_key)

    def analyze(self, symbol):
        ticker = yf.Ticker(symbol)
        info = ticker.info

        pe = info.get('trailingPE', None)
        pb = info.get('priceToBook', None)
        eps = info.get('trailingEps', None)
        revenue = info.get('totalRevenue', None)
        profit_margin = info.get('profitMargins', None)
        debt_to_equity = info.get('debtToEquity', None)
        roe = info.get('returnOnEquity', None)
        roa = info.get('returnOnAssets', None)
        gross_margin = info.get('grossMargins', None)
        operating_margin = info.get('operatingMargins', None)
        current_ratio = info.get('currentRatio', None)
        quick_ratio = info.get('quickRatio', None)
        price = info.get('currentPrice', None)
        market_cap = info.get('marketCap', None)
        dividend_yield = info.get('dividendYield', None)

        def fmt(val, suffix='', multiplier=1, decimals=2):
            if val is None: return 'N/A'
            return f"{val * multiplier:.{decimals}f}{suffix}"

        def money_fmt(val):
            if val is None: return 'N/A'
            if val >= 1e12: return f"${val/1e12:.2f}T"
            if val >= 1e9: return f"${val/1e9:.2f}B"
            return f"${val/1e6:.2f}M"

        # So sánh với S&P500 từ data TV1
        market_ctx = {}
        market_file = "data/lan/market_context.csv"
        if os.path.exists(market_file):
            df_mkt = pd.read_csv(market_file)
            symbol_col = symbol.lower()
            if symbol_col in df_mkt.columns and 'sp500' in df_mkt.columns:
                df_30 = df_mkt.tail(30)
                aapl_ret = (df_30[symbol_col].iloc[-1] / df_30[symbol_col].iloc[0] - 1) * 100
                sp500_ret = (df_30['sp500'].iloc[-1] / df_30['sp500'].iloc[0] - 1) * 100
                market_ctx = {
                    "stock_30d_return": round(aapl_ret, 2),
                    "sp500_30d_return": round(sp500_ret, 2),
                    "outperform": aapl_ret > sp500_ret
                }

        raw_data = f"""
Company: {symbol}
Market Cap: {money_fmt(market_cap)}
Current Price: {fmt(price, suffix=' USD')}

=== PROFITABILITY ===
Gross Margin: {fmt(gross_margin, suffix='%', multiplier=100)}
Operating Margin: {fmt(operating_margin, suffix='%', multiplier=100)}
Net Profit Margin: {fmt(profit_margin, suffix='%', multiplier=100)}
ROE: {fmt(roe, suffix='%', multiplier=100)}
ROA: {fmt(roa, suffix='%', multiplier=100)}

=== VALUATION ===
P/E Ratio: {fmt(pe)}
P/B Ratio: {fmt(pb)}
EPS (TTM): {fmt(eps, suffix=' USD')}
Dividend Yield: {fmt(dividend_yield, suffix='%', multiplier=100)}

=== FINANCIAL HEALTH ===
Revenue: {money_fmt(revenue)}
Debt/Equity: {fmt(debt_to_equity)}
Current Ratio: {fmt(current_ratio)}
Quick Ratio: {fmt(quick_ratio)}

=== MARKET PERFORMANCE (30 days) ===
{symbol} Return: {market_ctx.get('stock_30d_return', 'N/A')}%
S&P500 Return: {market_ctx.get('sp500_30d_return', 'N/A')}%
Outperform Market: {market_ctx.get('outperform', 'N/A')}
"""

        prompt = f"""You are a professional fundamental analyst at a top-tier investment firm on Wall Street.
Based on the following financial data for {symbol}, write a comprehensive fundamental analysis report in Vietnamese.

{raw_data}

Your report MUST include these sections with headers:
### Tổng Quan Công Ty
### Chỉ Số Sinh Lời
### Định Giá Cổ Phiếu
### Sức Khỏe Tài Chính
### Hiệu Suất So Với Thị Trường
### Kết Luận Đầu Tư

Be specific, use the actual numbers provided, and write like a Wall Street expert. Include a markdown table summarizing key metrics at the end.
"""

        print(f"    [Fundamental] Đang phân tích với LLM...")
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )

        report_text = response.choices[0].message.content

        return {
            "agent": "Fundamental Analyst",
            "symbol": symbol,
            "raw_metrics": {
                "P/E": fmt(pe), "P/B": fmt(pb), "ROE": fmt(roe, suffix='%', multiplier=100),
                "Profit Margin": fmt(profit_margin, suffix='%', multiplier=100),
                "Revenue": money_fmt(revenue)
            },
            "report": report_text,
            "conclusion": f"P/E={fmt(pe)}, ROE={fmt(roe, suffix='%', multiplier=100)}, {symbol} {'vượt trội' if market_ctx.get('outperform') else 'kém hơn'} S&P500 30 ngày qua"
        }

