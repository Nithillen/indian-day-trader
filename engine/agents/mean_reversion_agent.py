"""Agent 3: Mean Reversion & Volatility Filter (RSI, VWAP & Overbought Guard)."""

from typing import Dict, Any
import numpy as np
import pandas as pd


class MeanReversionAgent:
    """Ensures intraday setups are not dangerously overextended (RSI > 80) and calculates pullback safety."""

    def __init__(self):
        self.name = "Mean Reversion & Volatility Guard"

    def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        close = df["Close"]
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        avg_gain = gain.ewm(span=14, adjust=False).mean()
        avg_loss = loss.ewm(span=14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = float((100 - (100 / (1 + rs))).fillna(50.0).iloc[-1])

        # VWAP approximation
        typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
        vwap = float(((typical * df["Volume"]).cumsum() / df["Volume"].cumsum()).iloc[-1])
        curr_c = float(close.iloc[-1])
        dist_from_vwap_pct = round(((curr_c - vwap) / vwap) * 100, 2)

        if 50.0 <= rsi <= 74.0 and 0.0 <= dist_from_vwap_pct <= 2.8:
            vote = "BUY"
            confidence = 85
            reason = f"Ideal intraday expansion window: RSI is {round(rsi, 1)} (strong trend without exhaustion) and price is comfortably {dist_from_vwap_pct}% above VWAP (₹{vwap:,.2f})."
        elif rsi > 78.0 or dist_from_vwap_pct > 3.8:
            vote = "PASS"
            confidence = 80
            reason = f"Overbought warning: RSI at {round(rsi, 1)} and {dist_from_vwap_pct}% above VWAP. Chasing here risks sudden mean-reversion pullbacks."
        elif rsi < 45.0:
            vote = "PASS"
            confidence = 70
            reason = f"Weak momentum (RSI: {round(rsi, 1)}). Intraday bulls have not taken control."
        else:
            vote = "BUY"
            confidence = 65
            reason = f"Neutral to positive volatility structure (RSI: {round(rsi, 1)})."

        return {
            "agent": self.name,
            "vote": vote,
            "confidence": confidence,
            "reasoning": reason,
            "rsi": round(rsi, 1),
            "vwap": round(vwap, 2),
            "dist_vwap_pct": dist_from_vwap_pct
        }
