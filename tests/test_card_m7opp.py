"""15 Nov 2026: model_fault (the Card's rule 7+) reads CARD_MODEL_OPP_MIN, so
the replay can put rule 6's opposition condition on the model's own picks
(m7opp9, m7opp5). Live is empty, so the live Card is unchanged."""
import os, sys, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as R


def leg(opp, sport="football"):
    l = {"event": "a v b", "pick": "a", "sport": sport, "comp": "c", "odds": 1.40, "p": 0.76, "pModel": 0.76,
         "when": "2026-11-15T15:00:00Z", "est": False, "margin": 1.0, "date": "2026-11-15", "code": "en.1", "opp": opp}
    return G.honest(l)


class M7Opp(unittest.TestCase):
    def setUp(self): self.saved = G.CARD_MODEL_OPP_MIN

    def tearDown(self): G.CARD_MODEL_OPP_MIN = self.saved

    def test_live_reads_no_opposition_floor(self):
        self.assertEqual(G.CARD_MODEL_OPP_MIN, {})
        self.assertIsNone(G.model_fault(leg(4.5)))
        self.assertIsNone(G.model_fault(leg(None)))

    def test_floor_refuses_short_opposition(self):
        G.CARD_MODEL_OPP_MIN = {"football": 9.0}
        self.assertIn("opposition is priced 4.50, under 9", G.model_fault(leg(4.5)))
        self.assertIsNone(G.model_fault(leg(9.0)))
        self.assertIn("no bookmaker price for the opposition", G.model_fault(leg(None)))

    def test_floor_is_football_only(self):
        G.CARD_MODEL_OPP_MIN = {"football": 9.0}
        self.assertIsNone(G.model_fault(leg(2.0, sport="nba")))

    def test_registered(self):
        self.assertEqual(R.VARIANTS["m7opp9"], {"CARD_MODEL_OPP_MIN": {"football": 9.0}})
        self.assertEqual(R.VARIANTS["m7opp5"], {"CARD_MODEL_OPP_MIN": {"football": 5.0}})
        self.assertNotIn("m7opp9", R.RULE6_FAMILY)
        src = open(os.path.join(HERE, "tools", "card_legs_history.py")).read()
        self.assertIn('"m7opp9", "m7opp5"', src)

    def test_replay_restores_live(self):
        R.build([leg(4.5)], "2026-11-15", "m7opp9")
        self.assertEqual(G.CARD_MODEL_OPP_MIN, {})


if __name__ == "__main__":
    unittest.main()
