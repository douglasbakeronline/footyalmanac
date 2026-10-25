"""Per-league home advantage (25 Oct 2026): off unless home-advantage.json
carries the league; when it does, the live build and the replay apply the
same factor. Standard library only."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import replay as R


class LeagueHome(unittest.TestCase):
    def test_absent_league_is_neutral(self):
        self.assertEqual(E.league_home("zz.none"), (1.0, 1.0))

    def test_factor_tilts_home_and_away(self):
        saved = dict(E.LEAGUE_HOME)
        try:
            E.LEAGUE_HOME["xx.1"] = 1.05
            h, a = E.league_home("xx.1")
            self.assertAlmostEqual(h * a, 1.0)
            self.assertGreater(h, 1.0)
        finally:
            E.LEAGUE_HOME.clear(); E.LEAGUE_HOME.update(saved)

    def test_replay_applies_home_s(self):
        prior = [("2025-01-0%d" % (i % 9 + 1), "A", "B", 1, 1) for i in range(10)]
        test = [("2026-01-01", "A", "B", 2, 1)]
        base = list(R.replay_league(prior, test, 1))[0]
        tilt = list(R.replay_league(prior, test, 1, params={"home_s": 1.1}))[0]
        self.assertAlmostEqual(tilt[1], base[1] * 1.1, places=6)
        self.assertAlmostEqual(tilt[2], base[2] / 1.1, places=6)


if __name__ == "__main__":
    unittest.main()
