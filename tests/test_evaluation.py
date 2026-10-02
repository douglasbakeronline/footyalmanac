"""Regression tests for the football evaluation infrastructure (2 Oct 2026).

    python3 -m unittest discover -s tests -v

Standard library only; no network. Covers: season-boundary validation,
explicit exclusions, one shared replay for backtest.py and tune.py that
matches the live build's calculation, date batching (no same-day leakage),
the live prior/current double count, and the prediction archive's
publish-before-kick-off guard.
"""
import json, os, sys, tempfile, unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import engine as E
import replay as R


def season(rows):
    return [tuple(r) for r in rows]


# A small synthetic league: six clubs, a low-scoring prior and a high-scoring
# test season, so a prior-vs-current goal-rate mix-up changes the numbers.
CLUBS = ["Ash", "Birch", "Cedar", "Dogwood", "Elm", "Fir"]


def round_robin(start_month, year, goals):
    out, day = [], 1
    for i, h in enumerate(CLUBS):
        for j, a in enumerate(CLUBS):
            if h == a:
                continue
            hg = (i * 3 + j + goals) % 4
            ag = (j * 2 + i + goals) % 3
            out.append((f"{year}-{start_month:02d}-{day:02d}", h, a, hg, ag))
            day = day % 27 + 1
    return sorted(out)


PRIOR = round_robin(2, 2025, 0)             # Feb 2025
TEST = round_robin(9, 2025, 2)              # Sep 2025, higher scoring


class SeasonValidation(unittest.TestCase):
    def test_clean_split_is_ok(self):
        v = R.validate_split("x.1", "fit", PRIOR, TEST)
        self.assertTrue(v["ok"], v)

    def test_overlap_is_refused_with_counts(self):
        prior = PRIOR + [("2025-09-03", "Ash", "Birch", 1, 0)]   # a test-season match in the prior
        test = TEST + [("2025-09-03", "Ash", "Birch", 1, 0)]
        v = R.validate_split("mx.1", "check", prior, test)
        self.assertFalse(v["ok"])
        self.assertIn("overlap", v["reasons"][0])
        self.assertIn("1 identical in both", v["reasons"][0])

    def test_missing_seasons_are_reported(self):
        self.assertEqual(R.validate_split("a", "fit", [], TEST)["reasons"], ["no prior season"])
        self.assertEqual(R.validate_split("a", "fit", PRIOR, [])["reasons"], ["no test season"])

    def test_coverage_lists_every_exclusion(self):
        data = {("good", "T"): TEST, ("good", "P"): PRIOR,
                ("bad", "T"): TEST, ("bad", "P"): PRIOR + [TEST[0]],
                ("empty", "P"): PRIOR}
        usable, excluded = R.coverage(data, ["good", "bad", "empty"],
                                      lambda c: {"fit": ("T", "P")}, "fit")
        self.assertEqual(usable, ["good"])
        self.assertEqual(sorted(v["code"] for v in excluded), ["bad", "empty"])


