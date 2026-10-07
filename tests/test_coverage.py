"""Daily List coverage: what each day's list was chosen from (7 Oct 2026)."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import daylist as DL


def fb(league, home, list_=False, why="below", conf=0.6):
    return ("football", {"league": league, "date": "2026-10-10", "kickoff": "2026-10-10T14:00:00Z",
                         "home": home, "away": home + " B", "p": {"h": conf, "d": 0.2, "a": 0.8 - conf},
                         "confidence": conf, "list": list_, "reserve": False, "why": None if list_ else why,
                         "published": "2026-10-10T06:00:00Z"})


class Coverage(unittest.TestCase):
    def test_counts_every_game_and_why(self):
        arch = [fb("en.1", "A", True, conf=0.85), fb("en.1", "B"), fb("afc.1", "C", why="cup"),
                fb("en.faq", "D", why="new"), fb("en.2", "E")]
        with tempfile.TemporaryDirectory() as d:
            now = datetime(2026, 10, 10, 9, tzinfo=timezone.utc)
            json.dump({"generated": "2026-10-10T08:00:00", "health": {"apiFootball": {"daysMissing": ["2026-10-10"]}}},
                      open(os.path.join(d, "data.json"), "w"))
            cv = DL.coverage("2026-10-10", arch, d, now)
        f = cv["sports"]["football"]
        self.assertEqual((f["games"], f["comps"], f["list"]), (5, 4, 1))
        self.assertEqual(f["why"], {"below": 2, "cup": 1, "new": 1})
        self.assertTrue(any("API-Football fixtures not fetched for 2026-10-10" in g for g in cv["gaps"]))
        self.assertTrue(any(g.startswith("tennis: no board file") for g in cv["gaps"]))

    def test_other_day_ignored(self):
        cv = DL.coverage("2026-10-11", [fb("en.1", "A")], tempfile.gettempdir(),
                         datetime(2026, 10, 11, 9, tzinfo=timezone.utc))
        self.assertNotIn("football", cv["sports"])


if __name__ == "__main__":
    unittest.main()
