"""5-point bands, per-day lines and the model card for the Analysis page (6 Oct 2026)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score as SC

def row(conf, pick, actual, score=(1, 0), d="2026-10-01", lst=False):
    p = {"h": (conf, 0.2, 0.8 - conf), "a": (0.8 - conf, 0.2, conf)}[pick]
    return {"confidence": conf, "pick": pick, "actual": actual, "score": score, "p": p, "date": d, "list": lst}

class Bands5(unittest.TestCase):
    def test_edges_and_counts(self):
        rows = [row(0.52, "h", "h"), row(0.55, "h", "a"), row(0.99, "h", "h", lst=True), row(1.0, "h", "h"),
                row(0.62, "h", "d", score=(1, 1))]
        b = SC.bands5(rows)
        self.assertEqual([x["from"] for x in b], [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])
        self.assertEqual((b[0]["n"], b[0]["won"]), (1, 1))
        self.assertEqual((b[1]["n"], b[1]["won"]), (1, 0))
        self.assertEqual((b[-1]["n"], b[-1]["won"], b[-1]["listN"], b[-1]["listWon"]), (2, 2, 1, 1))
        # a drawn game with a predicted draw scoreline: not won, but read right
        self.assertEqual((b[2]["won"], b[2]["read"], b[2]["draws"]), (0, 1, 1))
        self.assertAlmostEqual(b[2]["quotedRead"], 0.82)

    def test_empty_band(self):
        b = SC.bands5([row(0.52, "h", "h")])
        self.assertEqual(b[5]["n"], 0)
        self.assertIsNone(b[5]["quoted"])

    def test_by_day(self):
        d = SC.by_day([row(0.7, "h", "h", d="2026-10-02"), row(0.5, "h", "a", d="2026-10-01")])
        self.assertEqual([x["date"] for x in d], ["2026-10-01", "2026-10-02"])
        self.assertEqual((d[1]["n60"], d[1]["won60"]), (1, 1))
        self.assertEqual(len(d[1]["b5"]), 20)
        self.assertEqual(d[1]["b5"][14][:3], [1, 1, 1])      # 0.70 sits in 70-75%
        self.assertEqual(d[0]["b5"][10][:2], [1, 0])         # 0.50 sits in 50-55%

    def test_day_bands_top(self):
        self.assertEqual(SC.day_bands([row(1.0, "h", "h")])[19][0], 1)

    def test_model_card(self):
        c = SC.model_card()
        self.assertEqual(c["rho"], SC.E.RHO)
        self.assertIn("calibration", c)

if __name__ == "__main__":
    unittest.main()
