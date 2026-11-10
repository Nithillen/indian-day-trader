#!/usr/bin/env python3
"""Dalal Street Day Trader - Terminal Command Line & Live HUD."""

import argparse
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.market_clock import get_market_phase
from engine.tracker import DayTradeTracker

console = Console()


def render_banner():
    banner = Text(
        "╔═════════════════════════════════════════════════════════════════════════╗\n"
        "║       🇮🇳 DALAL STREET MORNING DAY TRADER (MULTI-AGENT CONSENSUS)        ║\n"
        "║            Autonomous Morning Analysis & Day Trading Signals            ║\n"
        "╚═════════════════════════════════════════════════════════════════════════╝",
        style="bold cyan"
    )
    console.print(banner)


def render_market_status():
    phase_info = get_market_phase()
    is_active = phase_info.get("is_trading_active", False)
    color = "green" if is_active else "yellow"

    p_text = (
        f"[bold {color}]SESSION PHASE: {phase_info['title']}[/bold {color}]\n"
        f"• Status: {phase_info['message']}\n"
        f"• Strategy Directive: [bold white]{phase_info.get('action_guidance', 'Awaiting open.')}[/bold white]"
    )
    console.print(Panel(p_text, title="⏰ NSE/BSE Market Clock (IST)", border_style=color))


def display_signal_card(sig):
    color = "green"
    card_text = (
        f"[bold white]{sig.company_name} ({sig.symbol})[/bold white] | Sector: [cyan]{sig.sector}[/cyan] | Current: [yellow]₹{sig.current_price:,.2f}[/yellow]\n"
        f"Consensus Score: [bold green]{sig.consensus_score}/100[/bold green] (Approved by Multi-Agent Council)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 [bold green]BUY TRIGGER PRICE:[/bold green]   [bold white]₹{sig.buy_trigger_price:,.2f}[/bold white] (Enter only when price breaks above)\n"
        f"🛑 [bold red]HARD STOP-LOSS:[/bold red]      [bold white]₹{sig.stop_loss_price:,.2f}[/bold white] (Max loss risk per trade)\n"
        f"🎯 [bold green]PROFIT TARGET 1:[/bold green]     [bold white]₹{sig.target_1_price:,.2f}[/bold white] (Take 50% profit; move SL to cost)\n"
        f"🚀 [bold green]PROFIT TARGET 2:[/bold green]     [bold white]₹{sig.target_2_price:,.2f}[/bold white] (Take remaining 50% profit)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• Suggested Sizing:    [bold yellow]{sig.recommended_shares} shares[/bold yellow] (Capital: ₹{sig.capital_required_inr:,.2f})\n"
        f"• Max Risk Budget:     ₹{sig.max_risk_inr:,.2f} | Risk/Reward: [bold cyan]1:{sig.reward_to_risk_ratio}[/bold cyan]\n"
        f"• Indian Taxes Buffer: +₹{sig.breakeven_cost_per_share:,.2f}/share covers all STT & GST charges\n\n"
        f"[bold cyan]HOW & WHEN TO BUY:[/bold cyan]\n"
        f"{sig.when_to_buy}\n\n"
        f"[bold cyan]HOW & WHEN TO SELL:[/bold cyan]\n"
        f"{sig.when_to_sell}\n\n"
        f"[bold yellow]TRAILING STOP-LOSS RULE:[/bold yellow]\n"
        f"{sig.trailing_stop_rule}\n\n"
        f"[bold red]MANDATORY SQUARE-OFF CUTOFF:[/bold red]\n"
        f"{sig.mandatory_time_exit}\n\n"
        f"[bold magenta]MULTI-AGENT COUNCIL DEBATE TRANSCRIPT:[/bold magenta]\n"
    )

    for ag_name, debate in sig.agent_debates.items():
        card_text += f"  • [bold white]{ag_name.replace('_', ' ')}:[/bold white] {debate}\n"

    console.print(Panel(card_text, title=f"⚡ DAY TRADE ACTION CARD: {sig.symbol}", border_style=color))


def run_scan():
    render_banner()
    render_market_status()

    tracker = DayTradeTracker()
    with console.status("[bold cyan]5 Specialized Agents debating and scanning top NSE stocks...[/bold cyan]"):
        picks = tracker.run_morning_scan(top_n=3)

    if not picks:
        console.print("[yellow]Council did not find high-conviction (>80 consensus) setups matching today's strict criteria. Cash is a valid position.[/yellow]")
        return

    console.print(f"\n[bold green]🏆 TOP {len(picks)} CONSENSUS DAY-TRADING PICKS FOR TODAY:[/bold green]\n")
    for pick in picks:
        display_signal_card(pick)


def watch_mode(interval_sec: int = 60):
    """Continuously monitors signals on laptop screen."""
    tracker = DayTradeTracker()
    console.clear()
    picks = tracker.run_morning_scan(top_n=3)

    try:
        while True:
            console.clear()
            render_banner()
            render_market_status()
            console.print("[italic cyan]• LIVE MONITORING MODE: Keeping watch on Dalal Street triggers... (Press Ctrl+C to stop)[/italic cyan]\n")

            for pick in picks:
                display_signal_card(pick)

            time.sleep(interval_sec)
    except KeyboardInterrupt:
        console.print("\n[yellow]Watch mode stopped. Happy Trading![/yellow]")


def main():
    parser = argparse.ArgumentParser(description="Dalal Street Morning Day Trader")
    parser.add_argument("--watch", action="store_true", help="Keep live HUD open and auto-refresh on your laptop")
    parser.add_argument("--interval", type=int, default=60, help="Refresh interval in seconds for watch mode")
    args = parser.parse_args()

    if args.watch:
        watch_mode(interval_sec=args.interval)
    else:
        run_scan()


if __name__ == "__main__":
    main()
