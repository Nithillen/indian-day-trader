"""Dalal Street Morning Day Trader - Laptop Dashboard (Streamlit)."""

import datetime
import streamlit as st
import pandas as pd
import time

from engine.market_clock import get_market_phase
from engine.tracker import DayTradeTracker

st.set_page_config(
    page_title="Dalal Day Trader | AI Morning Signals",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Trading Styling
st.markdown("""
<style>
    .market-bar {
        background: linear-gradient(90deg, #0b132b 0%, #1c2541 100%);
        border: 1px solid #3a506b;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 20px;
    }
    .signal-card {
        background-color: #0d1b2a;
        border: 1px solid #1b263b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 6px solid #00D09C;
    }
    .price-badge {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
    }
    .buy-box {
        background-color: rgba(0, 208, 156, 0.1);
        border: 1px solid #00D09C;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    .sl-box {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #FF4B4B;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    .t1-box {
        background-color: rgba(0, 180, 216, 0.1);
        border: 1px solid #00B4D8;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    .t2-box {
        background-color: rgba(114, 9, 183, 0.1);
        border: 1px solid #7209B7;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.title("🇮🇳 Day Trader Controls")
auto_refresh = st.sidebar.checkbox("Auto-Refresh Live Feed (Keep open)", value=False)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", min_value=15, max_value=120, value=60)
capital = st.sidebar.number_input("Day Trading Capital (₹ INR)", min_value=25000.0, value=500000.0, step=25000.0)

# Market Phase Status
phase = get_market_phase()
is_active = phase.get("is_trading_active", False)
badge_color = "#00D09C" if is_active else "#FFAA00"

st.markdown(f"""
<div class="market-bar">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; color: #ffffff;">🇮🇳 Dalal Street Morning Day Trader</h2>
            <p style="margin: 4px 0 0 0; color: #8d99ae;">Autonomous Multi-Agent Consensus Intelligence for NSE Day Trading</p>
        </div>
        <div style="text-align: right;">
            <span style="background-color: {badge_color}; color: #000; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">
                {phase['phase']}
            </span>
            <div style="font-size: 0.85rem; color: #edf2f4; margin-top: 4px;">{datetime.datetime.now().strftime('%H:%M:%S IST')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.info(f"**Directive:** {phase['title']} — {phase.get('action_guidance', phase['message'])}")

# Initialize Tracker & Run Scan
tracker = DayTradeTracker()

with st.spinner("Multi-Agent Council debating morning setups..."):
    signals = tracker.run_morning_scan(top_n=3)

st.subheader(f"🏆 Top High-Conviction Day Trading Picks for Today ({len(signals)} Approved)")
st.caption("Only stocks that received at least 4 out of 5 'BUY' votes from the Multi-Agent Council and passed the Risk Gatekeeper audit are shown below.")

if not signals:
    st.warning("The Multi-Agent Council did not detect any high-probability setups meeting strict 1:1.5+ risk-reward and momentum criteria right now. Capital preservation comes first.")
else:
    for sig in signals:
        st.markdown(f"""
        <div class="signal-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div>
                    <h3 style="margin: 0; color: #ffffff;">{sig.company_name} ({sig.symbol})</h3>
                    <span style="color: #48cae4; font-size: 0.9rem;">Sector: {sig.sector}</span>
                </div>
                <div>
                    <span style="background: rgba(0, 208, 156, 0.2); color: #00D09C; border: 1px solid #00D09C; padding: 4px 14px; border-radius: 12px; font-weight: 700;">
                        CONSENSUS SCORE: {sig.consensus_score}/100
                    </span>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;">
                <div class="buy-box">
                    <div style="font-size: 0.8rem; color: #00D09C; font-weight: 600;">BUY TRIGGER PRICE</div>
                    <div class="price-badge">₹{sig.buy_trigger_price:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #aaa;">Enter when price breaks above</div>
                </div>
                <div class="sl-box">
                    <div style="font-size: 0.8rem; color: #FF4B4B; font-weight: 600;">HARD STOP LOSS</div>
                    <div class="price-badge">₹{sig.stop_loss_price:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #aaa;">Cut immediately if touched</div>
                </div>
                <div class="t1-box">
                    <div style="font-size: 0.8rem; color: #00B4D8; font-weight: 600;">TARGET 1 (SELL 50%)</div>
                    <div class="price-badge">₹{sig.target_1_price:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #aaa;">Book half & move SL to cost</div>
                </div>
                <div class="t2-box">
                    <div style="font-size: 0.8rem; color: #B5179E; font-weight: 600;">TARGET 2 (RUNNER EXIT)</div>
                    <div class="price-badge">₹{sig.target_2_price:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #aaa;">Sell remaining 50% shares</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 12px;">
                <div><b>Suggested Size:</b> {sig.recommended_shares} shares</div>
                <div><b>Capital Required:</b> ₹{sig.capital_required_inr:,.2f}</div>
                <div><b>Risk/Reward:</b> 1:{sig.reward_to_risk_ratio}</div>
                <div><b>Tax Breakeven:</b> {sig.breakeven_cost_per_share}/share</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**🟢 When & How to Buy:**\n\n{sig.when_to_buy}")
        with col2:
            st.warning(f"**🔴 When & How to Sell:**\n\n{sig.when_to_sell}")

        st.info(f"**⏰ Trailing Stop & Exit Cutoff:**\n- {sig.trailing_stop_rule}\n- {sig.mandatory_time_exit}")

        with st.expander(f"🎙️ Multi-Agent Council Debate Transcript ({sig.symbol})"):
            for ag, txt in sig.agent_debates.items():
                st.markdown(f"- **{ag.replace('_', ' ')}**: {txt}")

        st.markdown("---")

# Golden Rules Card
st.subheader("🛡️ The 4 Golden Rules of Indian Day Trading")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rule 1: Never Anticipate", "Wait for Trigger", "Buy only above trigger")
c2.metric("Rule 2: Free Trade Rule", "Book 50% at Target 1", "Move SL to cost")
c3.metric("Rule 3: No Overnight Risk", "Square-off by 3:15 PM", "Zero overnight risk")
c4.metric("Rule 4: Obey Stop Loss", "No Averaging Losses", "Protect capital")

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
