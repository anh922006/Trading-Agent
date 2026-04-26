from fundamental_agent import FundamentalAgent
from sentiment_agent import SentimentAgent
from news_agent import NewsAgent
from technical_agent import TechnicalAgent
from groq import Groq

# ===== CẤU HÌNH =====
FINNHUB_KEY = "d7k6mspr01qnk4odpl90d7k6mspr01qnk4odpl9g"
GROQ_KEY = "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"      
SYMBOL = "AAPL"             # Đổi thành NVDA, MSFT tuỳ ý

def print_report(report):
    print("\n" + "=" * 70)
    print(f"    {report['agent']}  —  {report['symbol']}")
    print("=" * 70)

    # In raw metrics nếu có
    if 'raw_metrics' in report:
        print("\n  [Chỉ số chính]")
        for k, v in report['raw_metrics'].items():
            print(f"    {k}: {v}")

    if 'indicators' in report:
        print("\n  [Chỉ báo kỹ thuật]")
        for k, v in report['indicators'].items():
            print(f"    {k}: {v}")

    if 'signals' in report:
        print("\n  [Tín hiệu]")
        for k, v in report['signals'].items():
            print(f"    {k}: {v}")

    # In báo cáo LLM
    if 'report' in report:
        print("\n" + "-" * 70)
        print("   BÁO CÁO PHÂN TÍCH:")
        print("-" * 70)
        print(report['report'])

def llm_final_summary(reports, groq_key):
    client = Groq(api_key=groq_key)
    summary = "\n\n".join([
        f"=== {r['agent']} ===\n{r.get('conclusion', '')}"
        for r in reports
    ])
    prompt = f"""Bạn là chuyên gia đầu tư cấp cao tại một quỹ hedge fund hàng đầu phố Wall.
Dựa trên báo cáo tổng hợp từ 4 analyst agents sau đây cho mã {reports[0]['symbol']}:

{summary}

Hãy viết kết luận đầu tư cuối cùng bằng tiếng Việt, bao gồm:
### Tổng Hợp 4 Phân Tích
### Điểm Mạnh
### Rủi Ro
### Quyết Định Đầu Tư: BUY / SELL / HOLD (chọn 1)
### Lý Do Quyết Định

Ngắn gọn, chuyên nghiệp, quyết đoán như chuyên gia phố Wall.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def main():
    print(f"\n{'#'*70}")
    print(f"    ANALYST AGENTS — BÁO CÁO PHÂN TÍCH: {SYMBOL}")
    print(f"{'#'*70}")

    reports = []

    print("\n [1/4] Fundamental Analyst đang chạy...")
    r = FundamentalAgent(GROQ_KEY).analyze(SYMBOL)
    print_report(r)
    reports.append(r)

    print("\n [2/4] Sentiment Analyst đang chạy...")
    r = SentimentAgent(FINNHUB_KEY, GROQ_KEY).analyze(SYMBOL)
    print_report(r)
    reports.append(r)

    print("\n [3/4] News Analyst đang chạy...")
    r = NewsAgent(FINNHUB_KEY, GROQ_KEY).analyze(SYMBOL)
    print_report(r)
    reports.append(r)

    print("\n [4/4] Technical Analyst đang chạy...")
    r = TechnicalAgent(GROQ_KEY).analyze(SYMBOL)
    print_report(r)
    reports.append(r)

    print("\n" + "=" * 70)
    print("    TỔNG HỢP KẾT LUẬN 4 AGENTS")
    print("=" * 70)
    for rep in reports:
        print(f"  {rep['agent']:<25}: {rep.get('conclusion', 'N/A')}")

    print("\n" + "=" * 70)
    print("    KẾT LUẬN ĐẦU TƯ CUỐI CÙNG (LLM)")
    print("=" * 70)
    print("\n Đang tổng hợp kết luận cuối...")
    final = llm_final_summary(reports, GROQ_KEY)
    print(final)
    print("=" * 70)

if __name__ == "__main__":
    main()

