"""tools/card_funnel.py under the live Card (11 Nov 2026, CARD_RULE 7 and 8):
model_fault's messages get their own keys, the reliefs are rule 7's, and
the days table counts every 2x a day can take. Synthetic legs; nothing is
fitted. tests/test_card_funnel.py covers the rule 6 reading."""
import os, sys, unittest
from unittest import mock
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_funnel as CF
import card_integrity as CI

DAY = "2026-11-20"
_LIVE = [mock.patch.object(G, "CARD_MODEL_RULE", True), mock.patch.object(G, "CARD_RULE", 8),
         mock.patch.object(G, "CARD_BUILD", ("Card 2x",))]
def setUpModule():
    for p in _LIVE: p.start()
def tearDownModule():
    for p in _LIVE: p.stop()


def nba(i, odds=1.30, fair=0.72, model=0.78):
    return {"sport": "nba", "event": f"Home{i} v Away{i}", "pick": f"Home{i}", "comp": f"Conf{i}", "when": f"{DAY}T19:00:00Z",
            "date": DAY, "odds": odds, "best": odds, "fair": fair, "margin": 1.05, "pModel": model, "pTested": model, "hit": 0.8,
            "p": model, "est": False, "implied": round(1 / odds, 4)}


def football(i, code="en.1", why=None):
    l = dict(nba(i), sport="football", event=f"FC{i} v United{i}", pick=f"FC{i}", home=f"FC{i}", away=f"United{i}", side="h",
             comp="Premier League", code=code)
    if why is not None: l["why"] = why
    return l


class OppositionRule12(unittest.TestCase):
    """17 Nov 2026: under CARD_RULE 12 the opposition's faults had no key.
    "no bookmaker price for the opposition" read as no-price (no column, so
    the leg vanished from the table) and "the opposition is priced 4.50,
    under 5" as other."""
    def setUp(self):
        p = mock.patch.object(G, "CARD_MODEL_OPP_MIN", {"football": 5.0}); p.start(); self.addCleanup(p.stop)

    def key(self, l): return CF.fault_key(G.card_fault(l))

    def test_opposition_faults_have_their_own_key(self):
        self.assertIn("opposition", CF.MODEL_KEYS)
        self.assertEqual(self.key(football(1)), "opposition")                 # no opposition price
        self.assertEqual(self.key(dict(football(1), opp=4.5)), "opposition")  # under the floor
        self.assertIsNone(self.key(dict(football(1), opp=6.0)))
        self.assertEqual(self.key(dict(nba(1), est=True)), "no-price")        # a missing price is still its own

    def test_opposition_relief_clears_the_leg(self):
        l = dict(football(1), opp=4.5)
        self.assertTrue(CF.clears_with(l, CF.rule_sets()[1]["opposition"]))

    def test_unpriced_football_leg_stands_in_at_the_floor(self):
        r = {k: v for k, v in football(1).items() if k not in ("odds", "best", "fair", "margin", "implied")}
        r["est"] = True
        self.assertTrue(CF.unpriced_ok(r))


