"""MAX_GOALS 15 (25 Oct 2026, bug 21 of claude/full-review-2026-10-25.md).
The 10x10 grid left up to 31% of the Poisson mass off it in lopsided ties,
which bent scorelines, BTTS and over 2.5. An ordinary fixture barely moves."""
import math, os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E


def grid_mass(lh, la, n):
    """Raw Poisson mass inside an n x n grid (no Dixon-Coles term)."""
    ph = [math.exp(-lh) * lh ** i / math.factorial(i) for i in range(n + 1)]
    pa = [math.exp(-la) * la ** i / math.factorial(i) for i in range(n + 1)]
    return sum(ph) * sum(pa)


def with_max_goals(n, fn):
    saved = E.MAX_GOALS
    E.MAX_GOALS = n
    try:
        return fn()
    finally:
        E.MAX_GOALS = saved


class MaxGoals(unittest.TestCase):
    def test_is_fifteen(self):
        self.assertEqual(E.MAX_GOALS, 15)

    def test_ordinary_fixture_1x2_unchanged_to_1e6(self):
        a = with_max_goals(10, lambda: E.probabilities_from_xg(1.2, 0.9))
        b = with_max_goals(15, lambda: E.probabilities_from_xg(1.2, 0.9))
        for k in ("home", "draw", "away", "confidence"):
            self.assertLess(abs(a[k] - b[k]), 1e-6, k)
        self.assertEqual(a["likely_score"], b["likely_score"])

    def test_lopsided_tie_mass_beyond_ten_is_captured(self):
        lh, la = 9.0, 1.0
        missing10 = 1 - grid_mass(lh, la, 10)
        missing15 = 1 - grid_mass(lh, la, 15)
        self.assertGreater(missing10, 0.25)          # a quarter of the mass fell off the old grid
        self.assertLess(missing15, 0.03)
        a = with_max_goals(10, lambda: E.probabilities_from_xg(lh, la))
        b = with_max_goals(15, lambda: E.probabilities_from_xg(lh, la))
        # the markets the truncation bent now see that mass
        self.assertGreater(b["home"], a["home"])
        self.assertGreater(b["over25"], a["over25"])
        self.assertAlmostEqual(b["home"] + b["draw"] + b["away"], 1.0, places=9)

    def test_tune_grid_follows_the_engine(self):
        import tune
        self.assertEqual(tune.MAXG, E.MAX_GOALS)
        p = tune.outcome(1.2, 0.9, E.RHO)
        self.assertAlmostEqual(sum(p), 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
