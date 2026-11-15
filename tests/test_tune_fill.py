"""tune.fill_current (15 Nov 2026): the check season's openfootball rows
filled from the committed ESPN cache, by the live build's own rule."""
import os, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune as T


def fx(d, h, a, hg=None, ag=None):
    return {"date": d, "home": h, "away": a, "hg": hg, "ag": ag}


class FillCurrent(unittest.TestCase):
    TODAY = date(2026, 11, 15)

    def base(self):
        fixtures = [fx("2026-09-20", "Arsenal FC", "Chelsea FC", 2, 1),
                    fx("2026-10-04", "Chelsea FC", "Everton FC"),
                    fx("2026-10-18", "Everton FC", "Arsenal FC"),
                    fx("2026-11-22", "Arsenal FC", "Everton FC")]
        rows = [("2026-09-20", "Arsenal FC", "Chelsea FC", 2, 1)]
        return fixtures, rows

    def test_fills_unscored_fixtures_before_today(self):
        fixtures, rows = self.base()
        results = [{"date": "2026-10-04", "home": "Chelsea", "away": "Everton", "hg": 1, "ag": 1},
                   {"date": "2026-10-19", "home": "Everton", "away": "Arsenal", "hg": 0, "ag": 3}]
        log = []
        out = T.fill_current("en.1", "2026-27", rows, today=self.TODAY, log=log,
                             fixtures=fixtures, results=results)
        self.assertEqual(out, [("2026-09-20", "Arsenal FC", "Chelsea FC", 2, 1),
                               ("2026-10-04", "Chelsea FC", "Everton FC", 1, 1),
                               ("2026-10-18", "Everton FC", "Arsenal FC", 0, 3)])
        self.assertTrue(any("2 result(s)" in x for x in log))

    def test_never_overwrites_the_source_or_adds_the_future(self):
        fixtures, rows = self.base()
        results = [{"date": "2026-09-20", "home": "Arsenal", "away": "Chelsea", "hg": 0, "ag": 0},
                   {"date": "2026-11-22", "home": "Arsenal", "away": "Everton", "hg": 5, "ag": 0}]
        out = T.fill_current("en.1", "2026-27", rows, today=self.TODAY,
                             fixtures=fixtures, results=results)
        self.assertEqual(out, rows)

    def test_unmatched_name_fills_nothing(self):
        fixtures, rows = self.base()
        results = [{"date": "2026-10-04", "home": "Chelsea", "away": "Everton", "hg": 1, "ag": 1},
                   {"date": "2026-10-18", "home": "Nowhere Rovers", "away": "Arsenal", "hg": 0, "ag": 3}]
        log = []
        out = T.fill_current("en.1", "2026-27", rows, today=self.TODAY, log=log,
                             fixtures=fixtures, results=results)
        self.assertEqual(out, rows)
        self.assertTrue(any("unmatched" in x for x in log))

    def test_ineligible_league_untouched(self):
        fixtures, rows = self.base()
        results = [{"date": "2026-10-04", "home": "Chelsea", "away": "Everton", "hg": 1, "ag": 1}]
        for code in ("fa.cup.not.a.league", ):
            self.assertEqual(T.fill_current(code, "2026-27", rows, today=self.TODAY,
                                            fixtures=fixtures, results=results), rows)

    def test_no_cache_means_no_change(self):
        fixtures, rows = self.base()
        self.assertEqual(T.fill_current("en.1", "2026-27", rows, today=self.TODAY,
                                        fixtures=fixtures, results=[]), rows)

    def test_load_skips_splits_without_check(self):
        # card_legs_history swaps tune.splits for a one-season split ({"season": ...})
        saved_s, saved_c, saved_f = T.splits, T.codes, T.S.fetch_season
        try:
            T.codes = lambda: ["en.1"]
            T.splits = lambda c: {"season": ("2024-25", "2023-24")}
            T.S.fetch_season = lambda c, s, cache=None: ([("2024-08-17", "A", "B", 1, 0)], True)
            d = T.load(None, log=[])
            self.assertEqual(d[("en.1", "2024-25")], [("2024-08-17", "A", "B", 1, 0)])
        finally:
            T.splits, T.codes, T.S.fetch_season = saved_s, saved_c, saved_f


if __name__ == "__main__":
    unittest.main()
