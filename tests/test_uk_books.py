"""Every UK bookmaker's price on every card leg (9 Nov 2026, Douglas: "make
sure all odds are being displayed across all cards"). A leg priced from one
non-UK source (ESPN's DraftKings line, Pinnacle) takes `bookOdds` from a UK
source; the price the Card rule reads stays exactly as it was. No network."""
import os, sys, tempfile, unittest
from datetime import datetime, timezone
from unittest import mock
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tests"))
import groupings as G
from test_groupings_sources import as_fetch, leg, NOW
from test_groupings import OddsApiTest


def priced(l, odds=1.40, src="ESPN, DraftKings moneyline"):
    return dict(l, odds=odds, margin=1.04, src=src, pModel=0.72, opp=3.0)


class ApiSportsBooks(unittest.TestCase):

    def fetch(self, url):
        r = as_fetch(url)
        if "/odds?game=77" in url:
            r["response"][0]["bookmakers"].append(
                {"name": "William Hill", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.36"}, {"value": "Away", "odd": "3.10"}]}]})
            r["response"][0]["bookmakers"].append(
                {"name": "1xBet", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.50"}]}]})   # not UK: left out
        return r

    def test_books_added_price_untouched(self):
        l = priced(leg()); before = {k: l[k] for k in ("odds", "margin", "src", "opp")}
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            rep = {}; G.price_api_sports([l], {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=self.fetch, books_only=True)
        self.assertEqual(l["bookOdds"], {"Bet365": 1.4, "Unibet": 1.44, "William Hill": 1.36})
        self.assertEqual({k: l[k] for k in before}, before)
        self.assertEqual(rep["apiSportsBooks"]["matched"], 1)

    def test_only_card_range_legs_spend_calls(self):
        calls = []
        def f(u): calls.append(u); return self.fetch(u)
        out_of_range = priced(leg(), odds=3.50)           # longer than any card takes
        low_model = dict(priced(leg()), pModel=0.50)
        off_card = priced(leg(sport="nfl"))                # NFL is off the Card
        est = dict(priced(leg()), est=True)
        have = dict(priced(leg()), bookOdds={"Bet365": 1.4})
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            rep = {}; G.price_api_sports([out_of_range, low_model, off_card, est, have], {"2026-10-26"}, rep,
                                         cache_dir=d, now=NOW, fetch=f, books_only=True)
        self.assertEqual(rep["apiSportsBooks"], "no legs"); self.assertEqual(calls, [])

    def test_primary_pricing_now_carries_uk_books(self):
        l = leg()
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            G.price_api_sports([l], {"2026-10-26"}, {}, cache_dir=d, now=NOW, fetch=self.fetch)
        self.assertEqual(l["bookOdds"]["William Hill"], 1.36)
        self.assertNotIn("1xBet", l["bookOdds"])


class OddsApiBooks(OddsApiTest):
    """Inherits the Odds API fixture; the parent's own tests run here too."""

    def test_pinnacle_tennis_leg_takes_uk_books_only(self):
        l = dict(self.tleg(), odds=1.62, best=1.62, bestBook="Pinnacle", books=1, margin=1.02, src="Pinnacle (PinnWire)")
        r = {}
        G.price_odds_api([l], {"2026-10-19"}, r, cache_dir=self.dir, fetch=self.fetch,
                         now=datetime(2026, 10, 19, 9, tzinfo=timezone.utc), books_only=True)
        self.assertEqual(l["bookOdds"], {"Bet365": 1.6, "William Hill": 1.7})
        self.assertEqual((l["odds"], l["best"], l["bestBook"], l["src"]), (1.62, 1.62, "Pinnacle", "Pinnacle (PinnWire)"))
        self.assertEqual(r["oddsApiBooks"]["matched"], 1)

    def test_tennis_under_the_card_bar_is_not_looked_up(self):
        l = dict(self.tleg(pModel=0.70), odds=1.62, margin=1.02, src="Pinnacle (PinnWire)")
        r = {}
        G.price_odds_api([l], {"2026-10-19"}, r, cache_dir=self.dir, fetch=self.fetch, books_only=True)
        self.assertEqual(r["oddsApiBooks"], "no legs"); self.assertNotIn("bookOdds", l)


class ModelCardBook(unittest.TestCase):

    def test_at_book_on_model_groups(self):
        g = {"legs": [{"bookOdds": {"William Hill": 1.5}}, {"bookOdds": {"William Hill": 1.2, "Bet365": 1.25}}]}
        self.assertEqual(G.at_book(g), 1.8)
        self.assertIsNone(G.at_book({"legs": [{"bookOdds": {"William Hill": 1.5}}, {"bookOdds": {}}]}))


if __name__ == "__main__":
    unittest.main()
