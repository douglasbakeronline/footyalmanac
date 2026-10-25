"""A club with no prior season stays flagged under Celtic's Law until it has
NO_PRIOR_GAMES games this season (25 Oct 2026, bug 11 of
claude/full-review-2026-10-25.md). Before, one match cleared the flag."""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B


class NoPrior(unittest.TestCase):
    def test_flagged_from_one_game_until_the_bar(self):
        for n in range(1, B.NO_PRIOR_GAMES):
            r = B.no_prior_reason("Wrexham", None, n)
            self.assertIsNotNone(r, n)
            self.assertIn("no prior season", r)
            self.assertIn(f"{n} game", r)
        self.assertIn("1 game this", B.no_prior_reason("Wrexham", None, 1))
        self.assertIn("2 games this", B.no_prior_reason("Wrexham", None, 2))

    def test_clears_at_the_bar(self):
        self.assertIsNone(B.no_prior_reason("Wrexham", None, B.NO_PRIOR_GAMES))
        self.assertIsNone(B.no_prior_reason("Wrexham", None, 30))

    def test_prior_season_or_nothing_played_is_not_this_flag(self):
        self.assertIsNone(B.no_prior_reason("Wrexham", {"P": 46}, 2))
        self.assertIsNone(B.no_prior_reason("Wrexham", None, 0))     # that one is "unrated"
        self.assertIsNone(B.no_prior_reason("Wrexham", None, None))

    def test_list_reason_treats_the_flag_as_celtic(self):
        g = {"p": {"h": 0.9, "d": 0.06, "a": 0.04}, "league": "en.1", "unrated": False,
             "celtic": {"reasons": [B.no_prior_reason("Wrexham", None, 3)], "early": True},
             "home": {"played": 3, "last": None}, "away": {"played": 9, "last": {"P": 38}}}
        self.assertEqual(B.list_reason(g), "celtic")
        g["celtic"] = None
        self.assertEqual(B.list_reason(g), "thin")


if __name__ == "__main__":
    unittest.main()
