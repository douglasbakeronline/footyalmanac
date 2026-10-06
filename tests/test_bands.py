"""bands.band_rate: a pick's own band, derived from the cumulative bands (6 Oct 2026)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bands import band_rate

WTA = [{"from": 0.55, "hit": 0.6829, "n": 965}, {"from": 0.6, "hit": 0.7151, "n": 737},
       {"from": 0.65, "hit": 0.7681, "n": 539}, {"from": 0.7, "hit": 0.8021, "n": 384},
       {"from": 0.75, "hit": 0.8103, "n": 253}, {"from": 0.8, "hit": 0.8696, "n": 138},
       {"from": 0.85, "hit": 0.9032, "n": 62}]


class Bands(unittest.TestCase):
    def test_low_pick_no_longer_borrows_the_strong_calls(self):
        b = band_rate(0.62, WTA)          # Sasnovich on 6 Oct: shown 72%, its band landed 57%
        self.assertEqual((b["from"], b["to"], b["n"]), (0.6, 0.65, 198))
        self.assertAlmostEqual(b["hit"], 0.5708, places=3)
        self.assertEqual(b["cumHit"], 0.7151)

    def test_top_band_is_open(self):
        b = band_rate(0.93, WTA)
        self.assertEqual((b["from"], b["to"], b["hit"], b["n"]), (0.85, None, 0.9032, 62))

    def test_thin_band_widens_until_it_holds_enough(self):
        bs = [{"from": 0.7, "hit": 0.7347, "n": 49}, {"from": 0.75, "hit": 0.7619, "n": 21},
              {"from": 0.8, "hit": 0.8, "n": 10}]
        b = band_rate(0.72, bs)           # 70-75% has 28 calls: widened to 70-80%
        self.assertEqual((b["from"], b["to"], b["n"]), (0.7, 0.8, 39))

    def test_below_every_band(self):
        self.assertIsNone(band_rate(0.5, WTA))
        self.assertIsNone(band_rate(0.9, None))


if __name__ == "__main__":
    unittest.main()
