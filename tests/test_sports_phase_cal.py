import unittest
import sports


class PhaseCal(unittest.TestCase):
    cal = {"a": -0.03, "b": 0.94, "early": {"a": 0.29, "b": 1.05}, "months": [11, 12]}

    def test_early_months_use_early_curve(self):
        e = sports.calibrate(0.7, self.cal, "2025-11-20T00:00Z")
        l = sports.calibrate(0.7, self.cal, "2026-02-20T00:00Z")
        self.assertGreater(e, 0.7)
        self.assertLess(l, 0.7)

    def test_plain_cal_and_no_date_unchanged(self):
        plain = {"a": 0.1, "b": 0.9}
        self.assertEqual(sports.calibrate(0.6, plain, "2025-11-20"), sports.calibrate(0.6, plain))
        self.assertEqual(sports.calibrate(0.6, None, "2025-11-20"), 0.6)
        self.assertAlmostEqual(sports.calibrate(0.7, self.cal), sports.calibrate(0.7, self.cal, "2026-02-01"))


if __name__ == "__main__":
    unittest.main()
