"""score.nearby_results: predictions archived under a round's nominal date
are graded from the cached result of the same pair a day or two away, and
never twice, never late (20 Nov 2026)."""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import score as SC  # noqa: E402

TODAY = date(2026, 11, 20)


def pred(code, d, h, a, published):
    return (code, d, h, a), {"league": code, "date": d, "home": h, "away": a, "published": published}


def preds_of(*rows):
    return dict(rows)


def loader(rows):
    def load(code, season):
        return {(r["date"], r["home"], r["away"]): r for r in rows.get(code, [])}, None
    return load


# a full league's names, so the all-or-nothing mapping has every club
BASE = [
    pred("en.1", "2026-11-07", "Crystal Palace", "Liverpool", "2026-11-07T11:46:10Z"),
    pred("en.1", "2026-11-07", "Everton", "Coventry City", "2026-11-07T11:46:10Z"),
]


class NearbyResults(unittest.TestCase):
    def test_day_after_is_graded(self):
        preds = preds_of(*BASE)
        cache = {"en.1": [{"date": "2026-11-08", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3}]}
        got = SC.nearby_results(preds, {}, today=TODAY, load=loader(cache))
        self.assertEqual(got, {("en.1", "2026-11-07", "Crystal Palace", "Liverpool"): (1, 3)})

    def test_espn_spelling_is_mapped(self):
        preds = preds_of(pred("es.1", "2026-11-01", "FC Barcelona", "Deportivo Alavés", "2026-10-30T05:00:00Z"),
                         pred("es.1", "2026-11-01", "Valencia", "Real Madrid", "2026-10-30T05:00:00Z"))
        cache = {"es.1": [{"date": "2026-11-02", "home": "Barcelona", "away": "Alavés", "hg": 6, "ag": 1}]}
        got = SC.nearby_results(preds, {}, today=TODAY, load=loader(cache))
        self.assertEqual(got, {("es.1", "2026-11-01", "FC Barcelona", "Deportivo Alavés"): (6, 1)})

    def test_already_graded_untouched(self):
        preds = preds_of(*BASE)
        key = BASE[0][0]
        cache = {"en.1": [{"date": "2026-11-08", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3}]}
        got = SC.nearby_results(preds, {key: (1, 3)}, today=TODAY, load=loader(cache))
        self.assertEqual(got, {})

    def test_real_date_copy_owns_the_result(self):
        # the retimed copy archived on the real date is graded by date; the
        # nominal copy must not be graded as well
        preds = preds_of(*BASE, pred("en.1", "2026-11-08", "Crystal Palace", "Liverpool", "2026-11-08T09:00:00Z"))
        cache = {"en.1": [{"date": "2026-11-08", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3}]}
        got = SC.nearby_results(preds, {}, today=TODAY, load=loader(cache))
        self.assertEqual(got, {})

    def test_played_earlier_needs_an_early_price(self):
        cache = {"es.1": [{"date": "2026-10-31", "home": "Barcelona", "away": "Alavés", "hg": 6, "ag": 1}]}
        names = pred("es.1", "2026-11-01", "Valencia", "Real Madrid", "2026-10-30T05:00:00Z")
        late = preds_of(pred("es.1", "2026-11-01", "FC Barcelona", "Deportivo Alavés", "2026-10-31T05:30:52Z"), names)
        self.assertEqual(SC.nearby_results(late, {}, today=TODAY, load=loader(cache)), {})
        early = preds_of(pred("es.1", "2026-11-01", "FC Barcelona", "Deportivo Alavés", "2026-10-30T21:00:00Z"), names)
        self.assertEqual(SC.nearby_results(early, {}, today=TODAY, load=loader(cache)),
                         {("es.1", "2026-11-01", "FC Barcelona", "Deportivo Alavés"): (6, 1)})

    def test_outside_window_or_ambiguous(self):
        preds = preds_of(*BASE)
        far = {"en.1": [{"date": "2026-11-12", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3}]}
        self.assertEqual(SC.nearby_results(preds, {}, today=TODAY, load=loader(far)), {})
        two = {"en.1": [{"date": "2026-11-06", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3},
                        {"date": "2026-11-08", "home": "Crystal Palace", "away": "Liverpool", "hg": 0, "ag": 0}]}
        self.assertEqual(SC.nearby_results(preds, {}, today=TODAY, load=loader(two)), {})

    def test_two_predictions_one_result(self):
        preds = preds_of(*BASE, pred("en.1", "2026-11-09", "Crystal Palace", "Liverpool", "2026-11-06T09:00:00Z"))
        cache = {"en.1": [{"date": "2026-11-08", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3}]}
        self.assertEqual(SC.nearby_results(preds, {}, today=TODAY, load=loader(cache)), {})

    def test_unmatched_name_fills_nothing(self):
        preds = preds_of(*BASE)
        cache = {"en.1": [{"date": "2026-11-08", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3},
                          {"date": "2026-11-08", "home": "Premier League All-Stars", "away": "Everton", "hg": 1, "ag": 1}]}
        log = []
        self.assertEqual(SC.nearby_results(preds, {}, today=TODAY, load=loader(cache), log=log), {})
        self.assertTrue(any("unmatched" in line for line in log))

    def test_today_not_graded(self):
        preds = preds_of(pred("en.1", "2026-11-20", "Crystal Palace", "Liverpool", "2026-11-19T09:00:00Z"),
                         BASE[1])
        cache = {"en.1": [{"date": "2026-11-19", "home": "Crystal Palace", "away": "Liverpool", "hg": 1, "ag": 3}]}
        self.assertEqual(SC.nearby_results(preds, {}, today=TODAY, load=loader(cache)), {})


if __name__ == "__main__":
    unittest.main()
