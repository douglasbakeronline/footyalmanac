"""The rule 6 family (11 Nov 2026): tools/card_replay.py's variants that were
pre-registered as one change to the rule 6 Card run on the rule 6 Card, not
on live (rule 7/8 reads none of their constants, so patched onto live they
rebuilt live exactly). Runs under the live rule. No network."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_replay as CR
import card_legs_history as H
import groupings as G


# helpers as in tests/test_card_fillers.py
CODES = ["en.1", "de.1", "es.1", "it.1", "fr.1", "nl.1", "pt.1"]


def row(i, avg, result=0, date="2026-11-14"):
    return {"date": date, "code": CODES[i % len(CODES)], "home": f"H{i}", "away": f"A{i}", "time": "15:00",
            "avg": list(avg), "best": [a + 0.05 for a in avg], "result": result}


def full_rule_day():
    """Seven legs the full rule takes: the model 8 points under the market,
    the opposition priced 11."""
    return [((0.66, 0.20, 0.14), row(i, (1.30, 5.0, 11.0))) for i in range(7)]


def by_day(L):
    out = {}
    for l in L:
        when = f"{l['date']}T{l['time']}:00Z"
        leg = {"sport": "football", "event": f"{l['home']} v {l['away']}", "pick": l["home"], "comp": l["code"], "code": l["code"],
               "when": when, "date": l["date"], "odds": round(l["price"], 2), "best": round(l["best"], 2), "margin": round(l["margin"], 4),
               "est": False, "pModel": round(l["model"], 4), "p": round(l["model"], 4), "hit": 0.8, "n": 100, "won": l["won"],
               "core": l["core"], "opp": round(l["opp"], 2), "draw": round(l["draw"], 2)}
        G.honest(leg)
        out.setdefault(G.uk_slot(leg)[0], []).append(leg)
    return out


class Rule6Family(unittest.TestCase):
    def test_family_patches_carry_rule6(self):
        for v in CR.RULE6_FAMILY:
            p = CR.patch_of(v)
            self.assertIs(p["CARD_MODEL_RULE"], False, v)
            self.assertEqual(p["CARD_RULE"], 6, v)
        self.assertEqual(CR.patch_of("opp7")["CARD_OPP_MIN"], {"football": 7.0})

    def test_rule7_variants_stay_on_live(self):
        for v in ("live", "m7edge3", "m7under5", "with3x", "comp3", "flatstake", "modelcard"):
            self.assertNotIn("CARD_MODEL_RULE", CR.patch_of(v), v)

    def test_family_builds_rule6_not_live(self):
        """Legs the model rates 8 points under the market: rule 8 refuses them
        all (no value), the rule 6 family builds from them."""
        days = by_day(H.legs(full_rule_day()))
        d = next(iter(days))
        self.assertTrue(G.CARD_MODEL_RULE)
        self.assertEqual(CR.build(days[d], d, "live"), [])
        self.assertTrue(CR.build(days[d], d, "rule6"))
        self.assertTrue(CR.build(days[d], d, "rule5"))
        self.assertTrue(CR.build(days[d], d, "uncapped"))
        # the filler builds under rule 5 on the day live leaves empty
        fg = CR.build(days[d], d, "fillrule5")
        self.assertTrue(fg and all(g.get("fill") for g in fg))
        # the patch is undone: live is still rule 8
        self.assertTrue(G.CARD_MODEL_RULE); self.assertEqual(G.CARD_RULE, CR.G.CARD_RULE)

    def test_review_line(self):
        import card_review_post as P
        rep = {"variants": {"live": {}, "rule5": {"base": "rule6", "vsRule6PerDay": 0.95, "pWorseVsRule6": 0.047},
                            "under8": {"base": "rule6", "vsRule6PerDay": 0.0, "pWorseVsRule6": None}, "comp3": {"vsLivePerDay": 0.2}}}
        line = P.rule6_lines(rep)[0]
        self.assertIn("rule5 +0.95 a day, p(worse) 0.047", line)
        self.assertIn("under8 +0.00 a day, identical", line)
        self.assertNotIn("comp3", line)
        self.assertEqual(P.rule6_lines({"variants": {"live": {}}}), [])


if __name__ == "__main__":
    unittest.main()
