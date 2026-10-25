"""The build and the grader anchor on the UK date, not UTC (25 Oct 2026,
bug 22 of claude/full-review-2026-10-25.md)."""
import os, sys, unittest
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E


class UkToday(unittest.TestCase):
    def test_summer_midnight_utc_is_already_tomorrow_in_london(self):
        if E._ZoneInfo is None:
            self.skipTest("no zoneinfo on this Python")
        self.assertEqual(E.uk_today(datetime(2026, 7, 14, 0, 10, tzinfo=timezone.utc)), date(2026, 7, 14))
        self.assertEqual(E.uk_today(datetime(2026, 7, 13, 23, 30, tzinfo=timezone.utc)), date(2026, 7, 14))

    def test_winter_matches_utc(self):
        if E._ZoneInfo is None:
            self.skipTest("no zoneinfo on this Python")
        self.assertEqual(E.uk_today(datetime(2026, 12, 13, 23, 30, tzinfo=timezone.utc)), date(2026, 12, 13))

    def test_default_is_a_date(self):
        self.assertIsInstance(E.uk_today(), date)

    def test_build_and_score_use_it(self):
        import build, score
        for mod in (build, score):
            src = open(mod.__file__).read()
            self.assertIn("E.uk_today()", src, mod.__name__)
        self.assertNotIn("else date.today()", open(build.__file__).read())
        self.assertNotIn("today = date.today().isoformat()", open(score.__file__).read())


if __name__ == "__main__":
    unittest.main()
