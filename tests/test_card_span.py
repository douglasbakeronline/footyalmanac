"""Two-day groups (12 Nov 2026, groupings.CARD_SPAN): a day whose picks make
no group borrows the next day's, holding at least one of its own; the next
day's Card never reuses a pick a two-day group holds. Live rule (rule 7+)."""
import os, sys, unittest
from datetime import date, datetime, timedelta, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G


def _day():
    d = date.today() + timedelta(days=7)
    if 4 <= d.month <= 10: d = date(d.year, 11, 1)
    while d.weekday() != 2: d += timedelta(days=1)       # a Wednesday in GMT
    return d
D1 = _day(); D2 = D1 + timedelta(days=1)
NOW = datetime(D1.year, D1.month, D1.day, 8, 0, tzinfo=timezone.utc)


def leg(i, d, hour, odds=1.40, model=0.76):
    l = {"event": f"h{i} v a{i}", "pick": f"h{i}", "home": f"h{i}", "away": f"a{i}", "sport": "football",
         "comp": f"league{i}", "code": "en.1", "odds": odds, "p": model, "pModel": model, "est": False,
         "margin": 1.04, "date": d.isoformat(), "when": f"{d.isoformat()}T{hour:02d}:00:00Z", "why": None,
         "opp": 8.0, "hit": 0.8}
    return G.honest(l)


class Span(unittest.TestCase):
    def setUp(self):
        self.L = [leg(0, D1, 19)] + [leg(i, D2, 15 + i) for i in range(1, 4)]

    def test_rule_admits_every_leg(self):
        for l in self.L: self.assertIsNone(G.card_fault(l), l["pick"])

    def test_empty_day_borrows_the_next(self):
        gs = G.build_card(self.L, D1.isoformat(), NOW, log=[])
        self.assertEqual(len(gs), 1)
        g = gs[0]
        self.assertEqual(g["span"], [D1.isoformat(), D2.isoformat()])
        self.assertIn("h0", [l["pick"] for l in g["legs"]])
        self.assertGreaterEqual(g["odds"], 2.0)
        self.assertEqual(g["lockAt"][:10], D1.isoformat())       # open until the first day's pick starts

    def test_next_day_does_not_reuse_held_picks(self):
        gs = G.build_card(self.L, D1.isoformat(), NOW, log=[])
        held = {l["event"] for l in gs[0]["legs"]}
        g2 = G.build_card(self.L, D2.isoformat(), NOW, log=[], taken=held)
        self.assertFalse({l["event"] for g in g2 for l in g["legs"]} & held)

    def test_no_span_without_a_pick_of_its_own(self):
        gs = G.build_card(self.L[1:], D1.isoformat(), NOW, log=[])
        self.assertEqual(gs, [])

    def test_a_day_that_builds_alone_does_not_span(self):
        L = [leg(i, D1, 12 + i) for i in range(3)] + [leg(i, D2, 15 + i) for i in range(3, 6)]
        gs = G.build_card(L, D1.isoformat(), NOW, log=[])
        self.assertTrue(gs and not any(g.get("span") for g in gs))

    def test_switch_off(self):
        with mock.patch.object(G, "CARD_SPAN", False):
            self.assertEqual(G.build_card(self.L, D1.isoformat(), NOW, log=[]), [])

    def test_open_span_group_holds_on_rebuild(self):
        first = G.build_card(self.L, D1.isoformat(), NOW, log=[])
        again = G.build_card(self.L, D1.isoformat(), NOW + timedelta(hours=1), prev=first, log=[])
        self.assertEqual([l["pick"] for l in again[0]["legs"]], [l["pick"] for l in first[0]["legs"]])
        self.assertEqual(again[0]["status"], "holding")

    def test_best_group_holding_its_own_pick(self):
        # 13 Nov 2026: the next day's three strongest picks alone make the best
        # group of the two days; the span must still find the best one that
        # holds the first day's pick, not give up because the overall best had none.
        L = [leg(0, D1, 19, odds=1.40, model=0.70)] + [leg(i, D2, 15 + i, odds=1.30, model=0.80) for i in range(1, 5)]
        for l in L: self.assertIsNone(G.card_fault(l), l["pick"])
        gs = G.build_card(L, D1.isoformat(), NOW, log=[])
        self.assertEqual(len(gs), 1)
        self.assertIn("h0", [l["pick"] for l in gs[0]["legs"]])
        self.assertTrue(gs[0].get("span"))

    def test_need_kept_past_the_pool_cut(self):
        L = [G.as_card(l) for l in [leg(0, D1, 19, odds=1.40, model=0.70)] + [leg(i, D2, 12, odds=1.30, model=0.80) for i in range(1, 30)]]
        after = NOW
        g = G.best_card(L, set(), after, "Card 2x", need=lambda l: l["pick"] == "h0")
        self.assertIsNotNone(g)
        self.assertIn("h0", [l["pick"] for l in g["legs"]])


if __name__ == "__main__":
    unittest.main()
