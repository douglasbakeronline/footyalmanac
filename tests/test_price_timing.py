"""tools/price_timing.py (9 Nov 2026, issue #156): the first price is the
row's own or its `priced` block, legs outside the Card rule are left out,
and timing and books are reported for each sport apart."""
import gzip, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import price_timing as PT

DAY = "2026-11-21"


def fb(i, odds, last, est=False, priced=None, books=None, opp=10.0):
    fair = round(1 / odds / 1.04, 4)
    l = {"sport": "football", "event": f"H{i} v A{i}", "pick": f"H{i}", "home": f"H{i}", "away": f"A{i}", "side": "h", "comp": "Premier League",
         "code": "en.1", "when": f"{DAY}T15:00:00Z", "date": DAY, "odds": odds, "est": est, "pModel": round(fair - 0.07, 4), "p": round(fair - 0.07, 4),
         "pTested": 0.8, "hit": 0.8, "n": 100, "firstAt": f"{DAY[:8]}18T09:00:00Z", "lastOdds": last, "lastBest": last}
    if not est: l.update(margin=1.04, fair=fair, opp=opp, bookOdds=books or {"William Hill": odds + 0.05, "Bet365": odds - 0.02})
    if priced: l["priced"] = priced
    return l


def tennis(i, odds, last, model=0.76):   # 75%+ on model and tested rate, no more than 5 points above the bookmakers
    return {"sport": "tennis", "event": f"P{i} v Q{i}", "pick": f"Q{i}", "comp": "Open", "when": f"{DAY}T12:00:00Z", "date": DAY, "odds": odds, "est": False,
            "margin": 1.05, "fair": round(1 / odds / 1.05, 4), "pModel": model, "p": model, "pTested": model, "hit": 0.8, "n": 100,
            "firstAt": f"{DAY[:8]}20T22:00:00Z", "lastOdds": last, "lastBest": last, "bookOdds": {"Bet365": odds + 0.03}}


class PriceTiming(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        legs = [fb(1, 1.30, 1.35), fb(2, 1.40, 1.36),
                fb(3, 1.25, 1.30, est=True, priced={"odds": 1.28, "best": 1.30, "bookOdds": {"William Hill": 1.30}, "margin": 1.04,
                                                     "fair": round(1 / 1.28 / 1.04, 4), "opp": 11.0, "at": f"{DAY[:8]}19T14:00:00Z"}),
                fb(4, 1.30, 1.40, est=True),                        # never priced: out
                fb(5, 2.50, 2.60),                                  # outside the Card's price band and the wide band: out
                tennis(6, 1.25, 1.23), tennis(7, 1.28, 1.32)]
        with gzip.open(os.path.join(self.dir, f"pool-{DAY}.json.gz"), "wt") as f: json.dump({"date": DAY, "legs": legs}, f)

    def test_legs_and_report(self):
        L = PT.legs(self.dir)
        self.assertEqual(sorted(l["pick"] for l in L), ["H1", "H2", "H3", "Q6", "Q7"])
        h3 = next(l for l in L if l["pick"] == "H3")
        self.assertEqual(h3["odds"], 1.28); self.assertFalse(h3["est"]); self.assertEqual(h3["firstPriceAt"], f"{DAY[:8]}19T14:00:00Z")
        rep = PT.report(L)
        self.assertEqual(rep["legs"], 5)
        self.assertEqual(rep["timing"]["drifted"], 3); self.assertEqual(rep["timing"]["shortened"], 2)
        self.assertEqual(set(rep["bySport"]), {"football", "tennis"})
        self.assertEqual(rep["bySport"]["football"]["timing"]["n"], 3); self.assertEqual(rep["bySport"]["tennis"]["timing"]["n"], 2)
        self.assertEqual(rep["bySport"]["tennis"]["timing"]["read"], "take the price late")
        self.assertEqual(rep["bySport"]["football"]["books"], {})          # under MIN_BOOK legs a book is not ranked
        self.assertEqual(set(PT.book_table(L, min_n=1)), {"William Hill", "Bet365"})
        self.assertIn("14", rep["hours"]); self.assertIn("09", rep["hours"]); self.assertIn("22", rep["hours"])

    def test_empty(self):
        self.assertEqual(PT.report([]), {"legs": 0})


if __name__ == "__main__":
    unittest.main()
