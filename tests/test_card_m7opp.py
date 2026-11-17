"""15 Nov 2026: model_fault (the Card's rule 7+) reads CARD_MODEL_OPP_MIN, so
the replay can put rule 6's opposition condition on the model's own picks
(m7opp9, m7opp5). 16 Nov 2026: 5.0 is live (CARD_RULE 12); m7noopp replays rule 11."""
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
        # 16 Nov 2026, CARD_RULE 12: m7opp5 set live; 17 Nov 2026, CARD_RULE 13:
        # emptied again with the value demand (Douglas: "just drop both of those")
        self.assertEqual(G.CARD_MODEL_OPP_MIN, {})
        self.assertGreaterEqual(G.CARD_RULE, 13)
        self.assertIsNone(G.model_fault(leg(4.5)))
        self.assertIsNone(G.model_fault(leg(None)))
        self.assertEqual(R.VARIANTS["rule12"], {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {"football": 5.0}})

    def test_floor_5_as_rule12_ran_it(self):
        G.CARD_MODEL_OPP_MIN = {"football": 5.0}
        self.assertIn("under 5", G.model_fault(leg(4.5)))
        self.assertIsNone(G.model_fault(leg(5.0)))
        self.assertIn("no bookmaker price for the opposition", G.model_fault(leg(None)))
        self.assertIsNone(G.model_fault(leg(2.0, sport="nba")))

    def test_rule11_replayed(self):
        self.assertEqual(R.VARIANTS["m7noopp"], {"CARD_MODEL_OPP_MIN": {}})
        src = open(os.path.join(HERE, "tools", "card_legs_history.py")).read()
        self.assertIn('"m7noopp"', src)

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
        live = dict(G.CARD_MODEL_OPP_MIN)
        R.build([leg(4.5)], "2026-11-15", "m7opp9")
        self.assertEqual(G.CARD_MODEL_OPP_MIN, live)


if __name__ == "__main__":
    unittest.main()
