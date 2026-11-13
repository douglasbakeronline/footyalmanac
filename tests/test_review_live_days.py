"""The nightly Card review's live-days section (tools/card_review_post.live_days_section, 13 Nov 2026)."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import card_review_post as C


def day(d, groups, folder):
    with open(os.path.join(folder, f"{d}.json"), "w") as f: json.dump({"date": d, "groups": groups}, f)


class TestLiveDays(unittest.TestCase):
    def test_run_of_empty_days_and_filters(self):
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-09", [{"name": "Card 2x", "rule": 6}, {"name": "Model 2x", "rule": 6}], t)
            day("2026-11-10", [{"name": "Card 2x", "rule": 6, "wide": True}, {"name": "Card 3x", "rule": 6}], t)
            day("2026-11-12", [{"name": "Model 3x", "rule": 8}], t)   # paper only: not a Card group
            day("2026-11-14", [{"name": "Card 2x", "rule": 11}], t)   # today, not finished: not read
            with open(os.path.join(t, "briefed.json"), "w") as f: json.dump({}, f)
            out = "\n".join(C.live_days_section(t, today_="2026-11-14", days=7))
        self.assertIn("2026-11-07 to 2026-11-13", out)
        self.assertIn("Days with a group: 2 of 7; groups 2;", out)
        self.assertIn("last group published for 2026-11-10", out)
        self.assertIn("**3 days running with no Card group (to 2026-11-13).**", out)

    def test_no_flag_under_three_days(self):
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-12", [{"name": "Card 2x", "rule": 11}], t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-14", days=7))
        self.assertNotIn("days running", out)
        self.assertIn("Rules: 11.", out)

    def test_missing_folder(self):
        out = "\n".join(C.live_days_section("/nonexistent", today_="2026-11-14", days=3))
        self.assertIn("Days with a group: 0 of 3", out)
        self.assertIn("no day on file", out)


if __name__ == "__main__":
    unittest.main()
