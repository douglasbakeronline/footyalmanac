"""sports.py: Elo, calibration, list threshold, ESPN event parsing. Standard library only, no network."""
import os, sys, math, random, unittest
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports as S

P = {"k": 20, "hfa": 50, "regress": 0.33, "mov": 1}
FEED = {"path": "football/nfl", "label": "NFL", "pool": "nfl", "skip": (1, 4)}


def game(h, a, hs, as_, when="2025-09-07T17:00Z", pool="nfl", neutral=False):
    return {"id": f"{h}{a}{when}", "when": when, "pool": pool, "h": h, "a": a, "hn": h.upper(), "an": a.upper(),
            "neutral": neutral, "final": True, "hs": hs, "as": as_}


def band(t, n, hit):
    return {"from": t, "n": n, "hit": hit}


def event(hs="24", as_="17", completed=True, name="STATUS_FINAL", season=2, neutral=False):
    return {"id": "9", "date": "2025-09-07T17:00Z", "season": {"type": season},
            "competitions": [{"date": "2025-09-07T17:00Z", "neutralSite": neutral,
                              "status": {"type": {"completed": completed, "name": name, "state": "post"}},
                              "competitors": [
                                  {"homeAway": "away", "score": as_, "team": {"id": "2", "displayName": "Away"}},
                                  {"homeAway": "home", "score": hs, "team": {"id": "1", "displayName": "Home"}}]}]}


class Probability(unittest.TestCase):
    def test_even_teams_neutral_is_half(self):
        self.assertAlmostEqual(S.p_home(1500, 1500, 50, True), 0.5)

    def test_home_advantage_only_when_not_neutral(self):
        self.assertGreater(S.p_home(1500, 1500, 50, False), 0.5)
        self.assertAlmostEqual(S.p_home(1600, 1500, 50, True), 1 - S.p_home(1500, 1600, 50, True))

    def test_tiers(self):
        self.assertEqual([S.tier_of(x) for x in (0.9, 0.70, 0.69, 0.62, 0.55, 0.5)],
                         ["Strong", "Strong", "Firm", "Firm", "Lean", "No read"])


class EloTests(unittest.TestCase):
    def test_zero_sum_and_winner_gains(self):
        elo = S.Elo(P)
        elo.update(game("a", "b", 20, 10))
        ra, rb = elo.r[("nfl", "a")][0], elo.r[("nfl", "b")][0]
        self.assertGreater(ra, 1500)
        self.assertAlmostEqual(ra + rb, 3000)

    def test_draw_with_no_edge_moves_only_by_home_advantage(self):
        elo = S.Elo(dict(P, hfa=0))
        elo.update(game("a", "b", 10, 10))
        self.assertAlmostEqual(elo.r[("nfl", "a")][0], 1500)

    def test_margin_off_gives_flat_k_step(self):
        elo = S.Elo(dict(P, mov=0, hfa=0))
        elo.update(game("a", "b", 50, 0))
        self.assertAlmostEqual(elo.r[("nfl", "a")][0], 1510)

    def test_bigger_margin_moves_more(self):
        a, b = S.Elo(P), S.Elo(P)
        a.update(game("a", "b", 21, 20))
        b.update(game("a", "b", 41, 20))
        self.assertGreater(b.r[("nfl", "a")][0], a.r[("nfl", "a")][0])

    def test_offseason_regresses_toward_mean_once(self):
        elo = S.Elo(P)
        elo.update(game("a", "b", 30, 0, when="2024-09-01T17:00Z"))
        before = elo.r[("nfl", "a")][0]
        e = elo.get("nfl", "a", "2025-09-07T17:00Z")
        self.assertAlmostEqual(e[0], 1500 + (before - 1500) * 0.67)
        self.assertAlmostEqual(elo.get("nfl", "a", "2025-09-08T17:00Z")[0], e[0])

    def test_repeat_predictions_after_a_break_regress_once(self):
        # Two upcoming games for one team in the opening week must not regress it twice.
        elo = S.Elo(P)
        elo.update(game("a", "b", 30, 0, when="2024-09-01T17:00Z"))
        before = elo.r[("nfl", "a")][0]
        elo.predict(game("a", "c", 0, 0, when="2025-04-01T17:00Z"))
        elo.predict(game("a", "d", 0, 0, when="2025-04-03T17:00Z"))
        self.assertAlmostEqual(elo.r[("nfl", "a")][0], 1500 + (before - 1500) * 0.67)

    def test_short_gap_does_not_regress(self):
        elo = S.Elo(P)
        elo.update(game("a", "b", 30, 0, when="2025-09-01T17:00Z"))
        before = elo.r[("nfl", "a")][0]
        self.assertEqual(elo.get("nfl", "a", "2025-09-08T17:00Z")[0], before)

    def test_pools_are_separate(self):
        elo = S.Elo(P)
        elo.update(game("a", "b", 30, 0, pool="club"))
        self.assertNotIn(("intl", "a"), elo.r)

    def test_replay_warm_flag_and_prediction_before_update(self):
        games = [game("a", "b", 20, 10, when=f"2025-09-{i + 1:02d}T17:00Z") for i in range(S.MIN_GAMES + 1)]
        _, out = S.replay(games, P)
        self.assertAlmostEqual(out[0][1], S.p_home(1500, 1500, 50, False))
        self.assertFalse(out[0][2])
        self.assertFalse(out[S.MIN_GAMES - 1][2])
        self.assertTrue(out[S.MIN_GAMES][2])