class Replay(unittest.TestCase):
    def test_same_day_results_are_not_used(self):
        """Two matches on one date: the second must be priced identically
        whatever the first one's result was."""
        d = "2025-09-30"
        a = TEST + [(d, "Ash", "Birch", 0, 0), (d, "Ash", "Cedar", 1, 1)]
        b = TEST + [(d, "Ash", "Birch", 7, 0), (d, "Ash", "Cedar", 1, 1)]
        pa = {m[:3]: (lh, la) for m, lh, la, _ in R.replay_league(PRIOR, a, 1)}
        pb = {m[:3]: (lh, la) for m, lh, la, _ in R.replay_league(PRIOR, b, 1)}
        self.assertEqual(pa[(d, "Ash", "Cedar")], pb[(d, "Ash", "Cedar")])

    def test_earlier_dates_are_used(self):
        a = TEST + [("2025-09-29", "Ash", "Birch", 0, 0), ("2025-09-30", "Ash", "Cedar", 1, 1)]
        b = TEST + [("2025-09-29", "Ash", "Birch", 7, 0), ("2025-09-30", "Ash", "Cedar", 1, 1)]
        pa = {m[:3]: lh for m, lh, la, _ in R.replay_league(PRIOR, a, 1)}
        pb = {m[:3]: lh for m, lh, la, _ in R.replay_league(PRIOR, b, 1)}
        self.assertNotEqual(pa[("2025-09-30", "Ash", "Cedar")], pb[("2025-09-30", "Ash", "Cedar")])

    def test_matches_the_live_build_calculation(self):
        """Rebuild one prediction the way build.py does (strength_from_table on
        this season's table, so THIS season's goal rate; blend; form; the
        prior season's level) and compare."""
        rows = list(R.replay_league(PRIOR, TEST, 2))
        (d, h, a, hg, ag), lh, la, _ = rows[-1]
        earlier = [m for m in TEST if m[0] < d]
        ptbl = E.build_table(PRIOR)
        prior_rt = E.strength_from_table(ptbl)
        tbl = E.build_table(earlier)
        cur = E.strength_from_table(tbl)
        rh = E.blend(prior_rt[h], cur.get(h), tbl[h]["P"])
        ra = E.blend(prior_rt[a], cur.get(a), tbl[a]["P"])
        fh = E.form_factor(E.form_points(tbl[h]))
        fa = E.form_factor(E.form_points(tbl[a]))
        live = E.match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                                     E.league_goal_rate(ptbl), tier=2, form_h=fh, form_a=fa)
        self.assertAlmostEqual(lh, live["xg_home"], places=12)
        self.assertAlmostEqual(la, live["xg_away"], places=12)

    def test_tune_and_backtest_give_the_same_predictions(self):
        import tune as T, backtest as B, sources as S
        data = {("x.1", "2025-26"): TEST, ("x.1", "2024-25"): PRIOR}
        saved = (T.codes, T.splits, S.fetch_season, dict(E.LEAGUES))
        try:
            E.LEAGUES["x.1"] = {"tier": 1, "name": "Test", "country": "Nowhere", "iso": "xx", "order": 0}
            T.codes = lambda: ["x.1"]
            T.splits = lambda c: {"fit": ("2025-26", "2024-25"), "check": ("2025-26", "2024-25")}
            S.fetch_season = lambda c, s, cache=None: (data.get((c, s), []), bool(data.get((c, s))))
            tuned = T.lambdas(data, "fit", meta=True)
            backed = B.evaluate(["x.1"], "2025-26", "2024-25", verbose=False)
        finally:
            T.codes, T.splits, S.fetch_season = saved[:3]
            E.LEAGUES.clear(); E.LEAGUES.update(saved[3])
        self.assertEqual(len(tuned), len(backed))
        for (lh, la, y, code, d, h, a), b in zip(tuned, backed):
            self.assertEqual((d, h, a), (b["date"], b["home"], b["away"]))
            raw = T.outcome(lh, la, E.RHO)
            t = T.curve_T(max(raw), E.CALIBRATION) if E.CALIBRATION else E.TEMPERATURE
            q = [max(x, 1e-12) ** (1 / t) for x in raw]
            s = sum(q)
            for x, z in zip([v / s for v in q], b["p"]):
                self.assertAlmostEqual(x, z, places=9)


class EngineRefactor(unittest.TestCase):
    def test_match_probabilities_unchanged(self):
        g = json.load(open(os.path.join(HERE, "golden_match_probabilities.json")))
        saved = E.CALIBRATION
        try:
            E.CALIBRATION = g["calibration"]
            for c in g["cases"]:
                p = E.match_probabilities(*c["args"], tier=c["tier"],
                                          form_h=c["form"][0], form_a=c["form"][1])
                for k, v in c["out"].items():
                    got = list(p[k]) if isinstance(p[k], tuple) else p[k]
                    self.assertEqual(got, v, k)
        finally:
            E.CALIBRATION = saved


