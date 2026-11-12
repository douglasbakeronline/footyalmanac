"""12 Nov 2026: `m7legs2`, the rule 11 Card 2x allowed two picks as well as
three to five, pre-registered in tools/card_replay.py. Live keeps 3-5."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import groupings as G
import card_replay as R


def leg(i, odds):
    l = {"event": f"T{i} v U{i}", "pick": f"T{i}", "sport": "nba", "comp": "NBA", "odds": odds, "best": odds,
         "p": 0.70, "pModel": 0.70, "pTested": 0.70, "hit": 0.70, "n": 100, "when": f"2026-11-13T0{i}:00Z",
         "est": False, "margin": 1.04, "date": "2026-11-12", "code": "nba", "opp": 2.6, "draw": None, "won": True}
    return G.honest(l)


class M7Legs2(unittest.TestCase):
    def test_registered_and_live_unchanged(self):
        self.assertEqual(R.VARIANTS["m7legs2"], {"CARD_LEGS": (2, 3, 4, 5)})
        self.assertNotIn("m7legs2", R.RULE6_FAMILY)
        self.assertEqual(G.CARD_LEGS, (3, 4, 5))

    def test_two_picks_make_a_group_only_under_the_variant(self):
        legs = [leg(1, 1.55), leg(2, 1.55)]
        for l in legs: self.assertIsNone(G.card_fault(l))
        self.assertEqual(R.build([dict(l) for l in legs], "2026-11-12", "live"), [])
        gs = R.build([dict(l) for l in legs], "2026-11-12", "m7legs2")
        self.assertEqual([(g["name"], len(g["legs"])) for g in gs], [("Card 2x", 2)])
        self.assertEqual(G.CARD_LEGS, (3, 4, 5))   # the patch is restored


if __name__ == "__main__":
    unittest.main()
