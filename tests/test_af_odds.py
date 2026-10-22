"""API-Football prices for every fixture (22 Oct 2026): parsing, the paged
date read and its cache, and matching to board fixtures. No network."""
import os, sys, tempfile, unittest
from datetime import date, datetime, timezone
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import odds as O
import sources as S


def item(fid, books):
    return {"fixture": {"id": fid}, "bookmakers": [
        {"name": n, "bets": [{"id": 1, "values": [{"value": "Home", "odd": h}, {"value": "Draw", "odd": d},
                                                  {"value": "Away", "odd": a}]},
                             {"id": 5, "values": [{"value": "Over 2.5", "odd": "1.9"}]}]}
        for n, (h, d, a) in books]}


class Parse(unittest.TestCase):

    def test_average_best_and_books_from_match_winner_only(self):
        rows = O.af_parse_odds([item(7, [("A", ("1.50", "4.0", "6.0")), ("B", ("1.60", "3.8", "5.5"))])])
        r = rows["7"]
        self.assertEqual(r["avg"], [1.55, 3.9, 5.75])
        self.assertEqual(r["max"], [1.6, 4.0, 6.0])
        self.assertEqual(r["books"], 2)

    def test_a_fixture_missing_a_side_is_left_out(self):
        bad = {"fixture": {"id": 8}, "bookmakers": [{"name": "A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.5"}, {"value": "Away", "odd": "6"}]}]}]}
        self.assertEqual(O.af_parse_odds([bad]), {})


class DateRead(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.p1 = mock.patch.object(S, "AF_CACHE_DIR", self.dir); self.p1.start()
        os.environ["API_FOOTBALL_KEY"] = "test"
        self.calls = []

    def tearDown(self):
        self.p1.stop(); os.environ.pop("API_FOOTBALL_KEY", None)

    def fake(self, pages):
        def get(path):
            self.calls.append(path)
            n = int(path.rsplit("page=", 1)[1])
            S.AF_PAGING[path] = {"current": n, "total": len(pages)}
            return pages[n - 1]
        return get

    def test_reads_every_page_then_serves_the_cache(self):
        pages = [[item(1, [("A", ("1.5", "4", "6"))])], [item(2, [("A", ("2.0", "3.4", "3.6"))])]]
        d, now = date(2026, 10, 24), datetime(2026, 10, 22, 12, tzinfo=timezone.utc).timestamp()
        with mock.patch.object(S, "_af_get", self.fake(pages)):
            rows = O.af_odds_day(d, now=now)
            self.assertEqual(set(rows), {"1", "2"})
            self.assertEqual(len(self.calls), 2)
            O.af_odds_day(d, now=now + 60)
            self.assertEqual(len(self.calls), 2)             # cached
            O.af_odds_day(d, now=now + O.AF_ODDS_TTL_FAR + 1)
            self.assertEqual(len(self.calls), 4)             # aged out, read again

    def test_an_empty_answer_keeps_the_last_copy(self):
        d, now = date(2026, 10, 24), datetime(2026, 10, 22, 12, tzinfo=timezone.utc).timestamp()
        with mock.patch.object(S, "_af_get", self.fake([[item(1, [("A", ("1.5", "4", "6"))])]])):
            O.af_odds_day(d, now=now)
        with mock.patch.object(S, "_af_get", self.fake([[]])):
            rows = O.af_odds_day(d, now=now + O.AF_ODDS_TTL_FAR + 1)
        self.assertEqual(set(rows), {"1"})

    def test_no_key_no_calls(self):
        os.environ.pop("API_FOOTBALL_KEY")
        with mock.patch.object(S, "_af_get", self.fake([[]])):
            self.assertEqual(O.af_odds_day(date(2026, 10, 24)), {})
        self.assertEqual(self.calls, [])


class Matching(unittest.TestCase):
    T = datetime(2026, 10, 24, 14, tzinfo=timezone.utc)
    IDX = [("11", T, "Hamilton Academical", "East Fife"),
           ("12", T, "Bodo/Glimt", "Valerenga"),
           ("13", T.replace(hour=19), "Hamilton Wanderers", "East Fife Reserves")]

    def test_names_and_kickoff(self):
        out = O.match_af([("a", self.T, "2026-10-24", "Hamilton Academical", "East Fife"),
                          ("b", self.T, "2026-10-24", "Bodø/Glimt", "Vålerenga")], self.IDX)
        self.assertEqual(out, {"a": "11", "b": "12"})

    def test_kickoff_too_far_apart_is_not_matched(self):
        out = O.match_af([("a", self.T.replace(hour=18), "2026-10-24", "Hamilton Academical", "East Fife")],
                         self.IDX[:1])
        self.assertEqual(out, {})

    def test_wrong_teams_not_matched(self):
        out = O.match_af([("a", self.T, "2026-10-24", "Celtic", "Rangers")], self.IDX)
        self.assertEqual(out, {})


if __name__ == "__main__":
    unittest.main()