class LiveBuild(unittest.TestCase):
    def setUp(self):
        import build
        self.build = build

    def test_identical_matches_are_dropped_from_the_prior(self):
        prior = [("2026-05-01", "A", "B", 1, 0), ("2026-07-20", "A", "C", 2, 2)]
        current = [{"date": "2026-07-20", "home": "A", "away": "C", "hg": 2, "ag": 2},
                   {"date": "2026-07-27", "home": "B", "away": "C", "hg": None, "ag": None}]
        kept, newer, msg = self.build.drop_current_from_prior("mx.1", prior, [], current)
        self.assertEqual(kept, [prior[0]])
        self.assertIn("1 match(es) in both dropped", msg)

    def test_clean_prior_is_untouched(self):
        prior = [("2026-05-01", "A", "B", 1, 0)]
        current = [{"date": "2026-08-01", "home": "A", "away": "B", "hg": 0, "ag": 0}]
        self.assertEqual(self.build.drop_current_from_prior("x", prior, [], current),
                         (prior, [], None))

    def _row(self, kickoff, p, date_="2026-10-02"):
        return {"league": "en.1", "date": date_, "home": "A", "away": "B", "p": p, "kickoff": kickoff}

    def test_archive_keeps_the_price_published_before_kickoff(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "2026-10-02.json")
            self.build.archive_predictions(path, [self._row("2026-10-02T14:00:00Z", 0.6)],
                                           now="2026-10-02T05:15:00Z")
            out = self.build.archive_predictions(path, [self._row("2026-10-02T14:00:00Z", 0.7)],
                                                 now="2026-10-02T14:32:00Z")
            g = list(out.values())[0]
            self.assertEqual((g["p"], g["published"]), (0.6, "2026-10-02T05:15:00Z"))

    def test_archive_refuses_a_first_price_after_kickoff(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.build.archive_predictions(os.path.join(d, "f.json"),
                                                 [self._row("2026-10-02T14:00:00Z", 0.7)],
                                                 now="2026-10-02T14:32:00Z")
            self.assertEqual(out, {})

    def test_archive_updates_a_fixture_not_yet_started(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "f.json")
            self.build.archive_predictions(path, [self._row("2026-10-02T19:00:00Z", 0.6)],
                                           now="2026-10-02T05:15:00Z")
            out = self.build.archive_predictions(path, [self._row("2026-10-02T19:00:00Z", 0.7)],
                                                 now="2026-10-02T14:32:00Z")
            self.assertEqual(list(out.values())[0]["p"], 0.7)

    def test_date_only_fixture_keeps_the_days_first_price(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "f.json")
            self.build.archive_predictions(path, [self._row(None, 0.6)], now="2026-10-02T05:15:00Z")
            out = self.build.archive_predictions(path, [self._row(None, 0.7)], now="2026-10-02T14:32:00Z")
            self.assertEqual(list(out.values())[0]["p"], 0.6)


class Grading(unittest.TestCase):
    def test_score_skips_a_price_published_after_kickoff(self):
        import score
        with tempfile.TemporaryDirectory() as d:
            rows = [{"league": "en.1", "date": "2026-10-02", "home": "A", "away": "B",
                     "kickoff": "2026-10-02T14:00:00Z", "published": "2026-10-02T14:30:00Z"},
                    {"league": "en.1", "date": "2026-10-02", "home": "C", "away": "D",
                     "kickoff": "2026-10-02T14:00:00Z", "published": "2026-10-02T05:15:00Z"},
                    {"league": "en.1", "date": "2026-10-02", "home": "E", "away": "F"}]  # old row, no fields
            json.dump(rows, open(os.path.join(d, "2026-10-02.json"), "w"))
            saved = score.PRED_DIR
            try:
                score.PRED_DIR = d
                got = score.load_predictions()
            finally:
                score.PRED_DIR = saved
        self.assertEqual(sorted(k[2] for k in got), ["C", "E"])


class Backfill(unittest.TestCase):
    def test_split_year_window_stops_before_july(self):
        import backfill
        start, end = backfill.season_window("mx.1", "2025-26")
        self.assertEqual((start, end), (date(2025, 6, 1), date(2026, 6, 30)))


if __name__ == "__main__":
    unittest.main()
