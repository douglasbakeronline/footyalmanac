"""The free price sources (11 Nov 2026): Betfair Exchange (delayed key),
Matchbook and SportsGameOdds, each on a reply shaped like its API's, with no
network. Each fills only unpriced legs, labels its source, and is silent
without its keys."""
import json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timezone
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import free_prices as FP
import groupings as G

NOW = datetime(2026, 11, 11, 9, tzinfo=timezone.utc)


def tennis(a="Alice Tubello", b="Tatjana Maria", pick="Tatjana Maria", **kw):
    l = {"sport": "tennis", "players": [a, b], "pick": pick, "event": f"{a} v {b}",
         "when": "2026-11-11T15:00:00Z", "date": "2026-11-11", "pModel": 0.63}
    l.update(kw); return l


def nba(home="Boston Celtics", away="Brooklyn Nets", pick="Boston Celtics", **kw):
    l = {"sport": "nba", "home": home, "away": away, "pick": pick, "event": f"{home} v {away}",
         "when": "2026-11-12T00:30:00Z", "date": "2026-11-11", "pModel": 0.8}
    l.update(kw); return l


class Base(unittest.TestCase):
    def setUp(self): self.dir = tempfile.mkdtemp()
    def tearDown(self): shutil.rmtree(self.dir)


class Betfair(Base):
    ENV = {"BETFAIR_APP_KEY": "k", "BETFAIR_USERNAME": "u", "BETFAIR_PASSWORD": "p"}

    def post(self, url, data, headers):
        self.calls.append(url)
        if "identitysso" in url: return {"status": "SUCCESS", "token": "T"}
        method = data[0]["method"]
        if method.endswith("listMarketCatalogue"):
            return [{"result": [{"marketId": "1.1", "marketStartTime": "2026-11-11T15:00:00.000Z",
                                 "runners": [{"selectionId": 11, "runnerName": "Alice Tubello"},
                                             {"selectionId": 12, "runnerName": "Tatjana Maria"}]},
                                {"marketId": "1.2", "marketStartTime": "2026-11-11T18:00:00.000Z",
                                 "runners": [{"selectionId": 21, "runnerName": "Someone Else"},
                                             {"selectionId": 22, "runnerName": "Another"}]}]}]
        return [{"result": [{"marketId": "1.1", "runners": [
            {"selectionId": 11, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 2.9}]}},
            {"selectionId": 12, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 1.52}]}}]}]}]

    def test_fills_an_unpriced_match_from_the_back_price(self):
        self.calls = []
        a, b = tennis(), tennis("X Y", "Z W", pick="X Y", odds=1.4)
        r = {}
        with mock.patch.dict(os.environ, self.ENV):
            FP.price_betfair([a, b], {"2026-11-11"}, r, cache_dir=self.dir, post=self.post)
        self.assertEqual((a["odds"], a["opp"], a["exchange"], a["bestBook"]), (1.52, 2.9, "betfair", "Betfair Exchange"))
        self.assertEqual(b["odds"], 1.4)                                    # a priced leg is left alone
        self.assertEqual(r["betfair"]["matched"], 1)
        # prices asked only for the market a wanted leg could match
        self.assertEqual(len(self.calls), 3)

    def test_silent_without_keys(self):
        r = {}
        with mock.patch.dict(os.environ, {}, clear=True):
            FP.price_betfair([tennis()], {"2026-11-11"}, r, cache_dir=self.dir, post=lambda *a: 1 / 0)
        self.assertEqual(r["betfair"], "no key")

    def test_a_failed_login_is_reported_not_raised(self):
        r = {}
        with mock.patch.dict(os.environ, self.ENV):
            FP.price_betfair([tennis()], {"2026-11-11"}, r, cache_dir=self.dir,
                             post=lambda u, d, h: {"status": "FAIL", "error": "INVALID_USERNAME_OR_PASSWORD"})
        self.assertIn("INVALID_USERNAME_OR_PASSWORD", r["betfair"]["error"])


class Matchbook(Base):
    def http(self, url, data=None, headers=None, method=None):
        if "security/session" in url: return {"session-token": "S"}
        if "lookups/sports" in url: return {"sports": [{"id": 9, "name": "Tennis"}]}
        return {"events": [{"start": "2026-11-11T15:00:00.000Z", "markets": [{"market-type": "money_line", "runners": [
            {"name": "Alice Tubello", "prices": [{"side": "back", "odds": 2.84}, {"side": "lay", "odds": 2.96}]},
            {"name": "Tatjana Maria", "prices": [{"side": "back", "odds": 1.53}]}]}]}]}

    def test_fills_from_the_back_side(self):
        a, r = tennis(), {}
        with mock.patch.dict(os.environ, {"MATCHBOOK_USERNAME": "u", "MATCHBOOK_PASSWORD": "p"}):
            FP.price_matchbook([a], {"2026-11-11"}, r, cache_dir=self.dir, http=self.http)
        self.assertEqual((a["odds"], a["opp"], a["exchange"]), (1.53, 2.84, "matchbook"))


