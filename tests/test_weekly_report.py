"""tools/weekly_report.py (9 Nov 2026): the week's Card groups by day, the
Daily List by sport, the releases in the window, and the markdown. Record
files are stubbed through HERE on a temp copy; nothing on disk is read."""
import json, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import weekly_report as WR


def group(name, odds, p, status, legs, lock="2026-11-05T07:00:00Z", wide=False):
    return {"name": name, "odds": odds, "p": p, "status": status, "wide": wide, "lockAt": lock, "paid": odds if status == "won" else 0,
            "paidBest": round(odds * 1.02, 2) if status == "won" else 0,
            "legs": [{"pick": pk, "sport": sp, "odds": o, "p": pp, "status": st} for pk, sp, o, pp, st in legs]}


class WeeklyReport(unittest.TestCase):
    def setUp(self):
        self.saved = WR.HERE; WR.HERE = tempfile.mkdtemp()
        days = [
            {"date": "2026-11-05", "groups": [
                group("Card 2x", 2.2, 0.42, "won", [("A", "tennis", 1.3, 0.75, "won"), ("B", "nba", 1.3, 0.76, "won"), ("C", "football", 1.3, 0.74, "won")]),
                group("Card 3x", 3.3, 0.27, "lost", [("D", "tennis", 1.5, 0.66, "lost"), ("E", "nba", 1.5, 0.66, "won"), ("F", "nba", 1.47, 0.67, "won")]),
                group("Card 2x", 2.1, 0.45, "won", [("G", "tennis", 1.2, 0.8, "won"), ("H", "nba", 1.75, 0.57, "won")], wide=True)]},   # wide: not counted
            {"date": "2026-11-07", "groups": [group("Card 2x", 2.0, 0.5, "pending", [("I", "nba", 1.4, 0.7, "pending"), ("J", "nba", 1.43, 0.7, "pending")], lock="2026-11-07T07:00:00Z")]},
            {"date": "2026-10-28", "groups": [group("Card 2x", 2.5, 0.4, "won", [("K", "football", 1.3, 0.75, "won"), ("L", "football", 1.3, 0.75, "won"), ("M", "football", 1.48, 0.66, "won")], lock="2026-10-28T07:00:00Z")]},
        ]
        json.dump({"graded": "2026-11-08T23:00:00Z", "card": {}, "days": days}, open(os.path.join(WR.HERE, "groupings-record.json"), "w"))
        json.dump({"generated": "x", "days": [{"date": "2026-11-04", "games": [
            {"list": True, "reserve": False, "confidence": 0.85, "won": True, "result": [2, 0]},
            {"list": True, "reserve": False, "confidence": 0.81, "won": False, "result": [1, 1]},
            {"list": False, "reserve": True, "confidence": 0.65, "won": True, "result": [1, 0]},
            {"list": True, "reserve": False, "confidence": 0.9, "won": True, "result": None}]}]},   # ungraded: out
                  open(os.path.join(WR.HERE, "record.json"), "w"))
        json.dump({"generated": "x", "days": [{"date": "2026-11-06", "games": [
            {"list": True, "reserve": False, "confidence": 0.8, "ok": True, "winner": "P", "void": False},
            {"list": True, "reserve": False, "confidence": 0.78, "ok": False, "winner": "Q", "void": False},
            {"list": True, "reserve": False, "confidence": 0.78, "ok": False, "winner": "R", "void": True}]}]},     # void: out
                  open(os.path.join(WR.HERE, "tennis-record.json"), "w"))
        json.dump({"generated": "x", "days": [{"date": "2026-11-06", "games": [
            {"sport": "nba", "list": True, "reserve": False, "confidence": 0.83, "ok": True, "winner": "T"},
            {"sport": "nba", "list": False, "reserve": True, "confidence": 0.7, "ok": False, "winner": "U"},
            {"sport": "nfl", "list": False, "reserve": False, "confidence": 0.6, "ok": True, "winner": "V"}]}]},
                  open(os.path.join(WR.HERE, "sports-record.json"), "w"))
        open(os.path.join(WR.HERE, "RELEASES.md"), "w").write(
            "# Releases\n\n## 2026-11-09 Newer thing (tag pending)\n\n**What changed:** one.\n**Files:** a.\n\n"
            "## release-2026-11-06-2 (pending tag): older thing\n\n**What changed.** two\nmore.\n\n**Files.** b.\n\n"
            "## 2026-10-30 Out of window (tag pending)\n\n**What changed:** three.\n")

    def tearDown(self):
        shutil.rmtree(WR.HERE, ignore_errors=True); WR.HERE = self.saved

    def test_build(self):
        r = WR.build("2026-11-08", {"decisions": ["Keep the 3x?"]})
        self.assertEqual(r["period"], {"from": "2026-11-02", "to": "2026-11-08"})
        w = r["card"]["week"]
        self.assertEqual((w["groups"], w["won"], w["card3x"]), (2, 1, 1))        # the wide and the pending group are not counted
        self.assertEqual(w["expected"], 0.69); self.assertEqual(w["returned"], 2.2); self.assertEqual(w["returnedBest"], 2.24)
        self.assertEqual(w["legsBySport"]["tennis"], {"legs": 2, "landed": 1, "quoted": 0.705})
        self.assertEqual((w["daysWithCard"], w["daysInRecord"]), (1, 2))
        self.assertEqual(r["card"]["toDate"]["groups"], 3)                        # the 28 Oct group joins to date
        self.assertEqual(r["list"]["football"]["list"], {"n": 2, "landed": 1, "rate": 0.5, "quoted": 0.83})
        self.assertEqual(r["list"]["football"]["reserve"]["n"], 1)
        self.assertEqual(r["list"]["tennis"]["list"], {"n": 2, "landed": 1, "rate": 0.5, "quoted": 0.79})
        self.assertEqual(r["list"]["nba"]["list"]["n"], 1); self.assertEqual(r["list"]["nfl"]["list"]["n"], 0)
        self.assertEqual([s["title"] for s in r["shipped"]], ["Newer thing", "Older thing"])
        self.assertEqual(r["shipped"][1]["what"], "two more.")
        self.assertEqual(r["decisions"], ["Keep the 3x?"])
        md = WR.markdown(r)
        self.assertIn("2 groups settled, 1 won against 0.69 expected", md)
        self.assertIn("| tennis | 2 | 1 (50%) | 70% |", md)
        self.assertIn("(+10%; at best prices +12%)", md)
        self.assertIn("## Decisions waiting on Douglas", md)

    def test_empty_week(self):
        r = WR.build("2026-09-20")
        self.assertEqual(r["card"]["week"]["groups"], 0); self.assertIsNone(r["card"]["week"]["return"])
        self.assertIn("No Card group settled this week.", WR.markdown(r))


if __name__ == "__main__":
    unittest.main()
