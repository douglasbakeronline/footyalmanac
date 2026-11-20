"""score.lag_results: the AF_LAG leagues (the Czech First League) are graded
from the same API-Football pool the build fills their table from, all or
nothing on names, never twice (20 Nov 2026)."""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import score as SC  # noqa: E402

TODAY = date(2026, 11, 20)


def pred(d, h, a, published="2026-11-07T11:46:00Z", code="cze.1"):
    return (code, d, h, a), {"league": code, "date": d, "home": h, "away": a, "published": published}


PREDS = dict([
    pred("2026-11-08", "Viktoria Plzeň", "Sparta Praha"),
    pred("2026-11-08", "Slavia Praha", "Artis Brno"),
    pred("2026-11-07", "Zbrojovka Brno", "Baník Ostrava"),
])


def fetch_of(rows, why=None):
    calls = []

    def fetch(code, season):
        calls.append(code)
        return rows, why
    fetch.calls = calls
    return fetch


class LagResults(unittest.TestCase):
    def test_same_date_graded_under_archive_spelling(self):
        af = [{"date": "2026-11-08", "home": "Plzen", "away": "Sparta Praha", "hg": 2, "ag": 2},
              {"date": "2026-11-08", "home": "Slavia Praha", "away": "Artis Brno", "hg": 3, "ag": 0},
              {"date": "2026-11-07", "home": "Zbrojovka Brno", "away": "Banik Ostrava", "hg": 0, "ag": 1}]
        got = SC.lag_results(PREDS, {}, today=TODAY, fetch=fetch_of(af))
        self.assertEqual(got, {
            ("cze.1", "2026-11-08", "Viktoria Plzeň", "Sparta Praha"): (2, 2),
            ("cze.1", "2026-11-08", "Slavia Praha", "Artis Brno"): (3, 0),
            ("cze.1", "2026-11-07", "Zbrojovka Brno", "Baník Ostrava"): (0, 1)})

    def test_unmatched_name_fills_nothing(self):
        af = [{"date": "2026-11-08", "home": "Slavia Praha", "away": "Artis Brno", "hg": 3, "ag": 0},
              {"date": "2026-11-08", "home": "Nowhere United", "away": "Sparta Praha", "hg": 1, "ag": 0}]
        log = []
        self.assertEqual(SC.lag_results(PREDS, {}, today=TODAY, fetch=fetch_of(af), log=log), {})
        self.assertIn("unmatched", log[0])

    def test_country_refusal_fills_nothing(self):
        log = []
        got = SC.lag_results(PREDS, {}, today=TODAY, fetch=fetch_of([], "AF id 345 returned ['Poland']"), log=log)
        self.assertEqual(got, {})
        self.assertIn("Poland", log[0])

    def test_graded_and_other_leagues_untouched(self):
        af = [{"date": "2026-11-08", "home": "Slavia Praha", "away": "Artis Brno", "hg": 3, "ag": 0}]
        preds = dict(PREDS)
        preds.update([pred("2026-11-08", "Arsenal", "Chelsea", code="en.1")])
        done = {k: (1, 1) for k in preds if k[0] == "cze.1"}
        f = fetch_of(af)
        self.assertEqual(SC.lag_results(preds, done, today=TODAY, fetch=f), {})
        self.assertEqual(f.calls, [])          # nothing pending in an AF_LAG league: no pool read

    def test_today_and_unplayed_not_graded(self):
        preds = dict([pred("2026-11-20", "Slavia Praha", "Artis Brno")] + list(PREDS.items()))
        af = [{"date": "2026-11-20", "home": "Slavia Praha", "away": "Artis Brno", "hg": 1, "ag": 0},
              {"date": "2026-11-08", "home": "Plzen", "away": "Sparta Praha", "hg": None, "ag": None}]
        self.assertEqual(SC.lag_results(preds, {}, today=TODAY, fetch=fetch_of(af)), {})

    def test_day_off_goes_through_nearby_guards(self):
        # played a day after the archived date, price published before: graded
        af = [{"date": "2026-11-09", "home": "Slavia Praha", "away": "Artis Brno", "hg": 3, "ag": 0},
              {"date": "2026-11-08", "home": "Plzen", "away": "Sparta Praha", "hg": 2, "ag": 2},
              {"date": "2026-11-06", "home": "Zbrojovka Brno", "away": "Banik Ostrava", "hg": 0, "ag": 1}]
        got = SC.lag_results(PREDS, {}, today=TODAY, fetch=fetch_of(af))
        self.assertEqual(got.get(("cze.1", "2026-11-08", "Slavia Praha", "Artis Brno")), (3, 0))
        # played the day before, prediction published on the archived day: late, not graded
        self.assertNotIn(("cze.1", "2026-11-07", "Zbrojovka Brno", "Baník Ostrava"), got)


if __name__ == "__main__":
    unittest.main()
