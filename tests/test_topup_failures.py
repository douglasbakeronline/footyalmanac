import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sources

THROUGH = date(2026, 10, 10)
UNTIL = date(2026, 10, 16)
BAD = date(2026, 10, 14)


def event_for(day):
    return {"day": day}


class TopupFailureTests(unittest.TestCase):
    def run_topup(self, through, bad, rows=()):
        tmp = tempfile.mkdtemp()
        calls = []

        def fake_day(slug, day, timeout, errs, pause=1.0):
            calls.append(day)
            if day in bad:
                errs.append(f"{slug} {day}: URLError down")
                return []
            return [event_for(day)]

        def fake_row(ev):
            d = ev["day"].isoformat()
            return {"date": d, "home": "A", "away": "B", "hg": 1, "ag": 0}

        with mock.patch.object(sources, "CURRENT_DIR", tmp), \
                mock.patch.object(sources, "ESPN_SLUGS", {"x.1": ["x.1"]}), \
                mock.patch.object(sources, "_espn_day", fake_day), \
                mock.patch.object(sources, "_row", fake_row), \
                mock.patch.object(sources, "season_window", lambda s: (date(2026, 8, 1), date(2027, 5, 30))), \
                mock.patch.object(sources.time, "sleep", lambda s: None):
            if through:
                json.dump({"through": through.isoformat(), "rows": list(rows)},
                          open(os.path.join(tmp, "x.1-2026-27.json"), "w"))
            log = []
            sources.topup_current("x.1", "2026-27", until=UNTIL, log=log)
            doc = json.load(open(os.path.join(tmp, "x.1-2026-27.json")))
        return doc, log

    def test_failed_day_is_not_marked_walked(self):
        doc, log = self.run_topup(THROUGH, {BAD})
        self.assertEqual(doc["through"], (BAD - timedelta(days=1)).isoformat())
        self.assertTrue(any("will be retried" in l for l in log))

    def test_clean_walk_advances_to_until(self):
        doc, _ = self.run_topup(THROUGH, set())
        self.assertEqual(doc["through"], UNTIL.isoformat())

    def test_total_outage_keeps_old_marker(self):
        bad = {THROUGH - timedelta(days=3) + timedelta(days=i) for i in range(12)}
        doc, _ = self.run_topup(THROUGH, bad)
        self.assertEqual(doc["through"], THROUGH.isoformat())

    def test_dead_slug_without_cache_is_saved_as_before(self):
        bad = {date(2026, 8, 1) + timedelta(days=i) for i in range(90)}
        doc, _ = self.run_topup(None, bad)
        self.assertEqual(doc["through"], UNTIL.isoformat())


if __name__ == "__main__":
    unittest.main()
