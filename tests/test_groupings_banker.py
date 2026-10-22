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

# 22 Oct 2026: these tests check grouping mechanics on short-priced boards;
# the 2.00 minimum return (groupings.MIN_RETURN) is tested on its own in
# tests/test_groupings_return.py.
_MIN_RETURN = None
def setUpModule():
    global _MIN_RETURN
    _MIN_RETURN, G.MIN_RETURN = G.MIN_RETURN, 1.0
def tearDownModule():
    G.MIN_RETURN = _MIN_RETURN



def leg(i, odds, p, sport="football", comp=None, model=None, lst=False):
    l = {"sport": sport, "event": f"E{i}", "pick": f"P{i}", "home": f"P{i}", "away": f"Q{i}",
         "side": "h", "comp": comp or f"C{i}", "when": "2026-10-20T15:00:00Z", "date": "2026-10-20",
         "p": p, "pModel": model if model is not None else p, "odds": odds, "est": False, "list": lst}
    return G.honest(l)


AFTER = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)


class LegChance(unittest.TestCase):

    def test_the_tested_rate_never_above_the_models_number(self):
        acc = {"hit": 0.77, "n": 31}
        self.assertEqual(G.leg_p(0.90, acc), 0.77)
        self.assertEqual(G.leg_p(0.76, {"hit": 0.80, "n": 60}), 0.76)
        self.assertIsNone(G.leg_p(0.90, {"hit": 0.80, "n": 20}))   # too few tested games
        self.assertIsNone(G.leg_p(0.90, {"hit": 0.70, "n": 90}))   # tested rate under 75% (21 Oct 2026)


class SafeLegs(unittest.TestCase):
    """21 Oct 2026: a leg needs the model and the market both at 75%+, and the
    model no more than 5 points above the market."""

    def test_agreeing_short_leg_is_safe(self):
        self.assertTrue(G.safe_leg(leg(0, 1.18, 0.80)))             # fair 0.807

    def test_market_below_75_is_out(self):
        self.assertFalse(G.safe_leg(leg(0, 1.35, 0.80)))            # fair 0.705

    def test_model_well_above_market_is_out(self):
        l = leg(0, 1.22, 0.78, model=0.86)                          # fair 0.781, model +8
        self.assertFalse(G.safe_leg(l))
        self.assertTrue(G.safe_leg(leg(0, 1.22, 0.78, model=0.82)))  # +4: allowed

    def test_estimates_are_never_safe(self):
        l = G.honest({"p": 0.9, "pModel": 0.9, "odds": 1.1, "est": True})
        self.assertFalse(G.safe_leg(l))


class DoubleAndTreble(unittest.TestCase):

    def setUp(self):
        prices = [1.08, 1.10, 1.12, 1.14, 1.16, 1.18, 1.20, 1.22, 1.45, 1.80]
        self.L = [leg(i, o, round(0.92 - 0.015 * i, 3)) for i, o in enumerate(prices)]

    def test_only_two_kinds_and_double_comes_first(self):
        self.assertEqual([b[0] for b in G.BANDS], ["Double", "Treble"])
        groups = G.build_day(self.L, AFTER)
        self.assertEqual(groups[0]["name"], "Double")
        self.assertEqual({g["name"] for g in groups}, {"Double", "Treble"})

    def test_legs_and_floors(self):
        for g in G.build_day(self.L, AFTER):
            self.assertEqual(len(g["legs"]), G.LEGS_IN[g["name"]])
            self.assertGreaterEqual(g["p"], G.MIN_CHANCE[g["name"]])
            self.assertTrue(all(G.safe_leg(l) for l in g["legs"]))
            self.assertTrue(all(l["odds"] < 1.30 for l in g["legs"]))   # the long legs never qualify

    def test_no_leg_used_twice(self):
        events = [l["event"] for g in G.build_day(self.L, AFTER) for l in g["legs"]]
        self.assertEqual(len(events), len(set(events)))

    def test_nothing_safe_means_no_group(self):
        L = [leg(i, o, 0.70) for i, o in enumerate([1.35, 1.40, 1.45, 1.5])]
        self.assertEqual(G.build_day(L, AFTER), [])

    def test_a_treble_under_its_floor_is_not_published(self):
        L = [leg(i, 1.27, 0.76) for i in range(3)]                  # 0.76^3 = 0.44
        self.assertIsNone(G.best(L, set(), AFTER, "Treble", 1.2, 2.6))

    def test_daily_list_legs_win_a_near_tie(self):
        L = [leg(0, 1.15, 0.82), leg(1, 1.15, 0.82), leg(2, 1.15, 0.815, lst=True), leg(3, 1.15, 0.815, lst=True)]
        g = G.best(L, set(), AFTER, "Double", 1.1, 2.0)
        self.assertEqual({l["event"] for l in g["legs"]}, {"E2", "E3"})


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


class FootballLegsAreClean(unittest.TestCase):
    """21 Oct 2026: a Celtic's Law fixture, or one the Daily List keeps out
    for blindness (new competition, thin history, cup...), never makes a leg."""

    def test_only_listed_or_under_the_bar(self):
        acc = {"hit": 0.85, "n": 80}
        def game(i, **kw):
            g = {"home": {"name": f"H{i}"}, "away": {"name": f"A{i}"}, "p": {"h": 0.82, "d": 0.12, "a": 0.06},
                 "league": "x.1", "kickoff": "2026-10-20T15:00:00Z", "accuracy": acc, "celtic": None, "why": None}
            g.update(kw); return g
        data = {"days": [{"date": "2026-10-20", "games": [
            game(0), game(1, why="below"), game(2, celtic={"reasons": ["promoted"]}, why="celtic"),
            game(3, why="new"), game(4, why="thin"), game(5, why="cup"), game(6, unrated=True, why="unrated")]}]}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "HERE", d), \
             mock.patch.object(G, "read_js", lambda name: None):
            with open(os.path.join(d, "data.json"), "w") as f:
                json.dump(data, f)
            out = G.legs({"2026-10-20"})
        self.assertEqual(sorted(l["pick"] for l in out), ["H0", "H1"])


if __name__ == "__main__":
    unittest.main()
