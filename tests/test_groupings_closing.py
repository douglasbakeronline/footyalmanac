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


class LockPrice(unittest.TestCase):
    """25 Oct 2026 (review bug 10): the first build after a Card window's lock
    that prices an archived leg records lockPrice once; builds before the lock
    do not, and a leg no post-lock build has priced keeps none."""

    def card(self):
        return {"date": "2026-10-25", "groups": [{"name": "Card 2x", "window": "Daytime", "odds": 2.1, "p": 0.4,
                "lockAt": "2026-10-25T07:00:00Z", "locked": True, "legs": [
                    arch_leg("A", "2026-10-25T15:00:00Z", 1.50), arch_leg("B", "2026-10-25T14:00:00Z", 1.40)]}]}

    def test_recorded_once_from_the_first_post_lock_build(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d):
            json.dump(self.card(), open(os.path.join(d, "2026-10-25.json"), "w"))
            L = [{"event": "A v X", "pick": "A", "odds": 1.45, "best": 1.52, "bestBook": "Bet365"}]
            G.update_closing(L, datetime(2026, 10, 25, 5, 15, tzinfo=timezone.utc), ["2026-10-25"])   # before the lock
            legs = json.load(open(os.path.join(d, "2026-10-25.json")))["groups"][0]["legs"]
            self.assertNotIn("lockPrice", legs[0])
            self.assertEqual(legs[0]["lastOdds"], 1.45)
            G.update_closing(L, datetime(2026, 10, 25, 8, 0, tzinfo=timezone.utc), ["2026-10-25"])    # first after it
            legs = json.load(open(os.path.join(d, "2026-10-25.json")))["groups"][0]["legs"]
            self.assertEqual(legs[0]["lockPrice"], {"odds": 1.45, "best": 1.52, "book": "Bet365", "at": "2026-10-25T08:00:00Z"})
            self.assertNotIn("lockPrice", legs[1])            # B was not priced this build
            L2 = [{"event": "A v X", "pick": "A", "odds": 1.60, "best": 1.65}]
            G.update_closing(L2, datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc), ["2026-10-25"])
            legs = json.load(open(os.path.join(d, "2026-10-25.json")))["groups"][0]["legs"]
            self.assertEqual(legs[0]["lockPrice"]["odds"], 1.45)   # never overwritten
            self.assertEqual(legs[0]["lastOdds"], 1.60)

    def test_a_late_group_is_archived_with_its_price_as_the_lock_price(self):
        g = {"name": "Card 3x", "window": "Evening", "odds": 3.1, "p": 0.3, "locked": True, "late": True,
             "lockAt": "2026-10-25T07:00:00Z", "legs": [dict(arch_leg("A", None, 1.50, 1.55), bestBook="Coral")]}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d):
            G.archive_locked({"date": "2026-10-25", "groups": [g]}, "2026-10-25T14:50:00Z")
            l = json.load(open(os.path.join(d, "2026-10-25.json")))["groups"][0]["legs"][0]
        self.assertEqual(l["lockPrice"], {"odds": 1.50, "best": 1.55, "book": "Coral", "at": "2026-10-25T14:50:00Z"})


class Grade(unittest.TestCase):
    def test_return_at_the_price_at_lock(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
            lp = lambda o: {"odds": o, "best": o, "book": "Bet365", "at": "t"}
            a = {"date": "2026-10-24", "groups": [
                {"name": "Card 2x", "window": "Daytime", "odds": 2.0, "p": 0.4, "locked": True, "legs": [
                    dict(arch_leg("A", None, 1.50), lockPrice=lp(1.40)), dict(arch_leg("B", None, 1.40), lockPrice=lp(1.50))]},
                {"name": "Card 3x", "window": "Daytime", "odds": 3.0, "p": 0.3, "locked": True, "legs": [
                    dict(arch_leg("C", None, 1.50), lockPrice=lp(1.40)), arch_leg("D", None, 2.00)]}]}   # D never priced after the lock
            json.dump(a, open(os.path.join(d, "2026-10-24.json"), "w"))
            with mock.patch.object(G, "results_index", return_value=None), \
                 mock.patch.object(G, "settle", return_value=("won", "1-0")):
                rec = G.grade()
        g1, g2 = rec["days"][0]["groups"]
        self.assertEqual((g1["paid"], g1["paidLock"]), (2.1, 2.1))
        self.assertEqual((g1["legs"][0]["lockOdds"], g1["legs"][0]["lockBook"]), (1.40, "Bet365"))
        self.assertIsNone(g2["paidLock"])
        self.assertEqual((rec["card"]["returnedLock"], rec["card"]["stakedLock"], rec["card"]["staked"]), (2.1, 1, 2))

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
