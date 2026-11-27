"""27 Nov 2026 (#569): tools/list_card_replay.py, the Daily 2x and the List
card with list and reserve ordered together by confidence, against live."""
import os, sys, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import list_card_replay as R

DAY = "2026-11-17"
AFTER = G.lock_time(DAY, G.CARD_WINDOWS[0][0])


def leg(i, odds, pm, lst=False, res=False, won=True, sport="nba", hour=15):
    return {"event": f"a{i} v b{i}", "pick": f"a{i}", "sport": sport, "odds": odds, "pModel": pm, "est": False,
            "when": f"{DAY}T{hour:02d}:00:00Z", "list": lst, "reserve": res, "won": won, "implied": round(1 / odds, 4)}


class ListCardReplay(unittest.TestCase):
    def test_confidence_puts_a_strong_reserve_pick_first(self):
        L = [leg(1, 1.45, 0.80, lst=True), leg(2, 1.45, 0.78, lst=True), leg(3, 1.45, 0.95, res=True)]
        live = R.build_daily(L, AFTER, "live")[0]; conf = R.build_daily(L, AFTER, "confidence")[0]
        self.assertEqual({l["pick"] for l in live["legs"]}, {"a1", "a2"})
        self.assertEqual({l["pick"] for l in conf["legs"]}, {"a3", "a1"})

    def test_list_card_admits_reserve_only_under_confidence(self):
        L = [leg(1, 1.50, 0.9, res=True), leg(2, 1.50, 0.85, res=True)]
        self.assertEqual(R.build_list(L, AFTER, "live"), [])
        self.assertEqual(len(R.build_list(L, AFTER, "confidence")[0]["legs"]), 2)

    def test_floors_unchanged(self):
        # 1.08 is under the Daily 2x floor, college is out, in either variant
        L = [leg(1, 1.08, 0.99, res=True), leg(2, 1.60, 0.99, res=True, sport="ncaab")]
        for v in R.VARIANTS: self.assertEqual(R.build_daily(L, AFTER, v), [])

    def test_graded_strictly_and_paired(self):
        L = [leg(1, 1.45, 0.80, lst=True), leg(2, 1.45, 0.78, lst=True, won=False), leg(3, 1.45, 0.95, res=True)]
        out = R.run({DAY: L}, "daily")
        self.assertFalse(out["live"][DAY][0]["won"]); self.assertTrue(out["confidence"][DAY][0]["won"])
        p = R.paired(out["live"], out["confidence"])
        self.assertEqual((p["daysDiffer"], p["legsDiffer"]), (1, 2))
        self.assertGreater(p["perDay"], 0)
        self.assertFalse(R.gate([p, p]))   # two legs is far under the 100-leg gate

    def test_ledger_legs_settled_and_priced_only(self):
        rows = [{"key": "k1", "sport": "nba", "pick": "x", "start": f"{DAY}T15:00:00Z", "date": DAY, "conf": 0.8,
                 "reserve": True, "result": "won", "first": {"o": 1.4}, "last": {"o": 1.5}},
                {"key": "k2", "sport": "nba", "pick": "y", "start": f"{DAY}T15:00:00Z", "date": DAY, "conf": 0.8,
                 "result": None, "first": {"o": 1.4}},
                {"key": "k3", "sport": "nba", "pick": "z", "start": f"{DAY}T15:00:00Z", "date": DAY, "conf": 0.8,
                 "result": "lost", "first": None}]
        by = R.ledger_legs(rows)
        self.assertEqual([l["pick"] for l in by[DAY]], ["x"]); self.assertEqual(by[DAY][0]["odds"], 1.4)
        self.assertEqual(R.ledger_legs(rows, closing=True)[DAY][0]["odds"], 1.5)


if __name__ == "__main__":
    unittest.main()
