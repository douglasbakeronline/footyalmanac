"""19 Nov 2026 (Douglas: a game played in the early hours loses its price chip
by the afternoon; "keep the odds there as we last knew them"): a started game
keeps its last pre-start price on the board from the pool archive
(groupings.past_prices), marked `past`; this build's own prices win."""
import gzip, json, os, sys, tempfile, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

NOW = datetime(2026, 11, 19, 15, 0, tzinfo=timezone.utc)


def write_pool(d, day, legs):
    with gzip.open(os.path.join(d, f"pool-{day}.json.gz"), "wt", encoding="utf-8") as f:
        json.dump({"date": day, "legs": legs}, f)


class PastPrices(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        write_pool(self.d, "2026-11-19", [
            {"sport": "nba", "event": "Celtics v Knicks", "home": "Celtics", "away": "Knicks", "pick": "Celtics",
             "odds": 1.40, "lastOdds": 1.36, "lastBest": 1.40, "lastAt": "2026-11-19T00:30:00Z", "opp": 3.1, "lastOpp": 3.3,
             "lastBooks": {"William Hill": 1.36, "Bet365": 1.40}, "pricedAt": "2026-11-18T10:00:00Z"},
            {"sport": "football", "event": "A v B", "home": "A", "away": "B", "pick": "A", "odds": 1.50, "est": True},
            {"sport": "tennis", "event": "X v Y", "home": "X", "away": "Y", "pick": "X", "odds": 1.80, "est": True,
             "priced": {"odds": 1.75, "bookOdds": {"Betfair": 1.75}}},
        ])
        write_pool(self.d, "2026-11-18", [
            {"sport": "nba", "event": "Lakers v Suns", "home": "Lakers", "away": "Suns", "pick": "Lakers", "odds": 1.25,
             "bookOdds": {"William Hill": 1.25}, "pricedAt": "2026-11-18T09:00:00Z"},
        ])

    def test_started_game_keeps_its_last_price(self):
        out = G.past_prices(set(), NOW, pool_dir=self.d)
        q = out[G._lb_key("nba", "Celtics", "Knicks")]
        self.assertEqual((q["o"], q["h"], q["b"], q["bb"], q["t"], q["past"]), (1.36, 1.36, 1.40, "Bet365", "2026-11-19T00:30:00Z", True))
        self.assertEqual((q["opp"], q["draw"], q["pk"]), (3.3, None, "Celtics"))   # the other side's last price, for the Bookies line

    def test_yesterday_and_priced_block_count_estimates_do_not(self):
        out = G.past_prices(set(), NOW, pool_dir=self.d)
        self.assertEqual(out[G._lb_key("nba", "Lakers", "Suns")]["h"], 1.25)
        self.assertEqual(out[G._lb_key("tennis", "X", "Y")]["o"], 1.75)
        self.assertNotIn(G._lb_key("football", "A", "B"), out)   # an estimate is not a price

    def test_this_builds_price_wins(self):
        k = G._lb_key("nba", "Celtics", "Knicks")
        self.assertNotIn(k, G.past_prices({k}, NOW, pool_dir=self.d))
        merged = {**G.past_prices(set(), NOW, pool_dir=self.d), k: {"o": 1.30}}
        self.assertEqual(merged[k], {"o": 1.30})


if __name__ == "__main__":
    unittest.main()
