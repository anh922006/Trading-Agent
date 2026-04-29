import os
import time
from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Import core từ framework TradingAgents 
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

console = Console()

# --- PHẦN WELCOME TEXT ---
welcome_ascii = """
  ______               ___             ___                    __      
 /_  __/________ _____/ (_)___  ____ _/   | ____ ____  ____  / /______
  / / / ___/ __ `/ __  / / __ \/ __ `/ /| |/ __ `/ _ \/ __ \/ __/ ___/
 / / / /  / /_/ / /_/ / / / / / /_/ / ___ / /_/ /  __/ / / / /_(__  ) 
/_/ /_/   \__,_/\__,_/_/_/ /_/\__, /_/  |_\__, /\___/_/ /_/\__/____/  
                             /____/      /____/     """

def run_simulation():
    # 1. Hiển thị Welcome và Workflow trước [cite: 2, 134]
    console.print(Panel(Text(welcome_ascii.strip(), style="bold cyan"), border_style="bright_blue", padding=(0, 1)))
    
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_row("[bold green]Framework:[/bold green]", "TradingAgents: Multi-Agents LLM Trading [cite: 2]")
    info_table.add_row("[bold white]Workflow:[/bold white]", "Analyst → Research → Trader → Risk → Portfolio [cite: 134]")
    console.print(info_table)

    # ---------------------------------------------------------
    # 2. GIỮ Y HỆT TỪNG DÒNG CODE LOGIC CỦA BẠN (KHÔNG ĐỔI)
    # ---------------------------------------------------------
    load_dotenv()
    config = DEFAULT_CONFIG.copy()
    config["deep_think_llm"] = "deepseek-chat"  # [cite: 164]
    config["quick_think_llm"] = "deepseek-chat"    # [cite: 167]
    config["max_debate_rounds"] = 1                # [cite: 145]

    config["data_vendors"] = {
        "core_stock_apis": "yfinance",           # [cite: 139]
        "technical_indicators": "yfinance",      # [cite: 84]
        "fundamental_data": "yfinance",          # [cite: 72]
        "news_data": "yfinance",                 # [cite: 80]
    }

    # Initialize với debug=True để hiện data thô ngay lập tức 
    ta = TradingAgentsGraph(debug=True, config=config)

    # In thông báo bắt đầu để phân biệt với Welcome Text
    rprint("\n[bold yellow]>>> ĐANG KHỞI CHẠY PROPAGATE VÀ TRÍCH XUẤT DATA...[/bold yellow]\n")

    # forward propagate - Chạy trực tiếp để debug=True in data ra terminal luôn
    # Không để trong console.status để tránh bị ẩn data khi đang chạy
    state, decision = ta.propagate("AAPL", "2026-04-24") 

    # ---------------------------------------------------------
    # 3. SAU KHI HIỆN DATA THÔ, ĐÓNG KHUNG LẠI CHO ĐẸP [cite: 142]
    # ---------------------------------------------------------
    rprint("\n[bold magenta]=== TỔNG HỢP BÁO CÁO CHI TIẾT ===[/bold magenta]")

    if "technical_analysis" in state:
        console.print(Panel(state["technical_analysis"].strip(), title="[bold blue]🔵 TECHNICAL REPORT[/bold blue]", border_style="blue", expand=True))
    
    if "fundamental_analysis" in state:
        console.print(Panel(state["fundamental_analysis"].strip(), title="[bold green]🟢 FUNDAMENTAL REPORT[/bold green]", border_style="green", expand=True))

    # In kết quả cuối cùng trong khung màu sáng [cite: 131]
    result_panel = Panel(
        Text(str(decision).strip(), style="bold white"),
        title="[bold bright_green]🎯 FINAL DECISION[/bold bright_green]",
        border_style="bright_green",
        padding=(1, 2),
        expand=True
    )
    console.print(result_panel)

    # ta.reflect_and_remember(1000) # [cite: 153]

if __name__ == "__main__":
    run_simulation()

