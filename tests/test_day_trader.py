"""Unit tests for Indian Day Trader Multi-Agent Consensus System."""

import unittest
from engine.data_provider import fetch_stock_candles, get_market_status
from engine.market_clock import get_market_phase
from engine.agents.orb_agent import ORBAgent
from engine.agents.momentum_agent import MomentumAgent
from engine.agents.mean_reversion_agent import MeanReversionAgent
from engine.agents.sector_flow_agent import SectorFlowAgent
from engine.agents.risk_gatekeeper_agent import RiskGatekeeperAgent
from engine.agents.consensus_moderator import ConsensusModerator
from engine.tracker import DayTradeTracker


class TestIndianDayTrader(unittest.TestCase):

    def setUp(self):
        self.df = fetch_stock_candles("RELIANCE.NS", days=30)

    def test_market_clock(self):
        phase = get_market_phase()
        self.assertIn("phase", phase)
        self.assertIn("title", phase)

    def test_data_provider(self):
        self.assertFalse(self.df.empty)
        self.assertGreaterEqual(len(self.df), 10)
        self.assertIn("Close", self.df.columns)

    def test_orb_agent(self):
        agent = ORBAgent()
        res = agent.evaluate("RELIANCE.NS", self.df)
        self.assertIn("vote", res)
        self.assertIn(res["vote"], ["BUY", "PASS"])

    def test_momentum_agent(self):
        agent = MomentumAgent()
        res = agent.evaluate("RELIANCE.NS", self.df)
        self.assertIn("rvol", res)
        self.assertIn(res["vote"], ["BUY", "PASS"])

    def test_mean_reversion_agent(self):
        agent = MeanReversionAgent()
        res = agent.evaluate("RELIANCE.NS", self.df)
        self.assertIn("rsi", res)
        self.assertIn(res["vote"], ["BUY", "PASS"])

    def test_sector_flow_agent(self):
        agent = SectorFlowAgent()
        res = agent.evaluate("RELIANCE.NS", "Energy / Oil & Gas")
        self.assertEqual(res["vote"], "BUY")

    def test_risk_gatekeeper_agent(self):
        agent = RiskGatekeeperAgent()
        res = agent.evaluate("RELIANCE.NS", 1285.0, 18.0)
        self.assertIn("entry_trigger", res)
        self.assertIn("stop_loss", res)
        self.assertIn("target_1", res)
        self.assertGreater(res["target_1"], res["entry_trigger"])
        self.assertLess(res["stop_loss"], res["entry_trigger"])

    def test_consensus_moderator(self):
        moderator = ConsensusModerator()
        signal = moderator.evaluate_stock("RELIANCE.NS", "Reliance Industries", "Energy / Oil & Gas", self.df)
        if signal:
            self.assertEqual(signal.action, "INTRADAY_BUY")
            self.assertGreater(signal.consensus_score, 50)
            self.assertTrue(len(signal.agent_debates) >= 5)

    def test_tracker_workflow(self):
        tracker = DayTradeTracker()
        picks = tracker.run_morning_scan(top_n=2)
        self.assertIsInstance(picks, list)
        if picks:
            first = picks[0]
            st = tracker.update_signal_status(first.symbol, first.buy_trigger_price + 5.0)
            self.assertIn(st, ["TRIGGERED_ACTIVE", "TARGET_1_HIT", "TARGET_2_HIT"])


if __name__ == "__main__":
    unittest.main()
