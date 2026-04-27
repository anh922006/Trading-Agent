from crawler import AppleCrawler
from analyst_agents import AnalystAgents


FINNHUB_KEY = "d7k6mspr01qnk4odpl90d7k6mspr01qnk4odpl9g"
GEMINI_KEY = "AIzaSyCVJqWlVFtxd4ZmbYSvSovJd6BWcjVeOGg"
TAVILY_KEY = "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"

def main():
    try:
        # Gọi Crawler đi cào dữ liệu
        scratcher = AppleCrawler(FINNHUB_KEY, tavily_key=TAVILY_KEY)
        scratcher.crawl_all()
        
        # Gọi Agent đi phân tích dữ liệu vừa cào được
        # analyst = AnalystAgents(GEMINI_KEY)
        # final_report = analyst.run_analysis("AAPL")
        
        
        # print("\n" + "="*50)
        # print("BÁO CÁO PHÂN TÍCH NỘI TẠI APPLE")
        # print("="*50)
        # print(final_report)
        # print("="*50)
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()