"""Regression tests for the tennis results history (8 Oct 2026).

    python3 -m unittest discover -s tests -v

tennis.json is fitted on an archive that stops (1-2 June 2026 when this was
written); until 8 Oct a build added only the last six days of ESPN results,
so everything in between never reached a rating. These check that every
result since the archive ends is applied once, in order, with the archive's
own last matches skipped, and that a failed fetch never marks days walked.
No network.
"""
import os, sys, tempfile, unittest
from datetime import date
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import build_tennis as BT
import tune_tennis as TT


def player(elo=1800.0, n=50):
    return {"overall": elo, "surface_Hard": elo, "matches": n}


POOL = {"Ann Able": player(), "Bea Bold": player(), "Cat Clay": player(), "Dee Dune": player()}
BOUNDARY = {"through": "2026-06-02", "pairs": [["Ann Able", "Bea Bold"]]}


def res(i, d, p0, p1, winner=None, note=None):
    return {"id": str(i), "date": d, "time": "10:00", "p0": p0, "p1": p1,
            "winner": winner or p0, "completed": True, "note": note,
            "tournament": "T", "round": "Round 1", "state": "post"}


class ResultsToApply(unittest.TestCase):

    def setUp(self):
        self.by_full, self.by_init = BT.build_index(POOL)

    def apply(self, rows, boundary=BOUNDARY, since=None):
        games = {}
        BT.add_results(games, rows)
        return BT.results_to_apply(games, boundary, self.by_full, self.by_init, since=since)

    def test_archive_matches_skipped_and_later_results_applied_in_order(self):
        rows = [
            res(1, "2026-05-10", "Cat Clay", "Dee Dune"),          # long before the boundary: archive's
            res(6, "2026-05-28", "Dee Dune", "Cat Clay"),          # a tournament that began before it: archive's
            res(2, "2026-06-05", "Ann Able", "Bea Bold"),          # met in the archive's last week: same match
            res(3, "2026-06-06", "Cat Clay", "Ann Able"),          # not in the archive: applied
            res(4, "2026-09-01", "Bea Bold", "Ann Able"),          # same pair, long after: a new match
            res(5, "2026-07-01", "Dee Dune", "Cat Clay", winner="Cat Clay"),
        ]
        todo, counts = self.apply(rows)
        self.assertEqual(todo, [("Cat Clay", "Ann Able", False), ("Cat Clay", "Dee Dune", False),
                                ("Bea Bold", "Ann Able", False)])
        self.assertEqual(counts, {"applied": 3, "unmatched": 0, "archive": 1, "walkover": 0, "retired": 0})

    def test_a_retirement_is_applied_and_marked(self):
        rows = [res(1, "2026-07-01", "Cat Clay", "Dee Dune", note="Clay (X) bt Dune (Y) 6-4 3-1 ret"),
                res(2, "2026-07-02", "Cat Clay", "Dee Dune", note="Clay (X) bt Dune (Y) 6-4 6-3")]
        todo, counts = self.apply(rows)
        self.assertEqual(todo, [("Cat Clay", "Dee Dune", True), ("Cat Clay", "Dee Dune", False)])
        self.assertEqual(counts["retired"], 1)

    def test_walkovers_and_unrated_players_are_left_out(self):
        rows = [res(1, "2026-07-01", "Cat Clay", "Dee Dune", note="Clay bt Dune walkover"),
                res(2, "2026-07-02", "Cat Clay", "Zed Unknown")]
        todo, counts = self.apply(rows)
        self.assertEqual(todo, [])
        self.assertEqual((counts["walkover"], counts["unmatched"]), (1, 1))

    def test_without_a_boundary_only_the_recent_window_is_used(self):
        rows = [res(1, "2026-07-01", "Cat Clay", "Dee Dune"),
                res(2, "2026-10-05", "Dee Dune", "Cat Clay")]
        todo, _ = self.apply(rows, boundary=None, since=date(2026, 10, 2))
        self.assertEqual(todo, [("Dee Dune", "Cat Clay", False)])

    def test_a_result_fetched_twice_counts_once(self):
        games = {}
        BT.add_results(games, [res(7, "2026-07-01", "Cat Clay", "Dee Dune")])
        BT.add_results(games, [res(7, "2026-07-01", "Cat Clay", "Dee Dune", winner="Dee Dune")])
        self.assertEqual(len(games), 1)
        self.assertEqual(games["7"]["winner"], "Dee Dune")    # the later fetch wins
        BT.add_results(games, [{**res(8, "2026-07-02", "Cat Clay", "Dee Dune"), "completed": False}])
        self.assertEqual(len(games), 1)                       # unfinished matches are not kept


