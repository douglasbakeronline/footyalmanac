"""The Multipliers (groupings.py, 24 Oct 2026): the 2-4 legs with the highest
combined chance whose combined price reaches a target return. A leg's chance
is the bookmakers' fair chance; the model is a veto. Standard library only."""
import math, os, sys, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

AFTER = datetime(2000, 1, 1, tzinfo=timezone.utc)


def leg(i, odds, model, sport="football", comp=None, margin=1.05, est=False):
    l = {"event": f"e{i}", "pick": f"p{i}", "sport": sport, "comp": comp or f"c{i}", "odds": odds,
         "p": model, "pModel": model, "when": None, "est": est, "list": False}
    if not est: l["margin"] = margin
    return G.honest(l)


class MultLeg(unittest.TestCase):
    def test_mid_priced_leg_the_market_backs(self):
        # 1.60 with a 5% margin is fair ~0.595: a model at 0.64 is within 5 points
        self.assertIsNone(G.mult_fault(leg(0, 1.60, 0.64)))
        self.assertIsNotNone(G.mult_fault(leg(1, 1.60, 0.66)))

    def test_model_below_market_is_fine(self):
        # Arsenal at 1.44, fair ~0.66, model 0.57: the market is the guide
        self.assertIsNone(G.mult_fault(leg(0, 1.44, 0.57)))

    def test_model_well_above_market_is_out(self):
        # Fiorentino at 1.66 (fair ~0.57), model 0.69: 12 points above
        self.assertIn("above the bookmakers", G.mult_fault(leg(0, 1.66, 0.69)))

    def test_very_short_and_long_prices_are_out(self):
        self.assertIn("outside", G.mult_fault(leg(0, 1.05, 0.93)))
        self.assertIn("outside", G.mult_fault(leg(1, 2.60, 0.38)))

    def test_needs_a_price_and_football(self):
        self.assertIn("no bookmaker price", G.mult_fault(leg(0, 1.50, 0.62, est=True)))
        self.assertIn("not football", G.mult_fault(leg(1, 1.50, 0.62, sport="rugby")))

    def test_chance_is_the_bookmakers(self):
        l = G.as_mult(leg(0, 1.44, 0.57))
        self.assertEqual(l["p"], l["fair"])
        self.assertEqual(l["basis"], "bookmakers")


class BestMult(unittest.TestCase):
    def board(self):
        return [leg(0, 1.44, 0.57), leg(1, 1.36, 0.52), leg(2, 1.60, 0.65), leg(3, 1.67, 0.62),
                leg(4, 1.80, 0.53), leg(5, 1.30, 0.70), leg(6, 1.05, 0.93), leg(7, 1.66, 0.69)]

    def test_reaches_target_and_floor(self):
        g = G.best_mult(self.board(), set(), AFTER, "Multiplier 3x")
        self.assertIsNotNone(g)
        lo, hi = G.MULT_RANGE["Multiplier 3x"]
        self.assertTrue(lo <= g["odds"] <= hi)
        self.assertGreaterEqual(g["p"], G.MIN_CHANCE["Multiplier 3x"])
        self.assertAlmostEqual(g["p"], math.prod(l["fair"] for l in g["legs"]), places=3)
        picks = {l["pick"] for l in g["legs"]}
        self.assertNotIn("p6", picks)      # 1.05: too short to multiply anything
        self.assertNotIn("p7", picks)      # model 12 points above the market

    def test_highest_chance_wins(self):
        # Whatever is chosen, no other valid combination has a higher chance.
        import itertools
        board = [G.as_mult(l) for l in self.board() if G.mult_leg(l)]
        lo, hi = G.MULT_RANGE["Multiplier 3x"]
        best_p = max(math.prod(l["p"] for l in c) for k in G.MULT_LEGS for c in itertools.combinations(board, k)
                     if G.mult_combo(c, lo, hi))
        g = G.best_mult(self.board(), set(), AFTER, "Multiplier 3x")
        self.assertAlmostEqual(g["p"], round(best_p, 4), places=4)

    def test_fewer_longer_legs_beat_more_short_ones(self):
        # Same payout, less margin compounded: two 1.75s beat four ~1.32s.
        two = [leg(0, 1.75, 0.58), leg(1, 1.75, 0.58)]
        four = [leg(i + 2, 1.32, 0.74) for i in range(4)]
        g = G.best_mult(two + four, set(), AFTER, "Multiplier 3x")
        self.assertEqual(len(g["legs"]), 2)

    def test_nothing_when_nothing_reaches(self):
        short = [leg(i, 1.26, 0.78) for i in range(3)]
        self.assertIsNone(G.best_mult(short, set(), AFTER, "Multiplier 5x"))


class InTheDay(unittest.TestCase):
    def test_built_after_the_safe_groups_and_kept_on_recheck(self):
        board = BestMult().board()
        gs = G.build_day(board, AFTER)
        mults = [g for g in gs if G.is_mult(g["name"])]
        self.assertTrue(mults)
        seen = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(seen), len(set(seen)))
        # The same board on the next build: every Multiplier holds.
        again = G.build_day(board, AFTER, prev=gs, now=AFTER, log=[])
        for g in again:
            if G.is_mult(g["name"]):
                self.assertEqual(g["status"], "holding")

    def test_recheck_drops_a_leg_that_drifts_too_far(self):
        board = BestMult().board()
        g = G.best_mult(board, set(), AFTER, "Multiplier 3x")
        g.update(rank="main", first="x")
        drifted = [dict(l) for l in board]
        target = g["legs"][0]["event"]
        for l in drifted:
            if l["event"] == target:
                l.update(odds=2.60); G.honest(l)
        ng, why = G.recheck_mult(g, drifted)
        self.assertIsNone(ng)
        self.assertTrue(why)

    def test_not_counted_toward_min_groups(self):
        # Only Multipliers possible: min_groups cannot be met by them.
        board = BestMult().board()
        gs = G.build_day(board, AFTER, min_groups=3)
        strict_or_wide = [g for g in gs if not G.is_mult(g["name"])]
        self.assertLessEqual(len(strict_or_wide), 3)


if __name__ == "__main__":
    unittest.main()
