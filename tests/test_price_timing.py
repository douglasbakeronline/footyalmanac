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
    # these fixtures are 76% tennis legs, written under the 75% floor; the
    # floor is 85% from 11 Nov 2026 (CARD_RULE 10), which is not what is tested
    def tearDown(self): self._floor.stop()
    def setUp(self):
        from unittest import mock
        self._floor = mock.patch.object(G, "CARD_SPORT_MIN", {"tennis": 0.75}); self._floor.start()
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
        self.assertEqual(rep["bySport"]["tennis"]["timing"]["read"], "too few legs to read")   # 10 Nov 2026: no read under MIN_READ legs
        self.assertEqual(rep["bySport"]["football"]["books"], {})          # under MIN_BOOK legs a book is not ranked
        self.assertEqual(set(PT.book_table(L, min_n=1)), {"William Hill", "Bet365"})
        self.assertIn("14", rep["hours"]); self.assertIn("09", rep["hours"]); self.assertIn("22", rep["hours"])

    def test_leads_and_last_after_start(self):
        # 9 Nov 2026 (#156): first-price lead buckets; a last price after the start on file is left out
        L = PT.legs(self.dir)
        rep = PT.report(L)
        # football firstAt 18th 09:00, start 21st 15:00 = 78h; H3 priced 19th 14:00 = 49h; tennis 20th 22:00 to 21st 12:00 = 14h
        self.assertEqual(rep["leads"]["72h+"]["n"], 2); self.assertEqual(rep["leads"]["48-72h"]["n"], 1); self.assertEqual(rep["leads"]["6-24h"]["n"], 2)
        self.assertEqual(rep["bySport"]["tennis"]["leads"], {"6-24h": {"n": 2, "meanMovePct": 0.76, "drifted": 1, "shortened": 1}})
        self.assertEqual(rep["lastLead"], {"n": 0}); self.assertEqual(rep["lastAfterStart"], 0)
        late = dict(fb(8, 1.30, 1.20), lastAt=f"{DAY}T15:30:00Z")          # after its 15:00 start: out
        moved = dict(fb(9, 1.30, 1.32), lastAt=f"{DAY}T15:30:00Z", whenLast=f"{DAY}T17:30:00Z")   # start moved: in
        with gzip.open(os.path.join(self.dir, "pool-2026-11-22.json.gz"), "wt") as f: json.dump({"date": "2026-11-22", "legs": [late, moved]}, f)
        dropped = []
        L = PT.legs(self.dir, dropped=dropped)
        self.assertEqual([l["pick"] for l in dropped], ["H8"]); self.assertIn("H9", [l["pick"] for l in L])
        rep = PT.report(L, dropped)
        self.assertEqual(rep["lastAfterStart"], 1); self.assertEqual(rep["lastAfterStartBySport"], {"football": 1})
        self.assertEqual(rep["lastLead"], {"n": 1, "medianH": 2.0, "within3h": 1})
        self.assertEqual(PT.lead_bucket(5.9), "<6h"); self.assertEqual(PT.lead_bucket(72), "72h+")

    def test_read_needs_evidence(self):
        # 10 Nov 2026 (#156): a side is read only on MIN_READ+ values beyond noise
        self.assertEqual(PT.read_of([0.02] * 10)[0], "too few legs to read")
        self.assertEqual(PT.read_of([0.02] * 60)[0], "take the price late")
        self.assertEqual(PT.read_of([-0.02] * 60)[0], "take the price when published")
        self.assertEqual(PT.read_of([0.05, -0.05] * 30 + [0.001])[0], "no clear read")
        # resampled by day: one big day cannot carry the read on its own
        xs = [0.30] * 30 + [-0.01] * 30; days = ["d1"] * 30 + [f"e{i}" for i in range(30)]
        self.assertEqual(PT.read_of(xs)[0], "take the price late")
        self.assertGreater(PT.p_not_positive(xs, days), PT.p_not_positive(xs))

    def test_settled_first_v_last(self):
        S = [dict(fb(1, 1.30, 1.40), won=True), dict(fb(2, 1.50, 1.40), won=True), dict(fb(3, 1.30, 2.00), won=False)]
        r = PT.settled(S)
        self.assertEqual((r["n"], r["won"]), (3, 2))
        self.assertAlmostEqual(r["returnFirstPct"], (2.80 / 3 - 1) * 100, places=2)
        self.assertAlmostEqual(r["returnLastPct"], (2.80 / 3 - 1) * 100, places=2)   # a loser's drift pays nothing
        self.assertEqual(r["lateGainPct"], 0.0); self.assertEqual(r["read"], "too few legs to read")
        self.assertEqual(PT.settled([]), {"n": 0})

    def test_unstarted_legs_wait(self):
        from datetime import datetime, timezone
        pending = []
        L = PT.legs(self.dir, now=datetime(2026, 11, 21, 13, 0, tzinfo=timezone.utc), pending=pending)
        self.assertEqual(sorted(l["pick"] for l in L), ["Q6", "Q7"])          # tennis 12:00 started, football 15:00 not
        self.assertEqual(len(pending), 3)
        self.assertEqual(PT.report(L, pending=pending)["notStarted"], 3)

    def test_empty(self):
        self.assertEqual(PT.report([]), {"legs": 0, "lastAfterStart": 0})


if __name__ == "__main__":
    unittest.main()
