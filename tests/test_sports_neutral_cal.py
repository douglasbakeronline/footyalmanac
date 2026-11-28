"""A neutral court and the calibration's home term (27 Nov 2026, sports.NEUTRAL0)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports  # noqa: E402

CAL = {"a": -0.03, "b": 0.92, "early": {"a": 0.31, "b": 0.98}, "months": [11, 12]}


def logit(p):
    return math.log(p / (1 - p))


class NeutralIntercept(unittest.TestCase):
    def test_old_cal_unchanged_at_a_neutral_site(self):
        # sports.json as it stands carries no flag: the board's numbers do not move
        for when in ("2026-11-27T20:00Z", "2027-02-01T20:00Z"):
            self.assertEqual(sports.calibrate(0.7, CAL, when, True), sports.calibrate(0.7, CAL, when))

    def test_flag_drops_the_intercept_at_a_neutral_site_only(self):
        cal = {**CAL, "neutral0": True}
        p = sports.calibrate(0.7, cal, "2026-11-27T20:00Z", True)
        self.assertAlmostEqual(logit(p), 0.98 * logit(0.7), places=9)
        p = sports.calibrate(0.7, cal, "2027-02-01T20:00Z", True)
        self.assertAlmostEqual(logit(p), 0.92 * logit(0.7), places=9)
        # a venue game keeps the full curve
        self.assertEqual(sports.calibrate(0.7, cal, "2026-11-27T20:00Z", False),
                         sports.calibrate(0.7, CAL, "2026-11-27T20:00Z"))

    def test_neutral_symmetry(self):
        # with no intercept, swapping the listed sides swaps the chance
        cal = {**CAL, "neutral0": True}
        a = sports.calibrate(0.64, cal, "2026-11-27T20:00Z", True)
        b = sports.calibrate(0.36, cal, "2026-11-27T20:00Z", True)
        self.assertAlmostEqual(a + b, 1.0, places=9)

    def test_fit_on_venue_games_only(self):
        def game(i, neutral, home_won):
            return ({"when": f"2024-11-{1 + i % 28:02d}T20:00Z", "hs": 70 if home_won else 60,
                     "as": 60 if home_won else 70, "neutral": neutral}, 0.6, True)
        venue = [game(i, False, i % 3 != 0) for i in range(300)]
        late = [({**g, "when": "2025-02" + g["when"][7:]}, p, w) for g, p, w in venue]
        neutral = [game(i, True, False) for i in range(300)]   # listed sides that always lose
        win = sports.FIT
        plain = sports.fit_phase_calibration(venue + late + neutral, win, (11, 12))
        venue_only = sports.fit_phase_calibration(venue + late, win, (11, 12))
        flagged = sports.fit_phase_calibration(venue + late + neutral, win, (11, 12), neutral0=True)
        self.assertTrue(flagged["neutral0"])
        self.assertNotIn("neutral0", plain)
        self.assertEqual(flagged["early"], venue_only["early"])
        self.assertNotEqual(plain["early"], venue_only["early"])

    def test_ncaab_is_the_only_sport(self):
        self.assertEqual(sports.NEUTRAL0, {"ncaab"})
        self.assertTrue(sports.NEUTRAL0 <= set(sports.PHASE_MONTHS))


if __name__ == "__main__":
    unittest.main()
