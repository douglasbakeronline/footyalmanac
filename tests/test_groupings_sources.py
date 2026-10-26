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


class UkBestPrice(unittest.TestCase):
    """25 Oct 2026 (review bug 2): the best price and its bookmaker come from
    UK-licensed books only; a better price elsewhere does not count."""

    def test_api_sports_best_is_uk_only(self):
        item = {"bookmakers": [
            {"name": "1xBet", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.60"}, {"value": "Away", "odd": "2.50"}]}]},
            {"name": "Bet365", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.40"}, {"value": "Away", "odd": "3.00"}]}]},
            {"name": "Unibet", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.44"}, {"value": "Away", "odd": "2.85"}]}]}]}
        avg, best, book, n, _ = G._as_side(item, True)
        self.assertEqual((avg, best, book, n), (1.48, 1.44, "Unibet", 3))

    def test_api_sports_no_uk_book_means_no_best_book(self):
        item = {"bookmakers": [
            {"name": "1xBet", "bets": [{"name": "Home/Away", "values": [{"value": "Home", "odd": "1.60"}, {"value": "Away", "odd": "2.50"}]}]}]}
        avg, best, book, n, _ = G._as_side(item, True)
        self.assertEqual((avg, best, book), (1.60, 1.60, None))

    def test_football_single_fixture_fallback_is_uk_only(self):
        import sources as S
        l = {"sport": "football", "event": "Alpha v Beta", "home": "Alpha", "away": "Beta", "side": "h", "pick": "Alpha",
             "date": "2026-10-26", "when": "2026-10-26T15:00:00Z", "pModel": 0.7, "p": 0.7}
        fx = [{"fixture": {"id": 5, "date": "2026-10-26T15:00:00+00:00"}, "teams": {"home": {"name": "Alpha"}, "away": {"name": "Beta"}}}]
        items = [{"fixture": {"id": 5}, "bookmakers": [
            {"name": "Betano", "bets": [{"id": 1, "values": [{"value": "Home", "odd": "1.80"}, {"value": "Draw", "odd": "4.0"}, {"value": "Away", "odd": "5.0"}]}]},
            {"name": "Bet365", "bets": [{"id": 1, "values": [{"value": "Home", "odd": "1.50"}, {"value": "Draw", "odd": "4.0"}, {"value": "Away", "odd": "6.0"}]}]},
            {"name": "Coral", "bets": [{"id": 1, "values": [{"value": "Home", "odd": "1.55"}, {"value": "Draw", "odd": "3.9"}, {"value": "Away", "odd": "5.5"}]}]}]}]
        import odds as O
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}), \
             mock.patch.object(S, "AF_CACHE_DIR", d), mock.patch.object(S, "_af_day", lambda day: fx), \
             mock.patch.object(O, "af_prices", lambda dates: {}), \
             mock.patch.object(G, "_odds_for", lambda fid, key, cd: (items, 1)):
            rep = {}; G.price_football([l], {"2026-10-26"}, rep)
        self.assertEqual((l["best"], l["bestBook"], l["books"]), (1.55, "Coral", 3))
        self.assertAlmostEqual(l["odds"], 1.62, places=2)


class FixtureOddsCache(unittest.TestCase):
    """25 Oct 2026 (review bug 8): one fixture's prices go through
    sources._af_get, and an empty quota answer is never cached as "no prices"."""

    def setUp(self):
        import sources as S
        self.S = S
        S._AF_CACHE.clear(); S._AF_SPENT[0] = False

    def tearDown(self):
        self.S._AF_CACHE.clear(); self.S._AF_SPENT[0] = False

    def test_a_real_answer_is_cached_and_served(self):
        S = self.S
        items = [{"fixture": {"id": 9}, "bookmakers": []}]
        def fake(path):
            S._AF_CACHE[path] = items; S.AF_USAGE["calls"] += 1; return items
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "_af_get", fake):
            self.assertEqual(G._odds_for(9, "k", d), (items, 1))
            self.assertTrue(os.path.exists(os.path.join(d, "odds-9.json")))
            S._AF_CACHE.clear()
            self.assertEqual(G._odds_for(9, "k", d), (items, 0))      # from disk, no call

    def test_a_quota_refusal_is_not_cached(self):
        S = self.S
        def spent(path):
            S._AF_SPENT[0] = True; return []      # what _af_get does on the daily-limit error
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "_af_get", spent):
            self.assertEqual(G._odds_for(9, "k", d), ([], 0))
            self.assertFalse(os.path.exists(os.path.join(d, "odds-9.json")))

    def test_once_spent_no_more_calls(self):
        S = self.S
        S._AF_SPENT[0] = True
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}), \
             mock.patch.object(S.urllib.request, "urlopen", side_effect=AssertionError("must not call")):
            self.assertEqual(G._odds_for(9, "k", d), ([], 0))


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


