"""API-Football domestic cups and the youth-side name guard (6 Oct 2026)."""
import json, os, sys, tempfile, time, unittest
from datetime import date, timedelta
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import sources as S
import build as B


def fx(lid, d, home, away, st="NS", hg=None, ag=None):
    return {"league": {"id": lid}, "fixture": {"date": f"{d}T19:00:00+00:00", "status": {"short": st}},
            "teams": {"home": {"name": home}, "away": {"name": away}},
            "score": {"fulltime": {"home": hg, "away": ag}}}


class YouthGuard(unittest.TestCase):
    def test_u21_is_not_the_first_team(self):
        self.assertIsNone(S.match_team("Sunderland U21", {"Sunderland", "Leeds United"}))
        self.assertIsNone(S.match_team("Borussia Dortmund II", {"Borussia Dortmund"}))
        self.assertIsNone(S.match_team("Jong Ajax", {"Ajax"}))

    def test_same_side_still_matches(self):
        self.assertEqual(S.match_team("Sunderland AFC", {"Sunderland", "Leeds"}), "Sunderland")
        self.assertEqual(S.match_team("Dortmund II", {"Borussia Dortmund II", "Borussia Dortmund"}),
                         "Borussia Dortmund II")
        self.assertEqual(S.match_team("Brentford U21", {"Brentford U21"}), "Brentford U21")


class CupFilter(unittest.TestCase):
    def test_wanted(self):
        ok = lambda n, c="Japan", t="Cup": S.af_cup_wanted({"name": n, "type": t}, c)
        self.assertTrue(ok("Emperor Cup"))
        self.assertTrue(ok("League Cup"))
        self.assertTrue(ok("U.S. Open Cup", "USA"))
        for n in ("Super Cup", "Supercopa", "Women's Cup", "FA Youth Cup", "U19 Cup",
                  "Community Shield", "Friendlies Clubs", "Premier League 2"):
            self.assertFalse(ok(n), n)
        self.assertFalse(ok("Emperor Cup", "World"))
        self.assertFalse(ok("J1 League", t="League"))


class Register(unittest.TestCase):
    def tearDown(self):
        for c in ("afc.99901", "afc.99902"):
            E.LEAGUES.pop(c, None)
            S.AF.pop(c, None)
            S.AF_CUPS.discard(c)

    def test_register_and_frame(self):
        added = S.register_new_cups([{"code": "afc.99901", "id": 99901, "name": "Emperor Cup",
                                      "country": "Japan", "season": 2026}])
        self.assertEqual(added, ["afc.99901"])
        m = E.LEAGUES["afc.99901"]
        self.assertTrue(m["cup"] and m["afCup"])
        self.assertEqual(m["iso"], E.LEAGUES["jp.1"]["iso"])
        self.assertAlmostEqual(m["strength"], round(E.LEAGUES["jp.1"]["strength"] - 0.03, 2))
        # its clubs are looked up in Japan only
        self.assertTrue(E.eligible_league("jp.1", "afc.99901"))
        self.assertFalse(E.eligible_league("kr.1" if "kr.1" in E.LEAGUES else "en.1", "afc.99901"))
        self.assertEqual(S.register_new_cups([{"code": "afc.99901", "id": 99901, "name": "x",
                                               "country": "Japan"}]), [])

    def test_alias_country(self):
        S.register_new_cups([{"code": "afc.99902", "id": 99902, "name": "Cup",
                              "country": "Czech-Republic", "season": 2026}])
        self.assertEqual(E.LEAGUES["afc.99902"]["country"], "Czechia")
        cz = next(c for c, m in E.LEAGUES.items() if m["country"] == "Czechia" and not m.get("cup"))
        self.assertTrue(E.eligible_league(cz, "afc.99902"))

    def test_off_the_list(self):
        S.register_new_cups([{"code": "afc.99901", "id": 99901, "name": "Emperor Cup",
                              "country": "Japan", "season": 2026}])
        self.assertIsNone(B.accuracy_for(0.9, False, league="afc.99901"))


