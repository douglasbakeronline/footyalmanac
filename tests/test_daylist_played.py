"""Results on every sport's tab (20 Nov 2026): daylist.board_results keys
each graded game as the page's rows are (lbKey) and keeps the UK day and
the day before only."""
import unittest
import daylist


class BoardResults(unittest.TestCase):
    def test_keys_and_days(self):
        record = {"days": [
            {"date": "2026-11-20", "games": [{"home": "Iskra", "away": "Spartanii", "result": [1, 0], "won": True}]},
            {"date": "2026-11-17", "games": [{"home": "Old", "away": "Gone", "result": [0, 2], "won": False}]}]}
        trec = {"graded": [{"date": "2026-11-19", "playerA": "A B", "playerB": "C D", "ok": False,
                            "void": False, "winner": "C D", "note": "C D bt A B 6-4 6-4"}]}
        srec = {"days": [{"date": "2026-11-20", "games": [
            {"sport": "nba", "home": "Spurs", "away": "Clippers", "ok": True, "score": [124, 112]},
            {"sport": "nba", "home": "Not", "away": "Graded", "ok": None}]}]}
        r = daylist.board_results("2026-11-20", (record, trec, srec))
        self.assertEqual(r["football|iskra|spartanii"], {"ok": True, "void": False, "score": "1-0"})
        self.assertFalse(r["tennis|a b|c d"]["ok"])
        self.assertEqual(r["nba|spurs|clippers"]["score"], "124-112")
        self.assertNotIn("football|old|gone", r)
        self.assertNotIn("nba|not|graded", r)


if __name__ == "__main__":
    unittest.main()
