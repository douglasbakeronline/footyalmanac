"""17 Nov 2026: the Daily 2x (groupings.daily_group), one slip a day, the
model's strongest picks at 1.10+, tier by tier, until it pays 2x."""
import os, sys, unittest
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G

DAY = "2026-11-17"
NOW = datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc)


def leg(i, odds, pm, lst=False, res=False, sport="nba", hour=15, est=False):
    l = {"event": f"a{i} v b{i}", "pick": f"a{i}", "sport": sport, "comp": "c", "odds": odds, "p": pm, "pModel": pm,
         "when": f"{DAY}T{hour:02d}:00:00Z", "est": est, "margin": 1.04, "date": DAY, "code": "x", "list": lst, "reserve": res}
    return G.honest(l)


class Daily2x(unittest.TestCase):
    def test_list_then_reserve_strongest_first(self):
        L = [leg(1, 1.40, 0.80, res=True), leg(2, 1.20, 0.90, lst=True), leg(3, 1.30, 0.85, lst=True), leg(4, 1.50, 0.95, res=True)]
        g = G.daily_group(L, NOW)
        # list first (a2, a3: 1.56), then the strongest reserve (a4): 2.34
        self.assertEqual({l["pick"] for l in g["legs"]}, {"a2", "a3", "a4"})
        self.assertFalse(g["short"]); self.assertEqual(g["tiers"], ["list", "reserve"])

    def test_floor_college_estimates_started(self):
        L = [leg(1, 1.08, 0.99, lst=True), leg(2, 1.60, 0.99, lst=True, sport="ncaab"), leg(3, 1.60, 0.99, lst=True, est=True),
             leg(4, 1.60, 0.99, lst=True, hour=7), leg(5, 1.45, 0.9, lst=True), leg(6, 1.45, 0.85, lst=True)]
        self.assertEqual([l["pick"] for l in G.daily_group(L, NOW)["legs"]], ["a5", "a6"])

    def test_football_tops_up_then_any(self):
        L = [leg(1, 1.30, 0.9, lst=True), leg(2, 1.30, 0.70, sport="football"), leg(3, 1.30, 0.60, sport="football"),
             leg(4, 1.30, 0.80, sport="tennis")]
        g = G.daily_group(L, NOW)
        self.assertEqual([l["tier"] for l in sorted(g["legs"], key=lambda l: l["pick"])], ["list", "football", "any"])

    def test_short_slip_still_published(self):
        g = G.daily_group([leg(1, 1.30, 0.9, lst=True)], NOW)
        self.assertTrue(g["short"]); self.assertEqual(g["odds"], 1.3)

    def test_built_every_day_and_graded_apart(self):
        gs = G.build_list_card([leg(1, 1.50, 0.9, lst=True), leg(2, 1.50, 0.9, lst=True)], DAY, NOW, archived=[])
        self.assertIn("Daily 2x", [g["name"] for g in gs])
        src = open(os.path.join(HERE, "groupings.py")).read()
        self.assertIn('"cardDaily": tally([g for g in allg if is_daily(g["name"])])', src)

    def test_reserve_reaches_the_leg(self):
        src = open(os.path.join(HERE, "groupings.py")).read()
        self.assertEqual(src.count('"reserve": bool('), 3)


if __name__ == "__main__":
    unittest.main()
