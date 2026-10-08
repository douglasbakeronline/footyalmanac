"""Tennis name matching: the same words in another order (7 Oct 2026)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_tennis as B


class WordOrder(unittest.TestCase):
    def test_family_name_first(self):
        idx = B.build_index({"Juncheng Shang": {}, "Yunchaokete Bu": {}})
        self.assertEqual(B.match_player("Shang Juncheng", *idx), "Juncheng Shang")
        self.assertEqual(B.match_player("Bu Yunchaokete", *idx), "Yunchaokete Bu")

    def test_two_players_same_words_refused(self):
        idx = B.build_index({"Xinyu Wang": {}, "Wang Xinyu": {}})
        self.assertIsNone(B.match_player("Xinyu Wang Jr", *idx))
        # exact spelling still wins
        self.assertEqual(B.match_player("Wang Xinyu", *idx), "Wang Xinyu")

    def test_rank_layer_off(self):
        self.assertFalse(B.ATP_RANK_LAYER)
        self.assertEqual(B.LIST_MIN["ATP"], 0.75)


if __name__ == "__main__":
    unittest.main()
