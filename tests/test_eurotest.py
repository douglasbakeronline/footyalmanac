"""eurotest.py: the pure helpers behind the European league-strength fit."""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import eurotest as T


class SeasonsTest(unittest.TestCase):
    def test_split_year_league(self):
        self.assertEqual(T.domestic_seasons("en.1", "2025-26"),
                         (["2024-25", "2023-24"], "2025-26"))

    def test_calendar_year_league(self):
        code = next(c for c, m in E.LEAGUES.items()
                    if "season" in m and "-" not in m["season"])
        self.assertEqual(T.domestic_seasons(code, "2026-27"),
                         (["2025", "2024"], "2026"))

    def test_century_rollover(self):
        self.assertEqual(T.domestic_seasons("en.1", "2099-00"),
                         (["2098-99", "2097-98"], "2099-00"))


class ConstantsTest(unittest.TestCase):
    def test_every_country_code_maps_to_a_league(self):
        for cc, code in T.CC.items():
            self.assertIn(code, E.LEAGUES, cc)

    def test_monaco_plays_in_ligue_1(self):
        self.assertEqual(T.CC["MON"], "fr.1")


class OutcomeTest(unittest.TestCase):
    def test_outcome(self):
        self.assertEqual(T.outcome({"hg": 2, "ag": 1}), "home")
        self.assertEqual(T.outcome({"hg": 0, "ag": 3}), "away")
        self.assertEqual(T.outcome({"hg": 1, "ag": 1}), "draw")

    def test_hand_is_every_league_strength(self):
        h = T.hand()
        self.assertEqual(set(h), set(E.LEAGUES))
        self.assertTrue(all(v > 0 for v in h.values()))


class PairedTest(unittest.TestCase):
    def test_clear_improvement_is_never_worse(self):
        mu, sd, p = T.paired([0.5] * 20, [1.0] * 20)
        self.assertAlmostEqual(mu, -0.5)
        self.assertEqual(p, 0.0)

    def test_clear_loss_is_always_worse(self):
        mu, sd, p = T.paired([1.0] * 20, [0.5] * 20)
        self.assertAlmostEqual(mu, 0.5)
        self.assertEqual(p, 1.0)

    def test_deterministic(self):
        a, b = [0.1, 0.9, 0.4, 0.7], [0.3, 0.2, 0.5, 0.6]
        self.assertEqual(T.paired(a, b), T.paired(a, b))


class BandsTest(unittest.TestCase):
    def test_bands_count_and_rate(self):
        out = T.bands([True, False, True], [0.50, 0.52, 0.90])
        self.assertEqual([(o[0], o[1], o[2]) for o in out],
                         [(0.45, 0.55, 2), (0.70, 1.01, 1)])
        self.assertAlmostEqual(out[0][3], 0.51)
        self.assertAlmostEqual(out[0][4], 0.5)
        self.assertEqual(out[1][4], 1.0)

    def test_edge_belongs_to_upper_band(self):
        out = T.bands([True], [0.55])
        self.assertEqual((out[0][0], out[0][1]), (0.55, 0.62))

    def test_empty(self):
        self.assertEqual(T.bands([], []), [])


if __name__ == "__main__":
    unittest.main()
