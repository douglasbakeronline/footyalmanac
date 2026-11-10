"""The briefings (10 Nov 2026): four pushes a UK day at Douglas's betting
times (07:40, 12:00, 17:00, 22:15 builds), each from the first build at or
after its hour, the latest due slot only, never twice."""
import json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import notify

AM = datetime(2026, 11, 10, 7, 45, tzinfo=timezone.utc)


def leg(pick, p, when, list_=True, id_=None):
    return {"pick": pick, "pModel": p, "when": when, "list": list_, "event": f"{pick} v X", "sport": "ncaab",
            "id": id_ or pick, "home": pick, "away": "X"}


OG = {"pool": {"2026-11-10": [leg("Done Early", .99, "2026-11-10T01:00Z"), leg("Georgetown", .91, "2026-11-10T23:30Z"),
                              leg("Not Listed", .99, "2026-11-10T20:00Z", list_=False), leg("Carle", .80, "2026-11-10T18:00Z"),
                              leg("Alves", .77, "2026-11-10T18:00Z"), leg("Lunch Game", .86, "2026-11-10T13:00Z")],
               "2026-11-09": [leg("Late Tip", .93, "2026-11-10T00:30Z")],
               "2026-11-11": [leg("Oregon Ducks", .97, "2026-11-11T03:00Z"), leg("Afternoon", .95, "2026-11-11T15:00Z")]},
      "days": [{"date": "2026-11-10", "groups": [{"name": "Card 2x", "status": "new", "bookOdds": 2.1},
                                                 {"name": "Card 3x", "status": "new", "wide": True}]}]}
DATA = {"days": [{"date": "2026-11-10", "games": [{"home": {"name": "Leeds"}, "away": {"name": "Hull"},
                                                   "kickoff": "2026-11-10T19:45Z", "edge": {"side": "h", "odds": 1.62}}]}]}
IDX = ({}, {}, {"Done Early": {"winner": "Done Early"}, "Late Tip": {"winner": "X"}})


class Content(unittest.TestCase):
    def test_morning(self):
        title, body = notify.briefing(OG, DATA, AM, "morning")
        self.assertEqual(title, "Daily List, Tue 10 Nov: 6 picks")
        self.assertIn("Group A: Georgetown 91% 23:30; Lunch Game 86% 13:00", body)   # started picks are out
        self.assertNotIn("Not Listed", body)
        self.assertIn("Model treble", body)
        self.assertIn("Edge: 1 football pick (Leeds 1.62)", body)
        self.assertIn("Card: 1 group open, Hill 2.10", body)                       # the wider filler not counted
        self.assertNotIn("so far", body)

    def test_lunch_tally_and_what_is_left(self):
        title, body = notify.briefing(OG, DATA, datetime(2026, 11, 10, 12, 5, tzinfo=timezone.utc), "lunch", IDX)
        self.assertEqual(title, "Lunchtime, Tue 10 Nov: 4 list picks to start")
        self.assertIn("Today so far: 1 won, 1 lost", body)
        self.assertIn("Strongest to come: Georgetown 91% 23:30; Lunch Game 86% 13:00", body)

    def test_night_reaches_the_overnight_slate_only(self):
        title, body = notify.briefing(OG, DATA, datetime(2026, 11, 10, 22, 20, tzinfo=timezone.utc), "night", IDX)
        self.assertEqual(title, "Tonight and overnight: 2 list picks before 8am")
        self.assertIn("Oregon Ducks 97% 03:00", body)
        self.assertNotIn("Afternoon", body)
        self.assertNotIn("Edge", body)                                           # 19:45 has kicked off

    def test_nothing_to_back(self):
        self.assertIsNone(notify.briefing({"pool": {}}, {}, AM, "morning"))


class Slots(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.path = os.path.join(self.d, "briefed.json")

    def tearDown(self):
        shutil.rmtree(self.d)

    def at(self, h, m=0, day=10):
        return datetime(2026, 11, day, h, m, tzinfo=timezone.utc)

    def test_each_slot_once_latest_only(self):
        self.assertIsNone(notify.due_slot(self.at(5, 15), self.path))
        self.assertEqual(notify.due_slot(self.at(7, 45), self.path), "morning")
        notify.mark_sent(self.at(7, 45), "morning", self.path)
        self.assertIsNone(notify.due_slot(self.at(9, 0), self.path))
        self.assertEqual(notify.due_slot(self.at(12, 5), self.path), "lunch")
        notify.mark_sent(self.at(12, 5), "lunch", self.path)
        # the 17:00 build failed: the 19:30 build sends the evening, not the lunch again
        self.assertEqual(notify.due_slot(self.at(19, 35), self.path), "evening")
        notify.mark_sent(self.at(19, 35), "evening", self.path)
        self.assertEqual(notify.due_slot(self.at(22, 20), self.path), "night")
        notify.mark_sent(self.at(22, 20), "night", self.path)
        self.assertIsNone(notify.due_slot(self.at(23, 50), self.path))
        # a new day starts clean
        self.assertEqual(notify.due_slot(self.at(7, 41, day=11), self.path), "morning")

    def test_a_late_morning_build_skips_to_lunch(self):
        self.assertEqual(notify.due_slot(self.at(12, 30), self.path), "lunch")


if __name__ == "__main__":
    unittest.main()
