"""10 Nov 2026: the results walk reaches today. ESPN files a late tip-off
under its US Eastern day, which the UK build calls today, so walking only to
yesterday left finished games ungraded ("Result due") for a day."""
import os, shutil, sys, tempfile, unittest
from datetime import date, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports


class WalkToday(unittest.TestCase):
    def test_default_walk_asks_for_today_and_keeps_finals(self):
        d = tempfile.mkdtemp()
        asked = []
        today = date.today()
        def day(path, when, errs, q=""):
            asked.append(when)
            if when == today:
                return [{"final": True, "id": "g1"}, {"final": False, "id": "g2"}]
            return []
        feed = {"path": "basketball/test", "label": "T", "pool": "t", "months": tuple(range(1, 13)), "days": tuple(range(7))}
        try:
            with mock.patch.object(sports, "HIST_DIR", d), mock.patch.object(sports, "_day", day), \
                 mock.patch.object(sports, "_game", lambda ev, f: {**ev, "when": "2026-11-10T05:00Z"}), \
                 mock.patch.object(sports, "_hist_path", lambda f: os.path.join(d, "t.json")), \
                 mock.patch.object(sports, "HIST_START", today - timedelta(days=2)):
                n, _ = sports.walk_history(feed, sleep=0)
                games, through = sports.load_history(feed)
        finally:
            shutil.rmtree(d)
        self.assertEqual(asked[-1], today)
        self.assertEqual(through, today)
        self.assertEqual(set(games), {"g1"})          # the game still in play is not kept


if __name__ == "__main__":
    unittest.main()
