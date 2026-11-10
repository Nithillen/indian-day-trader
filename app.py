"""Dalal Street Morning Day Trader - Laptop Dashboard (Streamlit)."""

import datetime
import streamlit as st
import pandas as pd

from engine.market_clock import get_market_phase
from engine.tracker import DayTradeTracker

st.set_page_config(
    page_title="Dalal Day Trader | AI Morning Signals",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Only clean body styling without scroll-trapping containers)
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def load_morning_signals():
    """Cached scan so dashboard loads instantly without blocking the page."""
    tracker = DayTradeTracker()
    return tracker.run_morning_scan(top_n=3)


# Sidebar controls
st.sidebar.title("🇮🇳 Day Trader Controls")
if st.sidebar.button("🔄 Refresh Market Scan Now", use_container_width=True, type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Strategy:** Pre-Market & Opening Momentum")
st.sidebar.markdown("**Council:** 5 AI Agents + Floor Governor")
st.sidebar.markdown("**Exchange:** National Stock Exchange (NSE)")
st.sidebar.markdown("**Square-off:** 03:15 PM IST Mandatory")

# Header & Market Clock
phase = get_market_phase()
is_active = phase.get("is_trading_active", False)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🇮🇳 Dalal Street Morning Day Trader")
    st.caption("Autonomous Multi-Agent Consensus Intelligence for NSE Day Trading")
with col_h2:
    st.metric(
        label="Market Session (IST)",
        value=datetime.datetime.now().strftime("%H:%M:%S"),
        delta=phase.get("phase", "ACTIVE"),
        delta_color="normal" if is_active else "off"
    )

st.info(f"**Directive:** {phase['title']} — {phase.get('action_guidance', phase['message'])}")

# Load Signals
with st.spinner("Multi-Agent Council analyzing morning setups..."):
    signals = load_morning_signals()

st.subheader(f"🏆 Top High-Conviction Day Trading Picks for Today ({len(signals)} Approved)")
st.caption("Every trade below was independently scrutinized by 5 specialized agents and passed a strict 1:1.4+ risk/reward & Indian statutory tax audit.")

if not signals:
    st.warning("The Multi-Agent Council did not detect any high-probability setups meeting strict criteria right now. Capital preservation comes first.")
else:
    for idx, sig in enumerate(signals, 1):
        with st.container(border=True):
            # Card Header
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.markdown(f"### {idx}. {sig.company_name} (`{sig.symbol}`)")
                st.caption(f"Sector: **{sig.sector}** | Current Reference: **₹{sig.current_price:,.2f}**")
            with head_col2:
                st.success(f"★ Consensus: **{sig.consensus_score}/100**")

            # 4 Key Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 Buy Trigger", f"₹{sig.buy_trigger_price:,.2f}", "Enter above this")
            m2.metric("🛑 Hard Stop Loss", f"₹{sig.stop_loss_price:,.2f}", "Max loss limit", delta_color="inverse")
            m3.metric("🎯 Target 1 (Sell 50%)", f"₹{sig.target_1_price:,.2f}", "Move SL to cost")
            m4.metric("🚀 Target 2 (Runner)", f"₹{sig.target_2_price:,.2f}", "Sell remaining 50%")

            st.divider()

            # Trade Sizing & Breakeven
            d1, d2, d3, d4 = st.columns(4)
            d1.markdown(f"**Recommended Sizing:** `{sig.recommended_shares} shares`")
            d2.markdown(f"**Capital Required:** `₹{sig.capital_required_inr:,.2f}`")
            d3.markdown(f"**Risk/Reward Ratio:** `1:{sig.reward_to_risk_ratio}`")
            d4.markdown(f"**Taxes & STT Buffer:** `+₹{sig.breakeven_cost_per_share:,.2f}/share`")

            st.write("")

            # Action Guidance
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                st.success(f"**🟢 When & How to Buy:**\n\n{sig.when_to_buy}")
            with act_col2:
                st.warning(f"**🔴 When & How to Sell:**\n\n{sig.when_to_sell}")

            # Trailing & Exit Rules
            st.error(
                f"**⏰ Mandatory Time Exit:** {sig.mandatory_time_exit}\n\n"
                f"**🛡️ Trailing Stop Rule:** {sig.trailing_stop_rule}"
            )

            # Multi-Agent Debate Transcript
            with st.expander(f"🎙️ View Multi-Agent Council Debate Transcript ({sig.symbol})"):
                for ag_name, debate_txt in sig.agent_debates.items():
                    clean_name = ag_name.split("_", 1)[1] if "_" in ag_name else ag_name
                    st.markdown(f"- **{clean_name.replace('_', ' ')}**: {debate_txt}")

# Golden Rules
st.divider()
st.subheader("🛡️ The 4 Golden Rules of Indian Day Trading")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Rule 1: Never Anticipate", "Wait for Trigger", "Buy only above trigger")
r2.metric("Rule 2: Free Trade Rule", "Book 50% at Target 1", "Move SL to entry")
r3.metric("Rule 3: Zero Overnight", "Square-off by 3:15 PM", "No overnight gap risk")
r4.metric("Rule 4: Obey Stop Loss", "No Averaging", "Capital defense first")
