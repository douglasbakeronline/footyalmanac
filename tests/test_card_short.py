"""Why a day has no Card group (13 Nov 2026, groupings.card_short): the page
said "too few picks" on 13 Nov when three qualified and together paid 3.51,
over the 2x group's 3.00 top."""
import os, sys, unittest
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G
from test_card_span import D1, NOW, leg


class Short(unittest.TestCase):
    def day(self, L): return G.card_short(L, D1.isoformat(), NOW)

    def test_few(self):
        s = self.day([leg(i, D1, 15 + i) for i in range(2)])
        self.assertEqual((s["why"], s["picks"], s["need"]), ("few", 2, 3))

    def test_long(self):
        s = self.day([leg(i, D1, 15 + i, odds=1.60, model=0.66) for i in range(3)])
        self.assertEqual(s["why"], "long"); self.assertAlmostEqual(s["best"], 4.10, places=2)

    def test_spread(self):
        L = [leg(i, D1, 15 + i) for i in range(3)]
        for l in L: l["comp"] = "same"
        self.assertEqual(self.day(L)["why"], "spread")

    def test_none_when_a_group_builds(self):
        L = [leg(i, D1, 15 + i) for i in range(3)]
        self.assertIsNone(self.day(L))
        self.assertTrue(G.build_card(L, D1.isoformat(), NOW, log=[]))

    def test_started_picks_do_not_count(self):
        L = [leg(i, D1, 15 + i) for i in range(3)]
        L[0]["when"] = f"{D1.isoformat()}T08:05:00Z"
        self.assertEqual(self.day(L)["why"], "few")

    def test_other_days_and_used_left_out(self):
        L = [leg(i, D1, 15 + i) for i in range(3)] + [leg(9, D1 + timedelta(days=1), 15)]
        s = G.card_short(L, D1.isoformat(), NOW, used={L[0]["event"]})
        self.assertEqual((s["why"], s["picks"]), ("few", 2))


if __name__ == "__main__":
    unittest.main()
