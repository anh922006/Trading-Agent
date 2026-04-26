import finnhub
import json
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from groq import Groq

class SentimentAgent:
    def __init__(self, finnhub_key, groq_key):
        self.finnhub_client = finnhub.Client(api_key=finnhub_key)
        self.analyzer = SentimentIntensityAnalyzer()
        self.groq_client = Groq(api_key=groq_key)

    def analyze(self, symbol):
        # Đọc news từ JSON của crawler
        json_file = f"data/{symbol}_internal.json"
        news_headlines = []
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                internal = json.load(f)
            news_headlines = internal.get('news', [])
        else:
            end = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            try:
                news = self.finnhub_client.company_news(symbol, _from=start, to=end)
                news_headlines = [n.get('headline', '') for n in news[:15]]
            except Exception:
                news_headlines = []

        # Chấm điểm từng headline
        scored = []
        for headline in news_headlines:
            score = self.analyzer.polarity_scores(headline)['compound']
            label = "Tích cực" if score > 0.05 else "Tiêu cực" if score < -0.05 else "Trung tính"
            scored.append({"headline": headline, "score": round(score, 4), "label": label})

        scores = [a['score'] for a in scored]
        avg_score = round(sum(scores) / len(scores), 4) if scores else 0
        overall = "Tích cực " if avg_score > 0.05 else "Tiêu cực " if avg_score < -0.05 else "Trung tính "

        # Tạo bảng dữ liệu để LLM phân tích
        sentiment_table = "\n".join([
            f"- \"{a['headline'][:80]}\" → {a['label']} (score={a['score']})"
            for a in scored
        ])

        prompt = f"""You are a professional sentiment analyst at a top-tier investment firm.
Below is the sentiment analysis data for {symbol} based on {len(scored)} recent news articles:

Average Sentiment Score: {avg_score} → {overall}

Article-by-article breakdown:
{sentiment_table}

Write a comprehensive sentiment analysis report in Vietnamese with these sections:
### Tổng Quan Tâm Lý Thị Trường
### Phân Tích Chi Tiết Từng Bài Báo (nêu bật các tin tích cực và tiêu cực nhất)
### Xu Hướng Tâm Lý
### Tác Động Đến Giá Cổ Phiếu
### Kết Luận

Write like a Wall Street sentiment expert. Be specific about which news drives sentiment.
"""

        print(f"    [Sentiment] Đang phân tích với LLM...")
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )

        report_text = response.choices[0].message.content

        return {
            "agent": "Sentiment Analyst",
            "symbol": symbol,
            "average_score": avg_score,
            "sentiment": overall,
            "articles_analyzed": len(scored),
            "report": report_text,
            "conclusion": f"Tâm lý {overall} dựa trên {len(scored)} bài viết (score={avg_score})"
        }