class ApiSportsErrors(unittest.TestCase):
    def test_an_error_reply_is_not_cached(self):
        calls = []
        def f(url):
            calls.append(url)
            if len(calls) == 1: return {"errors": {"rateLimit": "Too many requests"}, "response": []}
            return as_fetch(url)
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            rep = {}; G.price_api_sports([leg()], {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=f)
            L = [leg()]
            rep2 = {}; G.price_api_sports(L, {"2026-10-26"}, rep2, cache_dir=d, now=NOW, fetch=f)
        self.assertIn("errors", rep["apiSports"])
        self.assertEqual(L[0].get("odds"), 1.42)     # the second build asked again and priced it


class PricedAt(unittest.TestCase):
    """26 Oct 2026: every leg says when its price was read (pricedAt), the
    cache file's time when the price came off disk, so a punter can see how
    old the number is and the page can mark a stale read."""

    def test_fresh_fetch_is_stamped_now(self):
        L = [leg()]
        before = G.iso(datetime.now(timezone.utc))
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            rep = {}; G.price_api_sports(L, {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=as_fetch)
        self.assertGreaterEqual(L[0]["pricedAt"], before)
        self.assertRegex(L[0]["pricedAt"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_cached_price_keeps_the_cache_time(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"}):
            L = [leg()]
            rep = {}; G.price_api_sports(L, {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=as_fetch)
            old = int(datetime.now(timezone.utc).timestamp()) - 30 * 60   # inside AS_ODDS_TTL: served from disk
            for f in os.listdir(d):
                if f.startswith("apisports2-"): os.utime(os.path.join(d, f), (old, old))
            L2 = [leg()]
            rep = {}; G.price_api_sports(L2, {"2026-10-26"}, rep, cache_dir=d, now=NOW, fetch=lambda u: 1 / 0)
        self.assertEqual(L2[0]["odds"], 1.42)
        self.assertEqual(L2[0]["pricedAt"], G.iso(datetime.fromtimestamp(old, timezone.utc)))

    def test_estimate_and_stale_price(self):
        l = {"sport": "rugby", "home": "A", "away": "B", "pick": "A", "event": "A v B", "date": "2026-10-26",
             "when": "2026-10-26T15:00:00Z", "pModel": 0.7, "p": 0.7}
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(G, "price_espn", lambda L, d, r: None), mock.patch.object(G, "price_espn_soccer", lambda L, d, r: None):
            G.price([l], {"2026-10-26"})
        self.assertTrue(l["est"]); self.assertIn("pricedAt", l)
        old = {"odds": 1.5, "best": 1.55, "bestBook": "Coral", "books": 3, "margin": 1.05, "src": "x", "pricedAt": "2026-10-26T05:00:00Z"}
        cur = G.stale_price(dict(l), old)
        self.assertEqual((cur["odds"], cur["pricedAt"], cur["stale"]), (1.5, "2026-10-26T05:00:00Z", True))


if __name__ == "__main__":
    unittest.main()
