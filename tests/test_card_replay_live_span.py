"""17 Nov 2026: tools/card_replay.py's "live" spans like the live Card.
CARD_SPAN (two-day groups) has been live since 12 Nov, but the replay built
"live" day by day and ran the two-day Card as a variant (span2), so every
variant was paired against a Card the page no longer builds. Now every
live-machinery variant spans while CARD_SPAN is on; nospan is the rollback;
the rule 6 family and the paper Model card do not. No network."""
import os, sys, unittest
from datetime import date, timedelta
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
sys.path.insert(0, os.path.join(HERE, "tests"))
import card_replay as CR
import groupings as G
from test_card_span import D1, D2, leg


def by_day():
    L = [leg(0, D1, 19)] + [leg(i, D2, 15 + i) for i in range(1, 4)]
    for l in L: l["won"] = True; l["best"] = l["odds"]
    by = {}
    for l in L: by.setdefault(l["date"], []).append(l)
    return by, [D1.isoformat(), D2.isoformat()]


class LiveSpans(unittest.TestCase):
    def test_who_spans(self):
        self.assertTrue(G.CARD_SPAN)
        self.assertTrue(CR.spans("live"))
        self.assertTrue(CR.spans("rule12"))
        self.assertFalse(CR.spans("nospan"))
        self.assertFalse(CR.spans("rule6"))
        self.assertFalse(CR.spans("opp7"))
        self.assertFalse(CR.spans("modelcard"))
        self.assertNotIn("span2", CR.VARIANTS)
        with mock.patch.object(G, "CARD_SPAN", False):
            self.assertFalse(CR.spans("live"))

    def test_live_takes_the_two_day_group(self):
        by, dates = by_day()
        days = CR.build_span(by, dates, "live")
        self.assertEqual(len(days[dates[0]]), 1)
        g = days[dates[0]][0]
        self.assertTrue(g.get("span"))
        self.assertIn("h0", [l["pick"] for l in g["legs"]])
        held = {l["event"] for l in g["legs"]}
        self.assertFalse({l["event"] for g2 in days[dates[1]] for l in g2["legs"]} & held)

    def test_nospan_leaves_the_day_empty(self):
        by, dates = by_day()
        self.assertEqual(CR.build(by[dates[0]], dates[0], "nospan"), [])

    def test_variant_constants_apply_to_the_span_pass(self):
        """A variant whose opposition floor (9.0) refuses every leg (opposition 8.0) must not span on live's rule."""
        by, dates = by_day()
        with mock.patch.dict(CR.VARIANTS, {"_none": {"CARD_MODEL_OPP_MIN": {"football": 9.0}}}):
            days = CR.build_span(by, dates, "_none")
        self.assertEqual(days[dates[0]], [])

    def test_constants_restored(self):
        by, dates = by_day()
        before = G.CARD_MODEL_OPP_MIN
        CR.build_span(by, dates, "rule12")
        self.assertIs(G.CARD_MODEL_OPP_MIN, before)


if __name__ == "__main__":
    unittest.main()
