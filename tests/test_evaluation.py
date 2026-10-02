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

    def test_rows_outside_the_season_window_are_refused(self):
        stray = [("2025-01-01", "Ash", "Birch", 1, 1)] + TEST          # en.3 2025-26 holds January 2025
        v = R.validate_split("en.3", "fit", PRIOR, stray, "2024-25", "2025-26")
        self.assertFalse(v["ok"])
        self.assertTrue(any("outside 2025-06-01..2026-07-31" in r for r in v["reasons"]), v["reasons"])
        late = TEST + [("2026-08-01", "Ash", "Birch", 1, 5)]           # mx.1 2025-26 holds August 2026
        v = R.validate_split("mx.1", "check", late, [("2026-08-08", "A", "B", 0, 0)], "2025-26", "2026-27")
        self.assertTrue(any("prior season 2025-26: 1 of" in r for r in v["reasons"]), v["reasons"])

    def test_unrecognised_season_labels_are_not_window_checked(self):
        self.assertTrue(R.validate_split("x", "fit", PRIOR, TEST, "P", "T")["ok"])

    def test_play_off_tails_inside_the_window_are_accepted(self):
        v = R.validate_split("x.1", "fit", [("2025-07-30", "A", "B", 1, 0)], [("2025-08-10", "A", "B", 0, 0)],
                             "2024-25", "2025-26")
        self.assertTrue(v["ok"], v["reasons"])

    def test_missing_seasons_are_reported(self):
        self.assertEqual(R.validate_split("a", "fit", [], TEST)["reasons"], ["no prior season"])
        self.assertEqual(R.validate_split("a", "fit", PRIOR, [])["reasons"], ["no test season"])

    def test_coverage_lists_every_exclusion(self):
        data = {("good", "2025-26"): TEST, ("good", "2024-25"): PRIOR,
                ("bad", "2025-26"): TEST, ("bad", "2024-25"): PRIOR + [TEST[0]],
                ("empty", "2024-25"): PRIOR}
        usable, excluded = R.coverage(data, ["good", "bad", "empty"],
                                      lambda c: {"fit": ("2025-26", "2024-25")}, "fit")
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
    # Numeric outputs are compared to 1e-12, relative and absolute. Different
    # CPython builds (3.7 here, 3.12 in CI, 3.13 at the reviewer) can differ in
    # the last bit of exp() and pow(): Julius saw 0.9906923790478912 against
    # ...911, a difference of 1.1e-16 (one ulp). 1e-12 is 10,000 times that,
    # 50 million times smaller than the 4-dp rounding the archive stores
    # (5e-5), and far below any real model change (>= 1e-6). The golden values
    # are not regenerated. Discrete outputs (the likeliest scoreline) are exact.
    TOL = 1e-12

    def test_match_probabilities_unchanged(self):
        import math
        with open(os.path.join(HERE, "golden_match_probabilities.json")) as f:
            g = json.load(f)
        saved = E.CALIBRATION
        try:
            E.CALIBRATION = g["calibration"]
            for c in g["cases"]:
                p = E.match_probabilities(*c["args"], tier=c["tier"],
                                          form_h=c["form"][0], form_a=c["form"][1])
                self.assertEqual(set(p), set(c["out"]))
                for k, v in c["out"].items():
                    got = list(p[k]) if isinstance(p[k], tuple) else p[k]
                    if isinstance(v, float):
                        self.assertTrue(math.isclose(got, v, rel_tol=self.TOL, abs_tol=self.TOL),
                                        f"{k}: {got!r} != {v!r} (beyond {self.TOL})")
                    else:
                        self.assertEqual(got, v, k)            # discrete: exact
        finally:
            E.CALIBRATION = saved

    def test_tolerance_still_catches_a_real_change(self):
        """The tolerance must not hide a model change: nudging one input by a
        realistic amount has to move the outputs well past it."""
        import math
        saved = E.CALIBRATION
        try:
            E.CALIBRATION = {"a": 1.05, "b": -0.3}
            p = E.match_probabilities(1.4, 0.8, 0.9, 1.2, 1.4, tier=1)
            q = E.match_probabilities(1.4 * 1.0001, 0.8, 0.9, 1.2, 1.4, tier=1)   # 0.01% stronger attack
            self.assertFalse(math.isclose(p["home"], q["home"], rel_tol=self.TOL, abs_tol=self.TOL))
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

    def test_archive_refuses_a_first_price_after_kickoff(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.build.archive_predictions(
                os.path.join(d, "f.json"),
                [{"league": "en.1", "date": "2026-10-02", "home": "A", "away": "B",
                  "p": 0.7, "kickoff": "2026-10-02T14:00:00Z"}],
                now="2026-10-02T14:32:00Z")
            self.assertEqual(out, {})


class Timestamps(unittest.TestCase):
    def test_parse_is_timezone_aware(self):
        import sources as S
        self.assertEqual(S.parse_utc("2026-10-02T15:00:00+01:00"), S.parse_utc("2026-10-02T14:00:00Z"))
        self.assertEqual(S.parse_utc("2026-10-02T14:00Z"), S.parse_utc("2026-10-02T14:00:00Z"))

    def test_zone_less_and_date_only_are_unknown(self):
        import sources as S
        for t in ("2026-10-02T14:00:00", "2026-10-02", "", None, "junk"):
            self.assertIsNone(S.parse_utc(t), t)


class Archive(unittest.TestCase):
    def setUp(self):
        import build
        self.archive = build.archive_predictions
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "2026-10-02.json")

    def tearDown(self):
        self.dir.cleanup()

    def row(self, kickoff, p, date_="2026-10-02"):
        return {"league": "en.1", "date": date_, "home": "A", "away": "B", "p": p, "kickoff": kickoff}

    def test_offset_kickoff_compared_in_utc(self):
        # 15:00 +01:00 is 14:00 UTC: a build at 14:30 UTC is after kick-off
        self.archive(self.path, [self.row("2026-10-02T15:00:00+01:00", 0.6)], now="2026-10-02T05:15:00Z")
        out = self.archive(self.path, [self.row("2026-10-02T15:00:00+01:00", 0.7)], now="2026-10-02T14:30:00Z")
        self.assertEqual(list(out.values())[0]["p"], 0.6)

    def test_zone_less_kickoff_is_treated_as_unknown(self):
        # no usable kick-off: the price published before the date's earliest
        # instant (2026-10-01T10:00Z) is kept, a later one refused
        self.archive(self.path, [self.row("2026-10-02T14:00:00", 0.6)], now="2026-10-01T05:15:00Z")
        out = self.archive(self.path, [self.row("2026-10-02T14:00:00", 0.7)], now="2026-10-02T09:00:00Z")
        self.assertEqual(list(out.values())[0]["p"], 0.6)

    def test_reviewer_case_past_date_unknown_kickoff_is_refused(self):
        out = self.archive(self.path, [self.row(None, 0.6, "2026-10-01")], now="2026-10-02T12:00:00Z")
        self.assertEqual(out, {})

    def test_match_day_first_price_with_unknown_kickoff_is_refused(self):
        out = self.archive(self.path, [self.row(None, 0.6, "2026-10-02")], now="2026-10-02T05:15:00Z")
        self.assertEqual(out, {})

    def test_unknown_kickoff_before_the_earliest_instant_is_accepted(self):
        out = self.archive(self.path, [self.row(None, 0.6, "2026-10-03")], now="2026-10-02T05:15:00Z")
        self.assertEqual(list(out.values())[0]["published"], "2026-10-02T05:15:00Z")
        out = self.archive(self.path, [self.row(None, 0.7, "2026-10-03")], now="2026-10-02T14:30:00Z")
        self.assertEqual(list(out.values())[0]["p"], 0.6)   # after 2026-10-02T10:00Z: kept, not replaced

    def test_legacy_entries_are_preserved_untouched(self):
        legacy = {"league": "en.1", "date": "2026-09-30", "home": "A", "away": "B", "p": 0.55}
        with open(self.path, "w") as f:
            json.dump([legacy], f)
        out = self.archive(self.path, [self.row(None, 0.9, "2026-09-30")], now="2026-10-02T05:15:00Z")
        self.assertEqual(list(out.values()), [legacy])

    def test_missing_kickoff_future_date_updates(self):
        self.archive(self.path, [self.row(None, 0.6, "2026-10-05")], now="2026-10-02T05:15:00Z")
        out = self.archive(self.path, [self.row(None, 0.7, "2026-10-05")], now="2026-10-02T14:30:00Z")
        self.assertEqual(list(out.values())[0]["p"], 0.7)

    def test_rescheduled_later_takes_the_new_price(self):
        self.archive(self.path, [self.row("2026-10-02T14:00:00Z", 0.6)], now="2026-10-02T05:15:00Z")
        out = self.archive(self.path, [self.row("2026-10-02T19:00:00Z", 0.7)], now="2026-10-02T14:30:00Z")
        g = list(out.values())[0]
        self.assertEqual((g["p"], g["kickoff"]), (0.7, "2026-10-02T19:00:00Z"))

    def test_rescheduled_earlier_keeps_price_and_corrects_kickoff(self):
        import score
        self.archive(self.path, [self.row("2026-10-02T19:00:00Z", 0.6)], now="2026-10-02T15:00:00Z")
        out = self.archive(self.path, [self.row("2026-10-02T14:00:00Z", 0.7)], now="2026-10-02T16:00:00Z")
        g = list(out.values())[0]
        self.assertEqual((g["p"], g["kickoff"], g["published"]), (0.6, "2026-10-02T14:00:00Z", "2026-10-02T15:00:00Z"))
        self.assertEqual(score.verification(g), "late")      # published after the real start: not graded

    def test_rescheduled_to_another_day_is_a_separate_entry(self):
        self.archive(self.path, [self.row("2026-10-02T14:00:00Z", 0.6)], now="2026-10-02T05:15:00Z")
        out = self.archive(self.path, [self.row("2026-10-03T14:00:00Z", 0.7, "2026-10-03")], now="2026-10-02T09:00:00Z")
        self.assertEqual(sorted((k[1], v["p"]) for k, v in out.items()), [("2026-10-02", 0.6), ("2026-10-03", 0.7)])

    def test_repeat_builds_after_kickoff_leave_the_file_unchanged(self):
        self.archive(self.path, [self.row("2026-10-02T14:00:00Z", 0.6)], now="2026-10-02T05:15:00Z")
        with open(self.path) as f:
            first = f.read()
        for now in ("2026-10-02T14:30:00Z", "2026-10-02T18:00:00Z"):
            self.archive(self.path, [self.row("2026-10-02T14:00:00Z", 0.7)], now=now)
        with open(self.path) as f:
            self.assertEqual(f.read(), first)


