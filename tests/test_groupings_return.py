"""Odds tab, 22 Oct 2026 (Douglas): every group pays at least double the
stake (groupings.MIN_RETURN = 2.0). No network."""
import copy, os, sys, unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import groupings as G

NOW = datetime(2026, 10, 24, 9, 0, tzinfo=timezone.utc)
AFTER = NOW + timedelta(minutes=20)


def leg(i, p, est=False, lst=True):
    l = {"sport": "football", "event": f"E{i}", "pick": f"P{i}", "home": f"P{i}", "away": f"Q{i}",
         "side": "h", "comp": f"C{i}", "when": "2026-10-24T15:00:00Z", "date": "2026-10-24",
         "p": p, "pModel": p, "list": lst, "est": est}
    if est:
        l["odds"] = round(1 / p, 2)
    else:
        l.update(odds=round(1 / (p * 1.05), 2), margin=1.05)
    return G.honest(l)


class MinimumReturn(unittest.TestCase):

    def test_the_floor_is_two(self):
        self.assertEqual(G.MIN_RETURN, 2.0)

    def test_every_group_pays_at_least_double(self):
        L = [leg(i, 0.80) for i in range(6)] + [leg(10 + i, 0.70) for i in range(6)]
        gs = G.build_day(L, AFTER, now=NOW, min_groups=3)
        self.assertGreaterEqual(len(gs), 3)
        self.assertTrue(all(g["odds"] >= 2.0 for g in gs), [g["odds"] for g in gs])

    def test_three_80_percent_legs_cannot_reach_two(self):
        # with the bookmakers' margin three 80% legs pay about 1.69
        self.assertEqual(G.build_day([leg(i, 0.80) for i in range(9)], AFTER, now=NOW, min_groups=3), [])

    def test_75_percent_legs_make_trebles_not_doubles(self):
        L = [leg(i, 0.75) for i in range(9)]
        gs = G.build_day(L, AFTER, now=NOW, min_groups=3)
        self.assertTrue(gs)
        self.assertTrue(all(len(g["legs"]) == 3 for g in gs))

    def test_the_most_likely_kind_is_chosen(self):
        L = [leg(i, 0.82, est=True) for i in range(3)] + [leg(10 + i, 0.69) for i in range(2)]
        g = G.build_day(L, AFTER, now=NOW, min_groups=1)[0]
        self.assertGreaterEqual(g["odds"], 2.0)
        self.assertEqual(len(g["legs"]), 3)          # 0.82^3 = 0.55 beats 0.69^2 = 0.48

    def test_a_held_group_that_shortens_below_two_is_replaced(self):
        L = [leg(i, 0.70) for i in range(8)]
        first = G.build_day(L, AFTER, now=NOW - timedelta(hours=3), min_groups=1)
        self.assertTrue(first)
        L2 = copy.deepcopy(L)
        pick = first[0]["legs"][0]["pick"]
        for l in L2:
            if l["pick"] == pick:
                l.pop("fair"); l.update(odds=1.05, p=l["pTested"], margin=1.05); G.honest(l)
        log = []
        G.build_day(L2, AFTER, prev=copy.deepcopy(first), now=NOW, log=log, min_groups=1)
        self.assertTrue(log)

    def test_nothing_under_two_when_only_short_legs_exist(self):
        L = [leg(0, 0.90), leg(1, 0.90)]
        self.assertEqual(G.build_day(L, AFTER, now=NOW, min_groups=3), [])


if __name__ == "__main__":
    unittest.main()