class Calibration(unittest.TestCase):
    def test_none_is_identity_and_identity_line(self):
        self.assertEqual(S.calibrate(0.7, None), 0.7)
        self.assertAlmostEqual(S.calibrate(0.7, {"a": 0, "b": 1}), 0.7)

    def test_extremes_do_not_overflow(self):
        for p in (0.0, 1.0):
            self.assertTrue(0 <= S.calibrate(p, {"a": 5, "b": 50}) <= 1)

    def test_fit_recovers_a_known_line(self):
        rng = random.Random(1)
        preds = []
        for i in range(4000):
            raw = rng.uniform(0.2, 0.8)
            true = S.calibrate(raw, {"a": 0.1, "b": 0.6})
            home = rng.random() < true
            g = game("a", "b", 2 if home else 1, 1 if home else 2, when="2025-10-01T17:00Z")
            preds.append((g, raw, True))
        c = S.fit_calibration(preds, (date(2025, 7, 1), None))
        self.assertAlmostEqual(c["a"], 0.1, delta=0.1)
        self.assertAlmostEqual(c["b"], 0.6, delta=0.1)

    def test_fit_ignores_cold_draws_and_other_windows(self):
        g = game("a", "b", 1, 1, when="2025-10-01T17:00Z")
        self.assertEqual(S.fit_calibration([(g, 0.6, True)], (date(2025, 7, 1), None)), {"a": 0.0, "b": 1.0})
        w = game("a", "b", 2, 1, when="2023-10-01T17:00Z")
        self.assertEqual(S.fit_calibration([(w, 0.6, True)], (date(2025, 7, 1), None)), {"a": 0.0, "b": 1.0})


class Losses(unittest.TestCase):
    WIN = (date(2025, 7, 1), None)

    def test_window_is_half_open_and_cold_skipped(self):
        win = (date(2025, 7, 1), date(2025, 9, 1))
        ins = game("a", "b", 2, 1, when="2025-08-31T10:00Z")
        edge = game("a", "b", 2, 1, when="2025-09-01T10:00Z")
        self.assertTrue(S.in_window(ins, win))
        self.assertFalse(S.in_window(edge, win))
        ll, rows = S.losses([(ins, 0.7, False), (edge, 0.7, True)], win)
        self.assertEqual((ll, rows), ([], []))

    def test_draw_is_a_miss_with_no_loss(self):
        ll, rows = S.losses([(game("a", "b", 1, 1), 0.7, True)], self.WIN)
        self.assertEqual(ll, [])
        self.assertFalse(rows[0][1])

    def test_away_pick_hits_and_loss_value(self):
        ll, rows = S.losses([(game("a", "b", 0, 3), 0.25, True)], self.WIN)
        self.assertAlmostEqual(rows[0][0], 0.75)
        self.assertTrue(rows[0][1])
        self.assertAlmostEqual(ll[0], -math.log(0.75))

    def test_paired_detects_a_clear_difference(self):
        a = [0.5] * 100
        b = [0.7] * 100
        mu, sd, pw = S.paired(a, b)
        self.assertAlmostEqual(mu, -0.2)
        self.assertEqual(pw, 0.0)

    def test_bands_cumulative(self):
        rows = [(0.9, True, None), (0.72, False, None), (0.56, True, None)]
        b = {x["from"]: x for x in S.bands(rows)}
        self.assertEqual(b[0.55]["n"], 3)
        self.assertEqual(b[0.70]["n"], 2)
        self.assertEqual(b[0.70]["hit"], 0.5)
        self.assertEqual(b[0.85]["n"], 1)
        self.assertNotIn(0.85, {x["from"] for x in S.bands([(0.8, True, None)])})


