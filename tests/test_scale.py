"""Scale (scale.py, 15 Nov 2026): the straight-sets reading of a tennis
score, the record's band rate, the day's nested groups, what is frozen at a
start, and how picks and groups are graded."""
import os, sys, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import scale as S

NOW = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)


def pick(key, start, chance, price=None, sport="football", conf=0.8, **kw):
    p = {"key": key, "sport": sport, "start": start, "home": "H" + key, "away": "A" + key, "pick": "H" + key,
         "side": "h", "conf": conf, "chance": chance, "price": price, "bet": S.BETS[sport]}
    p.update(kw)
    return p


class StraightSets(unittest.TestCase):
    def test_two_sets_to_love(self):
        self.assertIs(S.straight_sets({"ok": True, "note": "(3) A (CAN) bt B (USA) 6-3 6-3"}), True)

    def test_tie_break_set_counts_as_a_set(self):
        self.assertIs(S.straight_sets({"ok": True, "note": "A bt B 7-6(5) 6-4"}), True)
        self.assertIs(S.straight_sets({"ok": True, "note": "A bt B 7-6 (7-5) 6-4"}), True)

    def test_a_dropped_set(self):
        self.assertIs(S.straight_sets({"ok": True, "note": "A bt B 6-3 4-6 6-2"}), False)

    def test_best_of_five(self):
        self.assertIs(S.straight_sets({"ok": True, "note": "A bt B 6-3 6-4 7-5"}), True)
        self.assertIs(S.straight_sets({"ok": True, "note": "A bt B 6-3 6-7(4) 6-4 6-2"}), False)

    def test_retirement_void_and_no_score_cannot_be_said(self):
        self.assertIsNone(S.straight_sets({"ok": True, "retired": True, "note": "A bt B 6-3 2-0"}))
        self.assertIsNone(S.straight_sets({"void": True, "note": "walkover"}))
        self.assertIsNone(S.straight_sets({"ok": True, "note": "A bt B"}))
        self.assertIsNone(S.straight_sets({"ok": True, "note": "A bt B 6-3"}))

    def test_seedings_are_not_read_as_sets(self):
        self.assertIs(S.straight_sets({"ok": True, "note": "(12) A (USA) bt (3) B (GBR) 6-4 6-4"}), True)


class TennisRates(unittest.TestCase):
    def rec(self):
        g = []
        for i in range(40):      # 80-85%: 40 picks, 30 won, 20 in straight sets
            ok = i < 30
            g.append({"confidence": 0.82, "ok": ok, "note": "A bt B 6-3 6-3" if i < 20 else "A bt B 6-3 3-6 6-3"})
        for i in range(10):      # 90%+: too few for its own band
            g.append({"confidence": 0.93, "ok": True, "note": "A bt B 6-1 6-1"})
        g.append({"confidence": 0.82, "ok": True, "retired": True, "note": "A bt B 6-3 1-0"})
        g.append({"confidence": 0.70, "ok": True, "note": "A bt B 6-3 6-3"})
        return {"graded": g}

    def test_bands_and_pool(self):
        bands, pool = S.tennis_rates(self.rec())
        b = [x for x in bands if x["from"] == 0.80][0]
        self.assertEqual((b["n"], b["won"], b["straight"]), (40, 30, 20))
        self.assertEqual((pool["n"], pool["straight"]), (50, 30))      # the retirement and the 70% pick are out

    def test_chance_is_the_band_rate_or_the_pool_when_the_band_is_thin(self):
        rates = S.tennis_rates(self.rec())
        self.assertEqual(S.tennis_chance(0.82, rates), (0.5, 20, 40))
        self.assertEqual(S.tennis_chance(0.93, rates), (0.6, 30, 50))

    def test_no_record_no_chance(self):
        self.assertEqual(S.tennis_chance(0.9, S.tennis_rates({}))[0], None)


