"""16 Nov 2026: the List 2x on paper (groupings.build_list_card), the Daily
List's own picks at 1.15+, strongest first, until the slip pays 2x."""
import os, sys, unittest
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G

DAY = "2026-11-17"
NOW = datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc)


def leg(i, odds, pm, lst=True, est=False, hour=15, sport="nba"):
    l = {"event": f"a{i} v b{i}", "pick": f"a{i}", "sport": sport, "comp": "c", "odds": odds, "p": pm, "pModel": pm,
         "when": f"{DAY}T{hour:02d}:00:00Z", "est": est, "margin": 1.04, "date": DAY, "code": "x", "list": lst}
    return G.honest(l)


class ListCard(unittest.TestCase):
    def test_strongest_first_until_2x(self):
        L = [leg(1, 1.30, 0.95), leg(2, 1.20, 0.93), leg(3, 1.40, 0.90), leg(4, 1.50, 0.88), leg(5, 1.25, 0.80)]
        g = G.list_group(L, set(), NOW)
        self.assertEqual({l["pick"] for l in g["legs"]}, {"a1", "a2", "a3"})   # 1.30*1.20*1.40 = 2.18
        self.assertEqual(g["odds"], 2.18)
        self.assertAlmostEqual(g["p"], 0.95 * 0.93 * 0.90, places=3)

    def test_refuses_short_unlisted_estimated_started(self):
        L = [leg(1, 1.10, 0.99), leg(2, 1.60, 0.97, lst=False), leg(3, 1.60, 0.96, est=True), leg(4, 1.60, 0.95, hour=7),
             leg(5, 1.45, 0.90), leg(6, 1.45, 0.85)]
        g = G.list_group(L, set(), NOW)
        self.assertEqual([l["pick"] for l in g["legs"]], ["a5", "a6"])

    def test_none_when_list_cannot_reach_2x(self):
        self.assertIsNone(G.list_group([leg(1, 1.20, 0.9), leg(2, 1.20, 0.9)], set(), NOW))

    def test_paper_never_staked(self):
        L = [leg(1, 1.50, 0.9), leg(2, 1.50, 0.9)]
        gs = G.build_list_card(L, DAY, NOW, archived=[])
        self.assertEqual(len(gs), 1)
        g = gs[0]
        self.assertEqual((g["name"], g["stake"], g["paper"]), ("List 2x", 0, True))
        self.assertTrue(G.is_list(g["name"])); self.assertFalse(G.is_card(g["name"]))

    def test_held_as_first_built(self):
        L = [leg(1, 1.50, 0.9), leg(2, 1.50, 0.9)]
        g = G.build_list_card(L, DAY, NOW, archived=[])[0]
        L2 = [leg(3, 1.50, 0.99), leg(4, 1.50, 0.99)]
        again = G.build_list_card(L + L2, DAY, NOW, prev=[g], archived=[])
        self.assertEqual(len(again), 1)
        self.assertEqual({l["pick"] for l in again[0]["legs"]}, {"a1", "a2"})

    def test_graded_apart(self):
        src = open(os.path.join(HERE, "groupings.py")).read()
        self.assertIn('"cardList": tally([g for g in allg if is_list(g["name"])])', src)
        self.assertIn("build_list_card(L, d, now", src)


if __name__ == "__main__":
    unittest.main()