class Grading(unittest.TestCase):
    def test_earliest_start_convention(self):
        import sources as S
        self.assertEqual(S.earliest_start("2026-10-02"), S.parse_utc("2026-10-01T10:00:00Z"))

    def test_verification_categories(self):
        import score
        base = {"league": "en.1", "date": "2026-10-02", "home": "A", "away": "B"}
        cases = [({}, "legacy-unverified"),                                          # no publish time
                 ({"published": "2026-10-02T05:15:00Z", "kickoff": "2026-10-02T14:00:00Z"}, "verified"),
                 ({"published": "2026-10-02T14:30:00Z", "kickoff": "2026-10-02T14:00:00Z"}, "late"),
                 ({"published": "2026-10-01T05:15:00Z"}, "verified-by-date"),         # before 10-01T10:00Z
                 ({"published": "2026-10-01T20:00:00Z"}, "timing-unverifiable"),      # after the earliest instant
                 ({"published": "2026-10-02T05:15:00Z"}, "timing-unverifiable"),      # match day, no kick-off
                 ({"published": "2026-10-02T12:00:00Z", "date": "2026-10-01"}, "timing-unverifiable"),  # review case
                 ({"published": "2026-10-02T05:15:00Z", "kickoff": "2026-10-02T14:00:00"},
                  "timing-unverifiable")]                                                # zone-less kick-off
        for extra, want in cases:
            self.assertEqual(score.verification({**base, **extra}), want, extra)

    def test_late_and_unverifiable_are_distinct_and_both_excluded(self):
        """Same publish time, same date: with a known kick-off after it the
        row is verified; with a known kick-off before it, late; with no
        kick-off it cannot be proven either way, so timing-unverifiable."""
        import score
        base = {"league": "en.1", "date": "2026-10-02", "home": "A", "away": "B",
                "published": "2026-10-02T12:00:00Z"}
        self.assertEqual(score.verification({**base, "kickoff": "2026-10-02T15:00:00Z"}), "verified")
        self.assertEqual(score.verification({**base, "kickoff": "2026-10-02T11:00:00Z"}), "late")
        self.assertEqual(score.verification({**base, "kickoff": None}), "timing-unverifiable")
        self.assertEqual(score.EXCLUDED_FROM_GRADING, ("late", "timing-unverifiable"))
        self.assertEqual(score.verification({k: v for k, v in base.items() if k != "published"}),
                         "legacy-unverified")      # legacy rows stay graded

    def test_grading_keeps_legacy_and_evidenced_early_rows_and_drops_late_ones(self):
        import score
        with tempfile.TemporaryDirectory() as d:
            rows = [{"league": "en.1", "date": "2026-10-02", "home": "A", "away": "B",          # late: kick-off known
                     "kickoff": "2026-10-02T14:00:00Z", "published": "2026-10-02T14:30:00Z"},
                    {"league": "en.1", "date": "2026-10-02", "home": "C", "away": "D",          # verified
                     "kickoff": "2026-10-02T14:00:00Z", "published": "2026-10-02T05:15:00Z"},
                    {"league": "en.1", "date": "2026-10-02", "home": "E", "away": "F"},         # legacy
                    {"league": "en.1", "date": "2026-10-01", "home": "G", "away": "H",          # late: past date,
                     "kickoff": None, "published": "2026-10-02T12:00:00Z"},                    # no kick-off
                    {"league": "en.1", "date": "2026-10-03", "home": "I", "away": "J",          # verified by date
                     "kickoff": None, "published": "2026-10-02T05:15:00Z"}]
            with open(os.path.join(d, "2026-10-02.json"), "w") as f:
                json.dump(rows, f)
            saved = score.PRED_DIR
            try:
                score.PRED_DIR = d
                got = score.load_predictions()
                late = sorted(k[2] for k in score.SKIPPED["late"])
                unverifiable = sorted(k[2] for k in score.SKIPPED["timing-unverifiable"])
            finally:
                score.PRED_DIR = saved
        self.assertEqual(sorted(k[2] for k in got), ["C", "E", "I"])
        self.assertEqual(late, ["A"])                 # known kick-off proves lateness
        self.assertEqual(unverifiable, ["G"])         # no kick-off, fails the earliest-start cutoff
        self.assertEqual({k[2]: score.verification(v) for k, v in got.items()},
                         {"C": "verified", "E": "legacy-unverified", "I": "verified-by-date"})


