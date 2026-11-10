"""The morning briefing push (10 Nov 2026): once a UK day, from 05:00 UK,
with the day's list, Group A, the model treble, Edge picks and the Card."""
import json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import notify

NOW = datetime(2026, 11, 10, 5, 20, tzinfo=timezone.utc)


def leg(pick, p, when, list_=True, event=None):
    return {"pick": pick, "pModel": p, "when": when, "list": list_, "event": event or f"{pick} v X", "sport": "ncaab"}


OG = {"pool": {"2026-11-10": [leg("Oregon Ducks", .97, "2026-11-11T03:00Z"), leg("UCLA Bruins", .96, "2026-11-11T02:00Z"),
                              leg("Georgetown", .91, "2026-11-10T23:30Z"), leg("Done Early", .99, "2026-11-10T01:00Z"),
                              leg("Not Listed", .99, "2026-11-10T20:00Z", list_=False), leg("Carle", .80, "2026-11-10T18:00Z"), leg("Alves", .77, "2026-11-10T18:00Z")],
               "2026-11-09": [leg("Late Tip", .93, "2026-11-10T00:30Z")]},
      "days": [{"date": "2026-11-10", "groups": [{"name": "Card 2x", "status": "new"}, {"name": "Card 3x", "status": "new", "wide": True}]}]}
DATA = {"days": [{"date": "2026-11-10", "games": [{"home": {"name": "Leeds"}, "away": {"name": "Hull"},
                                                   "edge": {"side": "h", "odds": 1.62}}]}]}


class Briefing(unittest.TestCase):
    def test_content(self):
        title, body = notify.briefing(OG, DATA, NOW)
        self.assertEqual(title, "Daily List, Tue 10 Nov: 5 picks")   # the 11 Nov 02:00 / 03:00 UTC picks belong to tomorrow
        self.assertIn("Group A: Done Early 99%", body)
        self.assertNotIn("Not Listed", body)
        self.assertIn("Late Tip 93% 00:30", body)                   # filed under the 9th, starts today
        self.assertIn("Model treble 56%: Georgetown, Carle, Alves", body)
        self.assertNotIn("Done Early,", body.split("Model treble")[1])   # started picks are not in the treble
        self.assertIn("Edge: 1 football pick (Leeds 1.62)", body)
        self.assertIn("Card: 1 group open", body)                     # the wider-rule filler is not counted

    def test_none_without_list_picks(self):
        self.assertIsNone(notify.briefing({"pool": {}}, {}, NOW))

    def test_once_a_day_from_five(self):
        d = tempfile.mkdtemp(); path = os.path.join(d, "briefed.json")
        try:
            self.assertFalse(notify.brief_due(datetime(2026, 11, 10, 4, 59, tzinfo=timezone.utc), path))
            self.assertTrue(notify.brief_due(NOW, path))
            notify.mark_briefed(NOW, path)
            self.assertFalse(notify.brief_due(datetime(2026, 11, 10, 17, 0, tzinfo=timezone.utc), path))
            self.assertTrue(notify.brief_due(datetime(2026, 11, 11, 5, 15, tzinfo=timezone.utc), path))
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
