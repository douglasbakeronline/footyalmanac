"""25 Nov 2026: a football leg was settled from any earlier meeting of the
same ordered pair when its own date had no result (the dateless key in
groupings.results_index). The pool replay settled five unplayed MLS and Liga
MX play-off games (26 to 28 Nov) from regular-season results two months old,
and two archived groups took the result of a postponed game played weeks
later. Now only a result within SETTLE_NEAR_DAYS of the leg's date counts,
the nearest first (claude/settle-rematch-2026-11-25.md)."""
import json, os, sys, tempfile, unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G


def leg(date, home="Toluca", away="Atlas", side="h"):
    return {"sport": "football", "date": date, "home": home, "away": away, "side": side,
            "pick": home if side == "h" else away}


class SettleRematch(unittest.TestCase):
    def index(self, graded):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "HERE", d):
            for name, doc in (("record-graded.json", {"graded": graded}), ("tennis-record.json", {"graded": []}),
                              ("record.json", {"days": []})):
                with open(os.path.join(d, name), "w") as f:
                    json.dump(doc, f)
            with mock.patch("sports.graded_games", return_value=([], [])):
                return G.results_index()

    def test_an_old_meeting_never_settles_a_later_fixture(self):
        idx = self.index([{"date": "2026-09-12", "home": "Toluca", "away": "Atlas", "result": [5, 2]}])
        self.assertEqual(G.settle(leg("2026-11-26"), idx), ("pending", None))

    def test_a_result_weeks_later_is_not_this_fixture(self):
        idx = self.index([{"date": "2026-10-20", "home": "Toluca", "away": "Atlas", "result": [0, 0]}])
        self.assertEqual(G.settle(leg("2026-10-04"), idx), ("pending", None))

    def test_a_result_a_day_or_a_round_date_away_still_settles(self):
        idx = self.index([{"date": "2026-11-25", "home": "Toluca", "away": "Atlas", "result": [2, 0]}])
        self.assertEqual(G.settle(leg("2026-11-26"), idx), ("won", "2-0"))
        self.assertEqual(G.settle(leg("2026-11-22"), idx), ("won", "2-0"))      # 3 days: a round's nominal date
        self.assertEqual(G.settle(leg("2026-11-21"), idx), ("pending", None))   # 4 days: another fixture

    def test_the_nearest_result_wins(self):
        idx = self.index([{"date": "2026-11-20", "home": "Toluca", "away": "Atlas", "result": [0, 1]},
                          {"date": "2026-11-23", "home": "Toluca", "away": "Atlas", "result": [3, 1]}])
        self.assertEqual(G.settle(leg("2026-11-22"), idx), ("won", "3-1"))
        self.assertEqual(G.settle(leg("2026-11-20"), idx), ("lost", "0-1"))

    def test_the_reversed_pair_is_another_fixture(self):
        idx = self.index([{"date": "2026-11-26", "home": "Atlas", "away": "Toluca", "result": [1, 0]}])
        self.assertEqual(G.settle(leg("2026-11-26"), idx), ("pending", None))

    def test_a_leg_with_no_date_stays_pending(self):
        idx = self.index([{"date": "2026-11-26", "home": "Toluca", "away": "Atlas", "result": [1, 0]}])
        self.assertEqual(G.settle(dict(leg("2026-11-26"), date=None), idx), ("pending", None))


if __name__ == "__main__":
    unittest.main()