class Groups(unittest.TestCase):
    def picks(self):
        return [pick("a", "2026-11-15T15:00:00Z", 0.30, 3.0), pick("b", "2026-11-15T16:00:00Z", 0.40, 2.4),
                pick("c", "2026-11-15T17:00:00Z", 0.35, 2.6), pick("d", "2026-11-15T18:00:00Z", 0.25, 3.6),
                pick("e", "2026-11-15T09:00:00Z", 0.60, 1.6)]      # e has started

    def test_nested_from_the_most_likely_and_never_a_started_leg(self):
        gs = S.build_groups(self.picks(), NOW)
        self.assertEqual([g["kind"] for g in gs], [3, 4])           # four still to start: no fivefold
        self.assertEqual(gs[0]["legs"], ["b", "c", "a"])
        self.assertEqual(gs[1]["legs"], ["b", "c", "a", "d"])
        self.assertAlmostEqual(gs[0]["chance"], 0.042, places=4)
        self.assertEqual(gs[0]["price"], round(2.4 * 2.6 * 3.0, 2))
        self.assertEqual(gs[0]["first"], "2026-11-15T15:00:00Z")

    def test_two_picks_make_no_group(self):
        self.assertEqual(S.build_groups(self.picks()[:2], NOW), [])

    def test_a_group_with_an_unpriced_leg_has_no_price(self):
        ps = self.picks()[:3] + [pick("t", "2026-11-15T19:00:00Z", 0.66, None, sport="tennis")]
        gs = S.build_groups(ps, NOW)
        self.assertEqual(gs[0]["legs"][0], "t")
        self.assertIsNone(gs[0]["price"])


class MergeDay(unittest.TestCase):
    def test_a_started_pick_keeps_its_first_copy_and_an_open_one_is_replaced(self):
        old = {"picks": [pick("e", "2026-11-15T09:00:00Z", 0.60, 1.6), pick("a", "2026-11-15T15:00:00Z", 0.30, 3.0)]}
        new = [pick("e", "2026-11-15T09:00:00Z", 0.10, 9.9), pick("a", "2026-11-15T15:00:00Z", 0.31, 3.2)]
        m = S.merge_day(old, new, [], [], NOW, "t")
        by = {p["key"]: p for p in m["picks"]}
        self.assertEqual(by["e"]["price"], 1.6)
        self.assertEqual(by["a"]["price"], 3.2)

    def test_an_open_pick_no_longer_on_the_list_is_dropped_and_a_started_one_kept(self):
        old = {"picks": [pick("e", "2026-11-15T09:00:00Z", 0.60, 1.6), pick("a", "2026-11-15T15:00:00Z", 0.30, 3.0)]}
        m = S.merge_day(old, [], [], [], NOW, "t")
        self.assertEqual([p["key"] for p in m["picks"]], ["e"])

    def test_a_group_is_frozen_once_its_first_leg_starts(self):
        frozen = {"kind": 3, "name": "Scale threefold", "legs": ["e", "a", "b"], "first": "2026-11-15T09:00:00Z", "chance": 0.07, "price": 11.5}
        opened = {"kind": 4, "name": "Scale fourfold", "legs": ["a", "b", "c", "d"], "first": "2026-11-15T15:00:00Z", "chance": 0.01, "price": 60.0}
        ps = [pick(k, "2026-11-15T15:00:00Z", 0.3, 3.0) for k in "abcd"] + [pick("e", "2026-11-15T09:00:00Z", 0.6, 1.6)]
        new3 = dict(frozen, legs=["a", "b", "c"], first="2026-11-15T15:00:00Z")
        new4 = dict(opened, price=70.0)
        m = S.merge_day({"picks": ps, "groups": [frozen, opened]}, ps, [], [new3, new4], NOW, "t")
        by = {g["kind"]: g for g in m["groups"]}
        self.assertEqual(by[3]["legs"], ["e", "a", "b"])
        self.assertEqual(by[4]["price"], 70.0)

    def test_left_off_never_lists_a_pick_that_is_on(self):
        off = [{"key": "a", "start": "2026-11-15T15:00:00Z", "comp": "X", "pick": "Ha"}, {"key": "z", "start": "2026-11-15T15:00:00Z", "comp": "X", "pick": "Hz"}]
        m = S.merge_day({}, [pick("a", "2026-11-15T15:00:00Z", 0.3, 3.0)], off, [], NOW, "t")
        self.assertEqual([o["key"] for o in m["off"]], ["z"])


