"""Odds tab changes of 19 Oct 2026: the three-leg Banker group, legs only from
sports whose tested rates hold up live, and legs settled from each sport's
full graded history (a leg older than the records' 14 days used to fall back
to Pending). No network.
"""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import groupings as G


def leg(i, odds, p, sport="football", comp=None):
    return {"sport": sport, "event": f"E{i}", "pick": f"P{i}", "home": f"P{i}", "away": f"Q{i}",
            "side": "h", "comp": comp or f"C{i}", "when": "2026-10-20T15:00:00Z", "date": "2026-10-20",
            "p": p, "pModel": p, "odds": odds, "est": False, "edge": p * odds - 1, "implied": 1 / odds}


AFTER = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)


class LegChance(unittest.TestCase):

    def test_the_tested_rate_never_above_the_models_number(self):
        acc = {"hit": 0.77, "n": 31}
        self.assertEqual(G.leg_p(0.90, acc), 0.77)          # was 0.834, pulled toward 0.90
        self.assertEqual(G.leg_p(0.74, {"hit": 0.80, "n": 60}), 0.74)
        self.assertIsNone(G.leg_p(0.90, {"hit": 0.80, "n": 20}))   # too few tested games
        self.assertIsNone(G.leg_p(0.90, {"hit": 0.60, "n": 90}))   # tested rate under 65%


class Banker(unittest.TestCase):

    def setUp(self):
        prices = [1.12, 1.18, 1.22, 1.25, 1.28, 1.33, 1.38, 1.45, 1.52, 1.58, 1.65, 1.75, 1.9, 2.1, 2.3]
        self.L = [leg(i, o, round(0.92 - 0.02 * i, 3)) for i, o in enumerate(prices)]

    def test_banker_is_three_legs_inside_its_odds(self):
        g = G.best(self.L, set(), AFTER, "Banker", 1.5, 2.5)
        self.assertEqual(len(g["legs"]), 3)
        self.assertTrue(1.5 <= g["odds"] <= 2.5)

    def test_other_bands_keep_five_legs_and_their_price_spread(self):
        g = G.best(self.L, set(), AFTER, "Steady", 2.5, 4.0)
        self.assertEqual(len(g["legs"]), 5)
        self.assertTrue(any(l["odds"] < 1.30 for l in g["legs"]))
        self.assertTrue(any(1.30 <= l["odds"] < 1.60 for l in g["legs"]))

    def test_banker_comes_first_and_no_leg_is_used_twice(self):
        groups = G.build_day(self.L, AFTER)
        self.assertEqual(groups[0]["name"], "Banker")
        events = [l["event"] for g in groups for l in g["legs"]]
        self.assertEqual(len(events), len(set(events)))


class Sports(unittest.TestCase):

    def test_only_sports_that_hold_up_live_make_legs(self):
        self.assertEqual(G.GROUP_SPORTS, {"football", "rugby"})
        acc = {"hit": 0.85, "n": 80, "cumHit": 0.85, "cumN": 80}
        sd = {"sports": {k: {"published": True, "name": k, "games": [
            {"home": "A", "away": "B", "pick": "A", "when": "2026-10-20T18:00:00Z", "id": k,
             "confidence": 0.8, "accuracy": acc}]} for k in ("rugby", "cfb", "nfl")}}
        td = {"matches": [{"date": "2026-10-20", "time": "12:00", "round": "Round 1", "playerA": "X",
                           "playerB": "Y", "pick": "X", "confidence": 0.85, "accuracy": acc, "id": "t1"}]}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "HERE", d), \
             mock.patch.object(G, "read_js", lambda name: {"tennis-data.js": td, "sports-data.js": sd}.get(name)):
            out = G.legs({"2026-10-20"})
        self.assertEqual({l["sport"] for l in out}, {"rugby"})


class Settle(unittest.TestCase):

    def test_legs_settle_from_the_full_histories(self):
        graded = {"graded": [{"date": "2026-10-05", "home": "France", "away": "Belgium", "result": [2, 1]}]}
        tennis = {"graded": [{"key": "185333", "void": True}, {"key": "9", "void": False, "winner": "Iga Swiatek"}],
                  "days": []}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "HERE", d):
            for name, doc in (("record-graded.json", graded), ("tennis-record.json", tennis), ("record.json", {"days": []})):
                with open(os.path.join(d, name), "w") as f:
                    json.dump(doc, f)
            with mock.patch("sports.graded_games", return_value=([{"id": 7, "winner": "Rams", "score": [20, 17]}],
                                                               [{"id": 8, "score": [10, 10]}])):
                idx = G.results_index()
        fb = {"sport": "football", "date": "2026-10-05", "home": "France", "away": "Belgium", "side": "h"}
        self.assertEqual(G.settle(fb, idx), ("won", "2-1"))
        self.assertEqual(G.settle({"sport": "tennis", "id": "185333", "pick": "Iva Jovic"}, idx), ("void", "void"))
        self.assertEqual(G.settle({"sport": "tennis", "id": "9", "pick": "Iga Swiatek"}, idx)[0], "won")
        self.assertEqual(G.settle({"sport": "nfl", "id": 7, "pick": "Rams"}, idx), ("won", "20-17"))
        self.assertEqual(G.settle({"sport": "nfl", "id": 8, "pick": "Rams"}, idx), ("void", "tie"))


if __name__ == "__main__":
    unittest.main()
