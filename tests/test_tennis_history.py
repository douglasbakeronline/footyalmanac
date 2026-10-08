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
        self.assertEqual(todo, [("Cat Clay", "Ann Able"), ("Cat Clay", "Dee Dune"),
                                ("Bea Bold", "Ann Able")])
        self.assertEqual(counts, {"applied": 3, "unmatched": 0, "archive": 1, "walkover": 0})

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
        self.assertEqual(todo, [("Dee Dune", "Cat Clay")])

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
            for w, l in todo:
                BT.apply_result(pool, w, l, "Hard", 250)
            ratings.append(pool["Cat Clay"]["overall"])
        self.assertEqual(ratings[0], ratings[1])
        self.assertGreater(ratings[0], POOL["Cat Clay"]["overall"])
        self.assertEqual(POOL["Cat Clay"]["overall"], 1800.0)   # the snapshot itself is never changed


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
