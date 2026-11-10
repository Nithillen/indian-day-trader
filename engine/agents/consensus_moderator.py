"""Agent 6: Multi-Agent Consensus Floor Governor & Trade Coordinator."""

from typing import Dict, List, Optional, Tuple
import pandas as pd

from engine.agents.mean_reversion_agent import MeanReversionAgent
from engine.agents.momentum_agent import MomentumAgent
from engine.agents.orb_agent import ORBAgent
from engine.agents.risk_gatekeeper_agent import RiskGatekeeperAgent
from engine.agents.sector_flow_agent import SectorFlowAgent
from engine.signals.trade_card import DayTradeSignal


class ConsensusModerator:
    """Orchestrates the 5 specialized day-trading agents, moderates their debate, and tallies consensus."""

    def __init__(self):
        self.orb = ORBAgent()
        self.momentum = MomentumAgent()
        self.mean_rev = MeanReversionAgent()
        self.sector_flow = SectorFlowAgent()
        self.risk = RiskGatekeeperAgent()

    def evaluate_stock(
        self,
        symbol: str,
        name: str,
        sector: str,
        df: pd.DataFrame
    ) -> Optional[DayTradeSignal]:
        """Conduct multi-agent debate and consensus vote on a stock."""
        curr_price = float(df["Close"].iloc[-1])
        high_low_tr = (df["High"] - df["Low"]).tail(14).mean()
        atr = float(high_low_tr) if not pd.isna(high_low_tr) else (curr_price * 0.015)

        # 1. Gather Agent Assessments
        r_orb = self.orb.evaluate(symbol, df)
        r_mom = self.momentum.evaluate(symbol, df)
        r_mr = self.mean_rev.evaluate(symbol, df)
        r_sec = self.sector_flow.evaluate(symbol, sector)
        r_risk = self.risk.evaluate(symbol, curr_price, atr)

        agent_results = [r_orb, r_mom, r_mr, r_sec, r_risk]

        # 2. Tally Votes
        buy_votes = sum(1 for a in agent_results if a["vote"] == "BUY")
        weighted_score = sum(a["confidence"] for a in agent_results if a["vote"] == "BUY") / len(agent_results)
        consensus_score = int(round(weighted_score))

        # Build Debate Transcript
        debates = {
            "1_PriceAction_ORB": f"[{r_orb['vote']} ({r_orb['confidence']}%)]: {r_orb['reasoning']}",
            "2_Volume_Momentum": f"[{r_mom['vote']} ({r_mom['confidence']}%)]: {r_mom['reasoning']}",
            "3_Volatility_VWAP": f"[{r_mr['vote']} ({r_mr['confidence']}%)]: {r_mr['reasoning']}",
            "4_Sector_Macro": f"[{r_sec['vote']} ({r_sec['confidence']}%)]: {r_sec['reasoning']}",
            "5_Risk_Tax_Audit": f"[{r_risk['vote']} ({r_risk['confidence']}%)]: {r_risk['reasoning']}",
        }

        # Consensus Rule: At least 4 out of 5 agents must vote BUY, and Risk Gatekeeper MUST approve
        if buy_votes < 4 or r_risk["vote"] != "BUY":
            return None

        entry_trigger = r_risk["entry_trigger"]
        stop_loss = r_risk["stop_loss"]
        target_1 = r_risk["target_1"]
        target_2 = r_risk["target_2"]

        when_to_buy = (
            f"1. Wait for market open (09:15 AM IST).\n"
            f"2. Place a BUY LIMIT / SL-LIMIT order triggered only when price breaks above ₹{entry_trigger:,.2f}.\n"
            f"3. Do not buy if the opening 5-minute candle closes below ₹{stop_loss:,.2f}."
        )

        when_to_sell = (
            f"🎯 TARGET 1 (₹{target_1:,.2f}): SELL 50% OF YOUR SHARES. Immediately move Stop-Loss on remaining 50% to Entry (₹{entry_trigger:,.2f}) to eliminate all risk.\n"
            f"🎯 TARGET 2 (₹{target_2:,.2f}): SELL REMAINING 50% OF SHARES. Complete exit with maximum day-trading profit.\n"
            f"🛑 STOP-LOSS (₹{stop_loss:,.2f}): EXIT 100% OF SHARES IMMEDIATELY if price falls below this line. No exceptions."
        )

        trailing_stop_rule = (
            f"After Target 1 (₹{target_1:,.2f}) is reached, trail your stop loss upward below each 15-minute swing low "
            f"to protect runner profits until Target 2 is hit."
        )

        mandatory_time_exit = (
            "⏰ 03:15 PM IST HARD CUTOFF: Brokers begin automated square-off between 3:15 and 3:20 PM. "
            "Sell whatever shares remain at 03:15 PM IST market price regardless of current P&L."
        )

        signal = DayTradeSignal(
            symbol=symbol,
            company_name=name,
            sector=sector,
            current_price=curr_price,
            action="INTRADAY_BUY",
            consensus_score=consensus_score,
            buy_trigger_price=entry_trigger,
            stop_loss_price=stop_loss,
            target_1_price=target_1,
            target_2_price=target_2,
            recommended_shares=r_risk["shares"],
            capital_required_inr=r_risk["total_investment"],
            max_risk_inr=r_risk["max_loss"],
            reward_to_risk_ratio=r_risk["rr_ratio"],
            breakeven_cost_per_share=r_risk["breakeven_diff"],
            when_to_buy=when_to_buy,
            when_to_sell=when_to_sell,
            trailing_stop_rule=trailing_stop_rule,
            mandatory_time_exit=mandatory_time_exit,
            agent_debates=debates
        )

        return signal