class ModelKeys(unittest.TestCase):
    def key(self, l): return CF.fault_key(G.card_fault(l))

    def test_every_model_fault_branch_has_its_own_key(self):
        self.assertIsNone(self.key(nba(1)))
        self.assertEqual(self.key(dict(nba(1), sport="cfb")), "sport-off")
        self.assertEqual(self.key(dict(nba(1), timeEst=True)), "no-time")
        self.assertEqual(self.key(dict(nba(1), est=True)), "no-price")
        with mock.patch.object(G, "CARD_CORE_ONLY", True):   # the league limit (off live from 11 Nov 2026)
            self.assertEqual(self.key(football(1, code="af.187")), "league")      # was read as price-range
        self.assertEqual(self.key(dict(nba(1), odds=2.40)), "price-range")
        self.assertEqual(self.key(dict(nba(1), sport="tennis", pModel=0.70)), "sport-floor")
        self.assertEqual(self.key(dict(nba(1), pModel=0.58, fair=0.50)), "model-floor")
        self.assertEqual(self.key(dict(nba(1), pModel=0.68, fair=0.72)), "no-value")
        excl = football(1, why="promoted")
        if excl.get("why") not in G.CLEAN_WHY:
            self.assertEqual(self.key(excl), "list-excluded")

    def test_relief_and_kinds_follow_the_live_rule(self):
        self.assertEqual(CF.kinds(), ["Card 2x"])
        with mock.patch.object(G, "CARD_MODEL_OPP_MIN", {}):      # rule 11: no opposition floor, no relief for it
            self.assertNotIn("opposition", CF.leg_relief())
        with mock.patch.object(G, "CARD_MODEL_OPP_MIN", {"football": 5.0}):   # rule 12
            self.assertIn("opposition", CF.leg_relief())
            self.assertEqual(list(CF.rule_sets()[1])[-1], "comp-cap")
        self.assertIn("no-value", CF.leg_relief())

    def test_days_table_counts_every_2x(self):
        # nine clear legs at 1.30 from different competitions: three 2x groups (three legs each, 2.20)
        by = {DAY: [nba(i) for i in range(1, 10)]}
        f = CF.funnel(by)
        self.assertEqual(f["clear"], {"nba": 9})
        self.assertEqual(f["relief"]["live"], {"Card 2x": 1})
        self.assertEqual(f["groups"]["live"], 3)
        lines = "\n".join(CF.report_lines(f))
        self.assertIn("Read under CARD_RULE 8", lines)
        self.assertIn("| live | 1 | 3 |", lines)
        self.assertNotIn("Card 3x", lines)

    def test_no_value_relief_alone_adds_a_leg(self):
        by = {DAY: [nba(1), dict(nba(2), pModel=0.69, fair=0.72)]}
        f = CF.funnel(by)
        self.assertEqual(f["sole"]["nba"], {"no-value": 1})
        self.assertEqual(G.CARD_MODEL_EDGE, 0.0)   # restored


class OppIntegrity(unittest.TestCase):
    def test_opposition_price_needed_only_under_rule_6(self):
        l = football(1); l.pop("opp", None)
        self.assertTrue(CI.needs_opp({"rule": 6}, "2026-11-08", l))
        self.assertFalse(CI.needs_opp({"rule": 7}, "2026-11-11", l))
        self.assertFalse(CI.needs_opp({"rule": 8}, "2026-11-11", l))
        self.assertTrue(CI.needs_opp({"rule": 12}, "2026-11-16", l))   # 16 Nov 2026: rule 12 reads it again
        self.assertFalse(CI.needs_opp({"rule": 6, "wide": True}, "2026-11-08", l))
        self.assertFalse(CI.needs_opp({"rule": 6}, "2026-11-05", l))
        self.assertFalse(CI.needs_opp({"rule": 6}, "2026-11-08", dict(l, opp=9.5)))


if __name__ == "__main__":
    unittest.main()


class PoolOppositionFromArchive(unittest.TestCase):
    """17 Nov 2026: pool_days fills a football leg's missing opposition
    price from the football archive, as card_replay.pool_legs does."""
    def test_missing_opp_taken_from_the_archive(self):
        import gzip, json, tempfile
        pool, pred = tempfile.mkdtemp(), tempfile.mkdtemp()
        row = {k: v for k, v in football(1).items() if k not in ("implied",)}
        row["est"] = False
        with gzip.open(os.path.join(pool, f"pool-{DAY}.json.gz"), "wt", encoding="utf-8") as f:
            json.dump({"date": DAY, "legs": [row]}, f)
        with open(os.path.join(pred, f"{DAY}.json"), "w") as f:
            json.dump([{"league": "en.1", "date": DAY, "home": "FC1", "away": "United1", "kickoff": f"{DAY}T19:00:00Z",
                        "published": f"{DAY}T08:00:00Z", "market": {"avg": [1.30, 5.5, 7.5]}}], f)
        by, _ = CF.pool_days(pool_dir=pool, pred_dir=pred)
        (l,) = by[DAY]
        self.assertEqual((l["opp"], l.get("oppFrom")), (7.5, "archive"))
        by, _ = CF.pool_days(pool_dir=pool)          # a test pool reads no archive by default
        self.assertIsNone(by[DAY][0].get("opp"))
