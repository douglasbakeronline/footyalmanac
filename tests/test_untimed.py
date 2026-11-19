"""build.fill_untimed: board rows with no kick-off take API-Football's date
and time (19 Nov 2026, #417). All or nothing on names; one fixture only."""
import os, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B
import sources as S

START = date(2026, 11, 19)


def row(h, a, d, time=None, hg=None):
    return {"date": d, "time": time, "round": None, "home": h, "away": a, "hg": hg, "ag": hg}


def af(h, a, d, t):
    return {"date": d, "time": t, "utc": True, "home": h, "away": a, "hg": None, "ag": None}


class FillUntimed(unittest.TestCase):
    def rows(self):
        return [row("Athletic Club", "RCD Espanyol", "2026-11-22"),
                row("Real Madrid CF", "RC Celta de Vigo", "2026-11-22")]

    def test_takes_date_and_time(self):
        rows = self.rows()
        n, bad = B.fill_untimed(rows, [af("Athletic Club", "Espanyol", "2026-11-20", "20:00"),
                                       af("Real Madrid", "Celta Vigo", "2026-11-21", "15:15")], START)
        self.assertEqual((n, bad), (2, []))
        self.assertEqual((rows[0]["date"], rows[0]["time"], rows[0]["utc"]), ("2026-11-20", "20:00", True))
        self.assertEqual((rows[1]["date"], rows[1]["time"]), ("2026-11-21", "15:15"))
        self.assertEqual(rows[0]["timeFrom"], "apifootball")

    def test_unmatched_name_changes_nothing(self):
        rows = self.rows()
        n, bad = B.fill_untimed(rows, [af("Athletic Club", "Espanyol", "2026-11-20", "20:00"),
                                       af("Zzyzx Rovers", "Celta Vigo", "2026-11-21", "15:15")], START)
        self.assertEqual(n, 0)
        self.assertTrue(bad)
        self.assertIsNone(rows[0]["time"])
        self.assertEqual(rows[0]["date"], "2026-11-22")

    def test_timed_played_and_far_rows_untouched(self):
        rows = [row("Athletic Club", "RCD Espanyol", "2026-11-22", time="18:00"),
                row("Real Madrid CF", "RC Celta de Vigo", "2026-11-10", hg=1),
                row("Real Madrid CF", "RC Celta de Vigo", "2026-11-22")]
        n, _ = B.fill_untimed(rows, [af("Athletic Club", "Espanyol", "2026-11-20", "20:00"),
                                     af("Real Madrid", "Celta Vigo", "2026-12-20", "15:15")], START)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["date"], "2026-11-22")
        self.assertIsNone(rows[2]["time"])

    def test_pair_listed_twice_in_window_left_alone(self):
        rows = self.rows()
        n, _ = B.fill_untimed(rows, [af("Real Madrid", "Celta Vigo", "2026-11-21", "15:15"),
                                     af("Real Madrid", "Celta Vigo", "2026-11-23", "15:15"),
                                     af("Athletic Club", "Espanyol", "2026-11-20", "20:00")], START)
        self.assertEqual(n, 1)
        self.assertIsNone(rows[1]["time"])

    def test_no_af_rows(self):
        self.assertEqual(B.fill_untimed(self.rows(), [], START), (0, []))


class Pick(unittest.TestCase):
    def fx(self, status, country="Spain"):
        return {"fixture": {"date": "2026-11-20T20:00:00+00:00", "status": {"short": status}},
                "league": {"country": country}, "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
                "score": {"fulltime": {}}}

    def test_tbd_dropped(self):
        self.assertEqual(S.af_untimed_pick("es.1", [self.fx("TBD")]), [])
        self.assertEqual(len(S.af_untimed_pick("es.1", [self.fx("NS")])), 1)

    def test_wrong_country_dropped(self):
        self.assertEqual(S.af_untimed_pick("es.1", [self.fx("NS", "Italy")]), [])


if __name__ == "__main__":
    unittest.main()