class Backfill(unittest.TestCase):
    def setUp(self):
        import backfill
        self.b = backfill

    def test_evidenced_competitions_run_july_to_june(self):
        for code in ("mx.1", "ru.1", "dnk.1"):
            self.assertEqual(self.b.season_window(code, "2025-26"),
                             (date(2025, 7, 1), date(2026, 6, 30)), code)

    def test_other_competitions_keep_the_default_window(self):
        self.assertEqual(self.b.season_window("nl.2", "2025-26"), (date(2025, 6, 1), date(2026, 7, 31)))
        self.assertEqual(self.b.season_window("us.1", "2025"), (date(2025, 1, 1), date(2025, 12, 31)))

    def test_walk_stops_before_the_next_cached_season(self):
        import sources as S
        saved = S.load_current
        try:
            S.load_current = lambda c, s: ({("2026-07-17", "A", "B"): {"date": "2026-07-17"}}, None) \
                if s == "2026-27" else ({}, None)
            self.assertEqual(self.b.clip_to_next_season("nl.2", "2025-26", date(2026, 7, 31)),
                             date(2026, 7, 16))
            S.load_current = lambda c, s: ({}, None)
            self.assertEqual(self.b.clip_to_next_season("nl.2", "2025-26", date(2026, 7, 31)),
                             date(2026, 7, 31))
        finally:
            S.load_current = saved

    def test_next_season_strings(self):
        self.assertEqual(self.b.next_season("2025-26"), "2026-27")
        self.assertEqual(self.b.next_season("2025"), "2026")


if __name__ == "__main__":
    unittest.main()
