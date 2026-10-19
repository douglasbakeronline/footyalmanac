"""Domestic cup calibration (19 Oct 2026): cup favourites land far under a
league-style quote, so domestic cup ties carry a second curve on top of the
league calibration (engine.CUP_CALIBRATION, fitted by tools/cup_calibration.py
on the cup replay, checked on later ties). No network."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E


class CupTemper(unittest.TestCase):

    def test_confident_cup_favourites_are_pulled_down_hard(self):
        q = E.cup_temper({"home": 0.75, "draw": 0.17, "away": 0.08, "xg_home": 2.0})
        self.assertLess(q["home"], 0.62)
        self.assertAlmostEqual(q["home"] + q["draw"] + q["away"], 1.0, places=9)
        self.assertEqual(q["xg_home"], 2.0)                  # only the three outcomes move
        self.assertEqual(max(q, key=lambda k: q[k] if k in ("home", "draw", "away") else -1), "home")

    def test_close_ties_barely_move(self):
        q = E.cup_temper({"home": 0.40, "draw": 0.30, "away": 0.30})
        self.assertLess(abs(q["home"] - 0.40), 0.03)

    def test_switched_off_with_none(self):
        p = {"home": 0.75, "draw": 0.17, "away": 0.08}
        self.assertEqual(E.cup_temper(p, cal={}), p)


if __name__ == "__main__":
    unittest.main()
