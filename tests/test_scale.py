"""Scale (scale.py, 15 Nov 2026): the straight-sets reading of a tennis
score, the record's band rate, the day's nested groups, what is frozen at a
start, and how picks and groups are graded."""
import os, sys, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import scale as S

NOW = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)


def pick(key, start, chance, price=None, sport="football", conf=0.8, **kw):
    p = {"key": key, "sport": sport, "tier": "list", "start": start, "home": "H" + key, "away": "A" + key, "pick": "H" + key,
         "side": "h", "conf": conf, "chance": chance, "price": price, "bet": S.SPORTS[sport]["bet"]}
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


class Rates(unittest.TestCase):
    def trec(self):
        g = []
        for i in range(40):      # 80-85%: 40 picks, 30 won, 20 in straight sets
            ok = i < 30
            g.append({"confidence": 0.82, "ok": ok, "note": "A bt B 6-3 6-3" if i < 20 else "A bt B 6-3 3-6 6-3"})
        for i in range(10):      # 90%+: too few for its own band
            g.append({"confidence": 0.93, "ok": True, "note": "A bt B 6-1 6-1"})
        g.append({"confidence": 0.82, "ok": True, "retired": True, "note": "A bt B 6-3 1-0"})
        g.append({"confidence": 0.50, "ok": True, "note": "A bt B 6-3 6-3"})
        return {"graded": g}

    def test_tennis_sample_leaves_out_retirements_and_picks_under_the_floor(self):
        t = S.samples(self.trec(), {})["tennis"]
        self.assertEqual(len(t), 50)
        self.assertEqual(sum(1 for x in t if x[2]), 30)

    def test_chance_is_the_narrowest_band_with_enough_picks(self):
        t = S.samples(self.trec(), {})["tennis"]
        self.assertEqual(S.band_rate(0.82, t), (0.5, 20, 40))       # its own band holds 40
        self.assertEqual(S.band_rate(0.93, t), (0.6, 30, 50))       # 90%+ holds 10: widened to 80%+
        self.assertEqual(S.band_rate(0.60, t), (0.6, 30, 50))       # nothing near it: every pick at the floor or better

    def test_no_record_no_chance(self):
        self.assertEqual(S.band_rate(0.9, [])[0], None)

    def test_margin_sample(self):
        sg = {"graded": [
            {"sport": "nba", "confidence": 0.8, "home": "A", "away": "B", "pick": "A", "score": [110, 100]},      # by 10: landed
            {"sport": "nba", "confidence": 0.8, "home": "A", "away": "B", "pick": "B", "score": [100, 109]},      # by 9: won only
            {"sport": "nba", "confidence": 0.8, "home": "A", "away": "B", "pick": "A", "score": [90, 100]},       # lost
            {"sport": "nba", "confidence": 0.8, "home": "A", "away": "B", "pick": "A", "score": [1, 0], "void": True},
            {"sport": "nfl", "confidence": 0.7, "home": "A", "away": "B", "pick": "A", "score": [27, 20]},        # by 7: landed
            {"sport": "ncaab", "confidence": 0.9, "home": "A", "away": "B", "pick": "A", "score": [90, 60]},      # not a Scale sport
        ]}
        s = S.samples({}, sg)
        self.assertEqual(s["nba"], [(0.8, True, True), (0.8, True, False), (0.8, False, False)])
        self.assertEqual(s["nfl"], [(0.7, True, True)])
        self.assertNotIn("ncaab", s)


class Choose(unittest.TestCase):
    def cands(self, n_list, n_res, n_else):
        out = []
        for t, n in (("list", n_list), ("reserve", n_res), ("else", n_else)):
            for i in range(n):
                out.append(pick(f"{t}{i}", "2026-11-15T18:00:00Z", 0.5 - i / 100, tier=t))
        return out

    def test_everything_else_only_tops_the_day_up_to_the_target(self):
        got = S.choose(self.cands(2, 3, 12), {}, NOW)
        self.assertEqual(len(got), S.TARGET)
        self.assertEqual([p["key"] for p in got if p["tier"] == "else"], ["else0", "else1", "else2", "else3", "else4"])

    def test_a_full_day_takes_nothing_from_everything_else(self):
        got = S.choose(self.cands(6, 9, 12), {}, NOW)
        self.assertEqual(len(got), 15)
        self.assertFalse([p for p in got if p["tier"] == "else"])

    def test_a_started_else_game_is_never_added_and_one_on_file_counts(self):
        c = self.cands(2, 3, 4)
        c.append(pick("late", "2026-11-15T09:00:00Z", 0.9, tier="else"))            # started, not on file: stays out
        held = pick("held", "2026-11-15T08:00:00Z", 0.4, tier="else")               # started, on file: counts to the ten
        got = S.choose(c, {"picks": [held]}, NOW)
        keys = [p["key"] for p in got]
        self.assertNotIn("late", keys)
        self.assertEqual(len([p for p in got if p["tier"] == "else"]), 4)           # 2 + 3 + held + 4 = 10

    def test_order_is_tier_then_the_scale_chance(self):
        ps = [pick("e", "2026-11-15T18:00:00Z", 0.9, tier="else"), pick("r", "2026-11-15T18:00:00Z", 0.2, tier="reserve"),
              pick("l1", "2026-11-15T18:00:00Z", 0.3), pick("l2", "2026-11-15T18:00:00Z", 0.6)]
        self.assertEqual([p["key"] for p in sorted(ps, key=S.rank)], ["l2", "l1", "r", "e"])


