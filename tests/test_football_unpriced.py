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

    def test_capped_calls_go_to_card_reachable_legs_first(self):
        """19 Nov 2026: the capped per-fixture calls went in board order, so a 62% Premier League
        pick the Card could take was capped behind a 45% Oberliga pick. Card-reachable legs go first."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.60"}, {"value": "Draw", "odd": "4.0"}, {"value": "Away", "odd": "5.5"}]}]}]}]
        day = [fx(101, t, "Bamberg", "Ansbach", hour=13), fx(102, t, "Leeds", "Hull", hour=14),
               fx(103, t, "Arsenal", "Chelsea", hour=15)]
        weak = dict(leg(t, "Bamberg", "Ansbach", "Oberliga", hour=13, mult=True), code="af.999", pModel=0.45)
        listed = dict(leg(t, "Leeds", "Hull", "Championship", hour=14, mult=True), code="en.2", pModel=0.50, list=True)
        card = dict(leg(t, "Arsenal", "Chelsea", "Premier League", hour=15, mult=True), code="en.1", pModel=0.62)
        r = self.run_price([weak, listed, card], day, {101: book, 102: book, 103: book}, cap=1)
        self.assertEqual(card.get("odds"), 1.6)
        self.assertNotIn("odds", weak)
        self.assertNotIn("odds", listed)
        self.assertEqual(r["miss"], {"capped": 2})
        r = self.run_price([weak, dict(listed), dict(card, pModel=0.55)], day, {101: book, 102: book, 103: book}, cap=1)
        self.assertEqual(r["matched"], 1)   # the list pick outranks the rest when nothing reaches the Card

    def test_call_order(self):
        a = {"sport": "football", "code": "en.1", "pModel": 0.61, "date": "2026-11-22"}
        b = {"sport": "football", "code": "en.1", "pModel": 0.70, "date": "2026-11-21"}
        c = {"sport": "football", "code": "en.1", "pModel": 0.58, "date": "2026-11-20", "reserve": True}
        d = {"sport": "football", "code": "en.1", "pModel": 0.75, "date": "2026-11-20", "why": "celtic"}
        self.assertEqual(sorted([a, b, c, d], key=G.call_order), [b, a, c, d])
        self.assertTrue(G.card_reach(a))
        self.assertFalse(G.card_reach(d))                          # a Daily List blind spot
        self.assertFalse(G.card_reach(dict(a, pModel=0.59)))       # under CARD_FAIR_MIN

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

    def test_af_spelling_bolivia(self):
        """25 Nov 2026 16:05 build: GV San José beside API-Football's Gualberto Villarroel SJ."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.70"}, {"value": "Draw", "odd": "3.8"}, {"value": "Away", "odd": "4.5"}]}]}]}]
        r = self.run_price([leg(t, "GV San José", "Real Potosí", "División Profesional")],
                           [fx(95, t, "Gualberto Villarroel SJ", "Real Potosí")], {95: book})
        self.assertEqual(r["matched"], 1)
        self.assertNotIn("miss", r)

    def test_af_spellings_26_nov(self):
        """26 Nov 2026 00:14 build: four board names noFixture beside their fixture
        (WSG Wattens, Rennes, Los Angeles FC, Dynamo), each club's every pool row
        since 30 Oct archived as an estimate."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.70"}, {"value": "Draw", "odd": "3.8"}, {"value": "Away", "odd": "4.5"}]}]}]}]
        pairs = [(("Sturm Graz", "WSG Wattens"), ("Sturm Graz", "WSG Tirol", "Bundesliga")),
                 (("Toulouse", "Rennes"), ("Toulouse", "Stade Rennais FC 1901", "Ligue 1")),
                 (("Los Angeles FC", "St. Louis City"), ("LAFC", "St. Louis CITY", "Major League Soccer")),
                 (("Krylia Sovetov", "Dynamo"), ("Krylia Sovetov", "Dinamo Moscow", "Premier League"))]
        day = [fx(110 + i, t, h, a, hour=10 + i) for i, ((h, a), _) in enumerate(pairs)]
        L = [leg(t, h, a, c, hour=10 + i) for i, (_, (h, a, c)) in enumerate(pairs)]
        r = self.run_price(L, day, {110 + i: book for i in range(len(pairs))})
        self.assertEqual(r["matched"], len(pairs))
        self.assertNotIn("miss", r)

    def test_celta_fortuna_spelling(self):
        """27 Nov 2026: Real Oviedo v RC Celta Fortuna, LaLiga 2, noFixture on six
        builds beside "Oviedo v Celta de Vigo II" (Celta's reserve side)."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.70"}, {"value": "Draw", "odd": "3.8"}, {"value": "Away", "odd": "4.5"}]}]}]}]
        r = self.run_price([leg(t, "Real Oviedo", "RC Celta Fortuna", "LaLiga 2")],
                           [fx(120, t, "Oviedo", "Celta de Vigo II")], {120: book})
        self.assertEqual(r["matched"], 1)
        self.assertNotIn("miss", r)
        # the first team on the board is never read as the reserve side's
        # fixture (the reverse is guarded by the other name and the kick-off,
        # as for every spelling: test_af_spelling_still_needs_both_names_and_kickoff)
        self.assertFalse(G.af_same("Celta de Vigo II", "RC Celta"))

    def test_af_spellings_second_read(self):
        """19 Nov 2026 07:13 build: six more board names beside their fixture under another spelling."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.70"}, {"value": "Draw", "odd": "3.8"}, {"value": "Away", "odd": "4.5"}]}]}]}]
        pairs = [(("Kortrijk", "Union St. Gilloise"), ("KV Kortrijk", "Royale Union Saint-Gilloise", "Pro League")),
                 (("Energie Cottbus", "Hertha BSC"), ("Energie Cottbus", "Hertha Berlin", "2. Bundesliga")),
                 (("Colo Colo", "U. Catolica"), ("Colo Colo", "Universidad Católica", "Primera División")),
                 (("LDU de Quito", "Aucas"), ("Liga de Quito", "Aucas", "Liga Pro")),
                 (("Progreso", "Atletico Torque"), ("Progreso", "Montevideo City Torque", "Primera División")),
                 (("Arsenal W", "West Ham W"), ("Arsenal", "West Ham United", "Women's Super League"))]
        day = [fx(80 + i, t, h, a, hour=10 + i) for i, ((h, a), _) in enumerate(pairs)]
        L = [leg(t, h, a, c, hour=10 + i) for i, (_, (h, a, c)) in enumerate(pairs)]
        r = self.run_price(L, day, {80 + i: book for i in range(len(pairs))})
        self.assertEqual(r["matched"], len(pairs))
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


class NoKickoff(unittest.TestCase):
    """19 Nov 2026: La Liga, the Süper Lig and Brazil's Serie A reach the board with no kick-off time."""
    def test_matched_leg_with_no_time_takes_api_footballs(self):
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.50"}, {"value": "Draw", "odd": "4.0"}, {"value": "Away", "odd": "6.0"}]}]}]}]
        l = leg(t, "FC Barcelona", "Villarreal", "La Liga"); l["when"] = None
        r = FootballUnpriced.run_price(self, [l], [fx(91, t, "Barcelona", "Villarreal", hour=20)], {91: book})
        self.assertEqual(l["when"], f"{t}T20:00:00Z")
        self.assertEqual(l["whenSrc"], "API-Football")
        self.assertEqual(r["timed"], 1)
        self.assertEqual(l["odds"], 1.5)

    def test_tbd_fixture_time_is_not_taken(self):
        t = date.today().isoformat()
        f = fx(93, t, "Galatasaray", "Samsunspor", hour=0); f["fixture"]["status"]["short"] = "TBD"
        l = leg(t, "Galatasaray", "Samsunspor", "Süper Lig"); l["when"] = None
        FootballUnpriced.run_price(self, [l], [f], {})
        self.assertIsNone(l["when"])
        self.assertIn("no kick-off time", G.card_fault(dict(l, code="tr.1", odds=1.5, est=False, fair=0.64,
                                                             pModel=0.68, why=None, hit=0.8, opp=7.0, event="x")))

    def test_board_time_is_never_overwritten(self):
        t = date.today().isoformat()
        l = leg(t, "Arsenal", "Chelsea", "Premier League", hour=15)
        r = FootballUnpriced.run_price(self, [l], [fx(92, t, "Arsenal", "Chelsea", hour=16)], {})
        self.assertEqual(l["when"], f"{t}T15:00:00Z")
        self.assertNotIn("whenSrc", l)
        self.assertNotIn("timed", r)

    def test_card_refuses_a_leg_with_no_start(self):
        l = {"sport": "football", "event": "Ajax v Other", "pick": "Ajax", "code": "en.1", "comp": "Premier League",
             "odds": 1.50, "est": False, "fair": 0.64, "pModel": 0.68, "why": None, "hit": 0.8, "opp": 7.0, "when": None}
        self.assertIn("no kick-off time", G.card_fault(l))
        l["when"] = "2026-11-21T15:00:00Z"
        self.assertIsNone(G.card_fault(l))

    def test_funnel_reads_it_as_no_time(self):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
        import card_funnel as F
        l = {"sport": "football", "event": "Ajax v Other", "pick": "Ajax", "code": "en.1", "comp": "Premier League",
             "odds": 1.50, "est": False, "fair": 0.64, "pModel": 0.68, "why": None, "hit": 0.8, "opp": 7.0, "when": None}
        self.assertEqual(F.fault_key(G.card_fault(l)), "no-time")

    def test_recheck_keeps_the_published_kickoff(self):
        old = {"event": "Ajax v Other", "pick": "Ajax", "when": "2026-11-21T15:00:00Z", "whenSrc": "API-Football",
               "odds": 1.5}
        cur = {"sport": "football", "event": "Ajax v Other", "pick": "Ajax", "code": "en.1", "comp": "Premier League",
               "odds": 1.50, "est": False, "fair": 0.64, "pModel": 0.68, "p": 0.68, "why": None, "hit": 0.8, "opp": 7.0,
               "when": None}
        g = {"rule": G.CARD_RULE, "name": "Card 2x", "legs": [old]}
        _, why = G.recheck_card(g, [cur])
        self.assertFalse(any("kick-off" in w for w in why), why)


if __name__ == "__main__":
    unittest.main()



class CardUnpriced(unittest.TestCase):
    """20 Nov 2026: the price reports name a competition with its country, and
    count the Card-reachable football legs no source priced."""

    def test_comp_label_carries_country(self):
        self.assertEqual(G.comp_label({"comp": "Premier League", "country": "Russia"}), "Premier League (Russia)")
        self.assertEqual(G.comp_label({"comp": "Championship"}), "Championship")
        self.assertEqual(G.comp_label({"code": "en.1"}), "en.1")

    def test_card_unpriced_counts_reachable_legs_only(self):
        base = {"sport": "football", "date": "2026-11-21", "home": "A", "away": "B"}
        core = dict(base, code="en.1", comp="Premier League", country="England", pModel=0.64)
        priced = dict(core, home="C", odds=1.5)
        weak = dict(core, home="D", pModel=0.55)
        wider = dict(core, home="E", code="af.235", comp="Premier League", country="Russia")
        n, named = G.card_unpriced([core, priced, weak, wider])
        with mock.patch.object(G, "CARD_CORE_ONLY", True):
            n, named = G.card_unpriced([core, priced, weak, wider])
            self.assertEqual(n, 1)
            self.assertEqual(named, [{"date": "2026-11-21", "comp": "Premier League (England)", "home": "A",
                                      "away": "B", "pModel": 0.64}])
            self.assertFalse(G.card_reach(wider))   # rule 14: a wider league cannot reach the Card

    def test_card_unpriced_keep(self):
        legs = [{"sport": "football", "code": "en.1", "pModel": 0.6 + i / 100, "date": "2026-11-21",
                 "home": f"H{i}", "away": "X"} for i in range(5)]
        n, named = G.card_unpriced(legs, keep=2)
        self.assertEqual(n, 5)
        self.assertEqual([m["home"] for m in named], ["H4", "H3"])   # strongest first on a day

    def test_card_unpriced_near_counts_only_legs_close_to_the_start(self):
        """23 Nov 2026: a week of "football Card unpriced" lines named core legs two and three days
        out (Salisbury v AFC Totton from 20 Nov) that API-Football priced the day before; only a leg
        still unpriced within CARD_UNPRICED_NEAR_H of its start can cost the Card a group."""
        now = G.datetime(2026, 11, 23, 7, 0, tzinfo=G.timezone.utc)
        base = {"sport": "football", "code": "en.1", "pModel": 0.65, "home": "A", "away": "B"}
        soon = dict(base, date="2026-11-23", when="2026-11-23T19:45:00Z")
        later = dict(base, home="C", date="2026-11-25", when="2026-11-25T19:45:00Z")
        started = dict(base, home="D", date="2026-11-23", when="2026-11-23T06:00:00Z")
        untimed = dict(base, home="E", date="2026-11-23")
        priced = dict(soon, home="F", odds=1.5)
        with mock.patch.object(G, "CARD_CORE_ONLY", True):
            self.assertEqual(G.card_unpriced_near([soon, later, started, untimed, priced], now), 1)
            n, named = G.card_unpriced([soon, later], now=now)
            self.assertEqual(n, 2)
            self.assertEqual([m.get("hours") for m in named], [12.8, 60.8])
            self.assertEqual(G.card_unpriced_near([soon, later], now, hours=72), 2)


class KickoffNamed(unittest.TestCase):
    """20 Nov 2026: `kickoff` legs (both names on API-Football's day, kick-offs 90+ minutes apart) are
    named with the board's and API-Football's times, as noFixture legs are; the 03:08 UTC build counted
    kickoff 2 (Championship, Serie A) with no names."""
    run_price = FootballUnpriced.run_price

    def test_kickoff_legs_named_with_both_times(self):
        t = date.today().isoformat()
        day = [fx(91, t, "Leeds", "Hull", hour=12), fx(92, t, "Arsenal", "Chelsea")]
        L = [dict(leg(t, "Leeds", "Hull", "Championship", hour=15), code="en.2", pModel=0.66, country="England"),
             leg(t, "Arsenal", "Chelsea", "Premier League")]
        r = self.run_price(L, day, {})
        self.assertEqual(r["miss"].get("kickoff"), 1)
        self.assertEqual(r["kickoff"], [{"date": t, "comp": "Championship (England)", "home": "Leeds", "away": "Hull",
                                         "board": "15:00", "af": ["12:00"], "card": True}])
        self.assertNotIn("odds", L[0])           # still never priced: the guard is unchanged

    def test_no_kickoff_key_without_kickoff_misses(self):
        t = date.today().isoformat()
        r = self.run_price([leg(t, "Zzyzx Town", "Qwerty Rovers", "Liga X")], [fx(93, t, "Leeds", "Hull")], {})
        self.assertNotIn("kickoff", r)

    def test_ol_lyonnes_spelling(self):
        """D1 Arkema's OL Lyonnes is "Lyon W" on API-Football (the 03:08 UTC build's noFixture name)."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.20"}, {"value": "Draw", "odd": "6.0"}, {"value": "Away", "odd": "11.0"}]}]}]}]
        r = self.run_price([leg(t, "OL Lyonnes", "Strasbourg", "D1 Arkema")], [fx(94, t, "Lyon W", "Strasbourg W")], {94: book})
        self.assertEqual(r["matched"], 1)
        self.assertNotIn("miss", r)

    def test_kansas_city_current_spelling(self):
        """NWSL's Kansas City Current is "Kansas City W" on API-Football (the 21 Nov 16:05 UTC build's noFixture name)."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "2.40"}, {"value": "Draw", "odd": "3.4"}, {"value": "Away", "odd": "2.9"}]}]}]}]
        r = self.run_price([leg(t, "Washington Spirit", "Kansas City Current", "NWSL")],
                           [fx(97, t, "Washington Spirit W", "Kansas City W")], {97: book})
        self.assertEqual(r["matched"], 1)
        self.assertNotIn("miss", r)

    def test_abbreviations_odds_aliases(self):
        """21 Nov 2026 (03:11 UTC build): Norwich City v Queens Park Rangers, Championship,
        noFixture beside "Norwich v QPR". API-Football's short forms are football-data's
        (odds.ALIASES), so af_same reads them too."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.80"}, {"value": "Draw", "odd": "3.6"}, {"value": "Away", "odd": "4.2"}]}]}]}]
        day = [fx(95, t, "Norwich", "QPR"), fx(96, t, "Wolves", "Fulham", hour=15)]
        L = [leg(t, "Norwich City", "Queens Park Rangers", "Championship"),
             leg(t, "Wolverhampton Wanderers", "Fulham", "Premier League", hour=15)]
        r = self.run_price(L, day, {95: book, 96: book})
        self.assertEqual(r["matched"], 2)
        self.assertNotIn("miss", r)

    def test_brazil_club_normaliser(self):
        """23 Nov 2026 (02:41 UTC build): CA Mineiro v SC Corinthians Paulista, Serie A,
        noFixture beside "Atletico-MG v Corinthians": the build's club normaliser
        (sources._norm) reduces both to the same club, so the fallback prices it."""
        t = date.today().isoformat()
        book = [{"bookmakers": [{"name": "Book A", "bets": [{"id": 1, "values": [
            {"value": "Home", "odd": "1.90"}, {"value": "Draw", "odd": "3.4"}, {"value": "Away", "odd": "4.0"}]}]}]}]
        L = [leg(t, "CA Mineiro", "SC Corinthians Paulista", "Serie A"),
             leg(t, "CA Paranaense", "EC Bahia", "Serie A", hour=15)]
        day = [fx(93, t, "Atletico-MG", "Corinthians"), fx(94, t, "Athletico-PR", "Bahia", hour=15)]
        r = self.run_price(L, day, {93: book, 94: book})
        self.assertEqual(r["matched"], 2)
        self.assertNotIn("miss", r)

    def test_normaliser_never_crosses_clubs(self):
        """Equality of the normalised form only: Mineiro is not Paranaense,
        Inter is not AC Milan."""
        self.assertTrue(G.af_same("Atletico-MG", "CA Mineiro"))
        self.assertFalse(G.af_same("Atletico-MG", "CA Paranaense"))
        self.assertFalse(G.af_same("Inter", "AC Milan"))

    def test_alias_does_not_cross_clubs(self):
        """An alias widens a spelling, never a club: QPR is not Queen of the South."""
        self.assertTrue(G.af_same("QPR", "Queens Park Rangers"))
        self.assertFalse(G.af_same("QPR", "Queen of the South"))
        self.assertFalse(G.af_same("Wolves", "Wolfsburg"))
