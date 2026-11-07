"""7 Nov 2026: a tennis price is judged against the start ESPN recorded for
the match, not only when the archived time is a placeholder. Andreescu v
Giovannini (Cali, 5 Nov): listed 19:00, began 19:25, the row re-stamped at
19:09 by a build that saw it still "pre", refused as late, the Card leg pending."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_tennis as ST


class LateStart(unittest.TestCase):
    def test_recorded_start_replaces_scheduled(self):
        m = {"id": "186729", "date": "2026-11-05", "time": "19:00", "published": "2026-11-05T19:09:52Z"}
        self.assertEqual(ST.start_of(m, {"186729": "2026-11-05T19:25:00Z"}), "2026-11-05T19:25:00Z")

    def test_no_recorded_start_keeps_scheduled(self):
        m = {"id": "1", "date": "2026-11-05", "time": "19:00"}
        self.assertEqual(ST.start_of(m, {}), ST.kickoff(m))

    def test_recorded_start_on_another_day_ignored(self):
        m = {"id": "1", "date": "2026-11-05", "time": "19:00"}
        self.assertEqual(ST.start_of(m, {"1": "2026-11-06T10:00:00Z"}), ST.kickoff(m))


if __name__ == "__main__":
    unittest.main()
