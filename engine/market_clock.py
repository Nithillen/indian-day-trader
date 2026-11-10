"""Dalal Street Market Clock & Trading Session Phases (IST)."""

import datetime
from typing import Dict, Any


def get_market_phase() -> Dict[str, Any]:
    """Determine current NSE/BSE market phase in Indian Standard Time (IST)."""
    now = datetime.datetime.now()
    weekday = now.weekday()

    if weekday >= 5:
        return {
            "is_trading_active": False,
            "phase": "WEEKEND",
            "title": "Weekend (Market Closed)",
            "message": "National Stock Exchange is closed for the weekend.",
            "next_open": "Monday at 09:00 AM IST (Pre-Market)"
        }

    curr_time = now.time()

    t_0900 = datetime.time(9, 0)
    t_0908 = datetime.time(9, 8)
    t_0915 = datetime.time(9, 15)
    t_0945 = datetime.time(9, 45)
    t_1130 = datetime.time(11, 30)
    t_1330 = datetime.time(13, 30)
    t_1515 = datetime.time(15, 15)
    t_1530 = datetime.time(15, 30)

    if curr_time < t_0900:
        return {
            "is_trading_active": False,
            "phase": "PRE_SESSION",
            "title": "Pre-Market Opening Soon",
            "message": "Preparing watchlists. Pre-open auction begins at 09:00 AM IST.",
            "action_guidance": "Review multi-agent morning watchlists."
        }
    elif t_0900 <= curr_time < t_0908:
        return {
            "is_trading_active": False,
            "phase": "PRE_MARKET_AUCTION",
            "title": "Pre-Market Auction (9:00 - 9:08 AM)",
            "message": "Orders collecting for opening price discovery.",
            "action_guidance": "Agents analyzing gap-up/gap-down candidates."
        }
    elif t_0908 <= curr_time < t_0915:
        return {
            "is_trading_active": False,
            "phase": "ORDER_MATCHING",
            "title": "Pre-Market Matching (9:08 - 9:15 AM)",
            "message": "Opening prices matching. Regular trading starts in moments.",
            "action_guidance": "Finalize opening breakout triggers."
        }
    elif t_0915 <= curr_time < t_0945:
        return {
            "is_trading_active": True,
            "phase": "OPENING_ORB_WINDOW",
            "title": "⚡ PRIME TIME: Opening Range Window (9:15 - 9:45 AM)",
            "message": "Establishing 15m/30m high-low ranges. Highest volatility of the day.",
            "action_guidance": "Prepare to enter when stocks break ORB highs with volume surge."
        }
    elif t_0945 <= curr_time < t_1130:
        return {
            "is_trading_active": True,
            "phase": "MORNING_EXPANSION",
            "title": "🚀 Morning Trend Expansion (9:45 - 11:30 AM)",
            "message": "Breakouts expanding towards Target 1. Trend continuation phase.",
            "action_guidance": "Take 50% profit at Target 1 and trail stop-loss to cost."
        }
    elif t_1130 <= curr_time < t_1330:
        return {
            "is_trading_active": True,
            "phase": "MIDDAY_LULL",
            "title": "☕ Midday Consolidation (11:30 AM - 1:30 PM)",
            "message": "European pre-open lull. Range-bound price action typical.",
            "action_guidance": "Do not chase new trades. Protect morning profits with trailing stops."
        }
    elif t_1330 <= curr_time < t_1515:
        return {
            "is_trading_active": True,
            "phase": "AFTERNOON_POWER_HOUR",
            "title": "🔥 Afternoon Power Hour (1:30 - 3:15 PM)",
            "message": "European open and institutional closing flows active.",
            "action_guidance": "Target 2 runner exits. Tighten stops."
        }
    elif t_1515 <= curr_time <= t_1530:
        return {
            "is_trading_active": False,
            "phase": "MANDATORY_SQUARE_OFF",
            "title": "⚠️ MANDATORY INTRADAY SQUARE-OFF (3:15 - 3:30 PM)",
            "message": "Brokers initiate auto-squareoff. Exit all intraday positions immediately.",
            "action_guidance": "SELL ALL REMAINING INTRADAY POSITIONS NOW."
        }
    else:
        return {
            "is_trading_active": False,
            "phase": "POST_MARKET",
            "title": "Market Closed (Post 3:30 PM IST)",
            "message": "NSE session ended. Journal results and review trade performance.",
            "action_guidance": "Review realized day-trading P&L."
        }
