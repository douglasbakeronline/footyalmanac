"""tools/list_accas.py (10 Nov 2026): Daily List picks combined into
accumulators. The top N of a day by confidence, days with fewer picks left
out, the whole day only with two or more, expected the product of the
quoted chances."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "tools"))
import list_accas as A


class Accas(unittest.TestCase):
    def test_top_n_by_confidence(self):
        days = {"2026-11-01": [("d", 0.9, True, "f"), ("d", 0.8, False, "f"), ("d", 0.95, True, "f")],
                "2026-11-02": [("d", 0.85, True, "f")]}
        r = A.accas(days, lambda x: x[1], lambda x: x[2], sizes=(1, 2, 3))
        self.assertEqual(r["1"]["n"], 2); self.assertEqual(r["1"]["won"], 2)
        self.assertEqual(r["2"]["n"], 1); self.assertEqual(r["2"]["won"], 1)          # 0.95 and 0.9 both won
        self.assertAlmostEqual(r["2"]["expected"], round(0.95 * 0.9, 2))
        self.assertEqual(r["3"]["won"], 0)                                            # the 0.8 lost
        self.assertEqual(r["all"]["n"], 1)                                            # a one-pick day is no acca

    def test_uk_day(self):
        self.assertEqual(A.uk_day("2026-11-10T00:30Z"), "2026-11-10")
        self.assertEqual(A.uk_day("2026-07-10T23:30Z"), "2026-07-11")                 # BST
        self.assertIsNone(A.uk_day("not a time"))


if __name__ == "__main__":
    unittest.main()
