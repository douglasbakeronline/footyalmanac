"""17 Nov 2026: the rule 13 Card split by what rule 12 would have said
(`cardRule13Split` in groupings-record.json). Every rule 13 Card leg carries
`rule12Fault` as built; the record keeps it on the graded leg and tallies the
groups rule 12 would also have built (`rule12`, every leg None) apart from
those holding a pick only rule 13 admits (`rule13only`), plus the legs each
way. Groups without the field on every leg are counted as `unknown`.
A tally of the scoreboard, nothing fitted (Rule 1)."""
import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

R12 = "P: the model sees no value"


def leg(pick, fault="none", p=0.7):
    l = {"pick": pick, "event": f"{pick} v X", "sport": "football", "home": pick, "away": "X", "side": "h",
         "date": "2026-11-18", "when": "2026-11-18T15:00:00Z", "odds": 1.4, "best": 1.4, "p": p}
    if fault != "none": l["rule12Fault"] = fault
    return l


def card(picks, rule=13, **kw):
    g = {"name": "Card 2x", "odds": 2.0, "p": 0.5, "window": "Day", "rank": "Day", "rule": rule,
         "locked": True, "lockAt": "2026-11-18T15:00:00Z", "legs": picks}
    g.update(kw)
    return g


def graded(groups, statuses):
    with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
        json.dump({"date": "2026-11-18", "groups": groups}, open(os.path.join(d, "2026-11-18.json"), "w"))
        it = iter(statuses)
        with mock.patch.object(G, "results_index", return_value=None), \
             mock.patch.object(G, "settle", side_effect=lambda l, idx, dead=None: (next(it), "1-0")):
            return G.grade()


class Split(unittest.TestCase):
    def setUp(self):
        groups = [card([leg("A", None), leg("B", None), leg("C", None)]),          # rule 12 would have built it: won
                  card([leg("D", None), leg("E", R12), leg("F", None)]),           # holds a rule-13-only pick: lost on E
                  card([leg("G"), leg("H"), leg("I")]),                            # no field: unknown, won
                  card([leg("J", None), leg("K", None), leg("L", None)], rule=12),  # not rule 13: not in the split
                  card([leg("M", R12), leg("N", None), leg("O", None)], wide=True)]  # wider rule: not the Card
        self.rec = graded(groups, ["won"] * 3 + ["won", "lost", "won"] + ["won"] * 3 + ["won"] * 3 + ["won"] * 3)
        self.s = self.rec["cardRule13Split"]

    def test_the_field_travels_with_the_graded_leg(self):
        legs = self.rec["days"][0]["groups"][1]["legs"]
        self.assertEqual([l.get("rule12Fault") for l in legs], [None, R12, None])
        self.assertTrue(all(l["r12"] for l in legs))
        self.assertFalse(self.rec["days"][0]["groups"][2]["legs"][0]["r12"])

    def test_groups_split(self):
        self.assertEqual((self.s["rule12"]["groups"], self.s["rule12"]["won"]), (1, 1))
        self.assertEqual((self.s["rule13only"]["groups"], self.s["rule13only"]["won"]), (1, 0))
        self.assertEqual(self.s["unknown"], 1)

    def test_legs_split(self):
        self.assertEqual(self.s["legs"]["rule12"], {"legs": 5, "landed": 5, "expected": 3.5})
        self.assertEqual(self.s["legs"]["rule13only"], {"legs": 1, "landed": 0, "expected": 0.7})

    def test_empty_record(self):
        s = graded([card([leg("A", None)], rule=11)], ["won"])["cardRule13Split"]
        self.assertEqual((s["rule12"]["groups"], s["rule13only"]["groups"], s["unknown"]), (0, 0, 0))



class ReviewSection(unittest.TestCase):
    def test_section_reads_the_split(self):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
        import card_review_post as P
        self.assertEqual(P.rule13_split_section(None), [])
        empty = {"rule12": {"groups": 0}, "rule13only": {"groups": 0}, "unknown": 0, "legs": {}}
        self.assertEqual(P.rule13_split_section(empty), [])
        s = graded([card([leg("A", None), leg("B", None), leg("C", None)]),
                    card([leg("D", None), leg("E", R12), leg("F", None)])], ["won"] * 3 + ["won", "lost", "won"])["cardRule13Split"]
        txt = "\n".join(P.rule13_split_section(s))
        self.assertIn("| rule 12 would have built it too | 1 | 1 | 1 v 0.5 | +174.0% | 5 of 5 v 3.5 expected |", txt)
        self.assertIn("| holds a pick only rule 13 admits | 1 | 1 | 0 v 0.5 | -100.0% | 0 of 1 v 0.7 expected |", txt)


if __name__ == "__main__":
    unittest.main()
