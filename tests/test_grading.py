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
        self.assertEqual(ST.outcome({}, {"note": "A bt B 6-4 ret", "winner": "A", "pool": {}})[0], "graded")


if __name__ == "__main__":
    unittest.main()
