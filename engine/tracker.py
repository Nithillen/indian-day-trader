"""Live Day Trading Market Scanner & Position Tracker."""

import datetime
from typing import Dict, List, Optional
from engine.agents.consensus_moderator import ConsensusModerator
from engine.data_provider import TOP_NSE_STOCKS, fetch_stock_candles, get_market_status
from engine.signals.trade_card import DayTradeSignal


class DayTradeTracker:
    """Scans Dalal Street universe, facilitates multi-agent consensus, and tracks live trade states."""

    def __init__(self):
        self.moderator = ConsensusModerator()
        self.active_signals: Dict[str, DayTradeSignal] = {}

    def run_morning_scan(self, top_n: int = 3) -> List[DayTradeSignal]:
        """Scan top liquid NSE stocks and filter for consensus day trading opportunities."""
        approved_signals: List[DayTradeSignal] = []

        for symbol, info in TOP_NSE_STOCKS.items():
            try:
                df = fetch_stock_candles(info["ticker"])
                if df.empty or len(df) < 10:
                    continue

                sector_map = {
                    "TATAMOTORS": "Automobile", "MARUTI": "Automobile",
                    "HDFCBANK": "Banking & Financials", "ICICIBANK": "Banking & Financials",
                    "SBIN": "Banking & Financials", "BAJFINANCE": "Banking & Financials", "AXISBANK": "Banking & Financials",
                    "TCS": "Information Technology", "INFY": "Information Technology",
                    "RELIANCE": "Energy / Oil & Gas", "LT": "Engineering & Construction",
                    "SUNPHARMA": "Healthcare / Pharma", "TITAN": "Consumer Discretionary", "ITC": "FMCG"
                }
                sector = sector_map.get(symbol, "Equities")

                signal = self.moderator.evaluate_stock(
                    symbol=info["ticker"],
                    name=info["name"],
                    sector=sector,
                    df=df
                )

                if signal:
                    approved_signals.append(signal)
            except Exception:
                continue

        # Sort descending by consensus score, then risk/reward
        approved_signals.sort(key=lambda s: (s.consensus_score, s.reward_to_risk_ratio), reverse=True)
        top_picks = approved_signals[:top_n]

        # Register in tracker
        for s in top_picks:
            self.active_signals[s.symbol] = s

        return top_picks

    def update_signal_status(self, symbol: str, current_live_price: float) -> str:
        """Update and return the lifecycle status of an active day-trading pick."""
        if symbol not in self.active_signals:
            return "UNKNOWN"

        sig = self.active_signals[symbol]
        sig.current_price = current_live_price

        # State machine for the trade
        if sig.trade_status == "PENDING_TRIGGER":
            if current_live_price >= sig.buy_trigger_price:
                sig.trade_status = "TRIGGERED_ACTIVE"
        elif sig.trade_status == "TRIGGERED_ACTIVE":
            if current_live_price <= sig.stop_loss_price:
                sig.trade_status = "STOPPED_OUT"
            elif current_live_price >= sig.target_2_price:
                sig.trade_status = "TARGET_2_HIT"
            elif current_live_price >= sig.target_1_price:
                sig.trade_status = "TARGET_1_HIT"
        elif sig.trade_status == "TARGET_1_HIT":
            if current_live_price >= sig.target_2_price:
                sig.trade_status = "TARGET_2_HIT"
            elif current_live_price <= sig.buy_trigger_price:
                # Breakeven stop hit on remaining 50%
                sig.trade_status = "BREAKEVEN_EXIT"

        return sig.trade_status
