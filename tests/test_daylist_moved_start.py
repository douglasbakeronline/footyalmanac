"""10 Nov 2026: a game ESPN first listed at a stand-in time and then moved to
another day is pinned on its new day only, not left on the old day reading
"Result due"."""
import os, sys, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import daylist


def row(when, published):
    return ("sport", {"id": "401929354", "sport": "ncaab", "label": "NCAA", "feed": "basketball/mens-college-basketball",
                      "when": when, "home": "Texas Southern Tigers", "away": "College of Biblical Studies Ambassadors",
                      "pick": "Texas Southern Tigers", "confidence": 0.9, "reserve": True, "published": published})


ARCH = [row("2026-11-10T05:00Z", "2026-11-04T22:28:46Z"), row("2026-11-11T00:00Z", "2026-11-06T23:50:29Z")]


class MovedStart(unittest.TestCase):
    def test_not_pinned_on_the_old_day(self):
        self.assertEqual(daylist.pinned("2026-11-10", ARCH, datetime(2026, 11, 10, 8, 50, tzinfo=timezone.utc)), [])

    def test_pinned_on_the_new_day(self):
        out = daylist.pinned("2026-11-11", ARCH, datetime(2026, 11, 11, 1, 0, tzinfo=timezone.utc))
        self.assertEqual([i["start"] for i in out], ["2026-11-11T00:00:00Z"])

    def test_a_game_that_never_moved_still_pins(self):
        out = daylist.pinned("2026-11-10", ARCH[:1], datetime(2026, 11, 10, 8, 50, tzinfo=timezone.utc))
        self.assertEqual(len(out), 1)


if __name__ == "__main__":
    unittest.main()