class ListThreshold(unittest.TestCase):
    def test_lowest_clearing_threshold(self):
        w = [[band(0.55, 100, 0.70), band(0.60, 80, 0.75), band(0.65, 60, 0.82), band(0.70, 40, 0.9),
              band(0.75, 30, 0.9), band(0.80, 30, 0.9), band(0.85, 30, 0.9)]]
        self.assertEqual(S.list_threshold(w), 0.65)

    def test_every_big_window_must_clear(self):
        good = [band(t, 40, 0.9) for t in S.LIST_THRESHOLDS]
        bad = [band(t, 40, 0.7) for t in S.LIST_THRESHOLDS]
        self.assertIsNone(S.list_threshold([good, bad]))

    def test_small_windows_do_not_count_but_one_big_needed(self):
        small = [band(t, 10, 0.5) for t in S.LIST_THRESHOLDS]
        big = [band(t, 40, 0.9) for t in S.LIST_THRESHOLDS]
        self.assertEqual(S.list_threshold([small, big]), 0.55)
        self.assertIsNone(S.list_threshold([small]))

    def test_missing_band_fails_that_threshold(self):
        w = [[band(0.55, 40, 0.5), band(0.60, 40, 0.9)]]
        self.assertEqual(S.list_threshold(w), 0.60)
        self.assertIsNone(S.list_threshold([[band(0.55, 40, 0.5)]]))
        self.assertIsNone(S.list_threshold([]))

    def test_accuracy_for_picks_highest_band_at_or_below(self):
        bs = [band(0.55, 100, 0.6), band(0.65, 50, 0.7), band(0.75, 20, 0.8)]
        self.assertEqual(S.accuracy_for(0.70, bs), {"from": 0.65, "hit": 0.7, "n": 50})
        self.assertEqual(S.accuracy_for(0.75, bs)["from"], 0.75)
        self.assertIsNone(S.accuracy_for(0.54, bs))
        self.assertIsNone(S.accuracy_for(0.9, None))


class Parsing(unittest.TestCase):
    def test_final_game(self):
        g = S._game(event(), FEED)
        self.assertEqual((g["h"], g["a"], g["hs"], g["as"], g["final"]), ("1", "2", 24, 17, True))
        self.assertEqual(g["hn"], "Home")

    def test_skipped_season_type_and_missing_sides(self):
        self.assertIsNone(S._game(event(season=1), FEED))
        ev = event()
        ev["competitions"][0]["competitors"].pop()
        self.assertIsNone(S._game(ev, FEED))
        ev = event()
        ev["competitions"][0]["competitors"][0]["team"] = {}
        self.assertIsNone(S._game(ev, FEED))

    def test_cancelled_postponed_and_bad_score_are_not_final(self):
        for name in ("STATUS_CANCELED", "STATUS_POSTPONED"):
            self.assertFalse(S._game(event(name=name), FEED)["final"])
        g = S._game(event(hs=None), FEED)
        self.assertFalse(g["final"])
        self.assertIsNone(g["hs"])
        self.assertFalse(S._game(event(completed=False), FEED)["final"])

    def test_same_game_keeps_doubleheaders_apart(self):
        a = game("a", "b", 1, 0, when="2025-07-01T17:00Z")
        b = dict(a, when="2025-07-01T23:00Z")
        self.assertNotEqual(S._same_game(a), S._same_game(b))
        self.assertEqual(S._same_game(a), S._same_game(dict(a, id="other")))


class Summaries(unittest.TestCase):
    def setUp(self):
        self.games = [game("a", "b", 3, 1, when="2024-01-01T10:00Z"),
                      game("b", "a", 2, 2, when="2025-09-01T10:00Z"),
                      game("a", "c", 0, 1, when="2025-09-08T10:00Z"),
                      game("c", "a", 5, 6, when="2025-09-15T10:00Z")]

    def test_result_perspective(self):
        self.assertEqual(S._result(self.games[2], "a"), ("L", 0, 1))
        self.assertEqual(S._result(self.games[2], "c"), ("W", 1, 0))
        self.assertEqual(S._result(self.games[1], "a")[0], "D")

    def test_form_newest_first_and_limited(self):
        f = S.form(self.games, "a", n=2)
        self.assertEqual([x["date"] for x in f], ["2025-09-15", "2025-09-08"])
        self.assertEqual(f[0]["opp"], "C")
        self.assertFalse(f[0]["home"])
        self.assertEqual(f[0]["score"], "6-5")

    def test_record_resets_after_offseason(self):
        self.assertEqual(S.record(self.games, "a"), {"w": 1, "l": 1, "d": 1})

    def test_head_to_head(self):
        h = S.head_to_head(self.games, "a", "c", n=1)
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["date"], "2025-09-15")
        self.assertEqual(len(S.head_to_head(self.games, "a", "b")), 2)


if __name__ == "__main__":
    unittest.main()
