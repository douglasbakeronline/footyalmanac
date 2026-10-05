"""Today's pinned Daily List (daylist.py). Standard library only."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import daylist as DL

NOW = datetime(2026, 10, 5, 17, 0, tzinfo=timezone.utc)


def tennis(pub, time="07:00", conf=0.88, lst=True, res=False, pid="1"):
    return {"id": pid, "tour": "ATP", "date": "2026-10-05", "time": time, "tournament": "Japan Open",
            "playerA": "A", "playerB": "B", "p": {"a": 1 - conf, "b": conf}, "pick": "B", "confidence": conf,
            "tier": "Strong", "accuracy": {"hit": 0.92, "n": 62}, "list": lst, "reserve": res, "published": pub}


class Pinning(unittest.TestCase):
    def test_keeps_a_started_pick(self):
        out = DL.pinned("2026-10-05", [("tennis", tennis("2026-10-05T04:00:00Z"))], NOW)
        self.assertEqual(len(out), 1); self.assertTrue(out[0]["started"])

    def test_price_after_the_start_is_ignored(self):
        arch = [("tennis", tennis("2026-10-05T04:00:00Z", conf=0.88)),
                ("tennis", tennis("2026-10-05T08:00:00Z", conf=0.95))]
        out = DL.pinned("2026-10-05", arch, NOW)
        self.assertEqual(out[0]["confidence"], 0.88)

    def test_latest_pre_start_price_decides_membership(self):
        arch = [("tennis", tennis("2026-10-04T05:00:00Z", lst=True)),
                ("tennis", tennis("2026-10-05T04:00:00Z", lst=False, res=False))]
        self.assertEqual(DL.pinned("2026-10-05", arch, NOW), [])

    def test_unpublished_legacy_and_other_days_skipped(self):
        legacy = tennis(None)
        other = dict(tennis("2026-10-05T04:00:00Z"), date="2026-10-06")
        self.assertEqual(DL.pinned("2026-10-05", [("tennis", legacy), ("tennis", other)], NOW), [])

    def test_uk_day_not_utc_day(self):
        g = {"id": "9", "sport": "nfl", "label": "NFL", "when": "2026-10-04T23:30Z", "home": "H", "away": "A",
             "pHome": 0.8, "pick": "H", "confidence": 0.8, "tier": "Strong", "list": True,
             "published": "2026-10-04T05:00:00Z"}
        self.assertEqual(len(DL.pinned("2026-10-05", [("sport", g)], NOW)), 1)   # 00:30 BST on the 5th


class Results(unittest.TestCase):
    def test_won_lost_void_upcoming(self):
        items = DL.pinned("2026-10-05", [("tennis", tennis("2026-10-05T04:00:00Z", pid="1")),
                                         ("tennis", dict(tennis("2026-10-05T04:00:00Z", pid="2"), playerA="C")),
                                         ("tennis", dict(tennis("2026-10-05T04:00:00Z", pid="3", time="20:00"), playerA="E"))], NOW)
        trec = {"graded": [{"key": "1", "ok": True, "void": False, "winner": "B"},
                           {"key": "2", "ok": False, "void": True}]}
        DL.attach_results(items, {}, trec, {})
        st = {i["id"]: i["status"] for i in items}
        self.assertEqual(st, {"1": "won", "2": "void", "3": "upcoming"})

    def test_build_writes_summary(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "predictions-tennis"))
            json.dump([tennis("2026-10-05T04:00:00Z")], open(os.path.join(d, "predictions-tennis", "2026-10-05.json"), "w"))
            json.dump({"graded": [{"key": "1", "ok": False, "void": False, "winner": "A"}]},
                      open(os.path.join(d, "tennis-record.json"), "w"))
            out = DL.build(NOW, here=d)
        self.assertEqual(out["summary"]["list"], {"n": 1, "won": 0, "lost": 1, "void": 0, "started": 0, "upcoming": 0})


if __name__ == "__main__":
    unittest.main()
