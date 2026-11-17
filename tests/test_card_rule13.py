"""17 Nov 2026, CARD_RULE 13 (Douglas: "forget about comparison to bookies ...
let's just follow the model", "just drop both of those"): the Card's leg rule
reads no bookmaker number but the price band. CARD_MODEL_EDGE None switches
the value demand off; CARD_MODEL_OPP_MIN is empty. Rule 12 is kept as the
replay variant `rule12`, the value demand alone as `m7value`."""
import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import groupings as G
import card_replay as R
import card_funnel as CF


def leg(odds=1.40, model=0.66, fair=None, opp=3.5, sport="football"):
    fair = fair if fair is not None else round(1 / odds * 0.95, 3)
    return {"pick": "A", "sport": sport, "code": "en.1", "odds": odds, "fair": fair, "pModel": model,
            "pTested": model, "hit": model, "why": None, "opp": opp, "draw": 4.0, "est": False, "p": fair}


class Rule13(unittest.TestCase):
    def test_live_constants(self):
        self.assertEqual(G.CARD_RULE, 13)
        self.assertIsNone(G.CARD_MODEL_EDGE)
        self.assertEqual(G.CARD_MODEL_OPP_MIN, {})
        self.assertTrue(G.CARD_MODEL_RULE)

    def test_model_under_the_bookmakers_passes(self):
        # bookmakers about 68%, model 62%: rule 12 refused it, rule 13 takes it
        self.assertIsNone(G.model_fault(leg(1.40, 0.62)))

    def test_opposition_price_never_read(self):
        self.assertIsNone(G.model_fault(leg(opp=2.2)))
        self.assertIsNone(G.model_fault(leg(opp=None)))

    def test_the_models_own_floors_still_hold(self):
        self.assertIn("under 60%", G.model_fault(leg(1.80, 0.58)))
        self.assertIn("outside", G.model_fault(leg(2.10, 0.66)))
        self.assertIn("no bookmaker price", G.model_fault(dict(leg(), est=True)))
        self.assertIsNotNone(G.model_fault(leg(sport="tennis", model=0.80)))   # the 85% tennis floor

    def test_rule12_is_a_variant(self):
        self.assertEqual(R.VARIANTS["rule12"], {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {"football": 5.0}})
        self.assertEqual(R.VARIANTS["m7value"], {"CARD_MODEL_EDGE": 0.0})
        with mock.patch.multiple(G, **R.VARIANTS["rule12"]):
            self.assertIn("sees no value", G.model_fault(leg(1.40, 0.62)))
            self.assertIn("under 5", G.model_fault(leg(model=0.72, opp=2.2)))

    def test_rule12_fault_kept_on_each_leg(self):
        self.assertEqual(G.RULE12_PATCH, R.VARIANTS["rule12"])
        self.assertIn("sees no value", G.fault_under(leg(1.40, 0.62), G.RULE12_PATCH))
        self.assertIsNone(G.fault_under(leg(1.40, 0.72, opp=6.0), G.RULE12_PATCH))
        self.assertIsNone(G.CARD_MODEL_EDGE)   # restored after the call
        # a built group carries the verdict on every leg
        from datetime import datetime, timedelta, timezone
        day = (datetime.now(timezone.utc) + timedelta(days=2)).astimezone(G.UK).date().isoformat()
        L = []
        for i in range(3):
            l = leg(1.30, 0.80 - i * 0.02, opp=4.0)
            l.update(event=f"H{i} v A{i}", pick=f"P{i}", comp=f"c{i}", date=day, margin=1.0,
                     when=f"{day}T15:{i:02d}:00Z", implied=round(1 / 1.30, 4))
            L.append(G.honest(l))
        g = G.best_card(L, set(), datetime.now(timezone.utc), "Card 2x")
        self.assertIsNotNone(g)
        self.assertTrue(all("rule12Fault" in l for l in g["legs"]))
        faults = {l["pick"]: l["rule12Fault"] for l in g["legs"]}
        self.assertIn("under 5", faults["P0"]); self.assertIn("under 5", faults["P1"])
        self.assertIn("sees no value", faults["P2"])   # 76% v the bookmakers' 77%

    def test_funnel_has_no_value_relief_live(self):
        self.assertNotIn("no-value", CF.leg_relief())
        self.assertNotIn("opposition", CF.leg_relief())
        self.assertEqual(list(CF.rule_sets()[1])[-1], "comp-cap")


if __name__ == "__main__":
    unittest.main()
