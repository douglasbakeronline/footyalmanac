"""12 Nov 2026: the rule 7 Card's variants paired against live on the
football-data seasons (tools/card_legs_history.py `cardM7Paired`,
`cardM7Pooled`), so the gate in CLAUDE.md (a variant beats live on both
football-data seasons and the pool, p(worse) at most 0.30 on 100+ legs) has
its football-data side for `m7under5` and `m7core`. No network."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_legs_history as H
import card_replay as CR

CODES = ["en.1", "de.1", "es.1", "it.1", "fr.1", "nl.1", "pt.1"]


def g(date, won, odds=2.0, stake=2, legs=3, p=0.5):
    return {"date": date, "name": "Card 2x", "p": p, "odds": odds, "stake": stake, "won": won, "legs": legs}


def row(i, avg, result=0, date="2026-11-14"):
    return {"date": date, "code": CODES[i % len(CODES)], "home": f"H{i}", "away": f"A{i}", "time": "15:00",
            "avg": list(avg), "best": [a + 0.05 for a in avg], "result": result}


class Paired(unittest.TestCase):
    def test_identical(self):
        c = {"groupList": [g("2026-01-01", True), g("2026-01-02", False)]}
        x = H.paired(c, dict(c))
        self.assertTrue(x["identical"]); self.assertIsNone(x["pWorse"]); self.assertEqual(x["legs"], 6)

    def test_better_candidate(self):
        base = {"groupList": [g("2026-01-01", False), g("2026-01-02", False), g("2026-01-03", True)]}
        cand = {"groupList": base["groupList"] + [g("2026-01-04", True), g("2026-01-05", True)]}
        x = H.paired(base, cand)
        self.assertFalse(x["identical"]); self.assertEqual(x["days"], 5)
        self.assertAlmostEqual(x["perDay"], 0.8)   # two extra wins of 2 units over 5 days
        self.assertEqual(x["pWorse"], 0.0); self.assertEqual(x["legs"], 15)

    def test_empty_candidate_is_worse(self):
        base = {"groupList": [g("2026-01-01", True), g("2026-01-02", True)]}
        x = H.paired(base, {"groups": 0})
        self.assertLess(x["perDay"], 0); self.assertEqual(x["pWorse"], 1.0)

    def test_pooled_counts_seasons_ahead(self):
        live1 = {"groupList": [g("2025-01-01", False)]}; live2 = {"groupList": [g("2026-01-01", True)]}
        v1 = {"groupList": [g("2025-01-01", True)]}; v2 = {"groupList": [g("2026-01-01", False)]}
        seasons = []
        for live, v in ((live1, v1), (live2, v2)):
            r = {"cardM7": {"live": live, "m7under5": v}}
            r["cardM7Paired"] = H.m7_paired(r["cardM7"])
            seasons.append(r)
        out = H.m7_pooled(seasons + [{"season": "x", "error": "no data"}])
        self.assertEqual(out["live"]["groups"], 2); self.assertEqual(out["m7under5"]["groups"], 2)
        self.assertEqual(out["m7under5"]["seasonsAhead"], 1); self.assertEqual(out["m7under5"]["seasons"], 2)
        self.assertEqual(out["m7under5"]["vsLive"]["perDay"], 0.0)
        self.assertEqual(H.m7_pooled([]), {})


class OnFootballData(unittest.TestCase):
    def test_registered(self):
        self.assertEqual(CR.VARIANTS["m7under5"], {"CARD_MODEL_EDGE": -0.05})
        self.assertEqual(CR.VARIANTS["m7core"], {"CARD_CORE_ONLY": True})

    def test_under5_admits_picks_just_under_the_market(self):
        # the model 3 points under the bookmakers' fair chance: live's value
        # demand refuses them, m7under5 takes them
        pairs = [((0.74, 0.16, 0.10), row(i, (1.28, 5.5, 11.0))) for i in range(6)]
        Lm = H.legs(pairs, model=True)
        self.assertEqual(len(Lm), 6)
        self.assertTrue(all(l["model"] < l["fair"] for l in Lm))
        live, u5 = H.card_season(Lm, "live"), H.card_season(Lm, "m7under5")
        self.assertEqual(live["groups"], 0)
        self.assertGreater(u5["groups"], 0)
        self.assertTrue(all(x["legs"] >= 3 for x in u5["groupList"]))
        x = H.m7_paired({"live": live, "m7under5": u5})["m7under5"]
        self.assertFalse(x["identical"]); self.assertGreater(x["perDay"], 0)


if __name__ == "__main__":
    unittest.main()
