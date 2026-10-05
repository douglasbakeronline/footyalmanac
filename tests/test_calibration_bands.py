import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import calibration_bands as C


class Bands(unittest.TestCase):
    def test_perfectly_calibrated_is_ok(self):
        rows = [(0.7, 1)] * 70 + [(0.7, 0)] * 30
        s = C.summarise(rows)
        self.assertEqual(s["verdict"], "ok")
        self.assertAlmostEqual(s["gap"], 0.0, places=6)

    def test_overconfident_is_flagged(self):
        rows = [(0.9, 1)] * 50 + [(0.9, 0)] * 50
        self.assertEqual(C.summarise(rows)["verdict"], "OVER-confident")

    def test_thin_band_is_not_read(self):
        self.assertEqual(C.summarise([(0.9, 0)] * 5)["verdict"], "thin")

    def test_bootstrap_is_deterministic(self):
        rows = [(0.6, i % 2) for i in range(40)]
        self.assertEqual(C.boot_gap(rows), C.boot_gap(rows))


if __name__ == "__main__":
    unittest.main()
