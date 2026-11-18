"""18 Nov 2026: `m7cap160`, the Card's price range capped at 1.60, pre-registered
on the pool replay and the football-data seasons (claude/card-m7cap160-2026-11-18.md).
A variant only: live keeps CARD_ODDS (1.15, 1.90)."""
import os, sys, unittest
from unittest import mock
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as R


def leg(odds, model=0.66):
    return {"pick": "A", "sport": "football", "code": "en.1", "odds": odds, "fair": round(1 / odds * 0.95, 3),
            "pModel": model, "pTested": model, "hit": model, "why": None, "opp": 5.0, "draw": 4.0, "est": False}


class Cap160(unittest.TestCase):
    def test_registered_on_the_pool(self):
        self.assertEqual(R.VARIANTS["m7cap160"], {"CARD_ODDS": (1.15, 1.60)})
        self.assertNotIn("m7cap160", R.RULE6_FAMILY)
        self.assertTrue(R.spans("m7cap160"))   # live machinery, two-day groups like live

    def test_registered_on_football_data(self):
        src = open(os.path.join(HERE, "tools", "card_legs_history.py"), encoding="utf-8").read()
        self.assertIn('"m7cap160"', src)

    def test_live_unchanged(self):
        self.assertEqual(G.CARD_ODDS, (1.15, 1.90))
        self.assertIsNone(G.model_fault(leg(1.80)))

    def test_the_cap_refuses_a_long_leg(self):
        with mock.patch.object(G, "CARD_ODDS", R.VARIANTS["m7cap160"]["CARD_ODDS"]):
            self.assertIn("outside", G.model_fault(leg(1.80)))
            self.assertIsNone(G.model_fault(leg(1.55)))


if __name__ == "__main__":
    unittest.main()
