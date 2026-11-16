"""College basketball's early-season K (16 Nov 2026, claude/ncaab-early-k-2026-11-16.md):
a team's first EARLY_K["earlyN"] games after a summer break move its rating
EARLY_K["earlyK"] times as far; the count resets at the next break. Params
without the keys behave exactly as before."""
import unittest

import sports


def game(when, h, a, hs, as_):
    return {"pool": "p", "h": h, "a": a, "when": when, "hs": hs, "as": as_, "neutral": False}


BASE = {"k": 32, "hfa": 100, "regress": 0.25, "mov": 0}


class EarlyK(unittest.TestCase):
    def deltas(self, p, games):
        elo = sports.Elo(p)
        out = []
        for g in games:
            before = elo.get("p", g["h"], g["when"])[0]
            elo.update(g)
            out.append(round(elo.r[("p", g["h"])][0] - before, 6))
        return out

    def test_no_keys_is_unchanged(self):
        gs = [game("2025-11-0%d" % i, "A", "B%d" % i, 70, 60) for i in range(1, 4)]
        self.assertEqual(self.deltas(BASE, gs), self.deltas({**BASE, "earlyK": 1.0, "earlyN": 6}, gs))

    def test_first_games_move_further(self):
        gs = [game("2025-11-0%d" % i, "A", "B%d" % i, 70, 60) for i in range(1, 4)]
        plain = self.deltas(BASE, gs)
        early = self.deltas({**BASE, "earlyK": 1.5, "earlyN": 2}, gs)
        self.assertAlmostEqual(early[0], plain[0] * 1.5, places=4)
        self.assertGreater(early[1], plain[1])
        # third game: both teams past (A) or new (B3)... A is past 2, B3 is new: still early
        self.assertGreater(early[2], 0)

    def test_count_resets_after_break(self):
        p = {**BASE, "earlyK": 2.0, "earlyN": 1}
        elo = sports.Elo(p)
        elo.update(game("2025-03-01", "A", "B", 70, 60))
        elo.update(game("2025-03-02", "A", "C", 70, 60))
        self.assertEqual(elo.season[("p", "A")], 2)
        elo.get("p", "A", "2025-11-05")   # a summer away
        self.assertEqual(elo.season[("p", "A")], 0)

    def test_ncaab_registered(self):
        self.assertEqual(sports.EARLY_K["ncaab"], {"earlyK": 1.5, "earlyN": 6})


if __name__ == "__main__":
    unittest.main()
