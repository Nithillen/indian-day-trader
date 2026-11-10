"""Agent 5: Risk Gatekeeper & Indian Statutory Tax Auditor."""

from typing import Dict, Any
import math


class RiskGatekeeperAgent:
    """Enforces strict 1% capital risk, calculates stop-loss/targets, and audits Indian STT/GST taxes."""

    def __init__(self, risk_budget_inr: float = 7500.0):
        self.name = "Risk & Statutory Tax Gatekeeper"
        self.risk_budget_inr = risk_budget_inr

    def evaluate(self, symbol: str, curr_price: float, atr: float) -> Dict[str, Any]:
        # Minimum ATR buffer for Indian equities
        atr_eff = max(atr, curr_price * 0.012)

        # Precise Day Trading Levels
        entry_trigger = round(curr_price * 1.002, 2)  # Buy when price crosses +0.2% above open
        stop_loss = round(entry_trigger - (1.1 * atr_eff), 2)
        target_1 = round(entry_trigger + (1.6 * atr_eff), 2)   # +1.6R: Book 50% profit
        target_2 = round(entry_trigger + (2.8 * atr_eff), 2)   # +2.8R: Final target

        risk_per_share = round(entry_trigger - stop_loss, 2)
        reward_1 = round(target_1 - entry_trigger, 2)
        rr_ratio = round(reward_1 / max(risk_per_share, 0.01), 2)

        # Position Sizing
        shares = max(5, math.floor(self.risk_budget_inr / max(risk_per_share, 1.0)))
        total_investment = round(shares * entry_trigger, 2)
        max_loss = round(shares * risk_per_share, 2)

        # Indian Taxes for NSE Intraday (Zerodha model)
        buy_turnover = shares * entry_trigger
        sell_turnover = shares * target_1
        total_turnover = buy_turnover + sell_turnover

        brokerage = min(40.0, total_turnover * 0.0003)
        stt = sell_turnover * 0.00025  # 0.025% on sell
        exchange_txn = total_turnover * 0.0000297  # NSE
        sebi_fee = total_turnover * 0.000001
        stamp_duty = buy_turnover * 0.00003
        gst = (brokerage + exchange_txn + sebi_fee) * 0.18

        total_taxes = round(brokerage + stt + exchange_txn + sebi_fee + stamp_duty + gst, 2)
        breakeven_diff = round(total_taxes / shares, 2)

        gross_profit_t1 = round((target_1 - entry_trigger) * shares, 2)
        net_profit_t1 = round(gross_profit_t1 - total_taxes, 2)

        is_approved = rr_ratio >= 1.4 and net_profit_t1 > (total_taxes * 3)

        vote = "BUY" if is_approved else "PASS"
        confidence = 90 if is_approved else 80

        if is_approved:
            reason = (
                f"Risk-Reward verified at 1:{rr_ratio}. "
                f"Target 1 yields net ₹{net_profit_t1:,.2f} after Indian STT/GST charges (₹{total_taxes:,.2f}). "
                f"Breakeven cushion required is only +₹{breakeven_diff:,.2f}/share."
            )
        else:
            reason = f"Unfavorable risk-reward (1:{rr_ratio}) or high tax friction relative to target profit."

        return {
            "agent": self.name,
            "vote": vote,
            "confidence": confidence,
            "reasoning": reason,
            "entry_trigger": entry_trigger,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "shares": shares,
            "total_investment": total_investment,
            "max_loss": max_loss,
            "rr_ratio": rr_ratio,
            "total_taxes": total_taxes,
            "breakeven_diff": breakeven_diff
        }
