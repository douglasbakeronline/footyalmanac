"""The publication log (publog.py, 26 Nov 2026): every item the page put
forward is kept with its first and last sight, changes and withdrawal, and a
published group that started without reaching the archive is named."""
import os, sys, json, tempfile, unittest
from datetime import datetime, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import publog as P


def group(name="Card 2x", status="new", odds=2.1, when="2026-11-25T01:00:00Z", picks=("A", "B", "C")):
    return {"name": name, "seq": 1, "status": status, "odds": odds, "locked": status in ("locked", "underway"),
            "legs": [{"event": f"{p} v X", "pick": p, "sport": "nba", "when": when, "odds": 1.3} for p in picks]}


def og(day, groups):
    return {"rules": {"card": {"rule": 14}}, "days": [{"date": day, "groups": groups}]}


class Merge(unittest.TestCase):
    def test_new_change_gone_back(self):
        doc = {"day": "2026-11-25", "items": {}}
        cov = {"card", "daily", "list", "model", "group"}
        items, _ = P.from_groupings(og("2026-11-25", [group()]))
        P.merge(doc, items["2026-11-25"], cov, "t1")
        (key, e), = doc["items"].items()
        self.assertEqual((e["kind"], e["builds"], e["firstSeen"], e["start"]), ("card", 1, "t1", "2026-11-25T01:00:00Z"))
        items, _ = P.from_groupings(og("2026-11-25", [group(status="holding", odds=2.2)]))
        P.merge(doc, items["2026-11-25"], cov, "t2")
        e = doc["items"][key]
        self.assertEqual(e["builds"], 2)
        self.assertEqual(e["changes"][-1]["status"], ["new", "holding"])
        self.assertEqual(e["first"]["odds"], 2.1); self.assertEqual(e["last"]["odds"], 2.2)
        P.merge(doc, {}, cov, "t3")
        self.assertEqual(doc["items"][key]["gone"], "t3")
        P.merge(doc, items["2026-11-25"], cov, "t4")
        self.assertNotIn("gone", doc["items"][key])
        self.assertTrue(doc["items"][key]["changes"][-1].get("back"))

    def test_seeded_item_seen_by_a_build(self):
        # 26 Nov 2026: seeded entries carry builds None; the first live build crashed on them
        doc = {"day": "d", "items": {"scale-pick|k": {"kind": "scale-pick", "source": "scale-archive", "builds": None,
                                                      "first": {"price": 1.4}, "last": {"price": 1.4}, "changes": []}}}
        P.merge(doc, {"scale-pick|k": ("scale-pick", {"price": 1.5})}, {"scale-pick"}, "t1")
        e = doc["items"]["scale-pick|k"]
        self.assertEqual((e["builds"], e["source"], e["seeded"], e["last"]["price"]), (1, "build", "scale-archive", 1.5))
        P.merge(doc, {}, {"scale-pick"}, "t2")
        self.assertEqual(doc["items"]["scale-pick|k"]["gone"], "t2")

    def test_uncovered_kind_is_not_marked_gone(self):
        doc = {"day": "d", "items": {}}
        P.merge(doc, {"edge|x": ("edge", {"start": "s"})}, {"edge"}, "t1")
        P.merge(doc, {}, {"card"}, "t2")
        self.assertNotIn("gone", doc["items"]["edge|x"])

    def test_kinds(self):
        self.assertEqual([P.group_kind(n) for n in ("Card 2x", "Daily 2x", "List long", "Model 3x", "Double")],
                         ["card", "daily", "list", "model", "group"])

    def test_edge_rows(self):
        rows = [{"league": "en.5", "date": "2026-11-25", "home": "H", "away": "A", "kickoff": "2026-11-25T19:45:00Z",
                 "edge": {"side": "h", "odds": 1.2}}, {"league": "en.5", "date": "2026-11-25", "home": "X", "away": "Y"}]
        out = P.from_edge_rows(rows)
        self.assertEqual(list(out["2026-11-25"]), ["edge|en.5|H|A"])


class Files(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for d in ("groupings-archive", "scale-archive", "slip-archive"): os.makedirs(os.path.join(self.tmp, d))
        p = mock.patch.object(P, "LOG_DIR", os.path.join(self.tmp, "groupings-archive", "published")); p.start(); self.addCleanup(p.stop)

    def w(self, rel, obj):
        with open(os.path.join(self.tmp, rel), "w") as f: json.dump(obj, f)

    def test_build_then_unarchived(self):
        self.w("groupings.json", og("2026-11-25", [group()]))
        self.w("scale-archive/2026-11-25.json", {"date": "2026-11-25", "picks": [{"key": "s|1", "start": "2026-11-25T20:00:00Z"}], "groups": []})
        P.record_build(datetime(2026, 11, 25, 21, 0, tzinfo=timezone.utc), here=self.tmp)
        doc = P.load_day("2026-11-25")
        self.assertEqual(sorted(e["kind"] for e in doc["items"].values()), ["card", "scale-pick"])
        # first pick 01:00 on the 26th: three hours on, not archived, named
        lost = P.unarchived(datetime(2026, 11, 26, 4, 0, tzinfo=timezone.utc), here=self.tmp)
        self.assertEqual([(f["check"], f["date"], f["picks"]) for f in lost], [("group-unarchived", "2026-11-25", ["A", "B", "C"])])
        # once archived, nothing to say
        self.w("groupings-archive/2026-11-25.json", {"date": "2026-11-25", "groups": [group(status="underway")]})
        self.assertEqual(P.unarchived(datetime(2026, 11, 26, 4, 0, tzinfo=timezone.utc), here=self.tmp), [])

    def test_withdrawn_group_is_not_flagged(self):
        self.w("groupings.json", og("2026-11-25", [group()]))
        P.record_build(datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc), here=self.tmp)
        self.w("groupings.json", og("2026-11-25", []))
        P.record_build(datetime(2026, 11, 25, 13, 0, tzinfo=timezone.utc), here=self.tmp)
        self.assertEqual(P.unarchived(datetime(2026, 11, 26, 4, 0, tzinfo=timezone.utc), here=self.tmp), [])

    def test_seed_is_idempotent(self):
        self.w("groupings-archive/2026-11-24.json", {"date": "2026-11-24", "published": "p", "groups": [group(status="underway")]})
        self.w("slip-archive/2026-11-24.json", {"date": "2026-11-24", "built": "b", "slip": {"legs": [{"key": "k1", "start": "s"}], "first": "s"}})
        with mock.patch.object(P, "LOST", []):
            n1 = P.seed(here=self.tmp); n2 = P.seed(here=self.tmp)
        self.assertEqual(n1, {"archive": 1, "slip-archive": 1}); self.assertEqual(n2, {})


if __name__ == "__main__":
    unittest.main()
