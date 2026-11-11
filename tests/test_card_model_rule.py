"""CARD_RULE 7 (11 Nov 2026, Douglas: "The model rules"): the Card is built
from the model's own picks (model_fault): priced, 1.15-1.90, the model 60%+
and at or above the bookmakers' chance, the group's chance the model's own.
The wider-rule filler is still chosen on the bookmakers' numbers."""
import os, sys, unittest
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

DAY = (datetime.now(timezone.utc) + timedelta(days=2)).astimezone(G.UK).date().isoformat()
NOW = datetime.now(timezone.utc)


def leg(i, odds, model, hour=13, sport="football"):
    l = {"event": f"e{i} v x", "pick": f"p{i}", "sport": sport, "comp": f"c{i}", "odds": odds, "p": model, "pModel": model,
         "when": f"{DAY}T{hour:02d}:{i:02d}:00Z", "est": False, "margin": 1.0, "date": DAY,
         "code": "en.1" if sport == "football" else None, "opp": 5.0}
    return G.honest(l)


class TwoXOnly(unittest.TestCase):
    """CARD_RULE 8 (11 Nov 2026): the Card builds the 2x alone, up to three a day."""
    def test_only_2x_groups(self):
        L = [leg(i, 1.40, 0.74, hour=10 + i) for i in range(12)]
        for i, l in enumerate(L): l["comp"] = f"c{i}"
        gs = G.build_card(L, DAY, NOW, log=[])
        self.assertTrue(gs)
        self.assertEqual({g["name"] for g in gs}, {"Card 2x"})
        self.assertLessEqual(len(gs), 3)
        self.assertEqual(G.CARD_RULE, 8)


class ModelRule(unittest.TestCase):
    def test_live_rule_is_the_models(self):
        self.assertTrue(G.CARD_MODEL_RULE)
        self.assertGreaterEqual(G.CARD_RULE, 7)

    def test_model_at_or_above_the_market_passes(self):
        self.assertIsNone(G.card_fault(leg(1, 1.50, 0.70)))       # bookmakers about 67%, model 70%: opposition 5.0 no longer matters

    def test_model_under_the_market_fails(self):
        self.assertIn("sees no value", G.card_fault(leg(1, 1.40, 0.66)))   # bookmakers about 71%

    def test_model_under_60_fails(self):
        self.assertIsNotNone(G.card_fault(leg(1, 1.80, 0.58)))

    def test_group_chance_is_the_models(self):
        L = [leg(i, 1.40, 0.74) for i in range(5)]   # three at 1.40 make a 2x (2.74)
        gs = G.build_card(L, DAY, NOW, log=[])
        self.assertTrue(gs)
        g = gs[0]
        self.assertFalse(g["wide"])
        self.assertEqual(g["basis"], "model")
        self.assertAlmostEqual(g["p"], 0.74 ** len(g["legs"]), places=3)

    def test_filler_still_bookmakers(self):
        l = leg(1, 1.40, 0.66)
        self.assertIsNone(G.card_fault(l, wide=True))
        self.assertEqual(G.as_card(l, wide=True)["p"], G.as_mult(l)["p"])


if __name__ == "__main__":
    unittest.main()
