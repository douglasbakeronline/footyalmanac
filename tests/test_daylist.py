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
            out = DL.build(NOW, here=d, fetch=False)
        self.assertEqual(out["summary"]["list"], {"n": 1, "won": 0, "lost": 1, "void": 0, "started": 0, "upcoming": 0})


class FullObjects(unittest.TestCase):
    def test_tennis_full_from_archive_and_football_carried(self):
        t = tennis("2026-10-05T04:00:00Z")
        items = DL.pinned("2026-10-05", [("tennis", t)], NOW)
        f = {"key": "f|en.1|2026-10-05|H|A", "sport": "football"}
        DL.attach_full(items + [f], [("tennis", t)], {}, {"f|en.1|2026-10-05|H|A": {"home": {"name": "H"}}})
        self.assertEqual(items[0]["full"]["playerA"], "A"); self.assertNotIn("published", items[0]["full"])
        self.assertEqual(f["full"]["home"]["name"], "H")


if __name__ == "__main__":
    unittest.main()


class UnconfirmedDay(unittest.TestCase):
    def test_placeholder_rows_never_pin(self):
        import daylist as D
        base = {"date": "2026-10-26", "playerA": "A", "playerB": "B", "pick": "A", "p": {"a": 0.8},
                "confidence": 0.8, "list": True, "reserve": False, "published": "2026-10-26T00:10:00Z"}
        self.assertIsNone(D.tennis_item(dict(base, time="04:00")))          # midnight New York, EDT
        self.assertIsNone(D.tennis_item(dict(base, time="12:30", timeTbc=True)))
        self.assertIsNotNone(D.tennis_item(dict(base, time="12:30")))
        self.assertIsNotNone(D.tennis_item(dict(base, time=None)))


class Order(unittest.TestCase):
    """28 Oct 2026: strongest first means confidence first, tested rate second,
    and a started football pick keeps its place (its archive row carried no
    tested rate, so it sorted last under the old key)."""
    def test_confidence_before_tested_rate(self):
        a = {"sport": "rugby", "confidence": 0.81, "accuracy": {"cumHit": 0.91, "hit": 0.91, "n": 76}}
        b = {"sport": "football", "confidence": 0.90, "accuracy": {"cumHit": 0.84, "hit": 0.84, "n": 131}}
        self.assertEqual(sorted([a, b], key=DL.strength), [b, a])

    def test_started_football_pick_keeps_its_place(self):
        g = {"league": "en.1", "date": "2026-10-05", "home": "H", "away": "A", "p": {"h": 0.9, "d": 0.07, "a": 0.03},
             "confidence": 0.9, "celtic": False, "unrated": False, "list": True, "reserve": False,
             "kickoff": "2026-10-05T14:00:00Z", "published": "2026-10-05T05:00:00Z"}
        it = DL.football_item(g, {"en.1": {"country": "England", "name": "Premier League"}})
        self.assertIsNotNone(it["accuracy"])          # recomputed for an old archive row
        self.assertGreater(it["accuracy"]["cumHit"], 0.8)
        t = tennis("2026-10-05T04:00:00Z", conf=0.81)
        tt = DL.tennis_item(t)
        self.assertEqual([x["sport"] for x in sorted([tt, it], key=DL.strength)], ["football", "tennis"])

    def test_archived_rate_is_kept(self):
        g = {"league": "en.1", "date": "2026-10-05", "home": "H", "away": "A", "p": {"h": 0.9, "d": 0.07, "a": 0.03},
             "confidence": 0.9, "accuracy": {"hit": 0.5, "n": 40}, "list": True, "kickoff": "2026-10-05T14:00:00Z"}
        self.assertEqual(DL.football_item(g, {})["accuracy"], {"hit": 0.5, "n": 40})

    def test_group_a_takes_only_85_and_better(self):
        lst = [{"confidence": c} for c in (0.93, 0.88, 0.86, 0.84, 0.82, 0.81, 0.80, 0.80)]
        a, b = DL.groups(lst)
        self.assertEqual([i["confidence"] for i in a], [0.93, 0.88, 0.86])
        self.assertEqual([i["confidence"] for i in b], [0.84, 0.82, 0.81, 0.80, 0.80])
        a, b = DL.groups([{"confidence": 0.9}] * 7)
        self.assertEqual((len(a), len(b)), (5, 2))
        self.assertEqual(DL.groups([{"confidence": 0.8}]), ([], [{"confidence": 0.8}]))
