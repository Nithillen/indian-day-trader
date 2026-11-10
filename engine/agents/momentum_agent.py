"""Agent 2: Volume & Momentum Specialist (Supertrend, RVOL, EMA)."""

from typing import Dict, Any
import numpy as np
import pandas as pd


class MomentumAgent:
    """Specializes in Supertrend (10, 3), Relative Volume (RVOL), and Moving Average velocity."""

    def __init__(self):
        self.name = "Volume & Momentum Specialist"

    def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        close = df["Close"]
        vol = df["Volume"]

        curr_c = float(close.iloc[-1])
        ema9 = float(close.ewm(span=9, adjust=False).mean().iloc[-1])
        ema21 = float(close.ewm(span=21, adjust=False).mean().iloc[-1])

        # Relative Volume (RVOL) compared to 20-period moving average
        avg_vol = float(vol.tail(20).mean())
        curr_vol = float(vol.iloc[-1])
        rvol = round(curr_vol / max(avg_vol, 1.0), 2)

        # Basic Supertrend proxy
        hl2 = (df["High"] + df["Low"]) / 2.0
        tr = (df["High"] - df["Low"]).ewm(span=10).mean()
        supertrend_lower = float((hl2 - 3.0 * tr).iloc[-1])
        is_supertrend_bullish = curr_c > supertrend_lower

        is_ema_bullish = curr_c > ema9 > ema21

        if is_supertrend_bullish and is_ema_bullish and rvol >= 1.25:
            vote = "BUY"
            confidence = 90
            reason = f"High velocity breakout confirmed: RVOL is {rvol}x average, EMA 9 > 21 stack active, Supertrend support solid at ₹{supertrend_lower:,.2f}."
        elif is_supertrend_bullish and curr_c > ema9:
            vote = "BUY"
            confidence = 70
            reason = f"Supertrend bullish with price leading EMA 9. RVOL is {rvol}x."
        else:
            vote = "PASS"
            confidence = 65
            reason = f"Momentum insufficient (RVOL: {rvol}x, EMA alignment weak)."

        return {
            "agent": self.name,
            "vote": vote,
            "confidence": confidence,
            "reasoning": reason,
            "rvol": rvol,
            "supertrend_support": round(supertrend_lower, 2)
        }
