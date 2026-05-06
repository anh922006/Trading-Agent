from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "deepseek-reasoner"  # Use a different model
config["quick_think_llm"] = "deepseek-chat" # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance, no extra API keys needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: alpha_vantage, yfinance
    "technical_indicators": "yfinance",      # Options: alpha_vantage, yfinance
    "fundamental_data": "yfinance",          # Options: alpha_vantage, yfinance
    "news_data": "yfinance",                 # Options: alpha_vantage, yfinance
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("AAPL", "2026-04-24")

# Chạy ngày 2 — hệ thống tự resolve ngày 1, viết reflection
_, decision = ta.propagate("AAPL", "2026-04-25")
print(decision)

_, decision3 = ta.propagate("AAPL", "2026-04-26")
print("Ngày 3:", decision3)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
