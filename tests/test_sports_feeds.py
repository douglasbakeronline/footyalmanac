"""ESPN feeds added 6 Oct 2026: NHL, college football and basketball, WNBA, NRL."""
import os, sys, unittest
from datetime import date
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports as SP


class Feeds(unittest.TestCase):
    def test_new_sports_registered_on_their_own(self):
        for k in ("nhl", "cfb", "ncaab", "wnba", "nrl"):
            self.assertIn(k, SP.SPORTS)
        # the NBA and union rugby keep their own feeds, so their fitted constants do not move
        self.assertEqual([f["path"] for f in SP.SPORTS["nba"]["feeds"]], ["basketball/nba"])
        self.assertNotIn("rugby-league/3", [f["path"] for f in SP.SPORTS["rugby"]["feeds"]])

    def test_college_basketball_asks_for_all_of_division_one(self):
        seen = []
        def fake(req, timeout=25):
            seen.append(req.full_url)
            raise OSError("offline")
        with mock.patch.object(SP.urllib.request, "urlopen", side_effect=fake):
            f = SP.SPORTS["ncaab"]["feeds"][0]
            SP.upcoming("ncaab", date(2026, 12, 5), 1)
        self.assertTrue(seen and all("groups=50" in u for u in seen))

    def test_rugby_world_cup_covers_november_for_2027(self):
        """RWC 2027 runs 1 Oct to 13 Nov (25 Oct 2026); the feed was Sep-Oct only."""
        wc = next(f for f in SP.SPORTS["rugby"]["feeds"] if f["path"] == "rugby/164205")
        for m in (9, 10, 11):
            self.assertIn(m, wc["months"])
        self.assertEqual(wc["days"], SP.ALL_DAYS)
        # the Rugby Championship feed stays registered, dead or not
        self.assertIn("rugby/244293", [f["path"] for f in SP.SPORTS["rugby"]["feeds"]])


if __name__ == "__main__":
    unittest.main()
