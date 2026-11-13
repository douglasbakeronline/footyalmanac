import unittest
import sports


class EarlyCal(unittest.TestCase):
    def test_nov_dec_only(self):
        c = sports.calibrate_for("ncaab", "2026-11-14T01:00Z", None)
        self.assertEqual(c, {"a": 0.2921, "b": 1.0497})
        self.assertIsNone(sports.calibrate_for("ncaab", "2027-02-01T01:00Z", None))

    def test_other_sports_untouched(self):
        self.assertEqual(sports.calibrate_for("nba", "2026-11-14T01:00Z", {"a": 1, "b": 1}), {"a": 1, "b": 1})

    def test_lifts_a_favourite(self):
        c = sports.calibrate_for("ncaab", "2026-12-01T00:00Z", None)
        self.assertGreater(sports.calibrate(0.8, c), 0.8)


if __name__ == "__main__":
    unittest.main()
