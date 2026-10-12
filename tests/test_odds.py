"""odds.py: price parsing, margin removal, fixture matching, the value gate.
Prices never feed a model; these guard the display and the advisory report."""
import os, sys, unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import odds as O

HEAD = "Div,Date,Time,HomeTeam,AwayTeam,FTR,AvgH,AvgD,AvgA,MaxH,MaxD,MaxA,PSCH,PSCD,PSCA\n"


class Parse(unittest.TestCase):
    def test_good_row(self):
        rows = O.parse(HEAD + "E0,15/08/2025,15:00,Arsenal,Wolves,H,1.5,4.0,6.0,1.6,4.2,6.5,1.45,4.1,6.2\n")
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["code"], r["date"], r["result"]), ("en.1", "2025-08-15", 0))
        self.assertEqual(r["avg"], [1.5, 4.0, 6.0])
        self.assertEqual(r["close"], [1.45, 4.1, 6.2])

    def test_bom_two_digit_year_and_result_codes(self):
        rows = O.parse("﻿" + HEAD + "D1,01/09/25,,A,B,A,2,3,4,,,,,,\nD1,02/09/25,,C,D,,2,3,4,,,,,,\n")
        self.assertEqual([r["date"] for r in rows], ["2025-09-01", "2025-09-02"])
        self.assertEqual([r["result"] for r in rows], [2, None])
        self.assertIsNone(rows[0]["max"])
        self.assertIsNone(rows[0]["time"])

    def test_dropped_rows(self):
        bad = ("XX,15/08/2025,,A,B,H,2,3,4,,,,,,\n"       # unknown division
               "E0,not-a-date,,A,B,H,2,3,4,,,,,,\n"       # bad date
               "E0,15/08/2025,,,B,H,2,3,4,,,,,,\n"        # no home side
               "E0,15/08/2025,,A,B,H,2,,4,,,,,,\n"        # missing draw price
               "E0,15/08/2025,,A,B,H,1.0,3,4,,,,,,\n")   # price must exceed 1
        self.assertEqual(O.parse(HEAD + bad), [])
        self.assertEqual(O.parse(""), [])
        self.assertEqual(O.parse(None), [])

    def test_close_falls_back_to_average_close(self):
        t = "Div,Date,HomeTeam,AwayTeam,AvgH,AvgD,AvgA,AvgCH,AvgCD,AvgCA\nE0,15/08/2025,A,B,2,3,4,1.9,3.1,4.2\n"
        self.assertEqual(O.parse(t)[0]["close"], [1.9, 3.1, 4.2])

    def test_live_file_uses_home_away_columns(self):
        t = "Div,Date,Home,Away,AvgH,AvgD,AvgA\nE0,15/08/2025,A,B,2,3,4\n"
        r = O.parse(t)[0]
        self.assertEqual((r["home"], r["away"]), ("A", "B"))


class Prices(unittest.TestCase):
    def test_fair_sums_to_one_and_removes_margin(self):
        p = O.fair([2.0, 4.0, 4.0])
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertAlmostEqual(p[0], 0.5)
        self.assertAlmostEqual(O.fair([3.0, 3.0, 3.0])[1], 1 / 3)

    def test_best_caps_stale_max(self):
        row = {"avg": [2.0, 3.0, 4.0], "max": [2.4, 3.9, 4.0]}
        self.assertEqual(O.best(row), [2.4, 3.0, 4.0])   # 3.9 > 3.0 * 1.25
        self.assertEqual(O.best({"avg": [2.0, 3.0, 4.0]}), [2.0, 3.0, 4.0])
        # exactly at the cap is accepted
        self.assertEqual(O.best({"avg": [2.0, 3.0, 4.0], "max": [2.5, 3.0, 4.0]})[0], 2.5)

    def test_market_block(self):
        r = {"avg": [2.0, 4.0, 4.0]}
        b = O.market_block(r, [0.6, 0.2, 0.2])
        self.assertEqual(b["p"], [0.5, 0.25, 0.25])
        self.assertEqual(b["ev"], [0.2, -0.2, -0.2])
        self.assertNotIn("ev", O.market_block(r))


class Names(unittest.TestCase):
    def test_aliases_and_abbreviations(self):
        self.assertGreaterEqual(O.name_sim("Sheffield Weds", "Sheffield Wednesday"), 0.9)
        self.assertGreaterEqual(O.name_sim("Ath Madrid", "Atletico Madrid"), 0.9)
        self.assertGreaterEqual(O.name_sim("Wolves", "Wolverhampton Wanderers"), 0.9)

    def test_different_clubs_score_low(self):
        self.assertLess(O.name_sim("Arsenal", "Chelsea"), 0.5)
        self.assertLess(O.name_sim("Man City", "Man United"), 0.9)

    def test_empty_name(self):
        self.assertEqual(O.name_sim("", "Arsenal"), 0.0)


