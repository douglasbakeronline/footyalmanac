"""Closing prices, best-price returns and the closing-line tally
(groupings.py, 25 Oct 2026). Standard library only."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)


def arch_leg(pick, when, odds, best=None):
    return {"pick": pick, "event": f"{pick} v X", "sport": "football", "home": pick, "away": "X", "side": "h",
            "date": "2026-10-25", "when": when, "odds": odds, "best": best or odds, "p": 0.65}


class Closing(unittest.TestCase):
    def test_unstarted_legs_take_this_builds_price_started_ones_do_not(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d):
            a = {"date": "2026-10-25", "groups": [{"name": "Multiplier", "odds": 3.0, "p": 0.3, "legs": [
                arch_leg("A", "2026-10-25T15:00:00Z", 1.50), arch_leg("B", "2026-10-25T11:00:00Z", 1.40)]}]}
            json.dump(a, open(os.path.join(d, "2026-10-25.json"), "w"))
            L = [{"event": "A v X", "pick": "A", "odds": 1.40, "best": 1.44}, {"event": "B v X", "pick": "B", "odds": 1.30}]
            G.update_closing(L, NOW, ["2026-10-25"])
            legs = json.load(open(os.path.join(d, "2026-10-25.json")))["groups"][0]["legs"]
        self.assertEqual((legs[0]["lastOdds"], legs[0]["lastBest"]), (1.40, 1.44))
        self.assertEqual(legs[0]["odds"], 1.50)            # what was published never changes
        self.assertNotIn("lastOdds", legs[1])               # B had kicked off


class Grade(unittest.TestCase):
    def test_best_price_return_and_closing_line(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
            a = {"date": "2026-10-24", "groups": [{"name": "Multiplier", "odds": 3.0, "p": 0.3, "legs": [
                dict(arch_leg("A", None, 1.50, 1.60), lastOdds=1.40), dict(arch_leg("B", None, 2.00, 2.10), lastOdds=2.20)]}]}
            json.dump(a, open(os.path.join(d, "2026-10-24.json"), "w"))
            with mock.patch.object(G, "results_index", return_value=None), \
                 mock.patch.object(G, "settle", return_value=("won", "1-0")):
                rec = G.grade()
        g = rec["days"][0]["groups"][0]
        self.assertEqual((g["paid"], g["paidBest"]), (3.0, 3.36))
        c = rec["overall"]["clv"]
        self.assertEqual((c["n"], c["shortened"], c["drifted"]), (2, 1, 1))
        self.assertEqual(rec["overall"]["returnedBest"], 3.36)


if __name__ == "__main__":
    unittest.main()
