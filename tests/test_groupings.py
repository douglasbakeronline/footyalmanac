"""The Odds tab's group rules (groupings.py). Standard library only."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

# 22 Oct 2026: these tests check grouping mechanics on short-priced boards;
# the 2.00 minimum return (groupings.MIN_RETURN) is tested on its own in
# tests/test_groupings_return.py.
_MIN_RETURN = None
def setUpModule():
    global _MIN_RETURN
    _MIN_RETURN, G.MIN_RETURN = G.MIN_RETURN, 1.0
def tearDownModule():
    G.MIN_RETURN = _MIN_RETURN


def leg(i, odds, p=0.8, sport="football", comp=None, est=False):
    l = {"event": f"e{i}", "pick": f"p{i}", "sport": sport, "comp": comp or f"c{i}", "odds": odds, "p": p,
         "pModel": p, "when": None, "est": est, "implied": 1 / odds, "edge": p * odds - 1}
    return l

class LegProbability(unittest.TestCase):
    def test_needs_a_tested_sample(self):
        self.assertIsNone(G.leg_p(0.9, {"hit": 0.9, "n": 10}))
        self.assertIsNone(G.leg_p(0.9, None))
    def test_needs_a_tested_rate_of_75(self):
        self.assertIsNone(G.leg_p(0.8, {"hit": 0.7, "n": 500}))
    def test_tested_rate_capped_at_the_model(self):
        # 19 Oct 2026: min(tested rate, model), no longer pulled toward the model
        self.assertAlmostEqual(G.leg_p(0.78, {"hit": 0.90, "n": 30}), 0.78, places=6)
        self.assertAlmostEqual(G.leg_p(0.95, {"hit": 0.90, "n": 3000}), 0.90, places=6)

class GroupRules(unittest.TestCase):
    def test_odds_range_and_estimates(self):
        two = [leg(0, 1.12), leg(1, 1.15)]
        o = G.ok_combo(two, 1.1, 2.0, "Double")
        self.assertIsNotNone(o); self.assertTrue(1.1 <= o <= 2.0)
        self.assertIsNone(G.ok_combo(two, 1.5, 2.0, "Double"))
        self.assertIsNone(G.ok_combo([leg(0, 1.12, est=True), leg(1, 1.15)], 1.1, 2.0, "Double"))
        self.assertIsNotNone(G.ok_combo([leg(0, 1.12, est=True), leg(1, 1.15)], 1.1, 2.0, "Double", max_est=2))

    def test_honest_chance_is_the_lower(self):
        l = G.honest({"p": 0.85, "odds": 1.25, "margin": 1.06})      # fair 0.8 / 1.06 = 0.7547
        self.assertEqual((l["pTested"], l["fair"], l["p"]), (0.85, 0.7547, 0.7547))
        l = G.honest({"p": 0.70, "odds": 1.25})                      # tested lower: kept; default margin
        self.assertEqual((l["p"], l["fair"]), (0.70, 0.7619))
        l = G.honest({"p": 0.85, "odds": 1.18, "est": True})         # estimate: no fair, never grouped
        self.assertNotIn("fair", l)
        self.assertEqual(G.margin_of([1.6, 2.3]), round(1 / 1.6 + 1 / 2.3, 4))
        self.assertIsNone(G.margin_of([1.6]))

    def test_estimates_never_grouped(self):
        from datetime import datetime, timezone
        L = [leg(i, o, est=True) for i, o in enumerate([1.2, 1.35, 1.65, 1.25, 1.4, 1.1, 1.5, 1.8])]
        self.assertEqual(G.build_day(L, datetime(2000, 1, 1, tzinfo=timezone.utc)), [])
    def test_one_competition_at_most_twice(self):
        same = [leg(i, o, comp="X") for i, o in enumerate([1.1, 1.12, 1.15])]
        self.assertIsNone(G.ok_combo(same, 1.2, 2.6, "Treble"))
    def test_groups_never_share_a_leg(self):
        import random
        random.seed(3)
        L = []
        for i in range(60):
            p = random.uniform(0.70, 0.93)
            L.append(G.honest(dict(leg(i, round(1 / (p * 1.04), 2), p=p, sport=random.choice(["football", "rugby"])), list=False)))
        from datetime import datetime, timezone
        gs = G.build_day(L, datetime(2000, 1, 1, tzinfo=timezone.utc))
        self.assertTrue(gs)
        seen = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(seen), len(set(seen)))
        for g in gs:
            self.assertEqual(len(g["legs"]), G.LEGS_IN[g["name"]])
            self.assertTrue(g["band"][0] <= g["odds"] <= g["band"][1])
            self.assertGreaterEqual(g["p"], G.MIN_CHANCE[g["name"]])

class EspnSoccerPrices(unittest.TestCase):
    def board(self, home, away, date="2026-10-10T11:30Z", ml=None):
        ml = ml or {"home": {"close": {"odds": "-260"}}, "away": {"close": {"odds": "+700"}}}
        return {"events": [{"date": date, "competitions": [{
            "competitors": [{"homeAway": "home", "team": {"displayName": home}},
                            {"homeAway": "away", "team": {"displayName": away}}],
            "odds": [{"provider": {"name": "DraftKings"}, "moneyline": ml}]}]}]}
    def run_price(self, legs_, board):
        real, G.get = G.get, lambda url, *a, **k: board
        try:
            rep = {}; G.price_espn_soccer(legs_, {"2026-10-10"}, rep); return rep["espn_soccer"]
        finally: G.get = real
    def fb(self, **kw):
        l = {"sport": "football", "code": "en.1", "home": "Arsenal", "away": "Leeds United", "side": "h",
             "date": "2026-10-10", "when": "2026-10-10T11:30:00Z"}
        l.update(kw); return l
    def test_prices_an_unpriced_leg(self):
        l = self.fb()
        rep = self.run_price([l], self.board("Arsenal", "Leeds United"))
        self.assertEqual(rep["matched"], 1); self.assertAlmostEqual(l["odds"], 1.38)
        a = self.fb(side="a"); self.run_price([a], self.board("Arsenal", "Leeds United"))
        self.assertAlmostEqual(a["odds"], 8.0)
    def test_wrong_teams_or_time_not_matched(self):
        for l in (self.fb(home="Spurs"), self.fb(when="2026-10-10T16:00:00Z")):
            self.run_price([l], self.board("Arsenal", "Leeds United")); self.assertNotIn("odds", l)
    def test_keeps_an_existing_price_and_skips_unknown_competitions(self):
        l = self.fb(odds=1.5); self.run_price([l], self.board("Arsenal", "Leeds United")); self.assertEqual(l["odds"], 1.5)
        u = self.fb(code="zz.9"); self.assertEqual(self.run_price([u], self.board("Arsenal", "Leeds United"))["legs"], 0)

if __name__ == "__main__":
    unittest.main()

class Grading(unittest.TestCase):
    def test_leg_results(self):
        idx = ({("2026-10-04", "arsenal", "chelsea"): [2, 1]}, {"t1": {"winner": "Iga Swiatek"}, "t2": {"void": True}},
               {"s1": {"winner": "Saracens", "score": [30, 10]}})
        fb = {"sport": "football", "date": "2026-10-04", "home": "Arsenal", "away": "Chelsea", "side": "a", "pick": "Chelsea"}
        self.assertEqual(G.settle(fb, idx), ("lost", "2-1"))
        self.assertEqual(G.settle(dict(fb, side="h", pick="Arsenal"), idx)[0], "won")
        self.assertEqual(G.settle(dict(fb, home="Spurs"), idx)[0], "pending")
        self.assertEqual(G.settle({"sport": "tennis", "id": "t1", "pick": "Iga Swiatek"}, idx)[0], "won")
        self.assertEqual(G.settle({"sport": "tennis", "id": "t2", "pick": "X"}, idx)[0], "void")
        self.assertEqual(G.settle({"sport": "rugby", "id": "s1", "pick": "Sale Sharks"}, idx), ("lost", "30-10"))


class OddsApiTest(unittest.TestCase):
    SPORTS = [{"key": "tennis_atp_european_open", "title": "ATP European Open", "active": True},
              {"key": "tennis_wta_ningbo", "title": "WTA Ningbo Open", "active": True},
              {"key": "rugbyunion_premiership_rugby", "title": "Premiership Rugby", "active": True},
              {"key": "rugbyunion_top_14", "title": "Top 14", "active": True}]
    EV = [{"home_team": "Martin Damm", "away_team": "Yannick Hanfmann", "commence_time": "2026-10-19T11:30:00Z",
           "bookmakers": [{"title": "Bet365", "markets": [{"key": "h2h", "outcomes": [{"name": "Yannick Hanfmann", "price": 1.6}, {"name": "Martin Damm", "price": 2.3}]}]},
                          {"title": "William Hill", "markets": [{"key": "h2h", "outcomes": [{"name": "Yannick Hanfmann", "price": 1.7}]}]}]}]

    def setUp(self):
        import tempfile
        self.dir = tempfile.mkdtemp(); self.calls = []
        os.environ["ODDS_API_KEY"] = "test"

    def tearDown(self):
        os.environ.pop("ODDS_API_KEY", None)

    def fetch(self, url):
        self.calls.append(url)
        if "/odds?" not in url: return self.SPORTS, None
        return (self.EV if "european" in url else []), 400

    def tleg(self, **kw):
        return dict({"sport": "tennis", "tour": "ATP", "tournament": "BNP Paribas Fortis European Open",
                     "players": ["Martin Damm", "Yannick Hanfmann"], "pick": "Yannick Hanfmann",
                     "when": "2026-10-19T11:30:00Z", "date": "2026-10-19"}, **kw)

    def run_(self, L, now=None):
        from datetime import datetime, timezone
        r = {}
        G.price_odds_api(L, {"2026-10-19"}, r, cache_dir=self.dir, fetch=self.fetch,
                         now=now or datetime(2026, 10, 19, 9, tzinfo=timezone.utc))
        return r["oddsApi"]

    def test_prices_a_tennis_leg_one_credit_and_caches(self):
        l = self.tleg(); rep = self.run_([l])
        self.assertEqual((l["odds"], l["best"], l["books"]), (1.65, 1.7, 2))
        self.assertEqual(rep["calls"], 1)                       # only the tournament it needs
        self.assertFalse(any("ningbo" in u for u in self.calls))
        n = len(self.calls); self.run_([self.tleg()])
        self.assertEqual(len(self.calls), n)                    # second build: all from cache

    def test_logs_active_tennis_keys_and_unkeyed_tournaments(self):
        rep = self.run_([self.tleg(), self.tleg(tournament="Almaty Open")])
        self.assertTrue(rep["tennisKeys"])
        self.assertEqual(rep["noKey"], ["ATP Almaty Open"])

    def test_rugby_with_no_named_key_tries_every_union_key(self):
        urc = {"sport": "rugby", "comp": "URC", "home": "Stormers", "away": "Scarlets", "pick": "Stormers",
               "when": "2026-10-19T15:00:00Z", "date": "2026-10-19"}
        ev = [{"home_team": "Stormers", "away_team": "Scarlets", "commence_time": "2026-10-19T15:00:00Z",
               "bookmakers": [{"title": "Bet365", "markets": [{"key": "h2h", "outcomes": [
                   {"name": "Stormers", "price": 1.14}, {"name": "Scarlets", "price": 6.0}]}]}]}]
        def fetch(url):
            self.calls.append(url)
            if "/odds?" not in url: return self.SPORTS, None
            return (ev if "premiership" in url else []), 400
        self.fetch = fetch
        rep = self.run_([urc])
        self.assertEqual(urc["odds"], 1.14)
        self.assertEqual(rep["noKey"], [])
        self.assertTrue(any(k.startswith("rugbyunion_top_14") for k in rep["rugbyKeys"]))

    def test_rugby_key_tried_but_wrong_teams_price_nothing(self):
        l = {"sport": "rugby", "comp": "URC", "home": "Leinster", "away": "Munster", "pick": "Leinster",
             "when": "2026-10-19T15:00:00Z", "date": "2026-10-19"}
        self.run_([l])
        self.assertNotIn("odds", l)

    def test_no_key_or_already_priced_costs_nothing(self):
        os.environ.pop("ODDS_API_KEY")
        self.assertEqual(self.run_([self.tleg()]), "no key")
        os.environ["ODDS_API_KEY"] = "test"
        self.assertEqual(self.run_([self.tleg(odds=1.5)]), "no legs")
        self.assertEqual(self.calls, [])

    def test_daily_cap(self):
        from datetime import datetime, timezone
        old = G.ODDS_API_DAY; G.ODDS_API_DAY = 1
        try:
            rugby = {"sport": "rugby", "comp": "Top 14", "home": "Toulon", "away": "Pau", "pick": "Toulon", "when": None, "date": "2026-10-19"}
            rep = self.run_([self.tleg(), rugby])
            self.assertEqual(rep["calls"], 1); self.assertEqual(len(rep["skipped"]), 1)
        finally:
            G.ODDS_API_DAY = old
