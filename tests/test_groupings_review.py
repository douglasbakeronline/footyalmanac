"""Odds tab, 21 Oct 2026: groups for today and three days ahead, re-checked on
every build. A group that still passes keeps its place; one that fails is
replaced and the reason logged; a group with a leg under way is kept as
published. No network.
"""
import copy, os, sys, unittest
from datetime import datetime, timedelta, timezone
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



def leg(i, odds, p):
    l = {"sport": "football", "event": f"E{i}", "pick": f"P{i}", "home": f"P{i}", "away": f"Q{i}",
         "side": "h", "comp": f"C{i}", "when": "2026-10-20T15:00:00Z", "date": "2026-10-20",
         "p": p, "pModel": p, "odds": odds, "est": False, "list": False}
    return G.honest(l)

NOW = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
AFTER = NOW + timedelta(minutes=20)


def board():
    prices = [1.08, 1.10, 1.12, 1.14, 1.16, 1.18, 1.20, 1.22, 1.45, 1.80]
    return [leg(i, o, round(0.92 - 0.015 * i, 3)) for i, o in enumerate(prices)]


def published():
    """What the last build put out, run through the same code."""
    return G.build_day(board(), AFTER, prev=None, now=NOW - timedelta(hours=5), log=[])


class Recheck(unittest.TestCase):

    def test_four_days(self):
        self.assertEqual(G.DAYS_AHEAD, 3)

    def test_first_build_marks_every_group_new(self):
        gs = published()
        self.assertTrue(gs)
        self.assertTrue(all(g["status"] == "new" for g in gs))
        self.assertTrue(all(l["firstOdds"] == l["odds"] for g in gs for l in g["legs"]))

    def test_unchanged_board_holds_every_group(self):
        prev = published(); log = []
        gs = G.build_day(board(), AFTER, prev=copy.deepcopy(prev), now=NOW, log=log)
        self.assertEqual([G.gid(g) for g in gs], [G.gid(g) for g in prev])
        self.assertTrue(all(g["status"] == "holding" for g in gs))
        self.assertEqual(log, [])
        self.assertEqual(gs[0]["first"], prev[0]["first"])        # first shown is carried

    def test_holding_takes_the_new_price_and_remembers_the_first(self):
        prev = published()
        pick = prev[0]["legs"][0]["pick"]
        L = board()
        for l in L:
            if l["pick"] == pick: l.update(odds=round(l["odds"] - 0.02, 2)); G.honest(l)
        gs = G.build_day(L, AFTER, prev=copy.deepcopy(prev), now=NOW, log=[])
        moved = next(l for l in gs[0]["legs"] if l["pick"] == pick)
        self.assertEqual(gs[0]["status"], "holding")
        self.assertAlmostEqual(moved["firstOdds"] - moved["odds"], 0.02, places=2)

    def test_a_drifting_price_replaces_the_group_and_says_why(self):
        prev = published()
        main = prev[0]
        pick = main["legs"][0]["pick"]
        L = board()
        for l in L:
            if l["pick"] == pick:                       # market now well under 75%
                l.pop("fair", None); l.update(odds=1.45, p=l["pTested"]); G.honest(l)
        log = []
        gs = G.build_day(L, AFTER, prev=copy.deepcopy(prev), now=NOW, log=log)
        self.assertEqual(len(log), 1)
        self.assertIn(pick, log[0]["why"][0])
        self.assertIn("bookmakers now give", log[0]["why"][0])
        new = next(g for g in gs if g["name"] == main["name"] and g["rank"] == main["rank"])
        self.assertEqual(new["status"], "replacement")
        self.assertNotIn(pick, [l["pick"] for l in new["legs"]])

    def test_a_game_gone_from_the_board_is_a_failure(self):
        prev = published()
        gone = prev[0]["legs"][0]["pick"]
        L = [l for l in board() if l["pick"] != gone]
        log = []
        G.build_day(L, AFTER, prev=copy.deepcopy(prev), now=NOW, log=log)
        self.assertIn("no longer a clean pick", log[0]["why"][0])

    def test_underway_group_kept_as_published_and_its_games_not_reused(self):
        prev = published()
        later = NOW.replace(hour=16)                     # every leg kicked off at 15:00
        gs = G.build_day(board(), later + timedelta(minutes=20), prev=copy.deepcopy(prev), now=later, log=[])
        self.assertTrue(gs)
        self.assertTrue(all(g["status"] == "underway" for g in gs))
        self.assertEqual([G.gid(g) for g in gs], [G.gid(g) for g in prev])

    def test_no_game_used_twice_after_a_replacement(self):
        prev = published()
        L = [l for l in board() if l["pick"] != prev[0]["legs"][0]["pick"]]
        gs = G.build_day(L, AFTER, prev=copy.deepcopy(prev), now=NOW, log=[])
        events = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(events), len(set(events)))

    def test_a_failed_price_source_does_not_drop_a_group(self):
        prev = published()
        pick = prev[0]["legs"][0]["pick"]
        L = board()
        for l in L:
            if l["pick"] == pick:                       # this build could not price it
                for k in ("fair", "margin", "src"): l.pop(k, None)
                l.update(odds=round(1 / l["pModel"], 2), est=True); G.honest(l)
        log = []
        gs = G.build_day(L, AFTER, prev=copy.deepcopy(prev), now=NOW, log=log)
        self.assertEqual(log, [])
        self.assertEqual(gs[0]["status"], "holding")
        held = next(l for l in gs[0]["legs"] if l["pick"] == pick)
        self.assertTrue(held["stale"])
        self.assertEqual(held["odds"], prev[0]["legs"][0]["odds"])

    def test_previous_takes_the_newer_copy_and_dates_old_groups(self):
        old = {"generated": "2026-10-20T05:15:00Z", "days": [{"date": "2026-10-20", "groups": [{"name": "Double", "legs": []}]}]}
        new = {"generated": "2026-10-20T12:00:00Z", "days": [{"date": "2026-10-20", "groups": [{"name": "Treble", "legs": []}]}]}
        with mock.patch.object(G, "load", return_value=old), mock.patch.object(G, "get", return_value=new):
            prev = G.previous()
        self.assertEqual(prev["2026-10-20"]["groups"][0]["name"], "Treble")
        self.assertEqual(prev["2026-10-20"]["groups"][0]["first"], "2026-10-20T12:00:00Z")

    def test_previous_survives_no_network(self):
        with mock.patch.object(G, "load", return_value={}), mock.patch.object(G, "get", side_effect=OSError):
            self.assertEqual(G.previous(), {})


if __name__ == "__main__":
    unittest.main()
