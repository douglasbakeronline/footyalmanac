"""18 Nov 2026: recheck_card rebuilt each leg from the board and dropped
`rule12Fault`, so no rule 13 Card group reached the archive with it and the
split (`cardRule13Split`) counted every one as unknown. The re-check now asks
rule 12 again, and the grader reads an archived rule 13 leg without the field
from the leg as frozen (`r12` "derived", `groupings.rule12_fault`).
claude/card-rule12-fault-recheck-2026-11-18.md."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G


def board(day):
    L = []
    for i in range(3):
        o = 1.30
        l = {"pick": f"P{i}", "sport": "football", "code": "en.1", "odds": o, "fair": round(1 / o * 0.95, 3),
             "pModel": 0.80 - i * 0.02, "pTested": 0.8, "hit": 0.8, "why": None, "opp": 4.0, "draw": 4.0,
             "est": False, "event": f"H{i} v A{i}", "comp": f"c{i}", "date": day, "margin": 1.0,
             "when": f"{day}T15:{i:02d}:00Z", "implied": round(1 / o, 4)}
        l["p"] = l["fair"]
        L.append(G.honest(l))
    return L


class Recheck(unittest.TestCase):
    def test_rule12_fault_survives_the_recheck(self):
        day = (datetime.now(timezone.utc) + timedelta(days=2)).astimezone(G.UK).date().isoformat()
        L = board(day)
        g = G.best_card(L, set(), datetime.now(timezone.utc), "Card 2x")
        self.assertIsNotNone(g)
        g2, why = G.recheck_card(g, L)
        self.assertEqual(why, [])
        self.assertTrue(all("rule12Fault" in l for l in g2["legs"]))
        self.assertEqual({l["pick"]: l["rule12Fault"] for l in g2["legs"]},
                         {l["pick"]: l["rule12Fault"] for l in g["legs"]})

    def test_rule12_fault_reread_on_this_builds_numbers(self):
        day = (datetime.now(timezone.utc) + timedelta(days=2)).astimezone(G.UK).date().isoformat()
        L = board(day)
        g = G.best_card(L, set(), datetime.now(timezone.utc), "Card 2x")
        L2 = [dict(l, opp=6.0) if l["pick"] == "P0" else l for l in L]
        g2, _ = G.recheck_card(g, L2)
        f = {l["pick"]: l["rule12Fault"] for l in g2["legs"]}
        self.assertIsNone(f["P0"])          # opposition now 6.0, and the model above the bookmakers
        self.assertIn("under 5", f["P1"])


class Derived(unittest.TestCase):
    def test_rule12_fault_alone(self):
        l = {"pick": "A", "sport": "football", "pModel": 0.63, "fair": 0.50, "opp": 3.65}
        self.assertIn("under 5", G.rule12_fault(l))
        self.assertIn("sees no value", G.rule12_fault(dict(l, fair=0.69, opp=7.7)))
        self.assertIsNone(G.rule12_fault(dict(l, opp=6.0)))
        self.assertIsNone(G.rule12_fault({"pick": "B", "sport": "nba", "pModel": 0.72, "fair": 0.70, "opp": 3.2}))

    def test_grader_derives_a_missing_field_on_rule13_legs_only(self):
        def lg(pick, **kw):
            l = {"pick": pick, "event": f"{pick} v X", "sport": "football", "home": pick, "away": "X", "side": "h",
                 "date": "2026-11-18", "when": "2026-11-18T15:00:00Z", "odds": 1.4, "best": 1.4, "p": 0.7,
                 "pModel": 0.7, "fair": 0.6, "opp": 6.0}
            l.update(kw); return l
        card = lambda legs, rule=13: {"name": "Card 2x", "odds": 2.0, "p": 0.5, "window": "Day", "rank": "Day",
                                       "rule": rule, "locked": True, "lockAt": "2026-11-18T15:00:00Z", "legs": legs}
        groups = [card([lg("A"), lg("B"), lg("C")]),                    # rule 12 would have built it
                  card([lg("D"), lg("E", opp=3.0), lg("F")]),           # E only under rule 13
                  card([lg("G"), lg("H"), lg("I")], rule=11)]           # not rule 13: stays unknown-free and r12 False
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
            json.dump({"date": "2026-11-18", "groups": groups}, open(os.path.join(d, "2026-11-18.json"), "w"))
            with mock.patch.object(G, "results_index", return_value=None), \
                 mock.patch.object(G, "settle", side_effect=lambda l, idx, dead=None: ("won", "1-0")):
                rec = G.grade()
        s = rec["cardRule13Split"]
        self.assertEqual((s["rule12"]["groups"], s["rule13only"]["groups"], s["unknown"], s["derived"]), (1, 1, 0, 2))
        gl = rec["days"][0]["groups"]
        self.assertEqual([l["r12"] for l in gl[1]["legs"]], ["derived"] * 3)
        self.assertIn("under 5", gl[1]["legs"][1]["rule12Fault"])
        self.assertEqual([l["r12"] for l in gl[2]["legs"]], [False] * 3)


if __name__ == "__main__":
    unittest.main()
