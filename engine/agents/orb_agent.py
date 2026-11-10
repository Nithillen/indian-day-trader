"""Agent 1: Opening Range Breakout (ORB) & Price Action Specialist."""

from typing import Dict, Any
import pandas as pd


class ORBAgent:
    """Analyzes the opening 15m/30m high-low range and candle patterns."""

    def __init__(self):
        self.name = "Price Action & ORB Specialist"

    def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        curr = df.iloc[-1]
        prev = df.iloc[-2]

        curr_close = float(curr["Close"])
        curr_high = float(curr["High"])
        curr_low = float(curr["Low"])
        open_price = float(curr["Open"])

        # Range and body calculation
        candle_range = curr_high - curr_low
        body = abs(curr_close - open_price)
        body_ratio = body / max(candle_range, 0.01)

        is_green = curr_close >= open_price
        near_high = (curr_high - curr_close) / max(candle_range, 0.01) < 0.25

        if is_green and near_high and body_ratio > 0.55:
            vote = "BUY"
            confidence = 85
            reason = f"Bullish opening momentum candle. Closing near session high (₹{curr_close:,.2f}) with wide green body ({round(body_ratio*100)}% of range)."
        elif is_green:
            vote = "BUY"
            confidence = 65
            reason = f"Moderate bullish opening candle, trading above open."
        else:
            vote = "PASS"
            confidence = 75
            reason = f"Bearish or indecisive candle action (Close: ₹{curr_close:,.2f} < Open: ₹{open_price:,.2f}). Opening range not broken."

        return {
            "agent": self.name,
            "vote": vote,
            "confidence": confidence,
            "reasoning": reason,
            "orb_high": round(curr_high, 2),
            "orb_low": round(curr_low, 2)
        }
