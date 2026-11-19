"""19 Nov 2026 (Douglas: "which rule has performed the best over the entire
timeline"): every CARD_RULE is a replay variant (card_replay.RULES) read on the
whole pool, and the nightly review prints the table (rules_section)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import groupings as G
import card_replay as R
import card_review_post as P


class Rules(unittest.TestCase):
    def test_every_rule_is_a_variant_in_order(self):
        nums = [n for n, *_ in R.RULES]
        self.assertEqual(nums, sorted(nums))
        self.assertEqual(nums[-1], G.CARD_RULE)
        for n, v, a, b, what in R.RULES:
            self.assertIn(v, R.VARIANTS, v)
            self.assertTrue(what)
        self.assertIsNone(R.RULES[-1][3])   # the live rule has no end date

    def test_pre_model_rules_sit_on_the_rule6_base(self):
        for v in ("rule1", "rule4", "rule5", "rule6"):
            self.assertIn(v, R.RULE6_FAMILY)
            self.assertFalse(R.patch_of(v)["CARD_MODEL_RULE"])
        self.assertFalse(R.patch_of("rule1")["CARD_CORE_ONLY"])
        self.assertEqual(R.patch_of("rule4")["CARD_OPP_MIN"], {})
        self.assertTrue(R.patch_of("rule4")["CARD_CORE_ONLY"])

    def test_model_rules_as_they_ran(self):
        self.assertEqual(R.VARIANTS["rule7"]["CARD_BUILD"], ("Card 2x", "Card 3x"))
        self.assertEqual(R.VARIANTS["rule8"]["CARD_BUILD"], ("Card 2x",))
        self.assertEqual(R.VARIANTS["rule7"]["CARD_SPORT_MIN"]["tennis"], 0.75)
        self.assertNotIn("CARD_SPORT_MIN", R.VARIANTS["rule10"])   # the live 85% floor
        for v in ("rule7", "rule8", "rule10"):
            self.assertFalse(R.spans(v))                           # no two-day groups before 12 Nov
            self.assertEqual(R.VARIANTS[v]["CARD_MODEL_EDGE"], 0.0)
        self.assertTrue(R.spans("rule11")); self.assertTrue(R.spans("rule12"))

    def test_rules_table_and_section(self):
        variants = {"live": {"groups": 4, "won": 2, "expected": 1.5, "return": 1.1, "legs": 12, "emptyDays": 3},
                    "rule12": {"groups": 2, "won": 1, "expected": 0.8, "return": 0.9, "legs": 6, "emptyDays": 5, "vsLivePerDay": -0.2, "pWorse": 0.6}}
        rows = R.rules_table(variants)
        self.assertEqual([r["rule"] for r in rows], [n for n, *_ in R.RULES])
        r12 = next(r for r in rows if r["rule"] == 12); self.assertEqual((r12["groups"], r12["pWorse"]), (2, 0.6))
        self.assertEqual(next(r for r in rows if r["rule"] == 1)["groups"], 0)
        rep = {"from": "2026-10-29", "to": "2026-11-19", "rules": rows}
        rec = {"cardByRule": {"12": {"settled": 0, "won": 0, "expected": 0, "unitsStaked": 0, "unitsReturned": 0},
                              "13": {"settled": 4, "won": 1, "expected": 1.4, "unitsStaked": 8, "unitsReturned": 4.8}}}
        out = "\n".join(P.rules_section(rep, rec))
        self.assertIn("| 13: the model alone", out); self.assertIn("-40.0%", out); self.assertIn("| 12: football opposition", out)
        self.assertIn("0.6", out)
        self.assertEqual(P.rules_section({}, rec), [])


if __name__ == "__main__":
    unittest.main()
