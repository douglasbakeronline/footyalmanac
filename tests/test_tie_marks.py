"""build.tie_marks: the legs of two-legged ties and play-off series (27 Nov 2026)."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))

import build  # noqa: E402


def game(d, h, a, pick="h", lg="mx.1"):
    return {"league": lg, "date": d, "home": {"name": h}, "away": {"name": a}, "pick": pick}


class TieMarksTest(unittest.TestCase):
    def test_same_window_as_card_ties(self):
        import card_ties
        self.assertEqual(build.TIE_DAYS, card_ties.TIE_DAYS)

    def test_second_leg_carries_first_leg_score_and_lead(self):
        # Cruz Azul won 4-0 at León on 27 Nov; the return is on 30 Nov
        rows = {"mx.1": [{"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": 0, "ag": 4},
                         {"date": "2026-11-30", "home": "Cruz Azul", "away": "León", "hg": None, "ag": None}]}
        g = game("2026-11-30", "Cruz Azul", "León", pick="h")
        self.assertEqual(build.tie_marks([g], rows), 1)
        self.assertEqual(g["tie"], {"leg": 2, "other": "2026-11-27", "first": "León 0-4 Cruz Azul", "lead": [4, 0]})

    def test_lead_read_from_the_away_pick(self):
        rows = {"mx.1": [{"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": 0, "ag": 4}]}
        g = game("2026-11-30", "Cruz Azul", "León", pick="a")
        build.tie_marks([g], rows)
        self.assertEqual(g["tie"]["lead"], [0, 4])

    def test_first_leg_marked_with_the_return_date(self):
        rows = {"mx.1": [{"date": "2026-11-29", "home": "Atlas", "away": "Toluca", "hg": None, "ag": None}]}
        g = game("2026-11-26", "Toluca", "Atlas")
        build.tie_marks([g], rows)
        self.assertEqual(g["tie"], {"leg": 1, "other": "2026-11-29"})

    def test_unplayed_second_leg_has_no_score(self):
        rows = {"mx.1": [{"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": None, "ag": None}]}
        g = game("2026-11-30", "Cruz Azul", "León")
        build.tie_marks([g], rows)
        self.assertEqual(g["tie"], {"leg": 2, "other": "2026-11-27"})

    def test_a_played_copy_wins_over_an_unplayed_one(self):
        rows = {"mx.1": [{"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": None, "ag": None},
                         {"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": 1, "ag": 1}]}
        g = game("2026-11-30", "Cruz Azul", "León")
        build.tie_marks([g], rows)
        self.assertEqual(g["tie"]["first"], "León 1-1 Cruz Azul")

    def test_regular_season_reverse_months_apart_is_not_a_tie(self):
        rows = {"mx.1": [{"date": "2026-08-10", "home": "León", "away": "Cruz Azul", "hg": 2, "ag": 1}]}
        g = game("2026-11-30", "Cruz Azul", "León")
        self.assertEqual(build.tie_marks([g], rows), 0)
        self.assertNotIn("tie", g)

    def test_another_league_does_not_count(self):
        rows = {"mx.2": [{"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": 0, "ag": 4}]}
        g = game("2026-11-30", "Cruz Azul", "León")
        self.assertEqual(build.tie_marks([g], rows), 0)

    def test_nearest_reverse_decides(self):
        rows = {"us.1": [{"date": "2026-11-22", "home": "B", "away": "A", "hg": 2, "ag": 0},
                         {"date": "2026-11-29", "home": "B", "away": "A", "hg": None, "ag": None}]}
        g = game("2026-11-27", "A", "B", lg="us.1")
        build.tie_marks([g], rows)
        self.assertEqual(g["tie"]["leg"], 1)
        self.assertEqual(g["tie"]["other"], "2026-11-29")

    def test_draw_pick_has_no_lead(self):
        rows = {"mx.1": [{"date": "2026-11-27", "home": "León", "away": "Cruz Azul", "hg": 0, "ag": 4}]}
        g = game("2026-11-30", "Cruz Azul", "León", pick="d")
        build.tie_marks([g], rows)
        self.assertNotIn("lead", g["tie"])


if __name__ == "__main__":
    unittest.main()
