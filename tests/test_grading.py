"""Grading edge cases: ties, abandoned games, retirements. Standard library only, no network."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports as SP
import sources as S
import score_tennis as ST


def ev(name, completed=True, hs="2", as_="1"):
    return {"id": "1", "date": "2026-10-03T15:00Z", "season": {"type": 2},
            "competitions": [{"date": "2026-10-03T15:00Z",
                              "status": {"type": {"completed": completed, "name": name, "state": "post"}},
                              "competitors": [
                                  {"homeAway": "home", "score": hs, "team": {"id": "1", "displayName": "H"}},
                                  {"homeAway": "away", "score": as_, "team": {"id": "2", "displayName": "A"}}]}]}


class Grading(unittest.TestCase):
    def test_football_row_ignores_unplayed_statuses(self):
        self.assertEqual(S._row(ev("STATUS_FULL_TIME"))["hg"], 2)
        for n in ("STATUS_ABANDONED", "STATUS_POSTPONED", "STATUS_CANCELED", "STATUS_FORFEIT"):
            self.assertIsNone(S._row(ev(n))["hg"], n)

    def test_football_row_not_graded_after_extra_time_or_penalties(self):
        for n in ("STATUS_FINAL_AET", "STATUS_FINAL_PEN"):
            self.assertIsNone(S._row(ev(n, hs="3", as_="3"))["hg"], n)

    def test_sports_game_ignores_unplayed_statuses(self):
        feed = {"path": "football/nfl", "label": "NFL", "pool": "nfl", "skip": ()}
        self.assertTrue(SP._game(ev("STATUS_FINAL"), feed)["final"])
        for n in ("STATUS_ABANDONED", "STATUS_SUSPENDED", "STATUS_FORFEIT"):
            self.assertFalse(SP._game(ev(n), feed)["final"], n)

    def test_tie_is_void_not_a_miss(self):
        g = {"hn": "H", "an": "A", "hs": 20, "as": 20}
        self.assertIsNone(SP.settle({"pick": "H"}, g))
        self.assertTrue(SP.settle({"pick": "H"}, {**g, "hs": 21})["ok"])
        self.assertFalse(SP.settle({"pick": "H"}, {**g, "as": 21})["ok"])

    def test_retirement_is_a_word(self):
        self.assertTrue(ST.is_retirement("A (ITA) bt B (SLO) 5-7 5-3 ret"))
        self.assertFalse(ST.is_retirement("Matteo Berrettini (ITA) bt X (ESP) 6-4"))
        self.assertFalse(ST.is_retirement(None))

    def test_walkover_and_cancelled_void(self):
        self.assertEqual(ST.outcome({}, {"note": "A bt B w/o"})[0], "void")
        self.assertEqual(ST.outcome({}, {"statusName": "STATUS_CANCELED"})[0], "void")
        self.assertEqual(ST.outcome({}, {"statusName": "STATUS_WALKOVER", "winner": "A", "pool": {}})[0], "void")
        self.assertEqual(ST.outcome({}, {"note": "A bt B 6-4 ret", "winner": "A", "pool": {}})[0], "graded")

    def test_placeholder_start_is_judged_against_the_real_start(self):
        """Bug 15 (25 Oct 2026): a price archived against ESPN's midnight
        New York placeholder is held to the start history-tennis/ recorded."""
        starts = {"185363": "2026-10-15T10:00:00Z", "185999": "2026-10-16T10:00:00Z"}
        ph = {"id": "185363", "date": "2026-10-15", "time": "04:00", "published": "2026-10-15T04:30:00Z"}
        self.assertEqual(ST.start_of(ph, starts), "2026-10-15T10:00:00Z")
        self.assertLess(ph["published"], ST.start_of(ph, starts))
        # a placeholder with no history time keeps today's behaviour
        self.assertEqual(ST.start_of({**ph, "id": "0"}, starts), "2026-10-15T04:00:00Z")
        # a real start in history on a different day (rescheduled) is not used
        self.assertEqual(ST.start_of({**ph, "id": "185999"}, starts), "2026-10-15T04:00:00Z")
        # a scheduled (non-placeholder) time is kept even if history differs
        sched = {**ph, "time": "09:00"}
        self.assertEqual(ST.start_of(sched, starts), "2026-10-15T09:00:00Z")
        # no time at all: the start of the day, as before
        self.assertEqual(ST.start_of({"id": "185363", "date": "2026-10-15"}, starts), "2026-10-15T00:00:00Z")
        # EST placeholder (05:00 UTC) is a placeholder too
        est = {"id": "1", "date": "2026-11-09", "time": "05:00", "published": "2026-11-09T06:00:00Z"}
        self.assertEqual(ST.start_of(est, {"1": "2026-11-09T12:00:00Z"}), "2026-11-09T12:00:00Z")

    def test_history_starts_skips_placeholders_and_untimed_rows(self):
        from unittest import mock
        import build_tennis as B
        rows = {"1": {"id": 1, "date": "2026-10-15", "time": "10:00"},
                "2": {"id": 2, "date": "2026-10-15", "time": "04:00"},
                "3": {"id": 3, "date": "2026-10-15", "time": None}}
        with mock.patch.object(B, "load_history", lambda tour: (rows if tour == "wta" else {}, None)):
            self.assertEqual(ST.history_starts(), {"1": "2026-10-15T10:00:00Z"})

    def test_openfootball_extra_time_uses_the_90_minute_score(self):
        txt = ("Matchday 1\nSun May 4 2025\n"
               "  18:00  Sliema Wanderers   v Birkirkara FC   0-1 a.e.t. (0-0)\n"
               "  19:15  Floriana FC   v Hamrun Spartans   2-4 pen. 0-0 a.e.t. (0-0)\n"
               "  20:00  FC Kosice   v FK Podbrezova   4-5 pen. 2-2 a.e.t. (2-2, 2-1)\n"
               "  20:00  Foo FC   3-2 a.e.t. (2-2, 1-1)  Bar FC\n"
               "  20:00  Baz   1-0  Qux\n")
        rows = S.parse_fixture_txt(txt)
        self.assertEqual([(r["away"], r["hg"], r["ag"]) for r in rows],
                         [("Birkirkara", 0, 0), ("Hamrun Spartans", 0, 0),
                          ("FK Podbrezova", 2, 2), ("Bar", 2, 2), ("Qux", 1, 0)])

    def test_openfootball_extra_time_without_a_90_minute_score_is_not_graded(self):
        rows = S.parse_fixture_txt("Matchday 1\nSun May 4 2025\n  20:00  Foo FC   3-2 a.e.t.  Bar FC\n")
        self.assertEqual((rows[0]["hg"], rows[0]["ag"]), (None, None))


if __name__ == "__main__":
    unittest.main()
