"""tools/home_away_tilt.py: the side report and the tempering it applies,
offline (26 Oct 2026). The replay itself is covered by test_evaluation."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))
import home_away_tilt as HA
import tune as T
import engine as E


class SideReport(unittest.TestCase):
    def test_counts_by_picked_side(self):
        probs = [(0.6, 0.25, 0.15, 0), (0.6, 0.25, 0.15, 2),
                 (0.2, 0.3, 0.5, 2), (0.2, 0.3, 0.5, 0), (0.2, 0.3, 0.5, 2)]
        r = HA.side_report(probs)
        self.assertEqual(r["home"]["n"], 2)
        self.assertAlmostEqual(r["home"]["quoted"], 0.6)
        self.assertAlmostEqual(r["home"]["landed"], 0.5)
        self.assertEqual(r["away"]["n"], 3)
        self.assertAlmostEqual(r["away"]["landed"], 2 / 3, places=4)
        self.assertEqual(r["draw"]["n"], 0)
        self.assertAlmostEqual(sum(r["meanQuoted"]), 1.0, places=3)
        self.assertEqual(r["actual"], [0.4, 0.0, 0.6])

    def test_probs_under_matches_engine_temper(self):
        live = T.live_baseline()
        raw = [(0.55, 0.25, 0.20, 0), (0.30, 0.30, 0.40, 2)]
        got = HA.probs_under(raw, live)
        for (h, d, a, y), (gh, gd, ga, gy) in zip(raw, got):
            if live["kind"] == "curve":
                exp = E.temper(h, d, a)   # engine reads the same calibration.json
            else:
                exp = E.temper(h, d, a, T=live["T"])
            self.assertAlmostEqual(gh, exp[0], places=12)
            self.assertAlmostEqual(gd, exp[1], places=12)
            self.assertAlmostEqual(ga, exp[2], places=12)
            self.assertEqual(gy, y)

    def test_gates_match_tune(self):
        self.assertTrue(all(HA.gates_for(T.MIN_HOLDOUT, -T.MIN_GAIN, T.MAX_P_WORSE).values()))
        g = HA.gates_for(T.MIN_HOLDOUT - 1, -0.0001, 0.5)
        self.assertEqual(g, {"enoughData": False, "notWorse": False, "worthIt": False})

    def test_grid_is_live_inclusive(self):
        self.assertEqual(HA.HA_GRID[0], 0.80)
        self.assertEqual(HA.HA_GRID[-1], 1.00)
        self.assertEqual(len(HA.HA_GRID), 11)
        self.assertIn(E.RHO, HA.RHO_GRID)


if __name__ == "__main__":
    unittest.main()