class HistoryFile(unittest.TestCase):

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(BT, "HIST_DIR", d):
            games = {}
            BT.add_results(games, [res(2, "2026-07-02", "A B", "C D"), res(1, "2026-07-01", "A B", "C D")])
            BT.save_history("wta", games, date(2026, 7, 2))
            back, through = BT.load_history("wta")
            self.assertEqual(through, date(2026, 7, 2))
            self.assertEqual(set(back), {"1", "2"})
            self.assertEqual(BT.load_history("atp"), ({}, None))

    def test_a_failed_fetch_is_reported_so_days_are_not_marked_walked(self):
        def broken(tour, start, end, timeout=25, log=None):
            log.append(f"{tour}/{tour}: 0 matches  ERROR timed out")
            return []
        with mock.patch.object(BT, "fetch_week", broken):
            log = []
            rows, ok = BT.fetch_ok("wta", date(2026, 7, 1), date(2026, 7, 3), log)
        self.assertEqual((rows, ok), ([], False))
        self.assertIn("ERROR", log[0])


class Ratings(unittest.TestCase):

    def test_every_build_starts_from_the_snapshot_so_nothing_is_counted_twice(self):
        by_full, by_init = BT.build_index(POOL)
        games = {}
        BT.add_results(games, [res(i, f"2026-07-{i:02d}", "Cat Clay", "Dee Dune") for i in range(1, 6)])
        ratings = []
        for _ in range(2):                                    # two builds, same history
            pool = {k: dict(v) for k, v in POOL.items()}
            todo, _ = BT.results_to_apply(games, BOUNDARY, by_full, by_init)
            for w, l, _ret in todo:
                BT.apply_result(pool, w, l, "Hard", 250)
            ratings.append(pool["Cat Clay"]["overall"])
        self.assertEqual(ratings[0], ratings[1])
        self.assertGreater(ratings[0], POOL["Cat Clay"]["overall"])
        self.assertEqual(POOL["Cat Clay"]["overall"], 1800.0)   # the snapshot itself is never changed

    def test_a_retirement_moves_the_ratings_by_the_fitted_weight(self):
        """Bug 13 (25 Oct 2026): the live update matches tune_tennis.run_elo,
        where a retirement is scaled by retirementWeight (WTA 0.5)."""
        full = {k: dict(v) for k, v in POOL.items()}
        half = {k: dict(v) for k, v in POOL.items()}
        BT.apply_result(full, "Cat Clay", "Dee Dune", "Hard", 250)
        BT.apply_result(half, "Cat Clay", "Dee Dune", "Hard", 250, weight=0.5)
        gain_full = full["Cat Clay"]["overall"] - 1800.0
        gain_half = half["Cat Clay"]["overall"] - 1800.0
        self.assertGreater(gain_full, 0)
        self.assertAlmostEqual(gain_half, gain_full / 2)
        self.assertAlmostEqual(half["Cat Clay"]["surface_Hard"] - 1800.0, gain_half)
        self.assertAlmostEqual(half["Dee Dune"]["overall"] - 1800.0, -gain_half)
        self.assertEqual(half["Cat Clay"]["matches"], 51)      # still counts as a match played
        # and the same number run_elo produces for one retirement
        m = [{"winner": "Cat Clay", "loser": "Dee Dune", "surface": "Hard", "retired": True}]
        _, overall, _, _ = TT.run_elo(m, 0.3, 250, 0.5, start=1800.0)
        self.assertAlmostEqual(overall["Cat Clay"], 1800.0 + BT.dynamic_k(0, 250) * 0.5 * 0.5)
        fresh = {"Cat Clay": {"overall": 1800.0, "matches": 0}, "Dee Dune": {"overall": 1800.0, "matches": 0}}
        BT.apply_result(fresh, "Cat Clay", "Dee Dune", "Hard", 250, weight=0.5)
        self.assertAlmostEqual(fresh["Cat Clay"]["overall"], overall["Cat Clay"])

    def test_tennis_json_carries_a_retirement_weight_per_tour(self):
        import json
        doc = json.load(open(os.path.join(os.path.dirname(HERE), "tennis.json")))
        for tour in ("atp", "wta"):
            self.assertIn("retirementWeight", doc[tour]["constants"])


