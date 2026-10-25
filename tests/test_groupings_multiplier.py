"""The Multipliers (groupings.py, 24 Oct 2026; rule 2 the same evening): up to
three groups a day, each three or four picks the bookmakers rate 60%+,
paying 2.8x or more, chosen for the highest combined chance. A leg's chance
is the bookmakers' fair chance; the model is a veto. Standard library only."""
import itertools, math, os, sys, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

AFTER = datetime(2000, 1, 1, tzinfo=timezone.utc)
NAME = G.MULT_KINDS[0][0]


def leg(i, odds, model, sport="football", comp=None, margin=1.05, est=False):
    l = {"event": f"e{i}", "pick": f"p{i}", "sport": sport, "comp": comp or f"c{i}", "odds": odds,
         "p": model, "pModel": model, "when": None, "est": est, "list": False}
    if not est: l["margin"] = margin
    return G.honest(l)


def board(n=12):
    # likely legs, 1.33 to 1.53, fair 62-72%, the model a little below the market
    return [leg(i, round(1.33 + 0.02 * (i % 11), 2), 0.62) for i in range(n)]


class MultLeg(unittest.TestCase):
    def test_likely_leg_passes(self):
        self.assertIsNone(G.mult_fault(leg(0, 1.43, 0.57)))     # Arsenal: market 66%, model 57%

    def test_unlikely_leg_is_out(self):
        # 1.80 with a 5% margin is fair ~53%: not likely enough
        self.assertIn("the bookmakers now give", G.mult_fault(leg(0, 1.80, 0.53)))

    def test_model_well_above_market_is_out(self):
        self.assertIn("above the bookmakers", G.mult_fault(leg(0, 1.45, 0.73)))

    def test_very_short_prices_are_out(self):
        self.assertIn("outside", G.mult_fault(leg(0, 1.05, 0.93)))

    def test_needs_a_price_any_sport(self):
        # 24 Oct 2026 evening: Multipliers across all sports
        self.assertIn("no bookmaker price", G.mult_fault(leg(0, 1.40, 0.66, est=True)))
        for sport in ("rugby", "tennis", "nfl", "nba", "cfb"):
            self.assertIsNone(G.mult_fault(leg(1, 1.40, 0.66, sport=sport)))

    def test_mult_only_legs_never_enter_the_safer_groups(self):
        l = dict(leg(0, 1.20, 0.85, sport="tennis"), multOnly=True)
        G.honest(l)
        self.assertFalse(G.safe_leg(l))
        self.assertFalse(G.wide_leg(l))

    def test_chance_is_the_bookmakers(self):
        l = G.as_mult(leg(0, 1.43, 0.57))
        self.assertEqual((l["p"], l["basis"]), (l["fair"], "bookmakers"))


class BestMult(unittest.TestCase):
    def test_three_or_four_likely_picks_reaching_the_target(self):
        g = G.best_mult(board(), set(), AFTER, NAME)
        lo, hi = G.MULT_RANGE[NAME]
        self.assertIn(len(g["legs"]), (3, 4))
        self.assertTrue(lo <= g["odds"] <= hi)
        self.assertTrue(all(l["fair"] >= G.MULT_FAIR_MIN for l in g["legs"]))
        self.assertAlmostEqual(g["p"], math.prod(l["fair"] for l in g["legs"]), places=3)

    def test_highest_chance_wins(self):
        cands = [G.as_mult(l) for l in board() if G.mult_leg(l)]
        lo, hi = G.MULT_RANGE[NAME]
        best_p = max(math.prod(l["p"] for l in c) for k in G.MULT_LEGS
                     for c in itertools.combinations(cands, k) if G.mult_combo(c, lo, hi))
        self.assertAlmostEqual(G.best_mult(board(), set(), AFTER, NAME)["p"], round(best_p, 4), places=4)

    def test_never_two_picks(self):
        two = [leg(0, 1.75, 0.58, margin=1.0), leg(1, 1.75, 0.58, margin=1.0)]
        self.assertIsNone(G.best_mult(two, set(), AFTER, NAME))


class InTheDay(unittest.TestCase):
    def test_three_groups_no_shared_pick(self):
        gs = [g for g in G.build_day(board(), AFTER) if G.is_mult(g["name"])]
        self.assertEqual(len(gs), G.MULT_PER_DAY)
        self.assertEqual([g["rank"] for g in gs], ["main", "alternative", "third"])
        seen = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(seen), len(set(seen)))

    def test_fewer_when_the_day_is_thin(self):
        gs = [g for g in G.build_day(board(7), AFTER) if G.is_mult(g["name"])]
        self.assertEqual(len(gs), 2)

    def test_kept_on_recheck(self):
        b = board()
        gs = G.build_day(b, AFTER)
        again = G.build_day(b, AFTER, prev=gs, now=AFTER, log=[])
        for g in again:
            if G.is_mult(g["name"]):
                self.assertEqual(g["status"], "holding")

    def test_recheck_drops_a_leg_that_drifts(self):
        b = board()
        g = G.best_mult(b, set(), AFTER, NAME)
        g.update(rank="main", first="x")
        drifted = [dict(l) for l in b]
        for l in drifted:
            if l["event"] == g["legs"][0]["event"]:
                l.update(odds=2.20); G.honest(l)
        ng, why = G.recheck_mult(g, drifted)
        self.assertIsNone(ng)
        self.assertTrue(why)

    def test_old_rule_is_rebuilt(self):
        g = G.best_mult(board(), set(), AFTER, NAME)
        g["rule"] = 1
        ng, why = G.recheck_mult(g, board())
        self.assertIsNone(ng)


class Weekend(unittest.TestCase):
    """25 Oct 2026: the weekend's lessons as rules."""
    def test_sport_off_the_daily_list_is_out(self):
        l = dict(leg(0, 1.40, 0.66, sport="cfb"), listOff=True)
        self.assertIn("off the Daily List", G.mult_fault(l))

    def test_avoid_list_flags_the_model_above_the_market(self):
        oita = dict(leg(0, 1.92, 0.63), event="Oita v Kofu", pick="Oita")   # fair ~0.50
        ok = dict(leg(1, 1.43, 0.62), event="A v B", pick="A")
        unc = dict(leg(2, 1.25, 0.80, sport="cfb"), event="UNC v Syracuse", pick="UNC", listOff=True)
        out = G.avoid_list([oita, ok, unc])
        self.assertEqual([a["pick"] for a in out], ["Oita", "UNC"])
        self.assertEqual(out[0]["kind"], "gap")

    def test_no_forced_groups(self):
        self.assertEqual(G.MIN_GROUPS, 0)


if __name__ == "__main__":
    unittest.main()
