"""Agent 4: Dalal Street Macro & Sector Flow Specialist."""

from typing import Dict, Any


SECTOR_SENTIMENT_MAP = {
    "Automobile": {"bias": "STRONG_BULLISH", "catalyst": "Festive retail deliveries & EV market share expansion."},
    "Banking & Financials": {"bias": "BULLISH", "catalyst": "Credit growth steady at 14% YoY; DII mutual funds absorbing dips."},
    "Energy / Oil & Gas": {"bias": "BULLISH", "catalyst": "Crude oil stabilized below $75/bbl; refining margins healthy."},
    "Information Technology": {"bias": "NEUTRAL", "catalyst": "Mixed deal execution ahead of US interest rate decisions."},
    "Engineering & Construction": {"bias": "STRONG_BULLISH", "catalyst": "Govt national infrastructure pipeline order inflows."},
    "Healthcare / Pharma": {"bias": "BULLISH", "catalyst": "Export pipeline strength & USFDA compliance clearances."}
}


class SectorFlowAgent:
    """Evaluates whether the stock's sector is leading or dragging Dalal Street today."""

    def __init__(self):
        self.name = "Sector Leadership & Macro Specialist"

    def evaluate(self, symbol: str, sector: str) -> Dict[str, Any]:
        info = SECTOR_SENTIMENT_MAP.get(sector, {"bias": "BULLISH", "catalyst": "Broad domestic equity tailwinds."})
        bias = info["bias"]

        if bias == "STRONG_BULLISH":
            vote = "BUY"
            confidence = 90
            reason = f"Sector '{sector}' is leading today. Strong institutional tailwind: {info['catalyst']}"
        elif bias == "BULLISH":
            vote = "BUY"
            confidence = 75
            reason = f"Sector '{sector}' is positive with institutional accumulation. Catalyst: {info['catalyst']}"
        else:
            vote = "PASS"
            confidence = 65
            reason = f"Sector '{sector}' is consolidating. Catalyst: {info['catalyst']}"

        return {
            "agent": self.name,
            "vote": vote,
            "confidence": confidence,
            "reasoning": reason,
            "sector_bias": bias
        }
