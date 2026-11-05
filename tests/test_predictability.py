"""Pure-maths helpers of predictability.py (advisory tool)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predictability as P


class TestMaths(unittest.TestCase):
    def test_sig_logit_roundtrip_and_clamp(self):
        for p in (0.1, 0.5, 0.9):
            self.assertAlmostEqual(P._sig(P._logit(p)), p, places=9)
        self.assertTrue(math.isfinite(P._logit(0.0)))
        self.assertTrue(math.isfinite(P._logit(1.0)))
        self.assertEqual(P._sig(1e6), P._sig(30))
        self.assertGreater(P._sig(-1e6), 0)

    def test_ppg_needs_three(self):
        self.assertIsNone(P._ppg([3, 3]))
        self.assertEqual(P._ppg([3, 0, 0]), 1.0)

    def test_solve(self):
        x = P._solve([[2.0, 1.0], [1.0, 3.0]], [5.0, 10.0])
        self.assertAlmostEqual(x[0], 1.0)
        self.assertAlmostEqual(x[1], 3.0)

    def test_solve_singular_returns_zero_not_crash(self):
        x = P._solve([[1.0, 1.0], [1.0, 1.0]], [2.0, 2.0])
        self.assertEqual(len(x), 2)
        self.assertTrue(all(math.isfinite(v) for v in x))

    def test_fit_logistic_recovers_direction(self):
        X = [[1.0, v] for v in (-2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, -0.2, 0.2)]
        y = [0, 0, 0, 1, 0, 1, 1, 1, 1, 0]
        w = P.fit_logistic(X, y)
        self.assertGreater(w[1], 0)
        p = P.predict(w, X)
        self.assertLess(p[0], p[7])

    def test_bll(self):
        l = P.bll([0.8, 0.8], [1, 0])
        self.assertAlmostEqual(l[0], -math.log(0.8))
        self.assertAlmostEqual(l[1], -math.log(0.2))
        self.assertTrue(math.isfinite(P.bll([0.0], [1])[0]))

    def test_top_hit(self):
        p = [0.9, 0.8, 0.1, 0.2]
        y = [1, 1, 0, 0]
        self.assertEqual(P.top_hit(p, y, 0.5), 1.0)
        self.assertEqual(P.top_hit(p, y, 0.0), 1.0)  # at least one row

    def test_standardise_and_design(self):
        rows = [{"conf": 0.6, "sig": {"a": 1.0}}, {"conf": 0.7, "sig": {"a": 3.0}}]
        st = P.standardise(rows, ["a"])
        self.assertEqual(st["a"][0], 2.0)
        self.assertEqual(st["a"][1], 1.0)
        X = P.design(rows, ["a"], st)
        self.assertEqual(X[0][0], 1.0)
        self.assertEqual(X[0][2], -1.0)
        const = [{"conf": 0.6, "sig": {"a": 5.0}}] * 2
        self.assertEqual(P.standardise(const, ["a"])["a"][1], 1.0)

    def test_league_shift_shrinks_and_signs(self):
        rows = [{"code": "X", "conf": 0.6, "hit": 1}] * 50 + \
               [{"code": "Y", "conf": 0.6, "hit": 0}] * 50
        s = P.league_shift(rows, [0.0, 1.0])
        self.assertGreater(s["X"], 0)
        self.assertLess(s["Y"], 0)
        self.assertLess(abs(s["X"]), 10)


if __name__ == "__main__":
    unittest.main()
