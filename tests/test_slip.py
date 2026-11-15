"""slip.py: band rates, the leg rule, the slip search, grading, the gate. Standard library only."""
import os, sys, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import slip as S

NOW = datetime(2026, 11, 15, 9, 0, tzinfo=timezone.utc)


def row(key, sport, price, conf, result=None, start="2026-11-15T15:00:00Z", side="h", comp="X", hill=False):
    last = {"o": price, "src": "pool"}
    if hill: last["h"] = price
    return {"key": key, "sport": sport, "comp": comp, "home": f"H{key}", "away": f"A{key}", "pick": f"H{key}" if side == "h" else f"A{key}",
            "side": side, "conf": conf, "start": start, "result": result, "last": last, "list": False, "reserve": True}


def graded(sport, price, n, won, conf=0.8):
    return [row(f"{sport}{price}{i}", sport, price, conf, "won" if i < won else "lost", start="2026-11-01T15:00:00Z") for i in range(n)]


class Bands(unittest.TestCase):
    def test_band_of(self):
        self.assertEqual(S.band_of(1.10), "1.00-1.15")
        self.assertEqual(S.band_of(1.15), "1.15-1.30")
        self.assertEqual(S.band_of(3.0), "2.50+")

    def test_rates_and_fallback(self):
        rows = graded("football", 1.40, 60, 45) + graded("nba", 1.40, 10, 9)
        rates = S.band_rates(rows)
        f = rates["football"]["1.30-1.50"]
        self.assertEqual((f["n"], f["landed"]), (60, 45))
        self.assertAlmostEqual(f["ret"], 45 * 1.40 / 60 - 1, places=4)
        ch, ret, basis = S.leg_chance("football", "1.30-1.50", rates)
        self.assertAlmostEqual(ch, 0.75)
        ch, ret, basis = S.leg_chance("nba", "1.30-1.50", rates)       # 10 picks: falls back to the pool
        self.assertTrue(basis.startswith("all sports"))
        self.assertIsNone(S.leg_chance("tennis", "2.50+", rates)[0])


class LegRule(unittest.TestCase):
    def setUp(self):
        self.rates = S.band_rates(graded("football", 1.40, 100, 75) + graded("football", 1.60, 100, 50))

    def test_refusals(self):
        rows = [row("ok", "football", 1.40, 0.70),
                row("above", "football", 1.40, 0.80),               # model 80% v implied 71%: refused
                row("loses", "football", 1.60, 0.62),               # band at 1.60 returns -20%
                row("away", "cfb", 1.40, 0.70, side="a"),           # away college pick
                row("started", "football", 1.40, 0.70, start="2026-11-15T08:00:00Z"),
                row("weak", "football", 1.40, 0.60)]                # under CONF_MIN
        legs, off = S.candidates("2026-11-15", rows, self.rates, NOW)
        self.assertEqual([l["key"] for l in legs], ["ok"])
        self.assertEqual(off, {"model above the price": 1, "band loses": 1, "away college pick": 1})


class Search(unittest.TestCase):
    def legs(self, prices, comps=None, chance=0.75):
        comps = comps or ["c%d" % i for i in range(len(prices))]
        return [{"key": str(i), "price": p, "chance": chance, "comp": comps[i], "fixture": f"f{i}", "start": "2026-11-15T15:00:00Z"}
                for i, p in enumerate(prices)]

    def test_picks_the_band_and_the_best_return(self):
        best, why = S.best_slip(self.legs([1.5, 1.5, 1.5, 1.5, 1.5], chance=0.8))
        self.assertIsNone(why)
        self.assertEqual(len(best["legs"]), 4)                       # 3 legs 3.375 and 4 legs 5.06 both in band; each leg adds 1.2x
        self.assertGreaterEqual(best["price"], 3.0); self.assertLessEqual(best["price"], 6.0)
        self.assertAlmostEqual(best["ev"], (0.8 * 1.5) ** len(best["legs"]), places=3)

    def test_prefers_higher_expected_return(self):
        legs = self.legs([1.5, 1.5, 1.5, 1.5], chance=0.8)
        best, _ = S.best_slip(legs)
        self.assertEqual(len(best["legs"]), 4)                        # each leg adds 1.2x expected return

    def test_reasons(self):
        self.assertEqual(S.best_slip(self.legs([1.5, 1.5]))[1], "few")
        self.assertEqual(S.best_slip(self.legs([1.1, 1.1, 1.1]))[1], "short")
        self.assertEqual(S.best_slip(self.legs([2.0, 2.0, 2.0]))[1], "long")
        self.assertEqual(S.best_slip(self.legs([1.5, 1.5, 1.5], chance=0.6))[1], "value")   # 0.9^3 under the stake

    def test_competition_cap(self):
        legs = self.legs([1.5, 1.5, 1.5, 1.5], comps=["a", "a", "a", "b"], chance=0.8)
        best, _ = S.best_slip(legs)
        self.assertLessEqual(sum(l["comp"] == "a" for l in best["legs"]), S.COMP_MAX)


class Grading(unittest.TestCase):
    def test_states(self):
        slip = {"legs": [{"key": "a", "price": 1.5}, {"key": "b", "price": 2.0}]}
        self.assertEqual(S.grade(slip, {"a": "won", "b": "won"}), {"state": "won", "ret": 3.0})
        self.assertEqual(S.grade(slip, {"a": "won", "b": "void"}), {"state": "won", "ret": 1.5})
        self.assertEqual(S.grade(slip, {"a": "lost"})["state"], "lost")
        self.assertEqual(S.grade(slip, {"a": "won"})["state"], "pending")
        self.assertEqual(S.grade(slip, {"a": "void", "b": "void"}), {"state": "void", "ret": 1.0})

    def test_gate(self):
        settled = [{"date": f"2026-11-{d:02d}", "ret": 3.0 if d % 2 else 0.0, "state": "won" if d % 2 else "lost"} for d in range(1, 29)] * 4
        g = S.gate(settled)
        self.assertEqual(g["n"], 112); self.assertGreater(g["ret"], 0); self.assertTrue(g["pass"])
        self.assertFalse(S.gate(settled[:20])["pass"])


class Archive(unittest.TestCase):
    def test_slip_frozen_after_first_start(self):
        old = {"date": "2026-11-15", "slip": {"legs": [{"key": "x", "price": 1.5}], "first": "2026-11-15T08:00:00Z", "price": 1.5}}
        new = {"legs": [{"key": "y", "price": 1.6, "fixture": "f", "start": "2026-11-15T20:00:00Z"}], "price": 1.6, "chance": 0.8, "ev": 1.1}
        m = S.merge_day(old, new, None, 3, {}, NOW, "stamp", "2026-11-15")
        self.assertEqual(m["slip"]["legs"][0]["key"], "x")             # started: kept
        old["slip"]["first"] = "2026-11-15T20:00:00Z"
        m = S.merge_day(old, new, None, 3, {}, NOW, "stamp", "2026-11-15")
        self.assertEqual(m["slip"]["legs"][0]["key"], "y")             # open: replaced
        self.assertNotIn("fixture", m["slip"]["legs"][0])


if __name__ == "__main__":
    unittest.main()