class Grading(unittest.TestCase):
    def test_football_states(self):
        p = pick("a", "2026-11-14T15:00:00Z", 0.3, 3.0, league="eng.1", date="2026-11-14")
        res = lambda hg, ag: ({("eng.1", "Ha", "Aa"): [{"date": "2026-11-14", "result": [hg, ag], "kickoff": None}]}, {}, {})
        import markets as M
        orig = M._result_for
        M._result_for = lambda row, fb: (fb.get((row["league"], row["home"], row["away"])) or [None])[0]
        try:
            self.assertEqual(S.settle(p, res(2, 1)), ("scale", "2-1"))
            self.assertEqual(S.settle(p, res(2, 0)), ("won", "2-0"))
            self.assertEqual(S.settle(p, res(1, 1)), ("lost", "1-1"))
            self.assertEqual(S.settle(p, res(0, 1)), ("lost", "0-1"))
            self.assertEqual(S.settle(dict(p, side="a"), res(1, 3)), ("scale", "1-3"))
            self.assertEqual(S.settle(p, ({}, {}, {})), (None, None))
        finally:
            M._result_for = orig

    def test_tennis_states(self):
        p = pick("t", "2026-11-14T15:00:00Z", 0.66, None, sport="tennis", id="77", date="2026-11-14")
        st = lambda g: S.settle(p, ({}, {"77": g}, {}))[0]
        self.assertEqual(st({"ok": True, "note": "A bt B 6-3 6-3"}), "scale")
        self.assertEqual(st({"ok": True, "note": "A bt B 6-3 3-6 6-3"}), "won")
        self.assertEqual(st({"ok": False, "note": "B bt A 6-3 6-3"}), "lost")
        self.assertEqual(st({"ok": True, "retired": True, "note": "A bt B 6-3 1-0"}), "void")
        self.assertEqual(st({"void": True}), "void")

    def group(self, states, prices=(3.0, 2.0, 2.5)):
        legs = {k: {"state": s, "price": pr} for k, s, pr in zip("abc", states, prices)}
        g = {"legs": list("abc"), "price": round(3.0 * 2.0 * 2.5, 2) if all(prices) else None}
        return S.grade_group(g, legs)

    def test_group_won_only_when_every_leg_landed_the_scale(self):
        self.assertEqual(self.group(["scale", "scale", "scale"]), {"state": "won", "ret": 15.0})
        self.assertEqual(self.group(["scale", "won", "scale"]), {"state": "lost", "ret": 0.0})

    def test_group_lost_as_soon_as_one_leg_misses_and_pending_otherwise(self):
        self.assertEqual(self.group(["lost", None, None])["state"], "lost")
        self.assertEqual(self.group(["scale", None, "scale"])["state"], "pending")

    def test_a_void_leg_is_settled_on_the_rest(self):
        self.assertEqual(self.group(["scale", "void", "scale"]), {"state": "won", "ret": 7.5})
        self.assertEqual(self.group(["void", "void", "void"]), {"state": "void"})

    def test_an_unpriced_group_is_graded_without_a_return(self):
        self.assertEqual(self.group(["scale", "scale", "scale"], (3.0, None, 2.5)), {"state": "won"})
        self.assertEqual(self.group(["scale", "lost", "scale"], (3.0, None, 2.5)), {"state": "lost"})

    def test_tally(self):
        t = S._tally()
        for st, pr in (("scale", 3.0), ("won", 2.0), ("lost", None), ("void", 2.0), (None, 2.0)):
            S._add(t, {"state": st, "price": pr})
        d = S._done(t)
        self.assertEqual((d["n"], d["won"], d["scale"], d["lost"], d["void"], d["priced"]), (3, 2, 1, 1, 1, 2))
        self.assertEqual(d["ret"], 0.5)


class Wiring(unittest.TestCase):
    """The tab, its data file and the deploy steps stay in step."""
    def test_the_page_has_the_tab_and_loads_its_data(self):
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        html = open(os.path.join(here, "index.html"), encoding="utf-8").read()
        for bit in ('<button data-view="scale"', '<section id="scale" hidden>', '<script src="scale.js"></script>',
                    'if(v === "scale") renderScale();', "window.__SCALE__"):
            self.assertIn(bit, html)

    def test_deploy_runs_archives_and_publishes_it(self):
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        yml = open(os.path.join(here, ".github", "workflows", "deploy.yml"), encoding="utf-8").read()
        self.assertIn("python3 scale.py", yml)
        self.assertIn("cp scale.js scale.json _site/", yml)
        self.assertGreater(yml.index("python3 scale.py"), yml.index("python3 markets.py"))
        self.assertIn("markets-record.json scale-archive slip-archive 2>/dev/null", yml)


if __name__ == "__main__":
    unittest.main()
