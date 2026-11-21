"""Played today and yesterday (20-21 Nov 2026): daylist.played_today keeps
every started game of the UK day and the day before, list or not, with its
result and its UK day, and leaves games still to start out."""
import json, os, tempfile, unittest
from datetime import datetime, timezone
import daylist


def game(gid, when, home, away, ok=None):
    return {"id": gid, "sport": "nba", "label": "NBA", "when": when, "home": home, "away": away,
            "pick": home, "pHome": 0.7, "confidence": 0.7, "tier": "Strong",
            "published": "2026-11-19T10:00:00Z"}


class Played(unittest.TestCase):
    def test_two_days_started_only(self):
        with tempfile.TemporaryDirectory() as here:
            os.makedirs(os.path.join(here, "predictions-sports"))
            y = [game("1", "2026-11-20T19:00Z", "Spurs", "Clippers")]
            t = [game("2", "2026-11-21T00:30Z", "Heat", "Nets"), game("3", "2026-11-21T20:00Z", "Lakers", "Suns")]
            for d, gs in (("2026-11-20", y), ("2026-11-21", t)):
                json.dump(gs, open(os.path.join(here, "predictions-sports", d + ".json"), "w"))
            now = datetime(2026, 11, 21, 1, 0, tzinfo=timezone.utc)
            srec = {"days": [{"date": "2026-11-20", "games": [dict(y[0], score=[124, 112], ok=True)]}]}
            arch = daylist.read_archives("2026-11-21", here)
            out = daylist.played_today("2026-11-21", arch, now, ({}, {}, srec), here)
        got = {(p["home"], p["day"], p["status"]) for p in out}
        self.assertIn(("Spurs", "2026-11-20", "won"), got)
        self.assertIn(("Heat", "2026-11-21", "started"), got)
        self.assertNotIn("Lakers", {p["home"] for p in out})
        self.assertEqual(len([p for p in out if p["home"] == "Spurs"]), 1)


if __name__ == "__main__":
    unittest.main()
