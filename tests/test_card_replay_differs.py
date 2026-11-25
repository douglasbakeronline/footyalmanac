"""The days and legs a Card replay variant differs from live on (25 Nov 2026,
claude/card-replay-differs-2026-11-25.md): p(worse) and the 100-leg gate were
read on every leg a variant built, most shared with live, so m7cap160 read
p(worse) 0.0 from the few days it differs. Synthetic groups only."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_replay as CR
import card_review_post as P


def grp(picks, won, odds=2.0, stake=2):
    return {"legs": [{"event": f"{p} v X", "pick": p} for p in picks], "won": won, "odds": odds, "stake": stake}


class PairDays(unittest.TestCase):
    def test_same_groups_do_not_differ(self):
        live = {"d1": [grp("ABC", True)], "d2": [grp("DEF", False)]}
        var = {"d1": [grp("CBA", True)], "d2": [grp("DEF", False)]}
        alld, diffs, days, legs = CR.pair_days(live, var)
        self.assertEqual(alld, ["d1", "d2"])
        self.assertEqual(diffs, [0, 0])
        self.assertEqual((days, legs), (0, 0))

    def test_counts_only_differing_days(self):
        live = {"d1": [grp("ABC", True)], "d2": [grp("DEF", False)], "d3": [grp("GHI", True)]}
        var = {"d1": [grp("ABC", True)], "d2": [grp("DEX", True)], "d4": [grp("JKLM", False)]}
        alld, diffs, days, legs = CR.pair_days(live, var)
        self.assertEqual(alld, ["d1", "d2", "d3", "d4"])
        # d2: +2 v -2; d3: variant empty v live +2; d4: -2 v nothing
        self.assertEqual(diffs, [0, 4, -2, -2])
        self.assertEqual(days, 3)
        self.assertEqual(legs, 3 + 0 + 4)

    def test_same_result_different_picks_still_differs(self):
        live = {"d1": [grp("ABC", False)]}
        var = {"d1": [grp("ABD", False)]}
        _, diffs, days, legs = CR.pair_days(live, var)
        self.assertEqual(diffs, [0])
        self.assertEqual((days, legs), (1, 3))

    def test_stake_alone_differs(self):
        live = {"d1": [grp("ABC", True, stake=2)]}
        var = {"d1": [grp("ABC", True, stake=1)]}
        _, diffs, days, legs = CR.pair_days(live, var)
        self.assertEqual(diffs, [-1])
        self.assertEqual((days, legs), (1, 3))


class ReviewColumn(unittest.TestCase):
    def test_differs_cell(self):
        self.assertEqual(P.differs({"daysDiffer": 2, "legsDiffer": 6}), "2 / 6")
        self.assertEqual(P.differs({"daysDiffer": 0, "legsDiffer": 0}), "0 / 0")
        self.assertEqual(P.differs({}), "")


if __name__ == "__main__":
    unittest.main()
