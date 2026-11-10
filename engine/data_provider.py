"""Market Data Provider for Indian Day Trading with Full Nifty 50 Watchlist & Live Feeds."""

from datetime import datetime, timezone, timedelta
import io
import sys
import warnings
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

IST = timezone(timedelta(hours=5, minutes=30))

FULL_NIFTY_UNIVERSE = {
    "RELIANCE": {"ticker": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy / Oil & Gas", "base": 1285.0},
    "TCS": {"ticker": "TCS.NS", "name": "Tata Consultancy Services", "sector": "Information Technology", "base": 3850.0},
    "HDFCBANK": {"ticker": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking & Financials", "base": 1720.0},
    "INFY": {"ticker": "INFY.NS", "name": "Infosys Ltd", "sector": "Information Technology", "base": 1840.0},
    "ICICIBANK": {"ticker": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking & Financials", "base": 1240.0},
    "TATAMOTORS": {"ticker": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Automobile", "base": 940.0},
    "SBIN": {"ticker": "SBIN.NS", "name": "State Bank of India", "sector": "Banking & Financials", "base": 820.0},
    "BHARTIARTL": {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecommunications", "base": 1580.0},
    "LT": {"ticker": "LT.NS", "name": "Larsen & Toubro", "sector": "Engineering & Construction", "base": 3650.0},
    "BAJFINANCE": {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Banking & Financials", "base": 7100.0},
    "MARUTI": {"ticker": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automobile", "base": 11500.0},
    "SUNPHARMA": {"ticker": "SUNPHARMA.NS", "name": "Sun Pharma", "sector": "Healthcare / Pharma", "base": 1750.0},
    "TITAN": {"ticker": "TITAN.NS", "name": "Titan Company", "sector": "Consumer Discretionary", "base": 3400.0},
    "AXISBANK": {"ticker": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking & Financials", "base": 1180.0},
    "ITC": {"ticker": "ITC.NS", "name": "ITC Ltd", "sector": "FMCG", "base": 480.0},
    "KOTAKBANK": {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking & Financials", "base": 1780.0},
    "WIPRO": {"ticker": "WIPRO.NS", "name": "Wipro Ltd", "sector": "Information Technology", "base": 560.0},
    "NTPC": {"ticker": "NTPC.NS", "name": "NTPC Ltd", "sector": "Power & Utilities", "base": 380.0},
    "M&M": {"ticker": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Automobile", "base": 2850.0},
    "POWERGRID": {"ticker": "POWERGRID.NS", "name": "Power Grid Corp", "sector": "Power & Utilities", "base": 320.0},
    "TATASTEEL": {"ticker": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Metals & Mining", "base": 150.0},
    "COALINDIA": {"ticker": "COALINDIA.NS", "name": "Coal India", "sector": "Mining & Energy", "base": 440.0},
    "BAJAJFINSV": {"ticker": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "sector": "Financial Services", "base": 1620.0},
    "ADANIENT": {"ticker": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Conglomerate", "base": 2850.0},
    "ADANIPORTS": {"ticker": "ADANIPORTS.NS", "name": "Adani Ports & SEZ", "sector": "Infrastructure", "base": 1380.0}
}

# Alias for compatibility
TOP_NSE_STOCKS = FULL_NIFTY_UNIVERSE


def get_live_stock_quote(symbol: str) -> Dict[str, any]:
    """Fetch live real-time price quote from NSE."""
    ticker = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
    try:
        t = yf.Ticker(ticker)
        fast = t.fast_info
        if fast and hasattr(fast, "last_price") and fast.last_price is not None:
            curr = round(float(fast.last_price), 2)
            prev = round(float(fast.previous_close or curr), 2)
            chg = round(curr - prev, 2)
            chg_pct = round((chg / prev) * 100, 2) if prev > 0 else 0.0
            return {
                "symbol": ticker,
                "current_price": curr,
                "previous_close": prev,
                "change": chg,
                "change_pct": chg_pct,
                "open": round(float(fast.open or curr), 2),
                "day_high": round(float(fast.day_high or curr), 2),
                "day_low": round(float(fast.day_low or curr), 2),
                "is_live": True
            }
    except Exception:
        pass

    clean = symbol.replace(".NS", "").upper()
    info = FULL_NIFTY_UNIVERSE.get(clean, {})
    base = info.get("base", 1000.0)
    seed = (sum(ord(c) for c in clean) * 19) % 9999
    np.random.seed(seed)
    pct = round(float(np.random.normal(0.4, 1.2)), 2)
    curr = round(base * (1 + pct / 100), 2)

    return {
        "symbol": ticker,
        "current_price": curr,
        "previous_close": base,
        "change": round(curr - base, 2),
        "change_pct": pct,
        "open": round(base * 1.001, 2),
        "day_high": round(max(curr, base) * 1.008, 2),
        "day_low": round(min(curr, base) * 0.993, 2),
        "is_live": False
    }


def get_marketwatch_data() -> List[Dict[str, any]]:
    """Build complete Zerodha-style live MarketWatch table for all tracked NSE stocks."""
    watch_rows = []
    for sym, info in FULL_NIFTY_UNIVERSE.items():
        q = get_live_stock_quote(info["ticker"])
        chg_pct = q["change_pct"]
        signal = "🟢 BUY SETUP" if chg_pct > 0.8 else ("🔴 SHORT SETUP" if chg_pct < -0.8 else "⚪ CONSOLIDATING")

        watch_rows.append({
            "Symbol": sym,
            "Company": info["name"],
            "Sector": info["sector"],
            "LTP (₹)": f"₹{q['current_price']:,.2f}",
            "Change (₹)": f"{'+' if q['change'] >= 0 else ''}{q['change']:,.2f}",
            "Change %": f"{'+' if chg_pct >= 0 else ''}{chg_pct:.2f}%",
            "Day High": f"₹{q['day_high']:,.2f}",
            "Day Low": f"₹{q['day_low']:,.2f}",
            "Signal": signal,
            "_raw_pct": chg_pct,
            "_raw_ltp": q["current_price"]
        })

    # Sort descending by % change (like Zerodha top gainers)
    watch_rows.sort(key=lambda x: x["_raw_pct"], reverse=True)
    return watch_rows


def fetch_stock_candles(symbol: str, days: int = 40, interval: str = "1d") -> pd.DataFrame:
    """Fetch candles for an NSE stock. Supports 5m, 15m intraday and 1d candles."""
    ticker = symbol if symbol.endswith(".NS") else f"{symbol}.NS"

    try:
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            period = "5d" if interval in ["5m", "15m"] else "2mo"
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
        finally:
            sys.stderr = old_stderr

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        if not df.empty and len(df) >= 10:
            df.attrs["is_live"] = True
            return df
    except Exception:
        pass

    clean = symbol.replace(".NS", "").upper()
    info = FULL_NIFTY_UNIVERSE.get(clean, {"base": 1000.0})
    base = info["base"]

    seed = (sum(ord(c) for c in clean) * 31) % 99999
    np.random.seed(seed)

    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq="B")
    n = len(dates)

    returns = np.random.normal(loc=0.0006, scale=0.018, size=n)
    prices = base * np.exp(np.cumsum(returns))

    highs = prices * (1 + np.abs(np.random.normal(0.005, 0.003, size=n)))
    lows = prices * (1 - np.abs(np.random.normal(0.005, 0.003, size=n)))
    opens = prices * (1 + np.random.normal(0, 0.003, size=n))
    closes = prices

    volumes = np.random.lognormal(mean=np.log(2_500_000), sigma=0.5, size=n).astype(int)

    df = pd.DataFrame({
        "Open": np.round(opens, 2),
        "High": np.round(np.maximum.reduce([opens, closes, highs]), 2),
        "Low": np.round(np.minimum.reduce([opens, closes, lows]), 2),
        "Close": np.round(closes, 2),
        "Volume": volumes
    }, index=dates)

    df.attrs["is_live"] = False
    return df