class Refresh(unittest.TestCase):
    def test_writes_list_and_skips_unrated_countries(self):
        resp = [
            {"league": {"id": 101, "name": "Emperor Cup", "type": "Cup"}, "country": {"name": "Japan"},
             "seasons": [{"year": 2026, "current": True}]},
            {"league": {"id": 102, "name": "Super Cup", "type": "Cup"}, "country": {"name": "Japan"},
             "seasons": [{"year": 2026, "current": True}]},
            {"league": {"id": 103, "name": "Cup", "type": "Cup"}, "country": {"name": "Atlantis"},
             "seasons": [{"year": 2026, "current": True}]},
        ]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "af-cups.json")
            with mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
                 mock.patch.object(S, "_af_get", return_value=resp):
                new = S.af_refresh_cups(path=path)
                self.assertEqual([e["code"] for e in new], ["afc.101"])
                doc = json.load(open(path))
                self.assertEqual([e["code"] for e in doc["cups"]], ["afc.101"])
                # fresh: no second call inside three days
                self.assertEqual(S.af_refresh_cups(path=path), [])

    def test_no_key_no_call(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(S, "_af_get") as g:
            self.assertEqual(S.af_refresh_cups(path=os.path.join(d, "x.json")), [])
            g.assert_not_called()


class Pool(unittest.TestCase):
    def setUp(self):
        S.register_new_cups([{"code": "afc.99901", "id": 99901, "name": "Emperor Cup",
                              "country": "Japan", "season": 2026}])
        S._AF_POOL.clear()

    def tearDown(self):
        S._AF_POOL.clear()
        E.LEAGUES.pop("afc.99901", None)
        S.AF.pop("afc.99901", None)
        S.AF_CUPS.discard("afc.99901")

    def test_rows_from_the_date_pool(self):
        t = date.today()
        day = {t: [fx(99901, t, "Kashima Antlers", "Urawa Reds"), fx(5, t, "A", "B")],
               t - timedelta(days=2): [fx(99901, t - timedelta(days=2), "Gamba Osaka", "Kobe", "FT", 2, 1)]}
        with mock.patch.object(S, "_af_day", side_effect=lambda d: day.get(d, [])):
            rows = S.af_rows("afc.99901", "2026")
        self.assertEqual(len(rows), 2)
        played = [r for r in rows if r["hg"] is not None]
        self.assertEqual((played[0]["home"], played[0]["hg"], played[0]["ag"]), ("Gamba Osaka", 2, 1))

    def test_day_cache(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "AF_CACHE_DIR", d):
            old = date.today() - timedelta(days=5)
            with mock.patch.object(S, "_af_get", return_value=[fx(1, old, "A", "B", "FT", 1, 0)]) as g:
                S._af_day(old)
                S._af_day(old)
                self.assertEqual(g.call_count, 1)
            import gzip
            with gzip.open(os.path.join(d, f"day-{old}.json.gz"), "rt") as fh:
                self.assertTrue(json.load(fh)["final"])
            # read back in the full shape
            with mock.patch.object(S, "_af_get") as g:
                f = S._af_day(old)[0]
                g.assert_not_called()
            self.assertEqual((f["teams"]["home"]["name"], f["score"]["fulltime"]["home"]), ("A", 1))


class SeasonPool(unittest.TestCase):
    """Current API-Football seasons come from the date pool, not one call per
    league per build (6 Oct 2026)."""
    def setUp(self):
        S._AF_POOL.clear()

    def tearDown(self):
        S._AF_POOL.clear()

    def test_window(self):
        t = date(2026, 10, 6)
        self.assertEqual(S.af_season_window("2026-27", t)[0], date(2026, 6, 1))
        self.assertEqual(S.af_season_window("2026", t)[0], date(2026, 1, 1))
        self.assertIsNone(S.af_season_window("2024-25", t))
        self.assertIsNone(S.af_season_window("2025", t))

    def test_current_league_reads_pool_only(self):
        code = "en.6n"
        lid = S.AF[code]
        t = date.today()
        y = t.year if t.month >= 6 else t.year - 1
        season = f"{y}-{str(y + 1)[2:]}"
        days = {t - timedelta(days=3): [fx(lid, t - timedelta(days=3), "A", "B", "FT", 2, 0),
                                        fx(999, t - timedelta(days=3), "C", "D", "FT", 1, 1)],
                t + timedelta(days=1): [fx(lid, t + timedelta(days=1), "B", "A")]}
        for f in days[t - timedelta(days=3)] + days[t + timedelta(days=1)]:
            f["league"]["season"] = y
        with mock.patch.object(S, "_af_day", side_effect=lambda d: days.get(d, [])), \
             mock.patch.object(S, "_af_get") as g, \
             mock.patch.dict(E.LEAGUES[code], {"season": season}):
            rows = S.af_rows(code, season)
            g.assert_not_called()
        self.assertEqual([(r["home"], r["hg"]) for r in rows], [("A", 2), ("B", None)])

    def test_finished_season_one_call_then_disk(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "AF_CACHE_DIR", d), \
             mock.patch.object(S, "_af_get", return_value=[fx(1, date(2025, 3, 1), "A", "B", "FT", 1, 0)]) as g, \
             mock.patch.dict(E.LEAGUES["en.6n"], {"season": "2024-25"}):
            S.af_rows("en.6n", "2024-25")
            S.af_rows("en.6n", "2024-25")
            self.assertEqual(g.call_count, 1)


class Dedupe(unittest.TestCase):
    def setUp(self):
        S.register_new_cups([{"code": "afc.99903", "id": 99903, "name": "FA Cup",
                              "country": "England", "season": 2026}])

    def tearDown(self):
        E.LEAGUES.pop("afc.99903", None)
        S.AF.pop("afc.99903", None)
        S.AF_CUPS.discard("afc.99903")

    def test_native_tie_wins(self):
        fixtures = {
            "en.fa": [{"date": "2026-11-01", "home": "Manchester United", "away": "Wigan Athletic"}],
            "afc.99903": [{"date": "2026-11-01", "home": "Manchester United FC", "away": "Wigan"},
                          {"date": "2026-11-01", "home": "Leeds", "away": "Hull"}],
        }
        self.assertEqual(B.dedupe_cups(fixtures), 1)
        self.assertEqual([r["home"] for r in fixtures["afc.99903"]], ["Leeds"])


if __name__ == "__main__":
    unittest.main()


class GroupingsOdds(unittest.TestCase):
    """The Odds tab prices only the legs' fixtures, not every page of a date."""
    def test_one_call_per_leg_then_cached(self):
        import groupings as G
        t = date.today().isoformat()
        day = [fx(1, t, "Arsenal", "Chelsea"), fx(1, t, "Leeds", "Hull")]
        day[0]["fixture"]["id"], day[1]["fixture"]["id"] = 11, 12
        odds = {"response": [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.80"}, {"value": "Draw", "odd": "3.5"}, {"value": "Away", "odd": "4.0"}]}]}]}]}
        legs = lambda: [{"sport": "football", "date": t, "when": f"{t}T19:00:00Z", "home": "Arsenal",
                         "away": "Chelsea", "side": "h"}]
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "AF_CACHE_DIR", d), mock.patch.object(S, "_af_day", return_value=day), \
             mock.patch.object(G, "af", return_value=odds) as af:
            L, rep = legs(), {}
            G.price_football(L, {t}, rep)
            self.assertEqual((L[0]["odds"], rep["football"]["calls"]), (1.8, 1))
            self.assertIn("fixture=11", af.call_args[0][0])
            L, rep = legs(), {}
            G.price_football(L, {t}, rep)
            self.assertEqual((L[0]["odds"], rep["football"]["calls"]), (1.8, 0))
