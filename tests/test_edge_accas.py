"""Edge-flag legs as accumulators (10 Nov 2026): card_legs_history.edge_legs
keeps the flag's conditions, edge_accas takes the k most likely flagged legs
of each day, and build.edge_tested hands the result to the Bets tab."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_legs_history as H
import build as B


def leg(date, fair, won, opp=11.0, model=None, price=None):
    price = price or round(1 / fair / 1.05, 2)
    return {"date": date, "fair": fair, "model": fair if model is None else model, "opp": opp, "won": won,
            "price": price, "best": price + 0.03}


class EdgeAccas(unittest.TestCase):
    def test_edge_legs_keep_the_flags_conditions(self):
        L = [leg("2025-10-04", 0.8, True), leg("2025-10-04", 0.8, True, opp=7.0), leg("2025-10-04", 0.8, True, model=0.9)]
        self.assertEqual(len(H.edge_legs(L)), 1)

    def test_k_most_likely_per_day(self):
        L = [leg("2025-10-04", 0.85, True), leg("2025-10-04", 0.80, True), leg("2025-10-04", 0.70, False),
             leg("2025-10-05", 0.75, True)]
        a = H.edge_accas(L, sizes=(1, 2, 3))
        self.assertEqual(a["1"]["n"], 2)                      # one single a day, the most likely
        self.assertEqual((a["2"]["n"], a["2"]["won"]), (1, 1))    # 0.85 and 0.80 both won
        self.assertEqual((a["3"]["n"], a["3"]["won"]), (1, 0))    # the 0.70 lost
        self.assertEqual(a["all"]["n"], 1)                    # a one-leg day is no accumulator
        self.assertAlmostEqual(a["2"]["expected"], round(0.85 * 0.80, 3))

    def test_edge_tested_reads_the_history_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"seasons": {"fit": {"season": "2025-26", "edgeAccas": {"2": {"n": 56, "won": 38, "landed": 0.679, "expected": 0.596,
                                                                                  "avgOdds": 1.47, "roi": -0.0069, "roiBest": 0.0384, "months": 10}}},
                                   "check": {"season": "2026-27"}}}, f)
        try:
            out = B.edge_tested(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(list(out), ["2025-26"])
        self.assertEqual(out["2025-26"]["2"]["won"], 38)
        self.assertNotIn("months", out["2025-26"]["2"])
        self.assertEqual(B.edge_tested("/nonexistent.json"), {})


if __name__ == "__main__":
    unittest.main()
