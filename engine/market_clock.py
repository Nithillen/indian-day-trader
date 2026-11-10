"""Dalal Street Market Clock & Trading Session Phases strictly in Indian Standard Time (IST)."""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Fixed Indian Standard Time timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def get_ist_now() -> datetime:
    """Get current datetime strictly in Indian Standard Time (IST)."""
    return datetime.now(IST)


def get_market_phase() -> Dict[str, Any]:
    """Determine current NSE/BSE market phase strictly in Indian Standard Time (IST)."""
    now = get_ist_now()
    weekday = now.weekday()

    if weekday >= 5:
        return {
            "is_trading_active": False,
            "phase": "WEEKEND",
            "title": "Weekend (Market Closed)",
            "message": "National Stock Exchange is closed for the weekend.",
            "next_open": "Monday at 09:00 AM IST (Pre-Market)",
            "ist_time": now.strftime("%H:%M:%S IST"),
            "ist_date": now.strftime("%d %b %Y")
        }

    curr_time = now.time()

    t_0900 = datetime.strptime("09:00:00", "%H:%M:%S").time()
    t_0908 = datetime.strptime("09:08:00", "%H:%M:%S").time()
    t_0915 = datetime.strptime("09:15:00", "%H:%M:%S").time()
    t_0945 = datetime.strptime("09:45:00", "%H:%M:%S").time()
    t_1130 = datetime.strptime("11:30:00", "%H:%M:%S").time()
    t_1330 = datetime.strptime("13:30:00", "%H:%M:%S").time()
    t_1515 = datetime.strptime("15:15:00", "%H:%M:%S").time()
    t_1530 = datetime.strptime("15:30:00", "%H:%M:%S").time()

    ist_str = now.strftime("%H:%M:%S IST")
    ist_date_str = now.strftime("%d %b %Y")

    if curr_time < t_0900:
        return {
            "is_trading_active": False,
            "phase": "PRE_SESSION",
            "title": "Pre-Market Opening Soon",
            "message": "NSE Pre-open auction begins at 09:00 AM IST.",
            "action_guidance": "Review multi-agent morning watchlists.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_0900 <= curr_time < t_0908:
        return {
            "is_trading_active": False,
            "phase": "PRE_MARKET_AUCTION",
            "title": "⚡ Pre-Market Auction (9:00 - 9:08 AM IST)",
            "message": "Orders collecting for opening price discovery.",
            "action_guidance": "Agents analyzing gap-up/gap-down candidates.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_0908 <= curr_time < t_0915:
        return {
            "is_trading_active": False,
            "phase": "ORDER_MATCHING",
            "title": "Pre-Market Matching (9:08 - 9:15 AM IST)",
            "message": "Opening prices matching. Regular trading starts in moments.",
            "action_guidance": "Finalize opening breakout triggers.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_0915 <= curr_time < t_0945:
        return {
            "is_trading_active": True,
            "phase": "OPENING_ORB_WINDOW",
            "title": "⚡ PRIME TIME: Opening Range Window (9:15 - 9:45 AM IST)",
            "message": "Establishing 15m/30m high-low ranges. Highest volatility of the day.",
            "action_guidance": "Prepare to enter when stocks break ORB highs with volume surge.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_0945 <= curr_time < t_1130:
        return {
            "is_trading_active": True,
            "phase": "MORNING_EXPANSION",
            "title": "🚀 Morning Trend Expansion (9:45 - 11:30 AM IST)",
            "message": "Breakouts expanding towards Target 1. Trend continuation phase.",
            "action_guidance": "Take 50% profit at Target 1 and trail stop-loss to cost.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_1130 <= curr_time < t_1330:
        return {
            "is_trading_active": True,
            "phase": "MIDDAY_LULL",
            "title": "☕ Midday Consolidation (11:30 AM - 1:30 PM IST)",
            "message": "European pre-open lull. Range-bound price action typical.",
            "action_guidance": "Do not chase new trades. Protect morning profits with trailing stops.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_1330 <= curr_time < t_1515:
        return {
            "is_trading_active": True,
            "phase": "AFTERNOON_POWER_HOUR",
            "title": "🔥 Afternoon Power Hour (1:30 - 3:15 PM IST)",
            "message": "European open and institutional closing flows active.",
            "action_guidance": "Target 2 runner exits. Tighten stops.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    elif t_1515 <= curr_time <= t_1530:
        return {
            "is_trading_active": False,
            "phase": "MANDATORY_SQUARE_OFF",
            "title": "⚠️ MANDATORY INTRADAY SQUARE-OFF (3:15 - 3:30 PM IST)",
            "message": "Brokers initiate auto-squareoff. Exit all intraday positions immediately.",
            "action_guidance": "SELL ALL REMAINING INTRADAY POSITIONS NOW.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
    else:
        return {
            "is_trading_active": False,
            "phase": "POST_MARKET",
            "title": "Market Closed (Post 3:30 PM IST)",
            "message": "NSE session ended. Journal results and review trade performance.",
            "action_guidance": "Review realized day-trading P&L.",
            "ist_time": ist_str,
            "ist_date": ist_date_str
        }