class SportsGameOdds(Base):
    def reply(self, url):
        self.urls.append(url)
        return {"success": True, "data": [{
            "status": {"startsAt": "2026-11-12T00:30:00Z"},
            "teams": {"home": {"names": {"long": "Boston Celtics"}}, "away": {"names": {"long": "Brooklyn Nets"}}},
            "odds": {"points-home-game-ml-home": {"byBookmaker": {"draftkings": {"odds": "-400", "available": True},
                                                                   "williamhill": {"odds": "-380", "available": True}}},
                     "points-away-game-ml-away": {"byBookmaker": {"draftkings": {"odds": "+310"}}}}}]}

    def test_average_of_its_books_and_hill_kept_apart(self):
        self.urls = []
        a, r = nba(), {}
        with mock.patch.dict(os.environ, {"SGO_API_KEY": "k"}):
            FP.price_sgo([a], {"2026-11-11"}, r, cache_dir=self.dir, fetch=self.reply, now=NOW)
        self.assertAlmostEqual(a["odds"], round((1.25 + 1 + 100 / 380) / 2, 2))
        self.assertEqual(a["sgoBooks"], {"draftkings": 1.25, "williamhill": 1.26})
        self.assertNotIn("bookOdds", a)                 # not the UK Hill until shown to be
        self.assertEqual(a["opp"], 4.1)
        self.assertIn("leagueID=NBA", self.urls[0])
        self.assertEqual(r["sgo"]["monthObjects"], 1)

    def test_stops_at_the_monthly_allowance(self):
        with open(os.path.join(self.dir, "sgo-ledger.json"), "w") as f:
            json.dump({"month": "2026-11", "objects": FP.SGO_MONTH}, f)
        self.urls, r = [], {}
        with mock.patch.dict(os.environ, {"SGO_API_KEY": "k"}):
            FP.price_sgo([nba()], {"2026-11-11"}, r, cache_dir=self.dir, fetch=self.reply, now=NOW)
        self.assertEqual(self.urls, []); self.assertEqual(r["sgoSkipped"], ["NBA"])


class SgoConsensus(Base):
    def test_consensus_when_no_book_is_listed(self):
        r = {}
        reply = lambda u: {"data": [{"status": {"startsAt": "2026-11-12T00:30:00Z"},
            "teams": {"home": {"names": {"long": "Boston Celtics"}}, "away": {"names": {"long": "Brooklyn Nets"}}},
            "odds": {"points-home-game-ml-home": {"bookOdds": "-400", "bookOddsAvailable": True},
                     "points-away-game-ml-away": {"bookOdds": "+310", "bookOddsAvailable": True}}}]}
        a = nba()
        with mock.patch.dict(os.environ, {"SGO_API_KEY": "k"}):
            FP.price_sgo([a], {"2026-11-11"}, r, cache_dir=self.dir, fetch=reply, now=NOW)
        self.assertEqual((a["odds"], a["opp"], a["bestBook"]), (1.25, 4.1, "SportsGameOdds consensus"))
        self.assertEqual(r["sgo"]["matched"], 1)


class SgoDiagnostics(Base):
    def test_a_miss_leaves_a_sample_in_the_report(self):
        r = {}
        reply = lambda u: {"data": [{"teams": {"home": {"names": {"long": "Other Team"}}, "away": {"names": {"long": "Someone"}}},
                                      "status": {"startsAt": "2026-11-12T00:30:00Z"}, "odds": {}}]}
        with mock.patch.dict(os.environ, {"SGO_API_KEY": "k"}):
            FP.price_sgo([nba()], {"2026-11-11"}, r, cache_dir=self.dir, fetch=reply, now=NOW)
        self.assertEqual(r["sgo"]["matched"], 0)
        s = r["sgo"]["sample"]["NBA"]
        self.assertEqual(s["events"], 1); self.assertIn("Other Team", s["teams"]); self.assertEqual(s["leg"][0], ["Boston Celtics", "Brooklyn Nets"])


class BoardPrice(unittest.TestCase):
    def test_exchange_marked_on_the_board(self):
        P = G.board_prices([dict(tennis(), odds=1.52, exchange="betfair", bestBook="Betfair Exchange")])
        self.assertEqual(P["tennis|alice tubello|tatjana maria"]["x"], "betfair")


if __name__ == "__main__":
    unittest.main()
