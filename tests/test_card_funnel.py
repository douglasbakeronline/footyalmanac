"""tools/card_funnel.py (10 Nov 2026, #155): every card_fault branch has a
key, the pool is read at the first real price, and a relief relaxes one
condition only. Synthetic pool files in a temp dir; nothing is fitted."""
import gzip, json, os, sys, tempfile, shutil, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_funnel as CF

# 11 Nov 2026: the Card became the model's own picks (CARD_RULE 7). These tests
# cover the rule 6 machinery, which stays as the replay variant `rule6`, so the
# module runs under rule 6; tests/test_card_model_rule.py covers rule 7.
from unittest import mock as _mock
_RULE6 = [_mock.patch.object(G, "CARD_MODEL_RULE", False), _mock.patch.object(G, "CARD_RULE", 6),
          _mock.patch.object(G, "CARD_BUILD", ("Card 2x", "Card 3x"))]
def setUpModule():
    for p in _RULE6: p.start()
def tearDownModule():
    for p in _RULE6: p.stop()


DAY = "2026-11-20"


def nba(i, odds=1.30, fair=0.72, model=0.70, when=f"{DAY}T19:00:00Z"):
    return {"sport": "nba", "event": f"Home{i} v Away{i}", "pick": f"Home{i}", "comp": f"Conf{i}", "when": when, "date": DAY,
            "odds": odds, "best": odds, "fair": fair, "margin": 1.05, "pModel": model, "pTested": model, "hit": 0.8, "p": model, "est": False}


def football(i, opp=10.0, model=0.66, fair=0.72, code="en.1"):
    return {"sport": "football", "event": f"FC{i} v United{i}", "pick": f"FC{i}", "home": f"FC{i}", "away": f"United{i}", "side": "h",
            "comp": "Premier League", "code": code, "when": f"{DAY}T15:00:00Z", "date": DAY, "odds": 1.30, "best": 1.30, "fair": fair,
            "margin": 1.05, "pModel": model, "pTested": model, "hit": 0.8, "p": model, "est": False, "opp": opp, "draw": 5.0}


class FaultKeys(unittest.TestCase):
    def key(self, **kw):
        l = dict(nba(1), **kw)
        return CF.fault_key(G.card_fault(l))

    def test_every_branch_has_a_key(self):
        self.assertIsNone(self.key())
        self.assertEqual(self.key(sport="cfb"), "sport-off")
        self.assertEqual(self.key(listOff=True), "sport-off")
        with _mock.patch.object(G, "CARD_CORE_ONLY", True):   # the league limit (off live from 11 Nov 2026)
            self.assertEqual(CF.fault_key(G.card_fault(football(1, code="af.187"))), "league")
        self.assertEqual(CF.fault_key(G.card_fault(football(1, model=0.71, fair=0.72))), "under-market")
        self.assertEqual(CF.fault_key(G.card_fault(football(1, model=0.55, fair=0.72))), "under-market")   # 17 under, past the cap
        self.assertEqual(CF.fault_key(G.card_fault(football(1, opp=5.0))), "opposition")
        self.assertEqual(CF.fault_key(G.card_fault(football(1, opp=None))), "opposition")
        self.assertEqual(self.key(sport="tennis", pModel=0.70, hit=0.80), "sport-floor")
        self.assertEqual(self.key(timeEst=True), "no-time")
        self.assertEqual(self.key(est=True), "no-price")
        self.assertEqual(self.key(odds=2.40), "price-range")
        self.assertEqual(self.key(fair=0.58, pModel=0.58), "fair-floor")
        self.assertEqual(self.key(pModel=0.35), "model-floor")
        self.assertEqual(self.key(pModel=0.90), "model-above")
        self.assertIsNone(CF.fault_key(None))
        self.assertEqual(CF.fault_key("something new"), "other")


class Pool(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, legs, day=DAY):
        with gzip.open(os.path.join(self.dir, f"pool-{day}.json.gz"), "wt", encoding="utf-8") as f:
            json.dump({"date": day, "legs": legs}, f)

    def test_first_real_price_estimates_counted_and_duplicates_once(self):
        est = dict(nba(9), est=True, fair=None)
        blocked = dict(nba(8), est=True, fair=None, priced={"odds": 1.30, "best": 1.32, "fair": 0.72, "margin": 1.05})
        self.write([nba(1), nba(1), est, blocked])
        by, unpriced = CF.pool_days(pool_dir=self.dir)
        self.assertEqual(sorted(l["event"] for l in by[DAY]), ["Home1 v Away1", "Home8 v Away8"])
        self.assertEqual(sum(unpriced.values()), 1)
        self.assertEqual(next(l for l in by[DAY] if l["event"].startswith("Home8"))["best"], 1.32)

    def test_relief_relaxes_one_condition_and_live_is_unchanged(self):
        # two NBA legs clear; a third leg, football, fails only the opposition's price
        self.write([nba(1), nba(2), football(3, opp=5.0)])
        before = (dict(G.CARD_OPP_MIN), G.CARD_UNDER_MARKET)
        by, unpriced = CF.pool_days(pool_dir=self.dir)
        f = CF.funnel(by, unpriced)
        self.assertEqual(f["clear"], {"nba": 2})
        self.assertEqual(f["faults"]["football"], {"opposition": 1})
        self.assertEqual(f["sole"]["football"], {"opposition": 1})
        self.assertEqual(f["relief"]["opposition"]["Card 2x"], 1)      # three legs at 1.30: a 2x
        self.assertEqual(f["relief"]["live"]["Card 2x"], 0)            # two legs alone make no group
        self.assertEqual((dict(G.CARD_OPP_MIN), G.CARD_UNDER_MARKET), before)   # patches restored
        lines = "\n".join(CF.report_lines(f))
        self.assertIn("| no opposition condition | 1 | 0 |", lines)
        self.assertIn("| live | 0 | 0 |", lines)

    def test_three_from_one_competition_only_under_the_relief(self):
        # 9 Nov 2026: five clear NBA legs, all "NBA", built no group
        legs = [dict(nba(i), comp="NBA") for i in range(1, 6)]
        self.write(legs)
        by, _ = CF.pool_days(pool_dir=self.dir)
        f = CF.funnel(by)
        self.assertEqual(f["clear"], {"nba": 5})
        self.assertEqual(f["relief"]["live"]["Card 2x"], 0)
        self.assertEqual(f["relief"]["comp-cap"]["Card 2x"], 1)
        self.assertEqual(G.COMP_MAX, 2)
        self.assertIn("| three legs a competition | 1 |", "\n".join(CF.report_lines(f)))

    def test_comp3_registered_and_the_cap_unchanged(self):
        import card_replay as R
        self.assertEqual(R.VARIANTS["comp3"], {"COMP_MAX": 3})
        three = [dict(nba(i), comp="NBA") for i in range(1, 4)]
        self.assertIsNone(G.mult_combo(three, 2.0, 3.0))
        self.assertIsNotNone(G.mult_combo(three[:2] + [dict(nba(3), comp="Other")], 2.0, 3.0))

    def test_days_outside_the_range_left_out(self):
        self.write([nba(1, when="2026-11-19T19:00:00Z")])
        by, _ = CF.pool_days(since=DAY, pool_dir=self.dir)
        self.assertEqual(dict(by), {})
        self.assertEqual(CF.report_lines(CF.funnel(by)), ["No pool days to read."])


if __name__ == "__main__":
    unittest.main()
