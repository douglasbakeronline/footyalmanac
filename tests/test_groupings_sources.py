"""API-Sports (other sports) and PinnWire price sources (groupings.py,
25 Oct 2026). No network: fetch is stubbed. Standard library only."""
import os, sys, tempfile, unittest
from datetime import datetime, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)


def leg(sport="nba", home="Los Angeles Lakers", away="Sacramento Kings", pick=None, when="2026-10-26T02:30:00Z"):
    return {"sport": sport, "home": home, "away": away, "pick": pick or home, "event": f"{home} v {away}",
            "date": "2026-10-26", "when": when, "pModel": 0.7, "p": 0.7}


def as_fetch(url):
    if "/games?" in url:
        return {"response": [{"id": 77, "date": "2026-10-26T02:30:00+00:00",
                              "teams": {"home": {"name": "Los Angeles Lakers"}, "away": {"name": "Sacramento Kings"}}}]}
    if "/odds?game=77" in url:
        return {"response": [{"game": {"id": 77}, "bookmakers": [
            {"name": "Bet365", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.40"}, {"value": "Away", "odd": "3.00"}]}]},
            {"name": "Unibet", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.44"}, {"value": "Away", "odd": "2.85"}]}]}]}]}
    return {"response": []}


class ApiSports(unittest.TestCase):
    def test_prices_a_leg_with_average_best_and_book(self):
        L = [leg()]
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            rep = {}; G.price_api_sports(L, {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=as_fetch)
        l = L[0]
        self.assertEqual((l["odds"], l["best"], l["bestBook"], l["books"]), (1.42, 1.44, "Unibet", 2))
        self.assertEqual(rep["apiSports"]["matched"], 1)

    def test_away_pick_and_daily_cap(self):
        L = [leg(pick="Sacramento Kings")]
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}), \
             mock.patch.object(G, "AS_DAY", 1):
            rep = {}; G.price_api_sports(L, {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=as_fetch)
        self.assertNotIn("odds", L[0])                       # the cap stopped the odds call
        self.assertEqual(rep["apiSports"]["skipped"], 1)

    def test_no_key_no_calls(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            rep = {}; G.price_api_sports([leg()], set(), rep, fetch=lambda u: 1 / 0)
        self.assertEqual(rep["apiSports"], "no key")


class PinnWire(unittest.TestCase):
    def test_prices_tennis_from_pinnacle(self):
        t = {"sport": "tennis", "pick": "Jannik Sinner", "players": ["Jannik Sinner", "Casper Ruud"],
             "event": "Sinner v Ruud", "date": "2026-10-26", "when": "2026-10-26T13:00:00Z"}
        ev = {"events": [{"home": "Sinner, Jannik", "away": "Ruud, Casper", "starts": "2026-10-26T13:00:00Z",
                          "periods": {"num_0": {"money_line": {"home": 1.25, "away": 4.20}}}}]}
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"PINNWIRE_KEY": "k"}):
            rep = {}; G.price_pinnwire([t], set(), rep, cache_dir=d, fetch=lambda u: ev)
        self.assertEqual((t.get("odds"), t.get("bestBook")), (1.25, "Pinnacle"))

    def test_no_key_does_nothing(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            rep = {}; G.price_pinnwire([leg()], set(), rep)
        self.assertEqual(rep["pinnwire"], "no key")


if __name__ == "__main__":
    unittest.main()
