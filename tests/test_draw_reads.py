"""A predicted draw scoreline on a drawn game is a correct reading (score.py, 6 Oct 2026)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score as SC

def row(pick, actual, score, p=(0.45, 0.30, 0.25)):
    return {"pick": pick, "actual": actual, "score": score, "p": p, "confidence": max(p),
            "result": (1, 1), "celtic": False, "unrated": False}

class DrawReads(unittest.TestCase):
    def test_draw_scoreline_on_a_draw_is_right(self):
        self.assertTrue(SC.correct(row("h", "d", (1, 1))))
    def test_winner_scoreline_on_a_draw_is_wrong(self):
        self.assertFalse(SC.correct(row("h", "d", (2, 1))))
    def test_draw_scoreline_on_a_win_for_the_other_side_is_wrong(self):
        self.assertFalse(SC.correct(row("h", "a", (1, 1))))
    def test_top_pick_still_counts(self):
        self.assertTrue(SC.correct(row("h", "h", (1, 1))))
    def test_expected_adds_the_draw_chance(self):
        self.assertAlmostEqual(SC.expected(row("h", "d", (1, 1))), 0.75)
        self.assertAlmostEqual(SC.expected(row("h", "d", (2, 1))), 0.45)
    def test_summary_counts_draw_reads_and_not_as_drawn_out(self):
        s = SC.summarise([row("h", "d", (1, 1)), row("h", "d", (2, 0)), row("h", "h", (2, 0))])
        self.assertEqual((s["correct"], s["drawReads"], s["drawnOut"]), (2, 1, 1))
    def test_unknown_scoreline_is_not_a_draw(self):
        self.assertFalse(SC.correct(row("h", "d", (-1, -1))))

if __name__ == "__main__":
    unittest.main()
