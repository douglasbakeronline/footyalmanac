"""Every competition's effective season follows today's date
(engine.current_season, 25 Oct 2026, bug 6 of claude/full-review-2026-10-25.md),
so a rollover that nobody edited by hand fails here, not on the board."""
import os, re, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import build as B
import score
import tune


def expected(kind, today):
    if kind == "calendar":
        return str(today.year)
    y = today.year if today.month >= E.SPLIT_ROLL_MONTH else today.year - 1
    return f"{y}-{str(y + 1)[2:]}"


class Derivation(unittest.TestCase):
    def test_split_year_rolls_on_1_july(self):
        self.assertEqual(E.current_season("en.1", date(2026, 6, 30)), "2025-26")
        self.assertEqual(E.current_season("en.1", date(2026, 7, 1)), "2026-27")
        self.assertEqual(E.current_season("en.1", date(2027, 1, 15)), "2026-27")

    def test_calendar_year_rolls_on_1_january(self):
        for code in ("us.1", "br.1", "nor.1", "jp.1", "kr.1"):
            self.assertEqual(E.season_kind(code), "calendar", code)
            if E.LEAGUES[code].get("seasonSource") == "api":
                # current/af-seasons.json (bot-written) pins this league to the
                # API's current season; derivation is not what decides it.
                continue
            self.assertEqual(E.current_season(code, date(2026, 12, 31)), "2026", code)
            self.assertEqual(E.current_season(code, date(2027, 1, 1)), "2027", code)

    def test_prev_follows(self):
        self.assertEqual(E.prev_seasons("en.1", date(2027, 1, 15)), ["2025-26", "2024-25"])
        self.assertEqual(E.prev_seasons("us.1", date(2027, 1, 1)), ["2026", "2025"])

    def test_overrides_are_honoured(self):
        code = "zz.test"
        E.LEAGUES[code] = {"season": "2024-25", "seasonFixed": True}
        try:
            self.assertEqual(E.current_season(code, date(2026, 10, 25)), "2024-25")
            E.LEAGUES[code] = {"season": "2025", "seasonSource": "api"}
            self.assertEqual(E.current_season(code, date(2026, 10, 25)), "2025")
            E.LEAGUES[code] = {"season": "2024-25"}
            self.assertEqual(E.current_season(code, date(2026, 10, 25)), "2026-27")
            E.LEAGUES[code] = {"calendar": True}
            self.assertEqual(E.current_season(code, date(2026, 10, 25)), "2026")
        finally:
            del E.LEAGUES[code]

    def test_roll_changes_only_stale_entries(self):
        E.LEAGUES["zz.roll"] = {"season": "2024-25", "prev": ["2023-24", "2022-23"]}
        try:
            changed = E.roll_seasons(date(2026, 10, 25))
            self.assertEqual(changed.get("zz.roll"), ("2024-25", "2026-27"))
            self.assertEqual(E.LEAGUES["zz.roll"]["prev"], ["2025-26", "2024-25"])
            self.assertEqual(E.roll_seasons(date(2026, 10, 25)), {})
        finally:
            del E.LEAGUES["zz.roll"]


class Today(unittest.TestCase):
    """For today, every competition's effective season contains the current
    year (calendar) or the split-year pair. Fails CI the day a rollover is
    missed anywhere a season string is consumed."""

    def test_every_competition(self):
        today = date.today()
        split, cal = expected("split", today), expected("calendar", today)
        for code, m in E.LEAGUES.items():
            if m.get("cup") or m.get("international") or m.get("ratingsOnly"):
                continue
            s = m.get("season") or B.SEASON
            if m.get("seasonSource") == "api" or m.get("seasonFixed") or m.get("u21"):
                # the API's own answer, or a deliberate pin: must still be a season string
                self.assertRegex(s, r"^\d{4}(-\d{2})?$", code)
                continue
            self.assertEqual(s, cal if E.season_kind(code) == "calendar" else split, code)
            self.assertEqual(E.current_season(code, today), s, code)

    def test_build_globals(self):
        today = date.today()
        if not os.environ.get("ALMANAC_SEASON"):
            self.assertEqual(B.SEASON, expected("split", today))
            self.assertEqual(B.PREV, E.season_prev(B.SEASON))

    def test_cups_and_internationals_take_the_global_season(self):
        # The build plans a cup or an international on SEASON (no season of
        # its own), so the global string is what has to be right.
        self.assertRegex(B.SEASON, r"^\d{4}-\d{2}$")
        self.assertIn(str(date.today().year)[2:] if date.today().month < 7 else str(date.today().year),
                      B.SEASON)

    def test_score_and_tune_defaults_follow(self):
        # score.load_results and tune.splits used a literal "2026-27".
        src = open(score.__file__).read() + open(tune.__file__).read()
        self.assertNotIn('"2026-27"', src)
        self.assertEqual(tune.splits("en.1")["check"][0], E.current_season("en.1"))


if __name__ == "__main__":
    unittest.main()
