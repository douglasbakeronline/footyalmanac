"""The empty-day fillers (10 Nov 2026, issue #155): tools/card_replay.py's
fill variants are the live Card on a day the full rule fills, and only on a
day it leaves empty a group under the filler, marked `fill`; fillwide is the
page's wider-rule fallback (groupings.build_card's last block). The
football-data side (tools/card_legs_history.py) takes the wider gate for
fillwide only. No network."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_replay as CR
import card_legs_history as H
import groupings as G
import card_review_post as P

# 11 Nov 2026: the Card became the model's own picks (CARD_RULE 7). These tests
# cover the rule 6 machinery, which stays as the replay variant `rule6`, so the
# module runs under rule 6; tests/test_card_model_rule.py covers rule 7.
from unittest import mock as _mock
_RULE6 = [_mock.patch.object(G, "CARD_MODEL_RULE", False), _mock.patch.object(G, "CARD_RULE", 6)]
def setUpModule():
    for p in _RULE6: p.start()
def tearDownModule():
    for p in _RULE6: p.stop()


CODES = ["en.1", "de.1", "es.1", "it.1", "fr.1", "nl.1", "pt.1"]


def row(i, avg, result=0, date="2026-11-14"):
    return {"date": date, "code": CODES[i % len(CODES)], "home": f"H{i}", "away": f"A{i}", "time": "15:00",
            "avg": list(avg), "best": [a + 0.05 for a in avg], "result": result}


def near_market_day():
    """Seven legs the full rule refuses (the model on the market, the
    opposition short) and the wider rule takes."""
    return [((0.64, 0.20, 0.16), row(i, (1.50, 4.0, 6.0))) for i in range(7)]


def full_rule_day():
    """Seven legs the full rule takes: the model 8 points under the market,
    the opposition priced 11."""
    return [((0.66, 0.20, 0.14), row(i, (1.30, 5.0, 11.0))) for i in range(7)]


def by_day(L):
    out = {}
    for l in L:
        when = f"{l['date']}T{l['time']}:00Z"
        leg = {"sport": "football", "event": f"{l['home']} v {l['away']}", "pick": l["home"], "comp": l["code"], "code": l["code"],
               "when": when, "date": l["date"], "odds": round(l["price"], 2), "best": round(l["best"], 2), "margin": round(l["margin"], 4),
               "est": False, "pModel": round(l["model"], 4), "p": round(l["model"], 4), "hit": 0.8, "n": 100, "won": l["won"],
               "core": l["core"], "opp": round(l["opp"], 2), "draw": round(l["draw"], 2)}
        G.honest(leg)
        out.setdefault(G.uk_slot(leg)[0], []).append(leg)
    return out


class Fillers(unittest.TestCase):
    def test_registered(self):
        for v, fill in (("fillwide", "wide"), ("fillopp7", "opp7"), ("fillrule5", "rule5"), ("fillshort", "short")):
            self.assertEqual(CR.VARIANTS[v], {"_FILL": fill})
            if fill != "wide": self.assertIn(fill, CR.VARIANTS)

    def test_empty_day_takes_the_wider_rule(self):
        (d, legs), = by_day(H.legs(near_market_day(), wide=True)).items()
        self.assertEqual(CR.build(legs, d, "live"), [])
        gs = CR.build(legs, d, "fillwide")
        self.assertTrue(gs)
        self.assertTrue(all(g["fill"] for g in gs))
        self.assertEqual({g["seq"] for g in gs}, {1})
        for g in gs:
            for l in g["legs"]: self.assertIsNone(G.card_fault(l, wide=True))

    def test_full_day_is_live_unchanged(self):
        (d, legs), = by_day(H.legs(full_rule_day())).items()
        live = CR.build(legs, d, "live")
        self.assertTrue(live)
        for v in ("fillwide", "fillopp7", "fillrule5", "fillshort"):
            gs = CR.build(legs, d, v)
            self.assertEqual([[l["event"] for l in g["legs"]] for g in gs], [[l["event"] for l in g["legs"]] for g in live])
            self.assertFalse(any(g.get("fill") for g in gs))

    def test_filler_leaves_constants_as_they_were(self):
        (d, legs), = by_day(H.legs(near_market_day(), wide=True)).items()
        before = (dict(G.CARD_OPP_MIN), G.CARD_ODDS, G.CARD_UNDER_MAX)
        for v in ("fillopp7", "fillrule5", "fillshort"): CR.build(legs, d, v)
        self.assertEqual((dict(G.CARD_OPP_MIN), G.CARD_ODDS, G.CARD_UNDER_MAX), before)


class FootballData(unittest.TestCase):
    def test_wide_gate_only_when_asked(self):
        # 11 Nov 2026: the wider floor is 60% like the full rule's (CARD_WIDE_RULE 2),
        # so the gates differ on price: 1.10 is under the full rule's 1.15, inside 1.08
        rows = [((0.85, 0.10, 0.05), row(1, (1.10, 9.0, 21.0)))]
        self.assertEqual(H.legs(rows), [])
        wide = H.legs(rows, wide=True)
        self.assertEqual(len(wide), 1)
        self.assertGreaterEqual(wide[0]["fair"], G.CARD_WIDE_FAIR_MIN)
        thin = [((0.60, 0.22, 0.18), row(1, (1.70, 3.8, 5.0)))]   # the bookmakers about 56%: off both since 11 Nov 2026
        self.assertEqual(H.legs(thin, wide=True), [])

    def test_card_season_fill_variants(self):
        Lw = H.legs(near_market_day(), wide=True)
        self.assertEqual(H.card_season(H.legs(near_market_day()))["groups"], 0)
        self.assertGreater(H.card_season(Lw, "fillwide")["groups"], 0)
        L = H.legs(full_rule_day())
        self.assertEqual(H.card_season(L, "fillwide")["groups"], H.card_season(L)["groups"])


class Review(unittest.TestCase):
    def test_filler_gated_on_its_own_legs(self):
        rep = {"variants": {"live": {"legs": 300},
                            "fillrule5": {"legs": 320, "pWorse": 0.1, "vsLivePerDay": 0.4, "fill": {"legs": 20, "groups": 4}},
                            "short": {"legs": 120, "pWorse": 0.1, "vsLivePerDay": 0.4}}}
        self.assertEqual(P.gate_legs(rep["variants"]["fillrule5"]), 20)
        self.assertEqual([v for v, _ in P.candidates(rep)], ["short"])

    def test_fill_lines(self):
        rep = {"variants": {"fillwide": {"vsLivePerDay": -1.47, "pWorse": 0.95,
                                         "fill": {"days": 7, "groups": 12, "won": 2, "expected": 4.14, "legs": 36, "return": 0.46}},
                            "fillopp7": {"fill": {"groups": 0}}}}
        out = P.fill_lines(rep)
        self.assertTrue(any("fillwide: 7 days, 12 groups, 2 won" in x and "-54.0%" in x for x in out), out)
        self.assertTrue(any("fillopp7: no groups" in x for x in out))
        self.assertEqual(P.fill_lines({"variants": {"live": {}}}), [])


if __name__ == "__main__":
    unittest.main()
