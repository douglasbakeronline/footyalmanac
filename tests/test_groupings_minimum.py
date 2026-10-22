"""Odds tab, 22 Oct 2026: at least three groups a day. Strict Double and
Treble first; Wider groups fill the gap from 65%+ legs, then unpriced Daily
List legs; they are re-checked by their own rule and graded apart. No network."""
import copy, os, sys, unittest
from datetime import datetime, timedelta, timezone

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


NOW = datetime(2026, 10, 23, 9, 0, tzinfo=timezone.utc)
AFTER = NOW + timedelta(minutes=20)


def leg(i, p, odds=None, est=False, lst=False, model=None):
    l = {"sport": "football", "event": f"E{i}", "pick": f"P{i}", "home": f"P{i}", "away": f"Q{i}",
         "side": "h", "comp": f"C{i}", "when": "2026-10-23T15:00:00Z", "date": "2026-10-23",
         "p": p, "pModel": model if model is not None else p, "list": lst, "est": est,
         "odds": odds if odds else round(1 / p, 2)}
    if not est: l["margin"] = 1.05
    return G.honest(l)


def priced(i, p, **kw):
    return leg(i, p, odds=round(1 / (p * 1.05), 2), **kw)


class Minimum(unittest.TestCase):

    def test_strict_groups_first_then_wider_to_three(self):
        L = [priced(0, 0.82), priced(1, 0.80)] + [priced(i, 0.70) for i in range(2, 8)]
        gs = G.build_day(L, AFTER, now=NOW, min_groups=3)
        self.assertGreaterEqual(len(gs), 3)
        self.assertEqual(gs[0]["name"], "Double")
        self.assertTrue(any(G.is_wide(g["name"]) for g in gs))
        self.assertTrue(all(g["risk"] == "Higher risk" for g in gs if G.is_wide(g["name"])))
        events = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(events), len(set(events)))

    def test_no_wider_group_when_three_strict_exist(self):
        L = [priced(i, 0.84) for i in range(10)]
        gs = G.build_day(L, AFTER, now=NOW, min_groups=3)
        self.assertGreaterEqual(len(gs), 3)
        self.assertFalse(any(G.is_wide(g["name"]) for g in gs))

    def test_wider_legs_need_65_and_agreement(self):
        self.assertTrue(G.wide_leg(priced(0, 0.68)))
        self.assertFalse(G.wide_leg(priced(0, 0.62)))
        self.assertFalse(G.wide_leg(leg(0, 0.70, odds=1.55, model=0.80)))   # model 13 points over the market
        self.assertFalse(G.safe_leg(priced(0, 0.68)))                       # never a strict leg

    def test_unpriced_daily_list_picks_can_fill_a_day(self):
        L = [leg(i, 0.80, est=True, lst=True) for i in range(6)] + [leg(9, 0.80, est=True, lst=False)]
        gs = G.build_day(L, AFTER, now=NOW, min_groups=3)
        self.assertEqual(len(gs), 3)
        self.assertTrue(all(g["estimates"] == len(g["legs"]) for g in gs))
        self.assertNotIn("E9", [l["event"] for g in gs for l in g["legs"]])

    def test_stronger_unpriced_list_picks_beat_weaker_priced_ones(self):
        L = [priced(i, 0.70) for i in range(4)] + [leg(10 + i, 0.84, est=True, lst=True) for i in range(4)]
        gs = G.build_day(L, AFTER, now=NOW, min_groups=3)
        first = gs[0]
        self.assertTrue(all(l["list"] and l.get("est") for l in first["legs"]))
        self.assertEqual(first["rule"], G.WIDE_RULE)

    def test_a_wider_group_from_the_old_rule_is_rebuilt(self):
        L = [priced(i, 0.70) for i in range(6)]
        old = G.build_day(L, AFTER, now=NOW - timedelta(hours=3), min_groups=3)
        for g in old: g.pop("rule", None)
        log = []
        G.build_day(copy.deepcopy(L), AFTER, prev=copy.deepcopy(old), now=NOW, log=log, min_groups=3)
        self.assertEqual(len(log), len(old))
        self.assertIn("new rule", log[0]["why"][0])

    def test_too_few_legs_gives_what_it_can(self):
        gs = G.build_day([priced(0, 0.70), priced(1, 0.70)], AFTER, now=NOW, min_groups=3)
        self.assertEqual(len(gs), 1)

    def test_a_wider_group_holds_on_its_own_rule(self):
        L = [priced(i, 0.70) for i in range(6)]
        first = G.build_day(L, AFTER, now=NOW - timedelta(hours=3), min_groups=3)
        log = []
        again = G.build_day(copy.deepcopy(L), AFTER, prev=copy.deepcopy(first), now=NOW, log=log, min_groups=3)
        self.assertEqual(log, [])
        self.assertEqual(sorted(G.gid(g) for g in again), sorted(G.gid(g) for g in first))
        self.assertTrue(all(g["status"] == "holding" for g in again))

    def test_a_wider_leg_that_drifts_is_replaced_with_a_reason(self):
        L = [priced(i, 0.70) for i in range(8)]
        first = G.build_day(L, AFTER, now=NOW - timedelta(hours=3), min_groups=3)
        gone = first[0]["legs"][0]["pick"]
        L2 = copy.deepcopy(L)
        for l in L2:
            if l["pick"] == gone:
                l.pop("fair"); l.update(odds=1.80, p=l["pTested"]); G.honest(l)
        log = []
        G.build_day(L2, AFTER, prev=copy.deepcopy(first), now=NOW, log=log, min_groups=3)
        self.assertTrue(log and gone in log[0]["why"][0])
        self.assertIn("under 65%", log[0]["why"][0])

    def test_record_keeps_strict_and_wider_apart(self):
        self.assertIn("Wider Double", [b[0] for b in G.WIDE_BANDS])
        self.assertEqual(G.MIN_GROUPS, 3)


if __name__ == "__main__":
    unittest.main()
