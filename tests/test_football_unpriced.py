"""Why a football leg stayed unpriced (groupings.price_football, 14 Nov 2026).
No network: API-Football is stubbed. Standard library only."""
import os, sys, tempfile, unittest
from datetime import date
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G
import odds as O
import sources as S


def fx(fid, d, home, away, hour=19):
    return {"league": {"id": 1}, "fixture": {"id": fid, "date": f"{d}T{hour:02d}:00:00+00:00", "status": {"short": "NS"}},
            "teams": {"home": {"name": home}, "away": {"name": away}}, "score": {"fulltime": {"home": None, "away": None}}}


def leg(t, home, away, comp, hour=19, mult=False):
    l = {"sport": "football", "date": t, "when": f"{t}T{hour:02d}:00:00Z", "home": home, "away": away,
         "side": "h", "comp": comp, "pick": home}
    if mult: l["multOnly"] = True
    return l


class FootballUnpriced(unittest.TestCase):
    def run_price(self, L, day, odds_by_fid, cap=None):
        t = L[0]["date"]
        def af_get(path):
            fid = int(path.split("fixture=")[1].split("&")[0])
            items = odds_by_fid.get(fid, [])
            S._AF_CACHE[path] = items; S.AF_USAGE["calls"] += 1
            return items
        rep = {}
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "AF_CACHE_DIR", d), mock.patch.object(S, "_af_day", return_value=day), \
             mock.patch.object(O, "af_prices", lambda dates: {}), mock.patch.object(S, "_af_get", af_get), \
             mock.patch.object(G, "FB_CALLS_MULT", G.FB_CALLS_MULT if cap is None else cap):
            S._AF_CACHE.clear()
            G.price_football(L, {t}, rep)
            S._AF_CACHE.clear()
        return rep["football"]

    def test_each_reason_counted_by_competition(self):
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.50"}, {"value": "Draw", "odd": "4.0"}, {"value": "Away", "odd": "6.0"}]}]}]}]
        day = [fx(11, t, "Arsenal", "Chelsea"), fx(12, t, "Leeds", "Hull"), fx(13, t, "Celtic", "Rangers", hour=12)]
        L = [leg(t, "Arsenal", "Chelsea", "Premier League"),          # priced
             leg(t, "Leeds", "Hull", "Championship"),                 # listed, no odds
             leg(t, "Celtic", "Rangers", "Premiership", hour=19),     # moved: kick-offs 7h apart
             leg(t, "Zzyzx Town", "Qwerty Rovers", "Liga X")]         # not listed at all
        r = self.run_price(L, day, {11: book})
        self.assertEqual(r["matched"], 1)
        self.assertEqual(L[0]["odds"], 1.5)
        self.assertEqual(r["miss"], {"noOdds": 1, "kickoff": 1, "noFixture": 1})
        self.assertEqual(r["missComps"]["noFixture"], [("Liga X", 1)])
        self.assertEqual(r["missComps"]["noOdds"], [("Championship", 1)])

    def test_capped_mid_priced_legs(self):
        t = date.today().isoformat()
        day = [fx(21, t, "Leeds", "Hull")]
        L = [leg(t, "Leeds", "Hull", "Championship", mult=True)]
        r = self.run_price(L, day, {}, cap=0)
        self.assertEqual(r["miss"], {"capped": 1})

    def test_no_miss_key_when_all_priced(self):
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.50"}, {"value": "Draw", "odd": "4.0"}, {"value": "Away", "odd": "6.0"}]}]}]}]
        r = self.run_price([leg(t, "Arsenal", "Chelsea", "Premier League")], [fx(11, t, "Arsenal", "Chelsea")], {11: book})
        self.assertNotIn("miss", r)

    def test_nofixture_legs_named_with_near_fixtures(self):
        """19 Nov 2026: a noFixture leg is named, with the day's fixtures that share one of its names, so a
        session can tell a spelling (add it to LIVE_NAMES) from a fixture API-Football does not list."""
        t = date.today().isoformat()
        day = [fx(31, t, "Qqx Inter", "AC Milan"), fx(32, t, "Leeds", "Hull")]
        L = [leg(t, "Internazionale", "AC Milan", "Serie A"),   # one side spelt another way
             leg(t, "Zzyzx Town", "Qwerty Rovers", "Liga X")]   # not listed at all
        r = self.run_price(L, day, {})
        named = {(m["home"], m["away"]): m for m in r["noFixture"]}
        self.assertEqual(named[("Internazionale", "AC Milan")]["near"], ["Qqx Inter v AC Milan"])
        self.assertEqual(named[("Internazionale", "AC Milan")]["comp"], "Serie A")
        self.assertEqual(named[("Zzyzx Town", "Qwerty Rovers")]["near"], [])

    def test_nofixture_list_is_capped(self):
        t = date.today().isoformat()
        L = [leg(t, f"Side {i}", f"Other {i}", "Liga X") for i in range(G.NOFIXTURE_KEEP + 5)]
        r = self.run_price(L, [fx(41, t, "Leeds", "Hull")], {})
        self.assertEqual(r["miss"]["noFixture"], G.NOFIXTURE_KEEP + 5)
        self.assertEqual(len(r["noFixture"]), G.NOFIXTURE_KEEP)

    def test_af_spellings_match(self):
        """19 Nov 2026: board names API-Football spells another way (AF_SPELLINGS) are priced."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.70"}, {"value": "Draw", "odd": "3.8"}, {"value": "Away", "odd": "4.5"}]}]}]}]
        day = [fx(51, t, "Aarhus", "Lyngby"), fx(52, t, "Inverness CT", "Ayr Utd", hour=15),
               fx(53, t, "Charleroi", "St. Truiden", hour=17)]
        L = [leg(t, "AGF", "Lyngby Boldklub", "Superliga"),
             leg(t, "Inverness Caledonian Thistle", "Ayr United", "Championship", hour=15),
             leg(t, "Sporting Charleroi", "STVV", "Pro League", hour=17)]
        r = self.run_price(L, day, {51: book, 52: book, 53: book})
        self.assertEqual(r["matched"], 3)
        self.assertNotIn("miss", r)

    def test_af_spelling_still_needs_both_names_and_kickoff(self):
        t = date.today().isoformat()
        day = [fx(61, t, "Aarhus", "Brondby"), fx(62, t, "Aarhus", "Lyngby", hour=12)]
        L = [leg(t, "AGF", "Lyngby Boldklub", "Superliga", hour=19)]
        r = self.run_price(L, day, {})
        self.assertEqual(r["miss"], {"kickoff": 1})
        self.assertNotIn("odds", L[0])

    def test_fixture_on_another_day_is_moved_not_nofixture(self):
        """19 Nov 2026: a leg API-Football lists on another day in the window is `moved`, never priced."""
        t0, t1 = "2026-11-21", "2026-11-22"
        pools = {t0: [fx(71, t0, "Liverpool W", "Chelsea W")], t1: [fx(72, t1, "Liverpool", "Manchester United")]}
        L = [leg(t0, "Liverpool", "Manchester United", "Premier League")]
        rep = {}
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "AF_CACHE_DIR", d), mock.patch.object(S, "_af_day", lambda dd: pools[dd.isoformat()]), \
             mock.patch.object(O, "af_prices", lambda dates: {}):
            G.price_football(L, {t0, t1}, rep)
        r = rep["football"]
        self.assertEqual(r["miss"], {"moved": 1})
        self.assertEqual(r["moved"], [{"date": t0, "afDate": t1, "comp": "Premier League",
                                       "home": "Liverpool", "away": "Manchester United"}])
        self.assertNotIn("noFixture", r)
        self.assertNotIn("odds", L[0])


if __name__ == "__main__":
    unittest.main()
