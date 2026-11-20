import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import market_gap as mg


class MarketGapTest(unittest.TestCase):
    def test_american_implied(self):
        self.assertAlmostEqual(mg.american_implied(-192), 0.6575, places=3)
        self.assertAlmostEqual(mg.american_implied(160), 0.3846, places=3)
        self.assertIsNone(mg.american_implied(None))
        self.assertIsNone(mg.american_implied(0))

    def test_ml_fair_sfa(self):
        # Stephen F. Austin v Indiana State, 20 Nov 2026: home -192, away +160
        f = mg.ml_fair({"mlH": -192, "mlA": 160}, "h")
        self.assertAlmostEqual(f, 0.631, places=2)
        self.assertGreaterEqual(0.826 - f, mg.GAP_WARN)   # the model's 82.6% would be marked

    def test_ml_fair_away_side_and_missing(self):
        f = mg.ml_fair({"mlH": 200, "mlA": -245}, "a")
        self.assertAlmostEqual(f, 0.681, places=2)
        self.assertIsNone(mg.ml_fair({"spread": -4.5}, "h"))
        self.assertIsNone(mg.ml_fair(None, "h"))

    def test_bands(self):
        self.assertEqual(mg.band_of(-0.02), "under")
        self.assertEqual(mg.band_of(0.0), "0-5")
        self.assertEqual(mg.band_of(0.099), "5-10")
        self.assertEqual(mg.band_of(0.10), "10-15")
        self.assertEqual(mg.band_of(0.30), "15+")

    def test_tally_and_warned(self):
        rows = [
            {"sport": "ncaab", "conf": 0.80, "result": "lost", "first": {"o": 1.60}},   # fair 0.595: 20 above
            {"sport": "ncaab", "conf": 0.80, "result": "won", "first": {"o": 1.25}},    # fair 0.762: 4 above
            {"sport": "ncaab", "conf": 0.80, "result": None, "first": {"o": 1.25}},     # unsettled: out
            {"sport": "football", "conf": 0.50, "result": "won", "first": {"o": 2.0}},  # under the floor: out
            {"sport": "football", "conf": 0.70, "result": "won", "first": None},        # unpriced: out
        ]
        T = mg.tally(rows)
        self.assertEqual(T["all"]["15+"]["n"], 1)
        self.assertEqual(T["all"]["0-5"]["landed"], 1.0)
        self.assertAlmostEqual(T["ncaab"]["15+"]["ret"], -1.0)
        w = mg.warned(rows)
        self.assertEqual((w["warn"]["n"], w["rest"]["n"]), (1, 1))
        self.assertEqual(w["warn"]["landed"], 0.0)


if __name__ == "__main__":
    unittest.main()
