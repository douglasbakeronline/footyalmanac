"""The emails on the Mailer tab (mail_page.py, mailer.keep; 25 Nov 2026). Fixtures only, no network."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mailer as M
import mail_page as B


def pin(home, away, conf, status, start, sport="football", **kw):
    return {"sport": sport, "home": home, "away": away, "pick": home, "side": "h", "confidence": conf, "start": start,
            "timed": True, "list": True, "status": status, "comp": "Comp", **kw}


class Days(unittest.TestCase):
    def test_today_only_after_seven(self):
        self.assertEqual(B.mail_days("2026-11-26", 6)[0], "2026-11-25")
        self.assertEqual(B.mail_days("2026-11-26", 7)[0], "2026-11-26")

    def test_never_before_the_first_email_and_a_week_at_most(self):
        self.assertEqual(B.mail_days("2026-11-24", 9), ["2026-11-24", "2026-11-23"])
        xs = B.mail_days("2026-12-20", 9)
        self.assertEqual(len(xs), B.DAYS); self.assertEqual(xs[0], "2026-12-20")


class Keep(unittest.TestCase):
    def test_written_once_never_rewritten(self):
        src = {"daylist": {"date": "2026-11-26", "list": [pin("A", "B", .9, "upcoming", "2026-11-26T19:00:00Z", accuracy={"cumHit": .9})],
                           "early": [], "past": []},
               "groupings": {"days": [{"date": "2026-11-26", "groups": [
                   {"name": "Daily 2x", "seq": 1, "odds": 2.1, "p": .6, "legs": [{"pick": "A", "event": "A v B", "sport": "football",
                                                                                  "when": "2026-11-26T19:00:00Z", "odds": 1.4, "p": .9}]}],
                   "cardShort": {"why": "few", "picks": 1, "need": 3}}], "listBooks": {}, "prices": {}, "contexts": {}},
               "data": {"days": []}}
        now = datetime(2026, 11, 26, 7, 5, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as d:
            p = M.keep("2026-11-26", src, now, {"subject": "S"}, folder=d)
            snap = json.load(open(p))
            self.assertEqual([x["pick"] for x in snap["list"]], ["A"])
            self.assertTrue(snap["list"][0]["A"])
            self.assertEqual(snap["daily"]["legs"][0]["pick"], "A")
            self.assertEqual(snap["cards"], []); self.assertIn("No Card group", snap["cardShort"])
            src["daylist"]["list"] = []
            M.keep("2026-11-26", src, now, {"subject": "S"}, folder=d)
            self.assertEqual(len(json.load(open(p))["list"]), 1)


class Results(unittest.TestCase):
    def setUp(self):
        self.daylist = {"date": "2026-11-26", "list": [pin("A", "B", .9, "won", "2026-11-26T19:00:00Z"),
                                                       pin("C", "D", .86, "lost", "2026-11-26T20:00:00Z"),
                                                       pin("E", "F", .8, "upcoming", "2026-11-26T21:00:00Z")], "past": []}
        self.grec = {"days": [{"date": "2026-11-26", "groups": [{"name": "Daily 2x", "seq": 1, "status": "won", "paid": 2.2, "stake": 1,
                                                                  "legs": [{"pick": "A", "event": "A v B", "status": "won"}]}]}]}

    def test_sent_day_takes_each_result(self):
        snap = {"day": "2026-11-26", "list": [{"sport": "football", "home": h, "away": a, "pick": h, "conf": c}
                                              for h, a, c in (("A", "B", .9), ("C", "D", .86), ("E", "F", .8))],
                "daily": {"name": "Daily 2x", "seq": 1, "odds": 2.2, "stake": 1, "legs": [{"pick": "A", "event": "A v B"}]},
                "cards": [], "cardShort": "none", "edge": [{"pick": "G", "opp": "H", "kickoff": "2026-11-26T15:00:00Z", "odds": 1.4, "best": 1.5}]}
        rec = {"edge": {"days": [{"d": "2026-11-26", "p": [["G", "H", 1.4, 1.5, 1, 1, 9.0]]}]}}
        d = B.from_sent(snap, B.list_results(self.daylist), B.group_results(self.grec), B.edge_results(rec))
        self.assertEqual([x["st"] for x in d["list"]], ["won", "lost", "open"])
        self.assertEqual((d["daily"]["st"], d["daily"]["legs"][0]["st"]), ("won", "won"))
        self.assertEqual(d["edge"][0]["st"], "won")
        s = B.summary(d)
        self.assertEqual((s["list"]["won"], s["list"]["lost"], s["list"]["open"]), (1, 1, 1))

    def test_rebuilt_day_keeps_the_seven_to_seven_window_and_the_college_price(self):
        dl = {"date": "2026-11-27", "list": [pin("Late", "X", .9, "won", "2026-11-27T05:00:00Z"),      # 05:00 UK: the 26th's email
                                             pin("Next", "Y", .9, "upcoming", "2026-11-27T12:00:00Z")],
              "past": [{"date": "2026-11-26", "list": [pin("Early", "Z", .9, "won", "2026-11-26T06:00:00Z"),   # before 07:00: the 25th's
                                                       pin("Cheap", "W", .95, "won", "2026-11-26T20:00:00Z", sport="ncaab"),
                                                       pin("Priced", "V", .95, "won", "2026-11-26T20:00:00Z", sport="ncaab")]}]}
        rows = {B.key("ncaab", "Cheap", "W"): [{"last": {"o": 1.02}}], B.key("ncaab", "Priced", "V"): [{"last": {"o": 1.08}}]}
        d = B.rebuilt("2026-11-26", dl, {}, {}, rows, {})
        self.assertEqual(sorted(x["pick"] for x in d["list"]), ["Late", "Priced"])
        self.assertEqual(d["source"], "rebuilt")

    def test_trend_units_at_the_page_stakes(self):
        days = [{"day": "2026-11-26", "list": [{"st": "won", "conf": .9}, {"st": "lost", "conf": .8}],
                 "daily": {"st": "won", "stake": 1, "paid": 2.2}, "cards": [{"st": "lost", "stake": 2, "paid": 0}],
                 "edge": [{"st": "won", "best": 1.5}, {"st": "lost", "best": 1.3}]}]
        t = B.trend(days)
        self.assertEqual(t["list"][0], {"day": "2026-11-26", "won": 1, "n": 2, "quoted": 0.85, "open": 0})
        self.assertEqual((t["daily"][0]["net"], t["card"][0]["net"], t["edge"][0]["net"]), (1.2, -2.0, -0.5))


if __name__ == "__main__":
    unittest.main()
