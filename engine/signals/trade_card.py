"""Day Trading Signal Card Data Structure."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime


@dataclass
class DayTradeSignal:
    symbol: str
    company_name: str
    sector: str
    current_price: float
    action: str  # "INTRADAY_BUY", "WATCH", "AVOID"
    consensus_score: int  # 0 to 100

    # Exact Entry & Exit Prices
    buy_trigger_price: float  # Buy above this price
    stop_loss_price: float    # Hard Stop Loss
    target_1_price: float     # Take profit 1 (Sell 50%)
    target_2_price: float     # Take profit 2 (Sell remaining 50%)

    # Sizing & Breakeven
    recommended_shares: int
    capital_required_inr: float
    max_risk_inr: float
    reward_to_risk_ratio: float
    breakeven_cost_per_share: float

    # Execution Guidance
    when_to_buy: str
    when_to_sell: str
    trailing_stop_rule: str
    mandatory_time_exit: str

    # Agent Consensus Debate
    agent_debates: Dict[str, str] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"))
    trade_status: str = "PENDING_TRIGGER"  # PENDING_TRIGGER, TRIGGERED_ACTIVE, TARGET_1_HIT, TARGET_2_HIT, STOPPED_OUT

    def to_dict(self) -> Dict[str, any]:
        return {
            "symbol": self.symbol,
            "company_name": self.company_name,
            "sector": self.sector,
            "current_price": f"₹{self.current_price:,.2f}",
            "action": self.action,
            "consensus_score": f"{self.consensus_score}/100",
            "buy_trigger": f"₹{self.buy_trigger_price:,.2f}",
            "stop_loss": f"₹{self.stop_loss_price:,.2f}",
            "target_1": f"₹{self.target_1_price:,.2f}",
            "target_2": f"₹{self.target_2_price:,.2f}",
            "recommended_shares": self.recommended_shares,
            "capital_required": f"₹{self.capital_required_inr:,.2f}",
            "max_risk_amount": f"₹{self.max_risk_inr:,.2f}",
            "risk_reward": f"1:{self.reward_to_risk_ratio}",
            "breakeven_cost": f"+₹{self.breakeven_cost_per_share:,.2f}/share",
            "when_to_buy": self.when_to_buy,
            "when_to_sell": self.when_to_sell,
            "trailing_stop_rule": self.trailing_stop_rule,
            "mandatory_time_exit": self.mandatory_time_exit,
            "agent_debates": self.agent_debates,
            "trade_status": self.trade_status,
            "generated_at": self.generated_at
        }
