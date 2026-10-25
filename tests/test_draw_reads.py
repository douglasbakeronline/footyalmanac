"""A predicted draw scoreline on a drawn game is a correct reading (score.py,
6 Oct 2026) but not a win. Since 25 Oct 2026 (bug 3 of
claude/full-review-2026-10-25.md) the headline accuracy, the tier hit rates
and the band tables use the strict `won`; the reads are a separately
labelled figure."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score as SC

def row(pick, actual, score, p=(0.45, 0.30, 0.25), conf=None):
    return {"pick": pick, "actual": actual, "score": score, "p": p, "confidence": conf or max(p),
            "result": (1, 1), "celtic": False, "unrated": False}

class DrawReads(unittest.TestCase):
    def test_draw_scoreline_on_a_draw_is_a_read_not_a_win(self):
        r = row("h", "d", (1, 1))
        self.assertTrue(SC.correct(r))
        self.assertFalse(SC.won(r))
    def test_winner_scoreline_on_a_draw_is_wrong(self):
        self.assertFalse(SC.correct(row("h", "d", (2, 1))))
        self.assertFalse(SC.won(row("h", "d", (2, 1))))
    def test_draw_scoreline_on_a_win_for_the_other_side_is_wrong(self):
        self.assertFalse(SC.correct(row("h", "a", (1, 1))))
    def test_top_pick_counts_for_both(self):
        self.assertTrue(SC.correct(row("h", "h", (1, 1))))
        self.assertTrue(SC.won(row("h", "h", (1, 1))))
    def test_expected_adds_the_draw_chance(self):
        self.assertAlmostEqual(SC.expected(row("h", "d", (1, 1))), 0.75)
        self.assertAlmostEqual(SC.expected(row("h", "d", (2, 1))), 0.45)
    def test_unknown_scoreline_is_not_a_draw(self):
        self.assertFalse(SC.correct(row("h", "d", (-1, -1))))


ROWS = [row("h", "d", (1, 1)),      # read, not won
        row("h", "d", (2, 0)),      # drawn out
        row("h", "h", (2, 0)),      # won
        row("a", "a", (0, 1), p=(0.2, 0.25, 0.55))]   # won


class StrictHeadline(unittest.TestCase):
    def test_summary_headline_is_strict_and_reads_are_separate(self):
        s = SC.summarise(ROWS)
        self.assertEqual((s["correct"], s["won"], s["accuracy"]), (2, 2, 0.5))
        self.assertEqual((s["reads"], s["readRate"]), (3, 0.75))
        self.assertEqual((s["drawReads"], s["drawnOut"]), (1, 2))
        # the quoted side of each comparison
        self.assertAlmostEqual(s["quoted"], (0.45 * 3 + 0.55) / 4, places=4)
        self.assertAlmostEqual(s["quotedRead"], (0.75 + 0.45 * 2 + 0.55) / 4, places=4)
        # keys older readers depend on are still there
        for k in ("n", "correct", "accuracy", "logLoss", "homeRate", "exactScores", "exactRate",
                  "drawnOut", "drawReads", "picks", "actuals"):
            self.assertIn(k, s)

    def test_tier_table_is_strict(self):
        t = SC.tier_table(ROWS)
        n = sum(x["n"] for x in t)
        won = sum(x["correct"] for x in t)
        reads = sum(x["reads"] for x in t)
        self.assertEqual((n, won, reads), (4, 2, 3))
        for x in t:
            self.assertEqual(x["hit"], round(x["correct"] / x["n"], 4))
            self.assertEqual(x["readHit"], round(x["reads"] / x["n"], 4))
            self.assertIn("expectedRead", x)
            # strict quoted is the plain confidence, never with the draw chance added
            self.assertLessEqual(x["expected"], x["expectedRead"])

    def test_bands5_already_split_won_and_read(self):
        b = [x for x in SC.bands5(ROWS, lo=0.45) if x["n"]]
        self.assertEqual(sum(x["won"] for x in b), 2)
        self.assertEqual(sum(x["read"] for x in b), 3)


if __name__ == "__main__":
    unittest.main()
