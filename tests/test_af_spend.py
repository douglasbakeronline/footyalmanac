"""API-Football spend guards (6 Oct 2026)."""
import gzip, json, os, sys, tempfile, time, unittest
from datetime import date, timedelta
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sources as S


class Spend(unittest.TestCase):
    def test_spent_marker_stops_calls(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "_spent_marker", return_value=os.path.join(d, "spent")), \
             mock.patch.object(S, "_AF_SPENT", [False]), mock.patch.object(S, "_AF_CACHE", {}), \
             mock.patch.object(S.urllib.request, "urlopen", side_effect=AssertionError("no call")):
            S._af_mark_spent()
            self.assertEqual(S._af_get("/fixtures?date=2026-10-06"), [])
            self.assertTrue(S._AF_SPENT[0])

    def test_stale_day_beats_empty(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "AF_CACHE_DIR", d), \
             mock.patch.object(S, "_af_get", return_value=[]):
            day = date.today()
            path = os.path.join(d, f"day-{day.isoformat()}.json.gz")
            row = {"fixture": {"id": 1, "date": "2026-10-06T19:00:00+00:00", "status": {"short": "NS"}},
                   "league": {"id": 39, "season": 2026}, "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
                   "goals": {}, "score": {"fulltime": {}}}
            with gzip.open(path, "wt", encoding="utf-8") as fh:
                json.dump({"final": False, "rows": [S._compact(row)]}, fh)
            old = time.time() - 6 * 3600
            os.utime(path, (old, old))
            self.assertEqual(len(S._af_day(day)), 1)


if __name__ == "__main__":
    unittest.main()