class Match(unittest.TestCase):
    def row(self, home, away, d="2025-08-15", code="en.1"):
        return {"code": code, "date": d, "home": home, "away": away}

    def test_matches_and_tolerates_a_day(self):
        fx = [("k1", "en.1", "2025-08-16", "Arsenal", "Wolverhampton Wanderers")]
        out = O.match([self.row("Arsenal", "Wolves")], fx)
        self.assertEqual(list(out), ["k1"])

    def test_wrong_competition_or_far_date_dropped(self):
        fx = [("k1", "en.1", "2025-08-15", "Arsenal", "Chelsea")]
        self.assertEqual(O.match([self.row("Arsenal", "Chelsea", code="de.1")], fx), {})
        self.assertEqual(O.match([self.row("Arsenal", "Chelsea", d="2025-08-20")], fx), {})

    def test_poor_name_fit_dropped(self):
        fx = [("k1", "en.1", "2025-08-15", "Arsenal", "Chelsea")]
        self.assertEqual(O.match([self.row("Arsenal", "Everton")], fx), {})

    def test_ambiguous_dropped(self):
        fx = [("k1", "en.1", "2025-08-15", "Sheffield United", "Leeds United"),
              ("k2", "en.1", "2025-08-15", "Sheffield United", "Leeds United")]
        self.assertEqual(O.match([self.row("Sheffield United", "Leeds United")], fx), {})

    def test_fixture_used_once(self):
        fx = [("k1", "en.1", "2025-08-15", "Arsenal", "Chelsea")]
        a, b = self.row("Arsenal", "Chelsea"), self.row("Arsenal", "Chelsea")
        a["tag"], b["tag"] = 1, 2
        self.assertEqual(O.match([a, b], fx)["k1"]["tag"], 1)


class Evaluate(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(O.evaluate([]), {"n": 0})

    def test_value_gate_and_roi(self):
        r = {"avg": [2.0, 3.5, 4.0], "max": None, "result": 0, "close": [1.8, 3.6, 4.5]}
        # pick home at 0.6: edge 0.6*2-1 = 0.2 >= EDGE -> a bet that wins
        out = O.evaluate([([0.6, 0.25, 0.15], r)])
        self.assertEqual((out["n"], out["bets"], out["clvBets"]), (1, 1, 1))
        self.assertEqual(out["roi"], 1.0)
        self.assertGreater(out["clv"], 0)

    def test_no_bet_below_pick_min_or_edge(self):
        r = {"avg": [2.0, 3.5, 4.0], "result": 0}
        self.assertEqual(O.evaluate([([0.5, 0.3, 0.2], r)])["bets"], 0)     # < PICK_MIN
        thin = {"avg": [1.8, 3.5, 4.0], "result": 0}                         # 0.56*1.8-1 = 0.008 < EDGE
        self.assertEqual(O.evaluate([([0.56, 0.24, 0.2], thin)])["bets"], 0)

    def test_losing_bet(self):
        r = {"avg": [2.0, 3.5, 4.0], "result": 2}
        out = O.evaluate([([0.6, 0.25, 0.15], r)])
        self.assertEqual((out["bets"], out["roi"], out["clvBets"]), (1, -1.0, 0))


class Boot(unittest.TestCase):
    def test_empty_and_deterministic(self):
        self.assertEqual(O._boot([]), (0.0, 1.0))
        self.assertEqual(O._boot([0.1, -0.2, 0.3]), O._boot([0.1, -0.2, 0.3]))

    def test_all_positive_is_never_worse(self):
        self.assertEqual(O._boot([0.5] * 20)[1], 0.0)
        self.assertEqual(O._boot([-0.5] * 20)[1], 1.0)


class Report(unittest.TestCase):
    def stamp(self, **kw):
        return (datetime.now(timezone.utc) - timedelta(**kw)).isoformat()

    def test_stale_rules(self):
        self.assertTrue(O.report_is_stale(None))
        self.assertTrue(O.report_is_stale({}))
        self.assertTrue(O.report_is_stale({"generated": "garbage"}))
        self.assertFalse(O.report_is_stale({"generated": self.stamp(days=3)}))
        self.assertTrue(O.report_is_stale({"generated": self.stamp(days=8)}))

    def test_failed_run_retried_next_day(self):
        self.assertTrue(O.report_is_stale({"generated": self.stamp(days=2), "failed": True}))
        self.assertFalse(O.report_is_stale({"generated": self.stamp(hours=2), "failed": True}))

    def test_naive_timestamp_read_as_utc(self):
        naive = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None).isoformat()
        self.assertFalse(O.report_is_stale({"generated": naive}))

    def test_yy(self):
        self.assertEqual(O._yy("2025-26"), "2526")


if __name__ == "__main__":
    unittest.main()
