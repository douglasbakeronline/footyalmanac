"""The Odds tab's group rules (groupings.py). Standard library only."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

def leg(i, odds, p=0.8, sport="football", comp=None, est=False):
    l = {"event": f"e{i}", "pick": f"p{i}", "sport": sport, "comp": comp or f"c{i}", "odds": odds, "p": p,
         "pModel": p, "when": None, "est": est, "implied": 1 / odds, "edge": p * odds - 1}
    return l

class LegProbability(unittest.TestCase):
    def test_needs_a_tested_sample(self):
        self.assertIsNone(G.leg_p(0.9, {"hit": 0.9, "n": 10}))
        self.assertIsNone(G.leg_p(0.9, None))
    def test_needs_a_tested_rate_of_65(self):
        self.assertIsNone(G.leg_p(0.7, {"hit": 0.6, "n": 500}))
    def test_shrinks_toward_the_model_when_small(self):
        p = G.leg_p(0.70, {"hit": 0.90, "n": 30})
        self.assertAlmostEqual(p, 0.80, places=6)
        self.assertGreater(G.leg_p(0.70, {"hit": 0.90, "n": 3000}), 0.89)

class GroupRules(unittest.TestCase):
    def test_band_and_spread(self):
        good = [leg(0, 1.2), leg(1, 1.35), leg(2, 1.65), leg(3, 1.25), leg(4, 1.4)]
        o = G.ok_combo(good, 4.0, 7.0, "Balanced")
        self.assertIsNotNone(o); self.assertTrue(4.0 <= o <= 7.0)
        no_long = [leg(0, 1.2), leg(1, 1.35), leg(2, 1.55), leg(3, 1.45), leg(4, 1.5)]
        self.assertIsNone(G.ok_combo(no_long, 2.5, 7.0, "Balanced"))
    def test_too_many_very_short_or_estimated(self):
        short = [leg(0, 1.1), leg(1, 1.1), leg(2, 1.12), leg(3, 1.4), leg(4, 2.4)]
        self.assertIsNone(G.ok_combo(short, 2.5, 4.0, "Steady"))
        est = [leg(i, o, est=i < 3) for i, o in enumerate([1.2, 1.35, 1.65, 1.25, 1.4])]
        self.assertIsNone(G.ok_combo(est, 4.0, 7.0, "Balanced"))
        self.assertIsNotNone(G.ok_combo(est, 4.0, 7.0, "Balanced", max_est=5))
    def test_one_competition_at_most_twice(self):
        same = [leg(i, o, comp="X") for i, o in enumerate([1.2, 1.35, 1.65, 1.25, 1.4])]
        self.assertIsNone(G.ok_combo(same, 4.0, 7.0, "Balanced"))
    def test_groups_never_share_a_leg(self):
        import random
        random.seed(3)
        L = [leg(i, round(random.uniform(1.08, 2.4), 2), p=random.uniform(0.66, 0.92), sport=random.choice(["football", "nfl", "tennis"]))
             for i in range(60)]
        from datetime import datetime, timezone
        gs = G.build_day(L, datetime(2000, 1, 1, tzinfo=timezone.utc))
        self.assertTrue(gs)
        seen = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(seen), len(set(seen)))
        for g in gs:
            self.assertEqual(len(g["legs"]), 5)
            self.assertTrue(g["band"][0] <= g["odds"] <= g["band"][1])

if __name__ == "__main__":
    unittest.main()

class Grading(unittest.TestCase):
    def test_leg_results(self):
        idx = ({("2026-10-04", "arsenal", "chelsea"): [2, 1]}, {"t1": {"winner": "Iga Swiatek"}, "t2": {"void": True}},
               {"s1": {"winner": "Saracens", "score": [30, 10]}})
        fb = {"sport": "football", "date": "2026-10-04", "home": "Arsenal", "away": "Chelsea", "side": "a", "pick": "Chelsea"}
        self.assertEqual(G.settle(fb, idx), ("lost", "2-1"))
        self.assertEqual(G.settle(dict(fb, side="h", pick="Arsenal"), idx)[0], "won")
        self.assertEqual(G.settle(dict(fb, home="Spurs"), idx)[0], "pending")
        self.assertEqual(G.settle({"sport": "tennis", "id": "t1", "pick": "Iga Swiatek"}, idx)[0], "won")
        self.assertEqual(G.settle({"sport": "tennis", "id": "t2", "pick": "X"}, idx)[0], "void")
        self.assertEqual(G.settle({"sport": "rugby", "id": "s1", "pick": "Sale Sharks"}, idx), ("lost", "30-10"))
