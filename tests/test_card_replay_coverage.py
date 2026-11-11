"""The live Card's legs against the pool archive (9 Nov 2026): every Card leg
from PRICED_FROM must be in the pool at a real bookmaker price, or the
pool-based replay cannot rebuild the Card it is meant to judge; and the
tennis variants pre-registered for the 30 Nov review. Synthetic files only."""
import gzip, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_integrity as CI
import card_replay as CR

# 11 Nov 2026: the Card became the model's own picks (CARD_RULE 7). These tests
# cover the rule 6 machinery, which stays as the replay variant `rule6`, so the
# module runs under rule 6; tests/test_card_model_rule.py covers rule 7.
from unittest import mock as _mock
_RULE6 = [_mock.patch.object(G, "CARD_MODEL_RULE", False), _mock.patch.object(G, "CARD_RULE", 6)]
def setUpModule():
    for p in _RULE6: p.start()
def tearDownModule():
    for p in _RULE6: p.stop()



def pool(dirname, day, legs):
    with gzip.open(os.path.join(dirname, f"pool-{day}.json.gz"), "wt") as f:
        json.dump({"date": day, "legs": legs}, f)


class CardCoverage(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        pool(self.dir, "2026-11-21", [
            {"event": "Arsenal v Burnley", "pick": "Arsenal", "est": False, "fair": 0.78},                      # real price
            {"event": "A v B", "pick": "B", "est": True, "priced": {"odds": 1.3, "fair": 0.74}},                # estimate, then priced
            {"event": "C v D", "pick": "C", "est": True, "lastOdds": 1.25}])                                     # estimate only
        # a late US game: the Card day is 21 Nov, the start's UTC date (and pool file) is 22 Nov
        pool(self.dir, "2026-11-22", [{"event": "Knicks v Nets", "pick": "Knicks", "est": False, "fair": 0.8}])

    def test_findings_and_count(self):
        groups = {"2026-11-21": [
            {"name": "Card 2x", "legs": [{"event": "Arsenal v Burnley", "pick": "Arsenal"}, {"event": "A v B", "pick": "B"},
                                         {"event": "Knicks v Nets", "pick": "Knicks"}]},
            {"name": "Card 3x", "legs": [{"event": "C v D", "pick": "C"}, {"event": "E v F", "pick": "F"}]},
            {"name": "Model 2x", "legs": [{"event": "G v H", "pick": "G"}]}]}                                    # not the Card
        f, (have, total) = CI.card_coverage(groups, pool_dir=self.dir, since="2026-11-10")
        self.assertEqual((have, total), (3, 5))
        self.assertEqual(sorted((x["pick"], x["why"]) for x in f),
                         [("C", "pool holds the model's estimate only"), ("F", "not in the pool")])
        self.assertTrue(all(x["check"] == "card-leg-unreplayable" for x in f))

    def test_days_before_since_are_not_checked(self):
        groups = {"2026-11-21": [{"name": "Card 2x", "legs": [{"event": "E v F", "pick": "F"}]}]}
        self.assertEqual(CI.card_coverage(groups, pool_dir=self.dir, since="2026-11-22"), ([], (0, 0)))


class TennisVariants(unittest.TestCase):

    def test_registered_and_live_untouched(self):
        self.assertIn("tennis", CR.VARIANTS["notennis"]["CARD_SPORTS_OFF"])
        self.assertTrue(G.CARD_SPORTS_OFF <= CR.VARIANTS["notennis"]["CARD_SPORTS_OFF"])
        self.assertEqual(CR.VARIANTS["tennis80"]["CARD_SPORT_MIN"]["tennis"], 0.80)
        self.assertNotIn("tennis", G.CARD_SPORTS_OFF)
        self.assertEqual(G.CARD_SPORT_MIN["tennis"], 0.75)

    def test_patch_reaches_card_fault_and_is_restored(self):
        leg = {"sport": "tennis", "pick": "P", "pModel": 0.78, "hit": 0.78}
        saved = G.CARD_SPORT_MIN
        G.CARD_SPORT_MIN = CR.VARIANTS["tennis80"]["CARD_SPORT_MIN"]
        try:
            self.assertIn("80%+", G.card_fault(dict(leg)))
        finally:
            G.CARD_SPORT_MIN = saved
        G.CARD_SPORTS_OFF, old = CR.VARIANTS["notennis"]["CARD_SPORTS_OFF"], G.CARD_SPORTS_OFF
        try:
            self.assertIn("off the Card", G.card_fault(dict(leg)))
        finally:
            G.CARD_SPORTS_OFF = old
        # build() restores the live constants after a patched day
        CR.build([], "2026-11-21", "notennis")
        self.assertNotIn("tennis", G.CARD_SPORTS_OFF)


if __name__ == "__main__":
    unittest.main()
