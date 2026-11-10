"""Dalal Street Day Trader - Full Zerodha-Style MarketWatch & Multi-Agent Signals."""

from datetime import datetime, timezone, timedelta
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from engine.market_clock import get_market_phase
from engine.data_provider import get_marketwatch_data, fetch_stock_candles, FULL_NIFTY_UNIVERSE
from engine.tracker import DayTradeTracker

st.set_page_config(
    page_title="Zerodha Kite AI | Dalal Day Trader",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .block-container {
        padding-top: 1.0rem;
        padding-bottom: 2.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-weight: 600;
        font-size: 1.0rem;
        padding: 0px 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_all_marketwatch():
    return get_marketwatch_data()


@st.cache_data(ttl=60)
def load_top_day_signals():
    tracker = DayTradeTracker()
    return tracker.run_morning_scan(top_n=3)


# Top Navigation & Live Ticking IST Clock
phase = get_market_phase()
is_active = phase.get("is_trading_active", False)

h_col1, h_col2 = st.columns([3, 2])
with h_col1:
    st.title("🇮🇳 Zerodha Kite AI · Day Trader")
    st.caption("Live Dalal Street MarketWatch & Multi-Agent Day Trading Intelligence (NSE & BSE)")

with h_col2:
    # JavaScript Real-Time Live Clock (Ticks every second in Indian Standard Time UTC+5:30)
    components.html("""
    <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 10px 18px; display: flex; justify-content: space-between; align-items: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div>
            <div style="font-size: 0.72rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Indian Standard Time (IST)</div>
            <div id="live-ist-clock" style="font-size: 1.5rem; font-weight: 700; color: #00D09C; font-family: monospace;">--:--:-- IST</div>
        </div>
        <div style="text-align: right;">
            <div id="session-badge" style="background: rgba(0, 208, 156, 0.2); color: #00D09C; border: 1px solid #00D09C; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.75rem;">
                MARKET HOURS
            </div>
            <div id="ist-date" style="font-size: 0.75rem; color: #e5e7eb; margin-top: 3px;">--</div>
        </div>
    </div>
    <script>
    function updateIST() {
        const now = new Date();
        const utcMs = now.getTime() + (now.getTimezoneOffset() * 60000);
        const ist = new Date(utcMs + (3600000 * 5.5)); // IST is UTC + 5.5 hours
        const h = String(ist.getHours()).padStart(2, '0');
        const m = String(ist.getMinutes()).padStart(2, '0');
        const s = String(ist.getSeconds()).padStart(2, '0');
        document.getElementById('live-ist-clock').innerText = h + ':' + m + ':' + s + ' IST';
        
        const options = { day: 'numeric', month: 'short', year: 'numeric', weekday: 'short' };
        document.getElementById('ist-date').innerText = ist.toLocaleDateString('en-IN', options);

        // Session status check
        const hour = ist.getHours();
        const min = ist.getMinutes();
        const timeNum = hour * 60 + min;
        const badge = document.getElementById('session-badge');
        if (timeNum >= 540 && timeNum < 555) {
            badge.innerText = 'PRE-MARKET AUCTION';
            badge.style.color = '#FFAA00';
            badge.style.borderColor = '#FFAA00';
        } else if (timeNum >= 555 && timeNum <= 915) {
            badge.innerText = 'LIVE NSE TRADING';
            badge.style.color = '#00D09C';
            badge.style.borderColor = '#00D09C';
        } else if (timeNum > 915 && timeNum <= 930) {
            badge.innerText = 'SQUARE-OFF WINDOW';
            badge.style.color = '#FF4B4B';
            badge.style.borderColor = '#FF4B4B';
        } else {
            badge.innerText = 'POST-MARKET CLOSED';
            badge.style.color = '#9ca3af';
            badge.style.borderColor = '#4b5563';
        }
    }
    setInterval(updateIST, 1000);
    updateIST();
    </script>
    """, height=82)

# Session Guidance Banner
st.info(f"**NSE Session Directive ({phase['phase']}):** {phase['title']} — {phase.get('action_guidance', phase['message'])}")

# Sidebar Controls
st.sidebar.title("Zerodha Kite Console")
if st.sidebar.button("🔄 Refresh Market Feeds", use_container_width=True, type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Exchange:** National Stock Exchange (NSE)")
st.sidebar.markdown("**Trading Window:** 09:15 AM - 03:15 PM IST")
st.sidebar.markdown("**Mandatory Square-off:** 03:15 PM IST")
st.sidebar.markdown("**Statutory Taxes:** STT (0.025%), GST (18%), Stamp Duty")

# Tabs Layout
tab_marketwatch, tab_signals, tab_chart, tab_tax = st.tabs([
    "📊 Zerodha MarketWatch (All Nifty Stocks)",
    "⚡ Multi-Agent Day Trading Picks (Buy & Sell)",
    "📈 Technical Chart & Deep Dive",
    "🧾 Brokerage & STT Calculator"
])


# TAB 1: ZERODHA MARKETWATCH
with tab_marketwatch:
    st.subheader("📊 Live Dalal Street MarketWatch")
    st.caption("Real-time watchlist across major Nifty 50 constituents with live percentage change and day trading setup triggers.")

    mw_data = load_all_marketwatch()
    df_mw = pd.DataFrame(mw_data)

    # Filter controls
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search_query = st.text_input("🔍 Search Stock or Sector (e.g. Reliance, Bank, Auto, Tata)", "")
    with f_col2:
        sector_filter = st.selectbox(
            "Filter by Sector",
            ["All Sectors"] + sorted(list(set(r["Sector"] for r in mw_data)))
        )

    # Apply filters
    filtered_df = df_mw.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Symbol"].str.contains(search_query, case=False) |
            filtered_df["Company"].str.contains(search_query, case=False) |
            filtered_df["Sector"].str.contains(search_query, case=False)
        ]
    if sector_filter != "All Sectors":
        filtered_df = filtered_df[filtered_df["Sector"] == sector_filter]

    # Display MarketWatch Table
    display_cols = ["Symbol", "Company", "Sector", "LTP (₹)", "Change (₹)", "Change %", "Day High", "Day Low", "Signal"]
    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        hide_index=True,
        height=520
    )

    # Quick Summary stats
    g1, g2, g3 = st.columns(3)
    gainers = len([r for r in mw_data if r["_raw_pct"] > 0])
    losers = len([r for r in mw_data if r["_raw_pct"] < 0])
    g1.metric("Market Breadth", f"{gainers} Advances / {losers} Declines", f"+{round((gainers/len(mw_data))*100)}% Bullish")
    g2.metric("Top Gainer", f"{mw_data[0]['Symbol']} ({mw_data[0]['Change %']})", mw_data[0]["LTP (₹)"])
    g3.metric("Top Volume Sector", "Banking & Financials", "Active Institutional Flows")


# TAB 2: MULTI-AGENT DAY TRADING SIGNALS
with tab_signals:
    st.subheader("⚡ Multi-Agent Day Trading Action Cards")
    st.caption("Consensus trade plans generated by 5 specialized agents. Gives exact Buy Trigger, Stop-Loss, Target 1, Target 2, and step-by-step Sell rules.")

    signals = load_top_day_signals()

    if not signals:
        st.warning("The Multi-Agent Council did not detect high-conviction breakout setups meeting strict 1:1.4+ risk/reward right now. Capital preservation comes first.")
    else:
        for idx, sig in enumerate(signals, 1):
            with st.container(border=True):
                # Header row
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {idx}. {sig.company_name} (`{sig.symbol}`)")
                    st.caption(f"Sector: **{sig.sector}** | Current Reference: **₹{sig.current_price:,.2f}**")
                with c2:
                    st.success(f"★ Consensus Score: **{sig.consensus_score}/100**")

                # The 4 Main Day-Trading Price Badges
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💰 Buy Trigger", f"₹{sig.buy_trigger_price:,.2f}", "Enter only above this")
                m2.metric("🛑 Hard Stop Loss", f"₹{sig.stop_loss_price:,.2f}", "Max loss limit", delta_color="inverse")
                m3.metric("🎯 Target 1 (Sell 50%)", f"₹{sig.target_1_price:,.2f}", "Move SL to cost")
                m4.metric("🚀 Target 2 (Runner)", f"₹{sig.target_2_price:,.2f}", "Sell remaining 50%")

                st.divider()

                # Sizing & Statutory Taxes
                d1, d2, d3, d4 = st.columns(4)
                d1.markdown(f"**Recommended Sizing:** `{sig.recommended_shares} shares`")
                d2.markdown(f"**Capital Required:** `₹{sig.capital_required_inr:,.2f}`")
                d3.markdown(f"**Risk/Reward Ratio:** `1:{sig.reward_to_risk_ratio}`")
                d4.markdown(f"**Taxes & STT Buffer:** `+₹{sig.breakeven_cost_per_share:,.2f}/share`")

                st.write("")

                # When to Buy & When to Sell
                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    st.success(f"**🟢 When & How to Buy:**\n\n{sig.when_to_buy}")
                with act_col2:
                    st.warning(f"**🔴 When & How to Sell:**\n\n{sig.when_to_sell}")

                # Trailing Stop & Exit Cutoff
                st.error(
                    f"**⏰ Mandatory Time Exit:** {sig.mandatory_time_exit}\n\n"
                    f"**🛡️ Trailing Stop Rule:** {sig.trailing_stop_rule}"
                )

                # Expandable Multi-Agent Debate
                with st.expander(f"🎙️ View Multi-Agent Council Debate Transcript ({sig.symbol})"):
                    for ag_name, debate_txt in sig.agent_debates.items():
                        clean_name = ag_name.split("_", 1)[1] if "_" in ag_name else ag_name
                        st.markdown(f"- **{clean_name.replace('_', ' ')}**: {debate_txt}")


# TAB 3: CHART DEEP DIVE
with tab_chart:
    st.subheader("📈 Stock Technical Deep Dive")
    st.caption("Inspect candlestick patterns, Supertrend, moving averages, and support levels for any NSE equity.")

    selected_stock = st.selectbox("Select NSE Stock to Inspect", list(FULL_NIFTY_UNIVERSE.keys()), index=0)
    stock_info = FULL_NIFTY_UNIVERSE[selected_stock]

    df_stock = fetch_stock_candles(stock_info["ticker"], days=30)
    if not df_stock.empty:
        # Calculate moving averages
        df_stock["EMA 20"] = df_stock["Close"].ewm(span=20, adjust=False).mean()
        df_stock["EMA 50"] = df_stock["Close"].ewm(span=50, adjust=False).mean()

        p1, p2, p3 = st.columns(3)
        curr_p = float(df_stock["Close"].iloc[-1])
        prev_p = float(df_stock["Close"].iloc[-2]) if len(df_stock) >= 2 else curr_p
        diff_p = round(curr_p - prev_p, 2)
        diff_pct = round((diff_p / prev_p) * 100, 2) if prev_p > 0 else 0.0

        p1.metric(f"{stock_info['name']} LTP", f"₹{curr_p:,.2f}", f"{'+' if diff_p>=0 else ''}{diff_p} ({diff_pct}%)")
        p2.metric("20 EMA Support", f"₹{float(df_stock['EMA 20'].iloc[-1]):,.2f}")
        p3.metric("50 EMA Support", f"₹{float(df_stock['EMA 50'].iloc[-1]):,.2f}")

        st.line_chart(df_stock[["Close", "EMA 20", "EMA 50"]])
        st.caption("Price (Close) vs 20 EMA and 50 EMA")


# TAB 4: BROKERAGE & TAX CALCULATOR
with tab_tax:
    st.subheader("🧾 Zerodha Brokerage & Indian Statutory Taxes Calculator")
    st.caption("Calculate exact NSE statutory deductions (STT, GST, Stamp Duty, SEBI turnover) and post-tax net profit.")

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        calc_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=1285.0, step=10.0)
    with tc2:
        calc_sell = st.number_input("Sell Price (₹)", min_value=1.0, value=1310.0, step=10.0)
    with tc3:
        calc_qty = st.number_input("Shares Quantity", min_value=1, value=100, step=10)

    buy_turnover = calc_buy * calc_qty
    sell_turnover = calc_sell * calc_qty
    turnover = buy_turnover + sell_turnover

    brokerage = min(40.0, turnover * 0.0003)
    stt = sell_turnover * 0.00025
    nse_charges = turnover * 0.0000297
    sebi_fee = turnover * 0.000001
    stamp_duty = buy_turnover * 0.00003
    gst = (brokerage + nse_charges + sebi_fee) * 0.18
    total_tax = round(brokerage + stt + nse_charges + sebi_fee + stamp_duty + gst, 2)

    gross_pnl = round(sell_turnover - buy_turnover, 2)
    net_pnl = round(gross_pnl - total_tax, 2)
    be_diff = round(total_tax / calc_qty, 2)

    st.divider()
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Gross Profit", f"₹{gross_pnl:,.2f}")
    res2.metric("Total Statutory Taxes", f"₹{total_tax:,.2f}")
    res3.metric("Net In-Pocket Profit", f"₹{net_pnl:,.2f}", delta="Net Gain" if net_pnl>0 else "Loss")
    res4.metric("Breakeven Price", f"₹{calc_buy + be_diff:,.2f}", f"+₹{be_diff}/sh covers taxes")

    with st.expander("Itemized Tax Breakdown (Zerodha Model)"):
        st.write(f"- **Brokerage:** ₹{brokerage:,.2f}")
        st.write(f"- **STT (Securities Transaction Tax):** ₹{stt:,.2f}")
        st.write(f"- **Exchange Transaction Charges (NSE):** ₹{nse_charges:,.2f}")
        st.write(f"- **SEBI Turnover Fee:** ₹{sebi_fee:,.2f}")
        st.write(f"- **Stamp Duty:** ₹{stamp_duty:,.2f}")
        st.write(f"- **GST (18%):** ₹{gst:,.2f}")
