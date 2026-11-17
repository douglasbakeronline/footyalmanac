"""17 Nov 2026: the football-data Card replay (tools/card_legs_history.py
`card_season`) builds two-day groups like the page and the pool replay.
CARD_SPAN has been live since 12 Nov and tools/card_replay.py's live spans
since 17 Nov (claude/card-replay-live-span-2026-11-17.md), but card_season
still built day by day, so a variant paired on both sides of the gate read a
different live on each. Now card_season uses card_replay.spans and
build_span; nospan is the rollback on football-data too. No network."""
import os, sys, unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_legs_history as H
import groupings as G

CODES = ["en.1", "de.1", "es.1", "it.1", "fr.1", "nl.1", "pt.1"]
D1, D2 = "2026-11-14", "2026-11-15"


def row(i, date):
    avg = (1.28, 5.5, 11.0)
    return {"date": date, "code": CODES[i % len(CODES)], "home": f"H{i}", "away": f"A{i}", "time": "15:00",
            "avg": list(avg), "best": [a + 0.05 for a in avg], "result": 0}


def two_days():
    """Two picks on the first day (one short of a group), four on the next."""
    pairs = [((0.80, 0.12, 0.08), row(i, D1)) for i in range(2)]
    pairs += [((0.80, 0.12, 0.08), row(i, D2)) for i in range(2, 6)]
    return H.legs(pairs, model=True)


def days_of(card):
    return {g["date"] for g in card.get("groupList") or ()}


class FootballDataSpans(unittest.TestCase):
    def test_live_spans_the_short_day(self):
        L = two_days()
        self.assertEqual(len(L), 6)
        live = H.card_season(L, "live")
        self.assertIn(D1, days_of(live))
        self.assertIn(D2, days_of(live))

    def test_nospan_leaves_it_empty(self):
        L = two_days()
        self.assertNotIn(D1, days_of(H.card_season(L, "nospan")))

    def test_no_pick_twice(self):
        L = two_days()
        card = H.card_season(L, "live")
        self.assertLessEqual(sum(g["legs"] for g in card["groupList"]), 6)

    def test_card_span_off_means_day_by_day(self):
        L = two_days()
        with mock.patch.object(G, "CARD_SPAN", False):
            self.assertNotIn(D1, days_of(H.card_season(L, "live")))

    def test_rule6_family_does_not_span(self):
        import card_replay as CR
        self.assertFalse(CR.spans("rule5"))
        self.assertFalse(CR.spans("modelcard"))

    def test_nospan_registered_on_football_data(self):
        import inspect
        self.assertIn('"nospan"', inspect.getsource(H.replay_split))


if __name__ == "__main__":
    unittest.main()
