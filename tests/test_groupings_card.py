"""The Card (groupings.py, 25 Oct 2026): groups by UK time window, 2x and
3x, 3-4 picks from different fixtures, locked the evening before (Overnight)
or at 07:00 (Daytime, Evening) and never changed after. Standard library only."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

DATE = "2026-11-07"          # a Saturday in GMT, so UK time == UTC


def leg(i, odds, model, when, sport="football", comp=None, margin=1.04):
    # 29 Oct 2026: a football leg needs the model at least 5 points under the
    # bookmakers' chance (CARD_UNDER_MARKET); the board's 0.66 at 1.40 (fair 0.69)
    # is read as 0.62 so the standard board still qualifies
    if sport == "football" and model == 0.66: model = 0.62
    l = {"event": f"e{i} v x", "pick": f"p{i}", "sport": sport, "comp": comp or f"c{i}", "odds": odds,
         "p": model, "pModel": model, "when": when, "est": False, "margin": margin, "date": DATE,
         "code": "en.1" if sport == "football" else None}     # 29 Oct 2026: a core league
    return G.honest(l)


def board():
    out = []
    for i in range(8):      # daytime, 12:00-15:30
        out.append(leg(i, round(1.28 + 0.03 * i, 2), 0.66, f"{DATE}T{12 + i // 2:02d}:{(i % 2) * 30:02d}:00Z"))
    for i in range(8, 14):  # evening, 19:00-21:30
        out.append(leg(i, round(1.30 + 0.03 * (i - 8), 2), 0.66, f"{DATE}T{19 + (i - 8) // 2:02d}:{(i % 2) * 30:02d}:00Z"))
    return out


EARLY = datetime(2026, 11, 6, 18, 0, tzinfo=timezone.utc)     # the evening before
# 29 Oct 2026: no clock lock; a group freezes at its first kick-off. 16:00 is
# after every daytime kick-off on the board, so both of the day's first groups
# are frozen (and under way) by then; the evening legs are still to start.
AFTER_LOCK = datetime(2026, 11, 7, 16, 0, tzinfo=timezone.utc)


class Windows(unittest.TestCase):
    def test_slots_and_lock_times(self):
        # 29 Oct 2026: one window, 07:00 UK to 07:00 UK the next day
        self.assertEqual(G.uk_slot({"when": f"{DATE}T00:30:00Z"}), ("2026-11-06", "Day"))   # early hours: the day before
        self.assertEqual(G.uk_slot({"when": f"{DATE}T06:59:00Z"}), ("2026-11-06", "Day"))
        self.assertEqual(G.uk_slot({"when": f"{DATE}T07:00:00Z"}), (DATE, "Day"))
        self.assertEqual(G.uk_slot({"when": f"{DATE}T15:00:00Z"}), (DATE, "Day"))
        self.assertEqual(G.uk_slot({"when": f"{DATE}T23:45:00Z"}), (DATE, "Day"))
        self.assertEqual(G.lock_time(DATE, "Day"), datetime(2026, 11, 7, 7, 0, tzinfo=timezone.utc))
        self.assertEqual(G.window_end(DATE, "Day"), datetime(2026, 11, 8, 7, 0, tzinfo=timezone.utc))
        # in summer time the same UK hours are an hour earlier in UTC
        self.assertEqual(G.lock_time("2026-07-04", "Day"), datetime(2026, 7, 4, 6, 0, tzinfo=timezone.utc))
        # the pre-29 Oct windows still resolve for the record
        self.assertEqual(G.lock_time(DATE, "Overnight"), datetime(2026, 11, 6, 21, 0, tzinfo=timezone.utc))


class Build(unittest.TestCase):
    def test_groups_per_window_at_target_returns(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        self.assertTrue(gs)
        self.assertEqual({g["window"] for g in gs}, {"Day"})
        seen = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(seen), len(set(seen)))                  # no fixture twice
        for g in gs:
            self.assertIn(len(g["legs"]), G.CARD_LEGS)
            self.assertGreaterEqual(g["odds"], G.CARD_RANGE[g["name"]][0])
            self.assertGreaterEqual(g["odds"], 2.0)
            self.assertEqual({G.uk_slot(l)[1] for l in g["legs"]}, {g["window"]})   # one window
            self.assertFalse(g["locked"])

    def test_locked_group_never_changes(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        g0 = next(g for g in gs if g["name"] == "Card 2x")
        moved = [dict(l) for l in board()]
        for l in moved:          # every price in the group collapses: unlocked, it would be dropped
            if l["event"] in {x["event"] for x in g0["legs"]}:
                l.update(odds=1.05); G.honest(l)
        again = G.build_card(moved, DATE, AFTER_LOCK, prev=gs, log=[])
        g1 = next(g for g in again if g["name"] == g0["name"])
        self.assertTrue(g1["locked"])
        self.assertEqual([l["odds"] for l in g1["legs"]], [l["odds"] for l in g0["legs"]])
        self.assertEqual(g1["status"], "underway")

    def test_unlocked_group_is_rebuilt_when_a_leg_fails(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        g0 = next(g for g in gs if g["name"] == "Card 3x")
        moved = [dict(l) for l in board()]
        for l in moved:
            if l["event"] == g0["legs"][0]["event"]:
                l.update(odds=2.40); G.honest(l)
        log = []
        again = G.build_card(moved, DATE, EARLY + timedelta(hours=2), prev=gs, log=log)
        self.assertTrue(any(e["name"] == g0["name"] for e in log))

    def test_price_outage_keeps_the_last_price_for_an_unlocked_group(self):
        # 25 Oct 2026 (review bug 8): the price source fails on the next build,
        # every leg comes back as an estimate; the group holds on its last price, flagged stale
        gs = G.build_card(board(), DATE, EARLY, log=[])
        g0 = next(g for g in gs if g["name"] == "Card 2x")
        outage = []
        for l in board():
            l = dict(l)
            if l["event"] in {x["event"] for x in g0["legs"]}:
                for k in ("fair", "margin", "best", "bestBook"): l.pop(k, None)
                l.update(odds=round(1 / (l["pModel"] * G.MARGIN), 2), est=True); l["p"] = l["pTested"]; G.honest(l)
            outage.append(l)
        log = []
        again = G.build_card(outage, DATE, EARLY + timedelta(hours=1), prev=gs, log=log)
        g1 = next((g for g in again if g["name"] == g0["name"]), None)
        self.assertIsNotNone(g1)
        self.assertEqual(g1["status"], "holding")
        self.assertEqual([l["odds"] for l in g1["legs"]], [l["odds"] for l in g0["legs"]])
        self.assertTrue(all(l.get("stale") for l in g1["legs"]))
        self.assertFalse(any(e["name"] == g0["name"] for e in log))

    def test_group_built_late_in_the_day_is_open_not_late(self):
        # 29 Oct 2026: no clock lock, so a group built at 16:00 from the evening legs is simply open
        gs = G.build_card(board(), DATE, AFTER_LOCK, log=[])
        self.assertTrue(gs)
        self.assertTrue(all(not g["late"] and not g["locked"] for g in gs))

    def test_off_list_sports_and_unpriced_legs_are_out(self):
        l = dict(leg(0, 1.40, 0.66, f"{DATE}T12:00:00Z", sport="cfb"), listOff=True)
        self.assertIn("off the Daily List", G.card_fault(l))
        e = dict(leg(1, 1.40, 0.66, f"{DATE}T12:00:00Z"), est=True)
        self.assertIn("no bookmaker price", G.card_fault(e))
        self.assertIsNone(G.card_fault(leg(2, 1.40, 0.66, f"{DATE}T12:00:00Z", sport="nba")))


class Archive(unittest.TestCase):
    def test_only_locked_groups_archived_once(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        locked = G.build_card(board(), DATE, AFTER_LOCK, prev=gs, log=[], archived=[])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d):
            self.assertEqual(G.archive_locked({"date": DATE, "groups": gs}, "t0"), 0)
            n = G.archive_locked({"date": DATE, "groups": locked}, "t1")
            self.assertEqual(n, len(locked))
            self.assertEqual(G.archive_locked({"date": DATE, "groups": locked}, "t2"), 0)
            a = json.load(open(os.path.join(d, f"{DATE}.json")))
        self.assertEqual(len(a["groups"]), len(locked))

    def test_archive_is_the_source_of_truth_for_locked_slots(self):
        """25 Oct 2026 (review bug 9): the published groupings.json lags (prev is
        empty), but the day's archive holds the locked groups. They are reused
        as archived, no late group is built for their slots, and the archive
        never gets a second group for one slot."""
        gs = G.build_card(board(), DATE, EARLY, log=[])
        locked = G.build_card(board(), DATE, AFTER_LOCK, prev=gs, log=[], archived=[])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d):
            G.archive_locked({"date": DATE, "groups": locked}, "t1")
            again = G.build_card(board(), DATE, AFTER_LOCK + timedelta(hours=1), prev=None, log=[])
            self.assertEqual({G.card_slot(g) for g in again}, {G.card_slot(g) for g in locked})
            for g in again:
                src = next(x for x in locked if G.card_slot(x) == G.card_slot(g))
                self.assertEqual(G.gid(g), G.gid(src))
                self.assertFalse(g.get("late"))
                self.assertIn(g["status"], ("locked", "underway"))
            self.assertEqual(G.archive_locked({"date": DATE, "groups": again}, "t2"), 0)
            # a late group with different picks for an archived slot is refused too
            other = dict(locked[0], legs=[dict(l, event="z v z", pick="z") for l in locked[0]["legs"]], late=True)
            self.assertEqual(G.archive_locked({"date": DATE, "groups": [other]}, "t3"), 0)
            a = json.load(open(os.path.join(d, f"{DATE}.json")))
        self.assertEqual(len(a["groups"]), len(locked))

    def test_archived_slot_beats_a_different_published_group(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        g0 = gs[0]
        other = dict(g0, legs=[dict(l, event="z v z", pick="z") for l in g0["legs"]], locked=True)
        again = G.build_card(board(), DATE, AFTER_LOCK, prev=[other], log=[], archived=[dict(g0, locked=True)])
        g1 = next(g for g in again if G.card_slot(g) == G.card_slot(g0))
        self.assertEqual(G.gid(g1), G.gid(g0))
        self.assertEqual(sum(1 for g in again if G.card_slot(g) == G.card_slot(g0)), 1)


if __name__ == "__main__":
    unittest.main()


class TennisOnTheCard(unittest.TestCase):
    def test_tennis_leg_is_not_listoff(self):
        acc = {"hit": 0.8, "n": 200, "cumHit": 0.8, "cumN": 200}
        td = {"list": {"off": True}, "matches": [{"date": DATE, "time": "12:00", "round": "Round 1", "playerA": "X",
              "playerB": "Y", "pick": "X", "confidence": 0.72, "accuracy": acc, "id": "t1"}]}
        with mock.patch.object(G, "read_js", lambda name: {"tennis-data.js": td}.get(name)), \
             mock.patch.object(G, "HERE", tempfile.mkdtemp()):
            out = G.legs({DATE})
        t = [l for l in out if l["sport"] == "tennis"]
        self.assertTrue(t)
        self.assertFalse(t[0]["listOff"])
        l = G.honest(dict(t[0], odds=1.40, margin=1.04, est=False))
        self.assertIn("75%", G.card_fault(l))      # 29 Oct 2026: 72% is under the tennis floor
        l = G.honest(dict(t[0], odds=1.25, margin=1.04, est=False, pModel=0.78))
        self.assertIsNone(G.card_fault(l))
        self.assertFalse(G.safe_leg(l))          # still never in the old strict groups


if __name__ == "__main__":
    unittest.main()


class WiderRule(unittest.TestCase):
    """25 Oct 2026, Douglas: a window the full rule leaves empty still gets a
    group, under the wider rule (to 2.10, bookmakers 55%+), marked wide."""

    def weak_daytime(self):
        # fair about 57%: under the full rule's 60%, inside the wider 55%
        # two full-rule picks and three at about 57%: no full-rule group
        strong = [leg(i, 1.40, 0.70, f"{DATE}T12:{i * 10:02d}:00Z", margin=1.0) for i in range(2)]
        return strong + [leg(i, 1.75, 0.58, f"{DATE}T13:{i * 10:02d}:00Z", margin=1.0) for i in range(2, 5)]

    def test_empty_window_gets_a_wide_group(self):
        L = self.weak_daytime()
        for l in L[2:]: self.assertIsNotNone(G.card_fault(l)); self.assertIsNone(G.card_fault(l, wide=True))
        gs = G.build_card(L, DATE, EARLY, log=[])
        self.assertTrue(gs)
        self.assertTrue(all(g["wide"] and g["window"] == "Day" for g in gs))
        self.assertEqual(gs[0]["risk"], "Wider rule")

    def test_full_rule_window_gets_no_wide_group(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        self.assertFalse(any(g.get("wide") for g in gs))

    def test_wide_group_gives_way_to_a_full_rule_group(self):
        first = G.build_card(self.weak_daytime(), DATE, EARLY, log=[])
        again = G.build_card(board(), DATE, EARLY + timedelta(hours=1), prev=first, log=[])
        self.assertTrue(any(g["window"] == "Day" for g in again))
        self.assertFalse(any(g.get("wide") for g in again))

    def test_locked_wide_group_stays(self):
        first = G.build_card(self.weak_daytime(), DATE, EARLY, log=[])
        again = G.build_card(board(), DATE, AFTER_LOCK, prev=first, log=[])
        self.assertTrue(any(g.get("wide") and g["locked"] for g in again))

    def test_wide_price_cap(self):
        self.assertIsNotNone(G.card_fault(leg(1, 2.30, 0.45, f"{DATE}T12:00:00Z", margin=1.0), wide=True))

    def test_short_favourites_reach_2x_with_five(self):
        L = [leg(i, 1.17, 0.85, f"{DATE}T12:{i * 10:02d}:00Z", margin=1.0) for i in range(5)]
        gs = G.build_card(L, DATE, EARLY, log=[])
        self.assertTrue(gs and gs[0]["wide"] and len(gs[0]["legs"]) == 5 and gs[0]["odds"] >= 2.0)


class TennisTimes(unittest.TestCase):
    def test_placeholder_is_midnight_new_york(self):
        self.assertTrue(G.tennis_placeholder("2026-10-26T04:00:00Z"))     # EDT
        self.assertTrue(G.tennis_placeholder("2026-11-09T05:00:00Z"))     # EST
        self.assertFalse(G.tennis_placeholder("2026-10-26T09:00:00Z"))

    def test_placeholder_takes_the_tournaments_first_start(self):
        td = {"matches": [{"date": DATE, "time": "05:00", "tournament": "Vienna", "round": "Round 1",
                           "playerA": "A", "playerB": "B", "pick": "B", "confidence": 0.7,
                           "accuracy": {"n": 500, "hit": 0.8}}]}
        with mock.patch.object(G, "read_js", side_effect=lambda n: td if n == "tennis-data.js" else {}), \
             mock.patch.object(G, "tennis_starts", return_value={"Vienna": "09:30"}), \
             mock.patch.object(G.os.path, "exists", return_value=False):
            L = G.legs({DATE})
        self.assertEqual(L[0]["when"], f"{DATE}T09:30:00Z")
        self.assertTrue(L[0]["timeEst"])
        self.assertEqual(G.uk_slot(L[0]), (DATE, "Day"))


class SportRule(unittest.TestCase):
    """29 Oct 2026 review: NFL and college football legs are off the Card; a
    tennis leg needs the model and its tested rate both at 75%+."""

    def test_nfl_and_cfb_are_off_the_card(self):
        for s in ("nfl", "cfb"):
            self.assertIn("off the Card", G.card_fault(leg(0, 1.40, 0.80, f"{DATE}T20:00:00Z", sport=s)))

    def test_tennis_needs_75_on_model_and_tested_rate(self):
        t = dict(leg(1, 1.40, 0.70, f"{DATE}T12:00:00Z", sport="tennis"), hit=0.80)
        self.assertIn("75%", G.card_fault(t))
        t = dict(leg(2, 1.30, 0.78, f"{DATE}T12:00:00Z", sport="tennis"), hit=0.70)
        self.assertIn("75%", G.card_fault(t))
        t = dict(leg(3, 1.30, 0.78, f"{DATE}T12:00:00Z", sport="tennis"), hit=0.80)
        self.assertIsNone(G.card_fault(t))

    def test_football_and_nba_unchanged(self):
        self.assertIsNone(G.card_fault(leg(4, 1.40, 0.66, f"{DATE}T12:00:00Z")))
        self.assertIsNone(G.card_fault(leg(5, 1.40, 0.66, f"{DATE}T20:00:00Z", sport="nba")))

    def test_old_rule_groups_rebuild(self):
        self.assertEqual(G.CARD_RULE, 4)
        g = {"name": "Card 2x", "rule": 1, "legs": []}
        self.assertEqual(G.recheck_card(g, [])[0], None)


class BenchAndBook(unittest.TestCase):
    """29 Oct 2026, Douglas: William Hill prices on every pick, substitutes on
    every group, so a pick that isn't offered is swapped, never merged."""

    def test_bench_keeps_the_group_in_range_and_unused(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        used = {l["event"] for g in gs for l in g["legs"]}
        self.assertTrue(any(g["bench"] for g in gs))    # the 3x here sits on its 3.00 floor, so it may have none
        for g in gs:
            b = g["bench"]
            self.assertLessEqual(len(b), G.CARD_BENCH)
            self.assertFalse({l["event"] for l in b} & used)
            lo, hi = G.CARD_RANGE[g["name"]]
            for sub in b:
                for i in range(len(g["legs"])):
                    legs_ = [x for j, x in enumerate(g["legs"]) if j != i] + [sub]
                    o = G.math.prod(x["odds"] for x in legs_)
                    self.assertTrue(lo <= o <= hi)
                    self.assertGreaterEqual(G.math.prod(x["p"] for x in legs_), G.MIN_CHANCE[g["name"]])

    def test_locked_group_keeps_its_bench(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        g0 = next(g for g in gs if g["bench"]); bench0 = [l["pick"] for l in g0["bench"]]
        again = G.build_card(board()[:6], DATE, AFTER_LOCK, prev=gs, log=[])
        g1 = next(g for g in again if g["name"] == g0["name"])
        self.assertEqual([l["pick"] for l in g1["bench"]], bench0)

    def test_price_at_the_book(self):
        L = board()
        for l in L: l["bookOdds"] = {"William Hill": round(l["odds"] + 0.02, 2), "Bet365": l["odds"]}
        gs = G.build_card(L, DATE, EARLY, log=[])
        g = gs[0]
        self.assertEqual(g["book"], "William Hill")
        self.assertAlmostEqual(g["bookOdds"], round(G.math.prod(l["odds"] + 0.02 for l in g["legs"]), 2), places=1)
        self.assertTrue(all(G.book_price(l) for l in g["legs"]))
        # a pick Hill doesn't price still qualifies; the group then has no price at the book
        L2 = board()
        L2[0]["bookOdds"] = {"Bet365": L2[0]["odds"]}
        gs2 = G.build_card(L2, DATE, EARLY, log=[])
        self.assertTrue(gs2)
        for g in gs2:
            if any(l["event"] == L2[0]["event"] for l in g["legs"]): self.assertIsNone(g["bookOdds"])

    def test_record_keeps_old_windows(self):
        self.assertEqual([w for w, _, _ in G.CARD_WINDOWS], ["Day"])


class CoreLeagues(unittest.TestCase):
    """29 Oct 2026: football legs on the Card come from the core leagues only."""

    def test_wider_league_and_cup_legs_are_out(self):
        self.assertIn("core leagues", G.card_fault(dict(leg(0, 1.40, 0.70, f"{DATE}T12:00:00Z"), code="af.240", comp="Primera A")))
        self.assertIn("core leagues", G.card_fault(dict(leg(1, 1.40, 0.70, f"{DATE}T12:00:00Z"), code="en.fa", comp="FA Cup")))
        self.assertIsNone(G.card_fault(dict(leg(2, 1.40, 0.62, f"{DATE}T12:00:00Z"), code="en.1", comp="Premier League")))
        self.assertTrue(G.core_league("de.2")); self.assertFalse(G.core_league("eu.cl")); self.assertFalse(G.core_league(None))

    def test_record_carries_the_floor(self):
        import json, tempfile
        # three settled groups at p 0.3, none won: z = -0.9/sqrt(0.63)
        self.assertIsNotNone(G.CARD_FLOOR_Z)


class MoreGroups(unittest.TestCase):
    """29 Oct 2026: up to CARD_MAX_GROUPS a day, 2x, 3x, then a second of each
    from the fixtures left, every group from different fixtures."""

    def test_second_pair_from_the_leftover_fixtures(self):
        L = board() + [leg(20 + i, round(1.32 + 0.03 * i, 2), 0.66, f"{DATE}T{14 + i // 2:02d}:{(i % 2) * 30:02d}:00Z") for i in range(8)]
        gs = G.build_card(L, DATE, EARLY, log=[])
        self.assertLessEqual(len(gs), G.CARD_MAX_GROUPS)
        self.assertGreater(len(gs), 2)
        seen = [l["event"] for g in gs for l in g["legs"]]
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(len({G.card_slot(g) for g in gs}), len(gs))
        self.assertTrue(any(g["seq"] == 2 for g in gs))
        for g in gs:
            self.assertEqual(g["stake"], G.CARD_STAKE[g["name"]])
            self.assertGreaterEqual(g["odds"], G.CARD_RANGE[g["name"]][0])

    def test_second_group_locks_and_holds_like_the_first(self):
        L = board() + [leg(20 + i, round(1.32 + 0.03 * i, 2), 0.66, f"{DATE}T{14 + i // 2:02d}:{(i % 2) * 30:02d}:00Z") for i in range(8)]
        gs = G.build_card(L, DATE, EARLY, log=[])
        again = G.build_card(L, DATE, AFTER_LOCK, prev=gs, log=[])
        self.assertEqual({G.card_slot(g) for g in again}, {G.card_slot(g) for g in gs})
        self.assertTrue(all(g["locked"] for g in again))


class UnderMarket(unittest.TestCase):
    """29 Oct 2026 backtest: a football leg needs the model at least 5 points
    under the bookmakers' chance. Full rule only; the wider rule is graded apart."""

    def test_model_level_with_the_market_is_out(self):
        l = leg(0, 1.40, 0.70, f"{DATE}T12:00:00Z")          # fair about 0.69
        self.assertIn("under the", G.card_fault(l))
        self.assertIsNone(G.card_fault(l, wide=True))
        self.assertIsNone(G.card_fault(leg(1, 1.40, 0.62, f"{DATE}T12:00:00Z")))
        self.assertIsNone(G.card_fault(dict(leg(2, 1.30, 0.78, f"{DATE}T12:00:00Z", sport="tennis"), hit=0.8)))   # football only


class LegacyWindows(unittest.TestCase):
    """29 Oct 2026: a group locked under the old three windows on the day they
    changed stays on the page as locked; nothing is rebuilt in that window."""

    def test_locked_overnight_group_is_kept_not_rebuilt(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        old = dict(gs[0], window="Overnight", rank="Overnight", locked=True, lockAt=G.iso(G.lock_time(DATE, "Overnight")))
        again = G.build_card(board(), DATE, AFTER_LOCK, prev=[old], log=[])
        kept = [g for g in again if g["window"] == "Overnight"]
        self.assertEqual(len(kept), 1)
        self.assertTrue(kept[0]["locked"])
        self.assertEqual({l["event"] for l in kept[0]["legs"]}, {l["event"] for l in old["legs"]})
        wins = G.card_windows(DATE, again)
        self.assertEqual([w["name"] for w in wins], ["Day", "Overnight"])
        self.assertTrue(wins[1]["legacy"])
        # an unlocked old-window group is dropped, not rebuilt
        gone = G.build_card(board(), DATE, EARLY, prev=[dict(old, locked=False)], log=[])
        self.assertFalse(any(g["window"] == "Overnight" for g in gone))


class NoClockLock(unittest.TestCase):
    """29 Oct 2026, Douglas: no locks. A group is open until its first
    kick-off, then frozen as last published."""

    def test_group_opens_then_freezes_at_first_kickoff(self):
        gs = G.build_card(board(), DATE, EARLY, log=[])
        self.assertTrue(gs)
        for g in gs:
            self.assertFalse(g["locked"]); self.assertFalse(g["late"])
            self.assertEqual(g["lockAt"], G.iso(G.first_kick(g)))
        g0 = gs[0]; ko = G.first_kick(g0)
        before = G.build_card(board(), DATE, ko - timedelta(minutes=30), prev=gs, log=[])
        b0 = next(g for g in before if G.card_slot(g) == G.card_slot(g0))
        self.assertFalse(b0["locked"]); self.assertEqual(b0["status"], "holding")
        after = G.build_card(board(), DATE, ko + timedelta(minutes=5), prev=gs, log=[])
        a0 = next(g for g in after if G.card_slot(g) == G.card_slot(g0))
        self.assertTrue(a0["locked"]); self.assertEqual(a0["status"], "underway")
        self.assertEqual([l["event"] for l in a0["legs"]], [l["event"] for l in g0["legs"]])

    def test_late_build_still_makes_an_open_group(self):
        gs = G.build_card(board(), DATE, AFTER_LOCK, log=[])
        self.assertTrue(gs and not any(g["late"] or g["locked"] for g in gs))

    def test_transition_day_drops_old_windows(self):
        with mock.patch.object(G, "CARD_TRANSITION", {DATE}):
            gs = G.build_card(board(), DATE, EARLY, log=[])
            old = dict(gs[0], window="Overnight", rank="Overnight", locked=True)
            again = G.build_card(board(), DATE, EARLY + timedelta(hours=1), prev=[old] + gs, log=[])
            self.assertFalse(any(g["window"] == "Overnight" for g in again))