class Groups(unittest.TestCase):
    def picks(self):
        return [pick("a", "2026-11-15T15:00:00Z", 0.30, 3.0), pick("b", "2026-11-15T16:00:00Z", 0.40, 2.4),
                pick("c", "2026-11-15T17:00:00Z", 0.35, 2.6), pick("d", "2026-11-15T18:00:00Z", 0.25, 3.6),
                pick("e", "2026-11-15T09:00:00Z", 0.60, 1.6)]      # e has started

    def test_nested_from_the_most_likely_and_never_a_started_leg(self):
        gs = S.build_groups(self.picks(), NOW)
        self.assertEqual([g["kind"] for g in gs], [3, 4])           # four still to start: no fivefold; all football, so no second threefold
        self.assertEqual(gs[0]["legs"], ["b", "c", "a"])
        self.assertEqual(gs[1]["legs"], ["b", "c", "a", "d"])
        self.assertAlmostEqual(gs[0]["chance"], 0.042, places=4)
        self.assertEqual(gs[0]["price"], round(2.4 * 2.6 * 3.0, 2))
        self.assertEqual(gs[0]["first"], "2026-11-15T15:00:00Z")

    def test_two_picks_make_no_group(self):
        self.assertEqual(S.build_groups(self.picks()[:2], NOW), [])

    def test_a_list_pick_comes_before_a_likelier_reserve_pick(self):
        ps = self.picks()[:3] + [pick("r", "2026-11-15T19:00:00Z", 0.9, None, sport="nba", tier="reserve")]
        gs = S.build_groups(ps, NOW)
        self.assertEqual(gs[0]["legs"], ["b", "c", "a"])
        self.assertEqual(gs[1]["legs"], ["b", "c", "a", "r"])
        self.assertIsNone(gs[1]["price"])                           # one leg unpriced: no price for the group

    def test_the_football_threefold_is_priced_and_only_built_when_it_differs(self):
        ps = [pick("t", "2026-11-15T19:00:00Z", 0.66, None, sport="tennis")] + self.picks()[:4]
        gs = {g["kind"]: g for g in S.build_groups(ps, NOW)}
        self.assertEqual(gs[3]["legs"], ["t", "b", "c"])
        self.assertIsNone(gs[3]["price"])
        self.assertEqual(gs["f3"]["legs"], ["b", "c", "a"])
        self.assertEqual(gs["f3"]["price"], round(2.4 * 2.6 * 3.0, 2))
        self.assertEqual(gs["f3"]["name"], "Football threefold")


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
        st = lambda g: S.settle(p, ({}, {"77": g}, {}, {}))[0]
        self.assertEqual(st({"ok": True, "note": "A bt B 6-3 6-3"}), "scale")
        self.assertEqual(st({"ok": True, "note": "A bt B 6-3 3-6 6-3"}), "won")
        self.assertEqual(st({"ok": False, "note": "B bt A 6-3 6-3"}), "lost")
        self.assertEqual(st({"ok": True, "retired": True, "note": "A bt B 6-3 1-0"}), "void")
        self.assertEqual(st({"void": True}), "void")

    def test_margin_states(self):
        p = pick("n", "2026-11-14T23:00:00Z", 0.5, None, sport="nba", id="9")
        st = lambda g: S.settle(p, ({}, {}, {}, {("nba", "9"): g} if g else {}))
        row = lambda h, a, **kw: dict({"sport": "nba", "id": "9", "home": "Hn", "away": "An", "pick": "Hn", "score": [h, a]}, **kw)
        self.assertEqual(st(row(112, 102)), ("scale", "112-102"))
        self.assertEqual(st(row(111, 102)), ("won", "111-102"))
        self.assertEqual(st(row(100, 102)), ("lost", "100-102"))
        self.assertEqual(st(row(1, 0, void=True))[0], "void")
        self.assertEqual(st(None), (None, None))
        nfl = pick("f", "2026-11-14T23:00:00Z", 0.5, None, sport="nfl", id="9", side="a", pick="Af")
        self.assertEqual(S.settle(nfl, ({}, {}, {}, {("nfl", "9"): {"home": "Hf", "away": "Af", "pick": "Af", "score": [20, 27]}}))[0], "scale")
        self.assertEqual(S.settle(nfl, ({}, {}, {}, {("nfl", "9"): {"home": "Hf", "away": "Af", "pick": "Af", "score": [20, 26]}}))[0], "won")

    def test_a_result_from_an_earlier_meeting_is_not_this_game(self):
        # New Zealand v India, 12 and 15 Nov 2026: the second was graded 5-0 before it kicked off
        import markets as M
        res = {("friendly", "New Zealand", "India"): [("2026-11-12", {"result": [5, 0]})]}
        row = {"league": "friendly", "home": "New Zealand", "away": "India", "date": "2026-11-15"}
        self.assertIsNone(M._result_for(row, res))
        self.assertEqual(M._result_for(dict(row, date="2026-11-13"), res)["result"], [5, 0])     # a day's slip still matches
        res[("friendly", "New Zealand", "India")].append(("2026-11-15", {"result": [1, 1]}))
        self.assertEqual(M._result_for(row, res)["result"], [1, 1])

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
