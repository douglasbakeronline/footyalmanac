"""The Model card on the replay (10 Nov 2026): tools/card_replay.py's
modelcard builds groupings.MODEL_KINDS on the day's legs, graded and staked
as the Card kind it mirrors; tools/card_legs_history.legs(model=True) admits
legs on the model's own chance."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools")); sys.path.insert(0, os.path.join(HERE, "tests"))
import card_replay as CR
import card_legs_history as H
import groupings as G
from test_card_fillers import by_day, row

# 11 Nov 2026: the Card became the model's own picks (CARD_RULE 7). These tests
# cover the rule 6 machinery, which stays as the replay variant `rule6`, so the
# module runs under rule 6; tests/test_card_model_rule.py covers rule 7.
from unittest import mock as _mock
_RULE6 = [_mock.patch.object(G, "CARD_MODEL_RULE", False), _mock.patch.object(G, "CARD_RULE", 6)]
def setUpModule():
    for p in _RULE6: p.start()
def tearDownModule():
    for p in _RULE6: p.stop()



class ModelCard(unittest.TestCase):
    def test_registered(self):
        self.assertEqual(CR.VARIANTS["modelcard"], {"_KINDS": "model"})

    def model_day(self):
        # the model 6 points above the bookmakers: the Model card's pick, never the Card's
        return [((0.78, 0.14, 0.08), row(i, (1.38, 4.8, 8.0))) for i in range(7)]

    def test_builds_on_the_models_picks(self):
        (d, legs), = by_day(H.legs(self.model_day(), model=True)).items()
        self.assertEqual(CR.build(legs, d, "live"), [])
        gs = CR.build(legs, d, "modelcard")
        self.assertTrue(gs)
        for g in gs:
            self.assertIn(g["name"], ("Card 2x", "Card 3x"))
            self.assertTrue(g["model"])
            self.assertEqual(g["stake"], G.CARD_STAKE[g["name"]])
            for l in g["legs"]: self.assertIsNone(G.model_fault(l))

    def test_model_gate_admits_on_the_models_chance(self):
        rows = [((0.62, 0.22, 0.16), row(0, (1.80, 3.6, 4.6)))]          # bookmakers about 53%
        self.assertEqual(H.legs(rows), [])
        self.assertEqual(len(H.legs(rows, model=True)), 1)
        self.assertEqual(H.legs([((0.58, 0.24, 0.18), row(0, (1.45, 4.2, 7.0)))], model=True), [])   # model under 60%


if __name__ == "__main__":
    unittest.main()
