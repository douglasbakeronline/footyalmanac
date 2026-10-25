"""The groupings record after the 25 Oct 2026 review (groupings.grade):
graded rows keep wide / late / locked / lockAt, and the Card tallies the full
rule, the wider rule and late groups apart. Standard library only."""
import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G


def leg(pick, odds=1.50):
    return {"pick": pick, "event": f"{pick} v X", "sport": "football", "home": pick, "away": "X", "side": "h",
            "date": "2026-10-26", "when": "2026-10-26T15:00:00Z", "odds": odds, "best": odds, "p": 0.65}


def card(name, window, picks, **flags):
    g = {"name": name, "odds": 2.2, "p": 0.4, "window": window, "rank": window, "rule": G.CARD_RULE,
         "locked": True, "lockAt": "2026-10-26T07:00:00Z", "legs": [leg(p) for p in picks]}
    g.update(flags)
    return g


def graded(groups, statuses):
    """grade() on one archive day with every leg settled as given."""
    with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
        json.dump({"date": "2026-10-26", "groups": groups}, open(os.path.join(d, "2026-10-26.json"), "w"))
        it = iter(statuses)
        with mock.patch.object(G, "results_index", return_value=None), \
             mock.patch.object(G, "settle", side_effect=lambda l, idx: (next(it), "1-0")):
            return G.grade()


class Flags(unittest.TestCase):
    def test_flags_travel_with_the_graded_row(self):
        rec = graded([card("Card 2x", "Daytime", ["A", "B", "C"], wide=True, late=True)], ["won"] * 3)
        g = rec["days"][0]["groups"][0]
        self.assertEqual((g["wide"], g["late"], g["locked"], g["lockAt"]), (True, True, True, "2026-10-26T07:00:00Z"))

    def test_old_rows_without_the_flags_still_grade(self):
        g = {"name": "Multiplier", "odds": 3.0, "p": 0.3, "legs": [leg("A"), leg("B")]}
        rec = graded([g], ["won", "lost"])
        r = rec["days"][0]["groups"][0]
        self.assertEqual((r["wide"], r["late"], r["locked"], r["lockAt"], r["status"]), (False, False, False, None, "lost"))


class Tallies(unittest.TestCase):
    def setUp(self):
        groups = [card("Card 2x", "Daytime", ["A", "B", "C"]),                       # full rule, on time: won
                  card("Card 3x", "Daytime", ["D", "E", "F"], wide=True),            # wider rule: won
                  card("Card 2x", "Evening", ["G", "H", "I"], late=True),            # late: lost
                  card("Card 3x", "Evening", ["J", "K", "L"], wide=True, late=True)]  # wide and late: won
        self.rec = graded(groups, ["won"] * 6 + ["lost", "won", "won"] + ["won"] * 3)

    def test_card_is_the_full_rule_locked_on_time(self):
        self.assertEqual((self.rec["card"]["groups"], self.rec["card"]["won"]), (1, 1))
        self.assertEqual(self.rec["cardByWindow"]["Daytime"]["groups"], 1)
        self.assertEqual(self.rec["cardByWindow"]["Evening"]["groups"], 0)

    def test_wide_and_late_have_their_own_lines(self):
        self.assertEqual((self.rec["cardWide"]["groups"], self.rec["cardWide"]["won"]), (1, 1))
        self.assertEqual((self.rec["cardLate"]["groups"], self.rec["cardLate"]["won"], self.rec["cardLate"]["lost"]), (2, 1, 1))

    def test_nothing_is_lost(self):
        self.assertEqual(self.rec["overall"]["groups"], 4)
        self.assertEqual(len(self.rec["days"][0]["groups"]), 4)


if __name__ == "__main__":
    unittest.main()
