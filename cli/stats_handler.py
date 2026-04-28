import threading
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import AIMessage

class StatsCallbackHandler(BaseCallbackHandler):
    """Callback handler để theo dõi số cuộc gọi LLM, Tool và lượng Token tiêu thụ."""
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self.llm_calls = 0
        self.tool_calls = 0
        self.tokens_in = 0
        self.tokens_out = 0

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        with self._lock:
            self.llm_calls += 1

    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Any]], **kwargs: Any) -> None:
        with self._lock:
            self.llm_calls += 1

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        try:
            generation = response.generations[0][0]
        except (IndexError, TypeError):
            return
        
        usage_metadata = None
        # LangChain tự động bóc tách metadata từ DeepSeek vì DeepSeek dùng chuẩn OpenAI
        if hasattr(generation, "message"):
            message = generation.message
            if isinstance(message, AIMessage) and hasattr(message, "usage_metadata"):
                usage_metadata = message.usage_metadata
        
        if usage_metadata:
            with self._lock:
                self.tokens_in += usage_metadata.get("input_tokens", 0)
                self.tokens_out += usage_metadata.get("output_tokens", 0)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        with self._lock:
            self.tool_calls += 1

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "llm_calls": self.llm_calls,
                "tool_calls": self.tool_calls,
                "tokens_in": self.tokens_in,
                "tokens_out": self.tokens_out,
            }

class PerformanceAnalyzer:
    """Phân tích hiệu năng hệ thống và các chỉ số tài chính (Dành cho DeepSeek)."""
    
    def __init__(self):
        self.stats_handler = StatsCallbackHandler()
        self.portfolio_values = [] 
        self.dates = []

    def add_snapshot(self, date, value: float):
        self.dates.append(date)
        self.portfolio_values.append(value)

    def calculate_metrics(self) -> Dict[str, float]:
        if len(self.portfolio_values) < 2:
            return {}
        values = np.array(self.portfolio_values)
        returns = np.diff(values) / values[:-1]
        cum_return = (values[-1] - values[0]) / values[0]
        
        days = (pd.to_datetime(self.dates[-1]) - pd.to_datetime(self.dates[0])).days
        ann_return = (1 + cum_return) ** (365 / max(days, 1)) - 1
        
        peak = np.maximum.accumulate(values)
        drawdowns = (values - peak) / peak
        max_drawdown = np.min(drawdowns)
        
        rf = 0.02 / 252
        sharpe = (np.mean(returns) - rf) / np.std(returns) * np.sqrt(252) if np.std(returns) != 0 else 0

        return {
            "Cumulative Return": cum_return,
            "Annualized Return": ann_return,
            "Max Drawdown": max_drawdown,
            "Sharpe Ratio": sharpe
        }

    def compute_deepseek_cost(self):
        """Tính toán chi phí dựa trên bảng giá DeepSeek-V3 thực tế."""
        stats = self.stats_handler.get_stats()
        # Giá DeepSeek-V3: ~$0.14/1M input, ~$0.28/1M output
        cost = (stats["tokens_in"] / 1_000_000 * 0.14) + (stats["tokens_out"] / 1_000_000 * 0.28)
        return round(cost, 6)

    def print_final_report(self):
        metrics = self.calculate_metrics()
        stats = self.stats_handler.get_stats()
        cost = self.compute_deepseek_cost()

        print("\n" + "="*45)
        print("🚀 BÁO CÁO TỔNG KẾT TRADING AGENTS (DEEPSEEK)")
        print("="*45)
        print(f"💰 [TÀI CHÍNH]")
        for k, v in metrics.items():
            fmt = ".2%" if "Return" in k or "Drawdown" in k else ".2f"
            print(f"  - {k}: {v:{fmt}}")
        
        print(f"\n⚙️ [HIỆU NĂNG AI - CHI PHÍ TỐI ƯU]")
        print(f"  - Tổng số LLM Calls: {stats['llm_calls']}")
        print(f"  - Tổng số Tool Calls: {stats['tool_calls']}")
        print(f"  - Input Tokens: {stats['tokens_in']}")
        print(f"  - Output Tokens: {stats['tokens_out']}")
        print(f"  - Ước tính chi phí: ${cost:.6f} (DeepSeek Rate)")
        print("="*45)
    
    def plot_results(self):
        """Vẽ biểu đồ lợi nhuận để An đưa vào slide thuyết trình."""
        import matplotlib.pyplot as plt
        if not self.portfolio_values:
            print("Không có dữ liệu để vẽ biểu đồ.")
            return
        
        plt.figure(figsize=(10, 5))
        plt.plot(self.dates, self.portfolio_values, label='Portfolio Value', color='blue')
        plt.title('Backtesting Result - AAPL')
        plt.xlabel('Date')
        plt.ylabel('Value ($)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show() # Hoặc plt.savefig('results/pnl_curve.png')