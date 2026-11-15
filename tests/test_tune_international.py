"""Regression tests for tune_international.py (the international rating fit).

The module had no tests. These pin the pure helpers: tournament tiers, row
parsing, recency weights, the fit's identifiability fix, the scoring
machinery and the paired bootstrap.
"""
import math
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune_international as T


def row(date, h, a, hs, as_, tour="Friendly", neutral="FALSE"):
    return {"date": date, "home_team": h, "away_team": a, "home_score": hs,
            "away_score": as_, "tournament": tour, "neutral": neutral}


class TierTests(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(T.tier_of("FIFA World Cup"), "world_cup")
        self.assertEqual(T.tier_of("FIFA World Cup qualification"), "qualifier")
        self.assertEqual(T.tier_of("UEFA Euro qualification"), "qualifier")
        self.assertEqual(T.tier_of("UEFA Euro"), "continental_final")
        self.assertEqual(T.tier_of("Copa América"), "continental_final")
        self.assertEqual(T.tier_of("UEFA Nations League"), "nations_league")
        self.assertEqual(T.tier_of("Friendly"), "other")

    def test_every_tier_has_a_weight(self):
        for t in ("FIFA World Cup", "UEFA Euro", "Friendly", "UEFA Nations League",
                  "African Cup of Nations qualification"):
            self.assertIn(T.tier_of(t), T.TIER_WEIGHTS)


class BuildMatchesTests(unittest.TestCase):
    def test_filters_date_and_unplayed(self):
        rows = [row("2015-12-31", "A", "B", "1", "0"),
                row("2016-01-01", "A", "B", "2", "1", neutral="TRUE"),
                row("2016-02-01", "A", "B", "NA", "NA"),
                row("2016-03-01", "A", "B", "", "")]
        out = T.build_matches(rows, "2016-01-01")
        self.assertEqual(len(out), 1)
        self.assertEqual((out[0]["hg"], out[0]["ag"]), (2, 1))
        self.assertTrue(out[0]["neutral"])
        self.assertEqual(out[0]["tier"], "other")

    def test_neutral_only_when_true(self):
        out = T.build_matches([row("2020-01-01", "A", "B", "0", "0")], "2016-01-01")
        self.assertFalse(out[0]["neutral"])


class WeightTests(unittest.TestCase):
    def test_half_life_and_tier(self):
        as_of = datetime(2020, 1, 1)
        m = {"date": "2019-01-01", "tier": "other"}
        tw = {"other": 1.0, "world_cup": 3.0}
        self.assertAlmostEqual(T.weight(m, as_of, 365, tw), 0.5, places=6)
        m["tier"] = "world_cup"
        self.assertAlmostEqual(T.weight(m, as_of, 365, tw), 1.5, places=6)

    def test_future_match_not_upweighted(self):
        as_of = datetime(2020, 1, 1)
        m = {"date": "2020-06-01", "tier": "other"}
        self.assertEqual(T.weight(m, as_of, 365, {"other": 1.0}), 1.0)


class FitTests(unittest.TestCase):
    def setUp(self):
        rows = []
        # Strong beats Weak and Mid at home and away; Mid beats Weak.
        for i in range(6):
            d = "2019-0%d-01" % (i + 1)
            rows += [row(d, "Strong", "Weak", "3", "0"), row(d, "Weak", "Strong", "0", "2"),
                     row(d, "Strong", "Mid", "2", "0"), row(d, "Mid", "Strong", "1", "2"),
                     row(d, "Mid", "Weak", "2", "0"), row(d, "Weak", "Mid", "0", "1")]
        self.matches = T.build_matches(rows, "2016-01-01")
        self.ratings, self.mu, self.ha = T.fit_ratings(
            self.matches, datetime(2020, 1, 1), 730, T.TIER_WEIGHTS)

    def test_ordering(self):
        r = self.ratings
        self.assertGreater(r["Strong"]["att"], r["Mid"]["att"])
        self.assertGreater(r["Mid"]["att"], r["Weak"]["att"])
        # defence is a multiplier on the opposition's goals: smaller is better
        self.assertLess(r["Strong"]["def"], r["Mid"]["def"])
        self.assertLess(r["Mid"]["def"], r["Weak"]["def"])

    def test_scalars_sane(self):
        self.assertGreater(self.mu, 0)
        self.assertGreater(self.ha, 0)
        for t in self.ratings.values():
            self.assertGreater(t["weight"], 0)

    def test_shared_shift_removed(self):
        # The fix pins sum(log att) + sum(log def-as-de) to zero: with
        # def = exp(-de) the product of all att * def stays ~ 1 (rounding aside).
        la = sum(math.log(t["att"]) for t in self.ratings.values())
        ld = sum(math.log(t["def"]) for t in self.ratings.values())
        self.assertAlmostEqual(la - ld, 0.0, places=1)

    def test_fit_beats_baseline_on_training_data(self):
        fit, _ = T.score(self.matches, self.ratings, self.mu, self.ha)
        base, _ = T.score(self.matches, self.ratings, self.mu, self.ha, baseline=True)
        self.assertLess(sum(fit) / len(fit), sum(base) / len(base))


class OutcomeTests(unittest.TestCase):
    def test_sums_to_one(self):
        for lh, la in [(1.5, 1.1), (0.3, 2.8), (2.0, 2.0)]:
            p = T.outcome(lh, la)
            self.assertAlmostEqual(sum(p), 1.0, places=9)
            self.assertTrue(all(0 <= x <= 1 for x in p))

    def test_stronger_home_favoured(self):
        h, d, a = T.outcome(2.2, 0.7)
        self.assertGreater(h, a)
        h2, d2, a2 = T.outcome(0.7, 2.2)
        self.assertGreater(a2, h2)

    def test_equal_rates_symmetric(self):
        h, d, a = T.outcome(1.3, 1.3)
        self.assertAlmostEqual(h, a, places=9)


class ScoreTests(unittest.TestCase):
    def test_unrated_teams_skipped(self):
        m = [{"home": "X", "away": "Y", "hg": 1, "ag": 0, "neutral": False}]
        per, acc = T.score(m, {}, 1.3, 1.2)
        self.assertEqual(per, [])
        self.assertEqual(acc, 0.0)

    def test_baseline_needs_no_ratings(self):
        m = [{"home": "X", "away": "Y", "hg": 1, "ag": 0, "neutral": True}]
        per, acc = T.score(m, {}, 1.3, 1.2, baseline=True)
        self.assertEqual(len(per), 1)
        self.assertGreater(per[0], 0)


class PairedTests(unittest.TestCase):
    def test_deterministic_and_directional(self):
        a = [1.0] * 50
        b = [0.9] * 50
        mu, pw = T.paired(a, b)
        self.assertAlmostEqual(mu, 0.1)
        self.assertEqual(pw, 1.0)
        self.assertEqual(T.paired(a, b), (mu, pw))
        mu2, pw2 = T.paired(b, a)
        self.assertLess(mu2, 0)
        self.assertEqual(pw2, 0.0)


if __name__ == "__main__":
    unittest.main()
