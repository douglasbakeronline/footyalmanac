"""tools/card_legs_history.py (9 Nov 2026): the replay legs carry the
opposition's and the draw's price (card_season read them and crashed on
main from 6 to 9 Nov), the opposition and gap tables, and --seasons (#153)
replays a past season with the season before as its prior, standing in for
tune.splits only while it runs. No network: the fetch and replay are stubbed."""
import os, sys, unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_legs_history as H
import tune


def price_row(date="2026-11-14", avg=(1.30, 5.0, 11.0), result=0, home="A", away="B", best=None):
    return {"date": date, "code": "en.1", "home": home, "away": away, "time": "15:00", "avg": list(avg),
            "best": list(best or [a + 0.05 for a in avg]), "result": result}


class Legs(unittest.TestCase):
    def test_opposition_and_draw_price_on_each_leg(self):
        L = H.legs([((0.70, 0.18, 0.12), price_row())])
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0]["opp"], 11.0); self.assertEqual(L[0]["draw"], 5.0)
        away = H.legs([((0.12, 0.18, 0.70), price_row(avg=(11.0, 5.0, 1.30), result=2))])
        self.assertEqual(away[0]["opp"], 11.0); self.assertEqual(away[0]["side"], "a")

    def test_card_season_runs_on_replay_legs(self):
        # 9 Nov 2026: a KeyError on "opp" here is what killed tune.yml's weekly run
        L = H.legs([((0.70, 0.18, 0.12), price_row())])
        self.assertIn("groups", H.card_season(L))
        self.assertIn("groups", H.card_season(L, "rule5"))

    def test_tables(self):
        rows = []
        for i in range(12):
            rows.append(((0.66, 0.20, 0.14), price_row(date=f"2026-11-{i + 1:02d}", avg=(1.30, 5.0, 11.0), result=0 if i % 4 else 2, home=f"H{i}", away=f"A{i}")))
            rows.append(((0.60, 0.22, 0.18), price_row(date=f"2026-11-{i + 1:02d}", avg=(1.45, 4.2, 7.0), result=0, home=f"K{i}", away=f"L{i}")))
        L = H.legs(rows)
        lop = H.lopsided(L)
        self.assertIn("opp 9+", lop["1.15-1.90"]); self.assertIn("opp 6-9", lop["1.15-1.90"])
        self.assertEqual(lop["1.15-1.90"]["opp 9+"]["n"], 12)
        gap = H.by_gap(L)
        self.assertIn("opp 9+", gap)
        self.assertTrue(any(k.endswith("under") for k in gap), gap.keys())
        for c in gap.values(): self.assertIn("roi", c)


class Seasons(unittest.TestCase):
    def test_season_split(self):
        self.assertEqual(H.season_split("2023-24")("en.1"), {"season": ("2023-24", "2022-23")})

    def test_replay_split_stands_in_for_tune_splits_and_restores_it(self):
        seen = {}
        def fake_load(cache):
            seen["splits"] = tune.splits("en.1"); return {}
        key = ("en.1", "2023-11-04", "A", "B")
        with mock.patch.object(H.tune, "load", fake_load), mock.patch.object(H.tune, "lambdas", lambda *a, **k: []), \
                mock.patch.object(H.O, "model_probs", lambda rows: {key: (0.70, 0.18, 0.12)}), \
                mock.patch.object(H.O, "_get", lambda url, log=None: f"fetched {url}"), \
                mock.patch.object(H.O, "parse", lambda text: [price_row(date="2023-11-04")] if "2324" in text and "E0" in text else []), \
                mock.patch.object(H.O, "match", lambda prices, fixtures: {key: prices[0]} if prices else {}), \
                mock.patch.object(H.time, "sleep", lambda s: None):
            saved = tune.splits
            res = H.replay_split("season", H.season_split("2023-24"), [])
            self.assertIs(tune.splits, saved)                       # restored
        self.assertEqual(seen["splits"], {"season": ("2023-24", "2022-23")})
        self.assertEqual(res["season"], "2023-24"); self.assertEqual(res["candidates"], 1)
        self.assertEqual(res["legs"][0]["opp"], 11.0)
        for k in ("cuts", "trebles", "card", "cardRule5", "cardUncapped", "cardOpp7", "lopsided", "byGap"): self.assertIn(k, res)


if __name__ == "__main__":
    unittest.main()
