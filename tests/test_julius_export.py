"""The Julius export (tools/julius_export.py, 8 Oct 2026): marks, groups and
tallies match the site's grading, and football is compared against the
chance the site quotes for its own rule (draw readings included). No network.
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
sys.path.insert(0, os.path.dirname(HERE))

import julius_export as J


class Rows(unittest.TestCase):

    def test_marks_groups_and_flags(self):
        won = J._row(group="list", result="won", confidence=0.81234)
        lost = J._row(group="reserve", result="lost", confidence=0.7)
        void = J._row(group="board", result="void")
        self.assertEqual((won["mark"], won["correct"], won["group"], won["on_daily_list"]), ("✓", 1, "Daily List", 1))
        self.assertEqual((lost["mark"], lost["correct"], lost["group"], lost["on_reserve"]), ("✗", 0, "Reserve", 1))
        self.assertEqual((void["mark"], void["correct"], void["quoted_chance"]), ("–", "", ""))
        self.assertEqual((won["confidence"], won["confidence_pct"], won["quoted_chance"]), (0.8123, 81.2, 0.8123))

    def test_a_draw_reading_is_right_but_not_a_top_pick_hit(self):
        r = J._row(group="board", result="won", confidence=0.5, top_pick_correct=0, quoted_chance=0.78)
        self.assertEqual((r["correct"], r["top_pick_correct"], r["quoted_chance"]), (1, 0, 0.78))

    def test_tally_uses_the_quoted_chance_and_leaves_voids_out(self):
        rows = [J._row(group="list", result="won", confidence=0.8),
                J._row(group="list", result="lost", confidence=0.8),
                J._row(group="list", result="won", confidence=0.5, quoted_chance=0.7),
                J._row(group="list", result="void")]
        t = J.tally(rows)
        self.assertEqual((t["picks"], t["won"], t["lost"], t["void"]), (4, 2, 1, 1))
        self.assertAlmostEqual(t["hit_rate"], 0.6667, places=4)
        self.assertAlmostEqual(t["mean_quoted"], 0.7667, places=4)


if __name__ == "__main__":
    unittest.main()
