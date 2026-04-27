"""Research Manager: turns the bull/bear debate into a structured investment plan for the trader."""

from __future__ import annotations
import os
import json
from datetime import datetime

from tradingagents.agents.schemas import ResearchPlan, render_research_plan
from tradingagents.agents.utils.agent_utils import build_instrument_context
from tradingagents.agents.utils.structured import (
    bind_structured,
    invoke_structured_or_freetext,
)


def _save_debate_checkpoint(symbol: str, state: dict, round_num: int):
    """Lưu toàn bộ debate history sau mỗi vòng tranh luận (Giữ nguyên chức năng cũ)."""
    os.makedirs("results", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    investment_debate_state = state["investment_debate_state"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 1. Markdown → results/ ───────────────────────────────────────────
    md_path = f"results/{symbol}_debate_round_{round_num}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {symbol} — Debate Checkpoint (Round {round_num})\n")
        f.write(f"_Saved at: {timestamp}_\n\n")

        f.write("## Full History\n")
        f.write(investment_debate_state.get("history", "") + "\n\n")

        f.write("## Bull History\n")
        f.write(investment_debate_state.get("bull_history", "") + "\n\n")

        f.write("## Bear History\n")
        f.write(investment_debate_state.get("bear_history", "") + "\n\n")

        current = investment_debate_state.get("current_response", "")
        if current:
            f.write("## Current Response (latest turn)\n")
            f.write(str(current) + "\n")

    # ── 2. JSON → data/ ──────────────────────────────────────────────────
    json_path = f"data/{symbol}_debate_round_{round_num}.json"
    checkpoint = {
        "symbol": symbol,
        "round": round_num,
        "timestamp": timestamp,
        "count": investment_debate_state.get("count", round_num),
        "history": investment_debate_state.get("history", ""),
        "bull_history": investment_debate_state.get("bull_history", ""),
        "bear_history": investment_debate_state.get("bear_history", ""),
        "current_response": str(investment_debate_state.get("current_response", "")),
        "judge_decision": str(investment_debate_state.get("judge_decision", "")),
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    print(f"💾 [CHECKPOINT] Round {round_num} saved → MD: {md_path} | JSON: {json_path}")


def create_research_manager(llm):
    structured_llm = bind_structured(llm, ResearchPlan, "Research Manager")

    def research_manager_node(state) -> dict:
        instrument_context = build_instrument_context(state["company_of_interest"])
        history = state["investment_debate_state"].get("history", "")
        investment_debate_state = state["investment_debate_state"]

        symbol = state.get("company_of_interest", "Unknown")
        current_round = investment_debate_state.get("count", 0)

        # ── 1. Lưu checkpoint (Markdown từng vòng + JSON data) ────────────────
        _save_debate_checkpoint(symbol, state, round_num=current_round)

        # ── 2. LƯU TOÀN BỘ LỊCH SỬ TRANH LUẬN (FULL DEBATE HISTORY) ────────────
        full_history_path = f"results/{symbol}_FULL_DEBATE_HISTORY.md"
        with open(full_history_path, "w", encoding="utf-8") as f:
            f.write(f"# FULL INVESTMENT DEBATE SESSION: {symbol}\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(history)
        print(f" [SYSTEM]: DA LUU TOAN BO CUOC TRANH LUAN TAI: {full_history_path}")

        prompt = f"""As the Research Manager and debate facilitator, your role is to critically evaluate this round of debate and deliver a clear, actionable investment plan for the trader.

{instrument_context}

---

**Rating Scale** (use exactly one):
- **Buy**: Strong conviction in the bull thesis; recommend taking or growing the position
- **Overweight**: Constructive view; recommend gradually increasing exposure
- **Hold**: Balanced view; recommend maintaining the current position
- **Underweight**: Cautious view; recommend trimming exposure
- **Sell**: Strong conviction in the bear thesis; recommend exiting or avoiding the position

Commit to a clear stance whenever the debate's strongest arguments warrant one; reserve Hold for situations where the evidence on both sides is genuinely balanced.

---

**Debate History:**
{history}"""

        investment_plan = invoke_structured_or_freetext(
            structured_llm,
            llm,
            prompt,
            render_research_plan,
            "Research Manager",
        )

        # ── 3. Lưu final investment plan ──────────────────────────────────────
        os.makedirs("results", exist_ok=True)
        file_path = f"results/{symbol}_final_investment_plan.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(investment_plan))

        print(f"\n💎 [SYSTEM]: DA CHOT QUYET DINH CUOI CUNG CHO {symbol}!")
        print(f"📂 [SYSTEM]: KET QUA DA DUOC LUU TAI: {file_path}")

        new_investment_debate_state = {
            "judge_decision": investment_plan,
            "history": history,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": investment_plan,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": investment_plan,
        }

    return research_manager_node