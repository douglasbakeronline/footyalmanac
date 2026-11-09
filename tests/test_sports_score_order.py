"""9 Nov 2026 audit: at a neutral site ESPN can swap home and away between the
archive and the result; the stored score must follow the priced home side."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports as SP

R = {"home": "California Golden Bears", "away": "Houston Cougars", "pick": "Houston Cougars"}


class ScoreOrder(unittest.TestCase):
    def test_same_order_kept(self):
        g = {"hn": "California Golden Bears", "an": "Houston Cougars", "hs": 68, "as": 86}
        row = SP.settle(R, g)
        self.assertEqual((row["score"], row["winner"], row["ok"]), ([68, 86], "Houston Cougars", True))

    def test_swapped_sides_reorder_the_score_not_the_winner(self):
        g = {"hn": "Houston Cougars", "an": "California Golden Bears", "hs": 86, "as": 68}
        row = SP.settle(R, g)
        self.assertEqual((row["score"], row["winner"], row["ok"]), ([68, 86], "Houston Cougars", True))

    def test_tie_is_void(self):
        self.assertIsNone(SP.settle(R, {"hn": "a", "an": "b", "hs": 3, "as": 3}))


if __name__ == "__main__":
    unittest.main()
