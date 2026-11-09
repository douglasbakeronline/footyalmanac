"""9 Nov 2026 audit: ESPN's "Alex de Minaur" was never matched to the priced
"Alex De Minaur", so the raw spelling became the winner and four wins were
graded as losses. The winner is resolved against the priced pair."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_tennis as ST

M = {"playerA": "Mariano Navone", "playerB": "Alex De Minaur", "pick": "Alex De Minaur"}


class WinnerSpelling(unittest.TestCase):
    def test_case_difference_is_the_same_player(self):
        r = {"p0": "Alex de Minaur", "p1": "Mariano Navone", "winner": "Alex de Minaur",
             "pool": {"Alex de Minaur": None, "Mariano Navone": "Mariano Navone"}, "note": "bt 7-6 6-2"}
        self.assertEqual(ST.outcome(M, r), ("graded", "Alex De Minaur"))

    def test_hyphen_difference(self):
        m = {"playerA": "Thiago Agustin Tirante", "playerB": "Jan Lennard Struff"}
        self.assertEqual(ST.resolve_winner(m, "Jan-Lennard Struff"), "Jan Lennard Struff")

    def test_pooled_name_wins(self):
        self.assertEqual(ST.resolve_winner(M, "x", "Mariano Navone"), "Mariano Navone")

    def test_unknown_name_is_returned_as_it_came(self):
        self.assertEqual(ST.resolve_winner(M, "Someone Else"), "Someone Else")

    def test_loser_is_not_turned_into_the_pick(self):
        self.assertEqual(ST.resolve_winner(M, "mariano navone"), "Mariano Navone")


if __name__ == "__main__":
    unittest.main()
