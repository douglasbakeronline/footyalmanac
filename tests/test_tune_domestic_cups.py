"""tune_domestic_cups.py: the cup-tie parser, the outcome model, the paired
bootstrap and the tier fit, with no network (fetch reads a temp cache)."""
import math
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import tune_domestic_cups as T


class ParseClean(unittest.TestCase):
    def test_both_line_shapes(self):
        text = "\n".join([
            "  Arsenal FC   2-1   Luton Town",
            "  Chelsea v Everton 0-0",
        ])
        self.assertEqual(T.parse_clean(text, "2023-24"), [
            ("2023-24", "Arsenal FC", "Luton Town", 2, 1),
            ("2023-24", "Chelsea", "Everton", 0, 0),
        ])

    def test_half_time_score_in_brackets_is_ignored(self):
        rows = T.parse_clean("  Leeds   3-2 (1-1)   Hull", "s")
        self.assertEqual(rows, [("s", "Leeds", "Hull", 3, 2)])

    def test_headers_comments_and_blanks_skipped(self):
        text = "= FA Cup\n# note\n\n▪ Round 1\n• x\n"
        self.assertEqual(T.parse_clean(text, "s"), [])

    def test_extra_time_penalties_and_aggregates_dropped(self):
        text = "\n".join([
            "  A   1-1 pen. 4-3   B",
            "  C   2-1 a.e.t.   D",
            "  E   3-3 (agg)   F",
            "  G   1-0   H",
        ])
        self.assertEqual(T.parse_clean(text, "s"), [("s", "G", "H", 1, 0)])

    def test_windows_line_endings(self):
        rows = T.parse_clean("  A   1-0   B\r\n  C   0-2   D\r\n", "s")
        self.assertEqual([r[1:] for r in rows], [("A", "B", 1, 0), ("C", "D", 0, 2)])


class Outcome(unittest.TestCase):
    def test_sums_to_one(self):
        for lh, la in ((1.4, 1.1), (0.3, 3.0), (2.5, 0.2)):
            self.assertAlmostEqual(sum(T.outcome(lh, la)), 1.0, places=9)

    def test_symmetric_when_teams_equal(self):
        h, d, a = T.outcome(1.3, 1.3)
        self.assertAlmostEqual(h, a, places=9)
        self.assertGreater(d, 0.2)

    def test_stronger_home_side_favoured(self):
        h, d, a = T.outcome(2.2, 0.7)
        self.assertGreater(h, 0.6)
        self.assertGreater(h, a)

    def test_rho_zero_matches_plain_poisson_draw(self):
        lh, la = 1.2, 0.9
        _, d, _ = T.outcome(lh, la, rho=0.0)
        plain = sum(math.exp(-lh) * lh ** i / math.factorial(i) *
                    math.exp(-la) * la ** i / math.factorial(i) for i in range(30))
        self.assertAlmostEqual(d, plain, places=3)


class Paired(unittest.TestCase):
    def test_identical_series_has_zero_delta(self):
        m, p = T.paired([0.5, 0.7, 0.6], [0.5, 0.7, 0.6])
        self.assertEqual(m, 0.0)
        self.assertEqual(p, 0.0)

    def test_clearly_worse_candidate(self):
        a = [1.0] * 40
        b = [0.5] * 40
        m, p = T.paired(a, b)
        self.assertAlmostEqual(m, 0.5)
        self.assertEqual(p, 1.0)

    def test_deterministic_seed(self):
        a = [0.9, 0.4, 0.7, 1.1, 0.3]
        b = [0.8, 0.5, 0.7, 0.9, 0.4]
        self.assertEqual(T.paired(a, b), T.paired(a, b))


class Score(unittest.TestCase):
    def test_accuracy_and_loss(self):
        strength = {"en.1": 1.0, "en.5": 0.4}
        rows = [("FA Cup", "s", "H", "en.1", "A", "en.5", 3, 0),
                ("FA Cup", "s", "H2", "en.1", "A2", "en.5", 0, 2)]
        per, acc = T.score(rows, strength, 1.3, 1.2, 0.95)
        self.assertEqual(len(per), 2)
        self.assertEqual(acc, 0.5)           # favourite home win hit, away win missed
        self.assertLess(per[0], per[1])      # the upset costs more
        self.assertTrue(all(x >= 0 for x in per))


class FitTiers(unittest.TestCase):
    def rows(self, n=60):
        out = []
        for i in range(n):
            out.append(("FA Cup", "s", "H", "en.1", "A", "en.2", 2, 1))
            out.append(("FA Cup", "s", "H", "en.3", "A", "en.4", 1, 1))
        return out

    def test_returns_every_tier_and_counts(self):
        fitted, mu, ha, aa, n = T.fit_tiers(self.rows(), epochs=50)
        self.assertEqual(set(fitted), set(T.TIERS))
        self.assertEqual(n["en.1"], 60)
        self.assertEqual(n["en.5"], 0)
        self.assertGreater(mu, 0)

    def test_top_tier_anchored_and_unseen_tier_stays_at_prior(self):
        import engine as E
        fitted, *_ = T.fit_tiers(self.rows(), epochs=50)
        self.assertAlmostEqual(fitted["en.1"], round(E.LEAGUES["en.1"]["strength"], 3), places=3)
        # no ties: gradient is zero and the regulariser sits at the prior
        self.assertAlmostEqual(fitted["en.5"], round(E.LEAGUES["en.5"]["strength"], 3), places=3)


class LoadCupTies(unittest.TestCase):
    def test_ties_resolve_to_tiers_without_network(self):
        s = T.SEASONS[0]
        files = {
            f"england/master/{s}/1-premierleague.txt": "  Alpha   1-0   Beta\n",
            f"england/master/{s}/2-championship.txt": "  Gamma   2-2   Delta\n",
            f"england/master/{s}/facup.txt": "  Alpha   3-1   Gamma\n  Alpha   1-0   Unknown FC\n",
        }

        def fake(path, cache_dir):
            if path in files:
                return files[path]
            raise OSError("not cached")
        old_fetch, old_seasons = T.fetch, T.SEASONS
        T.fetch, T.SEASONS = fake, [s]
        try:
            resolved, notes = T.load_cup_ties("unused")
        finally:
            T.fetch, T.SEASONS = old_fetch, old_seasons
        # the tie with a side in no league file is dropped, not guessed
        self.assertEqual(resolved, [("FA Cup", s, "Alpha", "en.1", "Gamma", "en.2", 3, 1)])
        self.assertTrue(any("EFL Cup" in n and "not available" in n for n in notes))
        self.assertTrue(any("Spain" in n for n in notes))


if __name__ == "__main__":
    unittest.main()
