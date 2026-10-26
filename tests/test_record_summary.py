"""The page no longer inlines record.json (26 Oct 2026): build.py writes a
small summary into data.js / dashboard.html and the full record to
record-data.js, which index.html fetches when "How it went" opens."""
import json
import os
import re
import unittest

import build

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RecordSummary(unittest.TestCase):
    def test_summary_carries_what_first_paint_reads(self):
        record = {"generated": "x", "ladder": [{"min": 0.7, "k": 3, "name": "Strong", "was": "79%"}],
                  "tiers": [{"name": "Strong", "n": 1, "hit": 1.0}], "overall": {"n": 10, "accuracy": 0.8},
                  "list": {"n": 4, "correct": 3}, "bands": [], "range": {"from": "a", "to": "b"},
                  "listDays": [{"date": "2026-10-25", "games": [
                      {"home": "A", "away": "B", "pick": "h", "actual": "h", "confidence": 0.9, "tier": "Strong",
                       "k": 3, "result": [2, 0], "ok": True, "won": True, "drawRead": False,
                       "formH": ["lots"], "p": [0.9, 0.05, 0.05]}]}],
                  "days": [{"date": "2026-10-25", "games": [{"big": "x" * 1000}]}],
                  "byLeague": {"en.1": {"n": 1}}}
        s = build.record_summary(record, {"list": {"n": 2, "correct": 2}, "bySport": {"nfl": {"n": 5, "correct": 3, "days": []}}},
                                 {"list": {"n": 1, "correct": 0}})
        self.assertEqual(s["ladder"], record["ladder"])
        self.assertEqual(s["tiers"], record["tiers"])
        self.assertEqual(s["overall"], record["overall"])
        self.assertEqual(s["list"], record["list"])
        self.assertEqual(s["listRecent"][0]["d"], "2026-10-25")
        self.assertEqual(s["listRecent"][0]["home"], "A")
        self.assertNotIn("formH", s["listRecent"][0])
        self.assertNotIn("days", s)
        self.assertNotIn("byLeague", s)
        self.assertNotIn("listDays", s)
        self.assertEqual(s["sports"]["bySport"]["nfl"], {"n": 5, "correct": 3})
        self.assertEqual(s["tennis"]["list"], {"n": 1, "correct": 0})
        self.assertLess(len(json.dumps(s)), 2000)

    def test_summary_without_records(self):
        self.assertIsNone(build.record_summary(None, None, None))
        self.assertEqual(build.record_summary(None, None, {"list": {"n": 1}}), {"tennis": {"list": {"n": 1}}})

    def test_live_record_summary_is_small(self):
        path = os.path.join(HERE, "record.json")
        if not os.path.exists(path):
            self.skipTest("no record.json")
        record = json.load(open(path))
        s = build.record_summary(record)
        self.assertIn("ladder", s)
        self.assertLess(len(json.dumps(s, separators=(",", ":"))), 40_000)

    def test_page_loads_record_on_demand(self):
        html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
        self.assertIn('"record-data.js"', html)
        self.assertIn("__RECORD_SUMMARY__", html)
        # none of the records is a synchronous script tag any more
        for src in ("record-data.js", "tennis-record.js", "sports-record.js"):
            self.assertIsNone(re.search(r'<script src="%s"></script>' % re.escape(src), html), src)
        # the build still inlines data.js in place of its script tag
        self.assertIn('<script src="data.js"></script>', html)


if __name__ == "__main__":
    unittest.main()