class UnratedReport(unittest.TestCase):
    """build_tennis.py --unrated-report (25 Oct 2026): advisory evidence for
    bug 14, counts only; nothing is seeded or applied."""

    def test_counts_dropped_results_per_month_and_sets_the_other_tour_apart(self):
        ratings = {"atp": {"ratings": {"Ann Able": player(), "Bea Bold": player()}, "archive": BOUNDARY},
                   "wta": {"ratings": {"Cat Clay": player(), "Dee Dune": player()}, "archive": BOUNDARY}}
        atp = {}
        BT.add_results(atp, [
            res(1, "2026-05-01", "Ann Able", "Bea Bold"),            # before the boundary: not counted
            res(2, "2026-07-01", "Ann Able", "Bea Bold"),            # both rated
            res(3, "2026-07-02", "Ann Able", "Zed Unknown", note=None),             # dropped
            res(4, "2026-08-02", "Zed Unknown", "Yan Nobody"),       # dropped, both unrated
            res(5, "2026-08-03", "Cat Clay", "Dee Dune"),            # the other tour's (combined event)
            res(6, "2026-08-04", "Ann Able", "Bea Bold", note="Able bt Bold w/o"),  # walkover: not counted
        ])
        atp["3"]["round"] = "Qualifying Round 1"
        with mock.patch.object(BT, "load_history", lambda tour: (atp if tour == "atp" else {}, date(2026, 10, 1))):
            rep = BT.unrated_report(ratings)
        t = rep["atp"]
        self.assertEqual((t["results"], t["dropped"], t["otherTour"]), (4, 2, 1))
        self.assertEqual(t["months"]["2026-07"], {"results": 2, "dropped": 1, "otherTour": 0, "bothUnrated": 0, "qualifying": 1})
        self.assertEqual(t["months"]["2026-08"], {"results": 2, "dropped": 1, "otherTour": 1, "bothUnrated": 1, "qualifying": 0})
        self.assertEqual(t["players"], [("Zed Unknown", 2), ("Yan Nobody", 1)])
        self.assertEqual(rep["wta"]["results"], 0)
        self.assertEqual(ratings["atp"]["ratings"]["Ann Able"], player())    # nothing applied
        import io
        buf = io.StringIO()
        BT.print_unrated_report(rep, file=buf)
        self.assertIn("ATP: 2 of 3 own-tour results", buf.getvalue())
        self.assertIn("advisory", buf.getvalue())


class ArchiveBoundary(unittest.TestCase):

    def test_boundary_is_the_last_start_and_the_pairs_of_its_last_fortnight(self):
        rows = [{"date": "20260501", "winner": "Old One", "loser": "Old Two"},
                {"date": "20260524", "winner": "Bea Bold", "loser": "Ann Able"},
                {"date": "20260601", "winner": "Cat Clay", "loser": "Dee Dune"}]
        b = TT.archive_boundary(rows)
        self.assertEqual(b["through"], "2026-06-01")
        self.assertEqual(b["pairs"], [["Ann Able", "Bea Bold"], ["Cat Clay", "Dee Dune"]])
        self.assertEqual(TT.BOUNDARY_DAYS, BT.BOUNDARY_DAYS)


if __name__ == "__main__":
    unittest.main()
