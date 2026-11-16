"""16 Nov 2026: comp3 (three Card picks from one competition, pre-registered
10 Nov) is built on the live rule 11 Card, on the pool and on the
football-data seasons (card_legs_history.py cardM7), so the 30 Nov review
has both sides of the gate. Live stays at two a competition."""
import os, sys, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as R


def leg(i, comp="NBA"):
    return {"event": f"t{i} v u{i}", "pick": f"t{i}", "comp": comp, "odds": 1.30, "p": 0.75}


class Comp3(unittest.TestCase):
    def test_live_cap_unchanged(self):
        self.assertEqual(G.COMP_MAX, 2)
        self.assertIsNone(G.mult_combo([leg(1), leg(2), leg(3)], 2.0, 3.0))
        self.assertIsNotNone(G.mult_combo([leg(1), leg(2), leg(3, "en.1")], 2.0, 3.0))

    def test_registered_on_live_not_rule6(self):
        self.assertEqual(R.VARIANTS["comp3"], {"COMP_MAX": 3})
        self.assertNotIn("comp3", R.RULE6_FAMILY)
        self.assertEqual(R.patch_of("comp3"), {"COMP_MAX": 3})

    def test_in_football_data_m7_list(self):
        src = open(os.path.join(HERE, "tools", "card_legs_history.py")).read()
        self.assertIn('"comp3")}', src)

    def test_patch_lifts_cap_and_restores(self):
        saved = G.COMP_MAX
        try:
            G.COMP_MAX = 3
            self.assertIsNotNone(G.mult_combo([leg(1), leg(2), leg(3)], 2.0, 3.0))
        finally:
            G.COMP_MAX = saved
        R.build([], "2026-11-16", "comp3")
        self.assertEqual(G.COMP_MAX, 2)


if __name__ == "__main__":
    unittest.main()
