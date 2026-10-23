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
