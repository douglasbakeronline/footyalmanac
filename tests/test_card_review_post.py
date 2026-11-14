"""The nightly Card review issue (tools/card_review_post.py): the legs-by-sport
section from the record, with the sport-off tripwire (9 Nov 2026). gh is
stubbed; nothing is posted. Standard library only."""
import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import card_review_post as P


def post_with(record):
    files = {"groupings-record.json": record}
    posted = []
    with mock.patch.object(P, "load", side_effect=lambda p: files.get(p, {})), \
         mock.patch.object(P, "gh", side_effect=lambda *a: posted.append(a) or {}), \
         mock.patch("builtins.print"):
        P.main()
    body = next(x for a in posted for x in a if isinstance(x, str) and x.startswith("body="))
    return body


class LegsBySport(unittest.TestCase):
    def test_table_and_the_rule_when_nothing_fired(self):
        body = post_with({"cardLegsBySport": {"tennis": {"legs": 40, "landed": 22, "rate": 0.55, "quoted": 0.7083, "z": -2.23, "tripwire": False}}})
        self.assertIn("| tennis | 40 | 22 (55%) | 71% | -2.23 | no |", body)
        self.assertIn("A sport comes off the Card at 50+ legs", body)
        self.assertNotIn("Tripwire fired", body)

    def test_fired_names_the_sport(self):
        body = post_with({"cardLegsBySport": {"tennis": {"legs": 52, "landed": 29, "rate": 0.5577, "quoted": 0.71, "z": -2.4, "tripwire": True}}})
        self.assertIn("**Tripwire fired for tennis", body)
        self.assertIn("`CARD_SPORTS_OFF`", body)

    def test_no_section_without_the_tally(self):
        body = post_with({})
        self.assertNotIn("Legs by sport", body)


class Gate(unittest.TestCase):
    def rep(self, **variants):
        base = {"groups": 40, "won": 18, "expected": 15.0, "return": 1.1, "emptyDays": 2}
        return {"from": "2026-11-10", "to": "2026-11-30", "days": 21,
                "variants": {"live": dict(base, legs=130), **{k: dict(base, **v) for k, v in variants.items()}}}

    def test_legs_gate_not_groups(self):
        r = self.rep(short={"legs": 99, "pWorse": 0.1, "vsLivePerDay": 0.5}, uncapped={"legs": 140, "pWorse": 0.2, "vsLivePerDay": 0.3},
                     opp7={"legs": 200, "pWorse": 0.4, "vsLivePerDay": 0.3}, rule5={"legs": 200, "pWorse": 0.1, "vsLivePerDay": -0.2})
        self.assertEqual([v for v, _ in P.candidates(r)], ["uncapped"])

    def test_review_lines(self):
        r = self.rep(short={"legs": 60, "pWorse": 0.05, "vsLivePerDay": 1.2}, uncapped={"legs": 140, "pWorse": 0.2, "vsLivePerDay": 0.3})
        files = {"card-replay.json": r}
        posted = []
        with mock.patch.object(P, "load", side_effect=lambda p: files.get(p, {})), \
             mock.patch.object(P, "gh", side_effect=lambda *a: posted.append(a) or {}), \
             mock.patch.object(P, "funnel_section", return_value=[]), mock.patch("builtins.print"):
            P.main()
        body = next(x for a in posted for x in a if isinstance(x, str) and x.startswith("body="))
        self.assertIn("p(worse) <= 0.30 on 100+ legs):** uncapped", body)
        self.assertIn("under the 100-leg gate (watch, do not act): short (60 legs)", body)
        self.assertIn("| short | 40 | 18 | 15.0 | 60 |", body)


class PriceTimingLines(unittest.TestCase):
    def test_settled_and_not_started(self):
        # 10 Nov 2026 (#156): the singles return first v last, the day-resampled p, unstarted legs counted
        pt = {"legs": 107, "lastAfterStart": 0, "notStarted": 5,
              "timing": {"n": 107, "drifted": 52, "shortened": 41, "unchanged": 14, "meanMovePct": 1.76, "pNoDrift": 0.003, "read": "take the price late"},
              "settled": {"n": 104, "won": 69, "returnFirstPct": -7.21, "returnLastPct": -5.26, "lateGainPct": 1.95, "pLateNoBetter": 0.011, "read": "take the price late"}}
        files = {"price-timing.json": pt}
        posted = []
        with mock.patch.object(P, "load", side_effect=lambda p: files.get(p, {})), \
             mock.patch.object(P, "gh", side_effect=lambda *a: posted.append(a) or {}), \
             mock.patch.object(P, "funnel_section", return_value=[]), mock.patch("builtins.print"):
            P.main()
        body = next(x for a in posted for x in a if isinstance(x, str) and x.startswith("body="))
        self.assertIn("(take the price late), day-resampled p(no drift) 0.003", body)
        self.assertIn("singles on 104 settled legs (69 won): -7.21% at the first price, -5.26% at the last pre-start price, late +1.95 points, p(late no better) 0.011", body)
        self.assertIn("not started yet, left out until their last price is in: 5 leg(s)", body)


class OncePerDay(unittest.TestCase):
    """10 Nov 2026: a missed 03:40 run is caught by a later schedule, so a
    day that already has its review posts nothing more."""
    def run_with(self, issues, force=None):
        posted = []
        def fake(*a):
            if a and isinstance(a[0], str) and a[0].startswith(f"repos/{P.REPO}/issues?"):
                return issues
            posted.append(a); return {}
        env = {"FORCE_POST": force} if force else {}
        with mock.patch.object(P, "load", side_effect=lambda p: {}), \
             mock.patch.object(P, "gh", side_effect=fake), \
             mock.patch.dict(os.environ, env), mock.patch("builtins.print"):
            P.main()
        return [a for a in posted if a and a[0] == "-X" and a[2].endswith("/issues")]

    def test_posts_when_today_is_missing(self):
        self.assertEqual(len(self.run_with([{"title": "Card review 2000-01-01"}])), 1)

    def test_skips_when_today_is_posted(self):
        self.assertEqual(self.run_with([{"title": f"Card review {P.today}"}]), [])

    def test_force_posts_anyway(self):
        self.assertEqual(len(self.run_with([{"title": f"Card review {P.today}"}], force="1")), 1)

    def test_an_unreadable_listing_still_posts(self):
        self.assertEqual(len(self.run_with(None)), 1)


class CoverageAndKelly(unittest.TestCase):
    def test_coverage_names_the_gap(self):
        rep = {"from": "2026-10-30", "to": "2026-11-09", "variants": {"live": {"groups": 0}}}
        rec = {"days": [{"date": "2026-10-31", "groups": [{"name": "Card 2x"}, {"name": "Card 3x"}, {"name": "Card 2x", "wide": True}]},
                        {"date": "2026-10-20", "groups": [{"name": "Card 2x"}]}, {"date": "2026-11-01", "groups": [{"name": "Double"}]}]}
        out = P.coverage_lines(rep, rec)
        self.assertEqual(len(out), 1)
        self.assertIn("holds **2** live Card groups", out[0])
        self.assertIn("rebuilt 0", out[0])

    def test_coverage_quiet_without_record(self):
        self.assertEqual(P.coverage_lines({"from": "a", "to": "b", "variants": {"live": {"groups": 3}}}, {}), [])

    def test_kelly_under_quote_says_no_stake(self):
        line = P.kelly_line({"landedOverExpected": 0.942, "quarterKelly": {"median": 0, "p95Drawdown": 0}, "halfKelly": {"median": 0, "p95Drawdown": 0}})
        self.assertIn("stakes nothing", line)
        self.assertNotIn("0%", line)

    def test_kelly_above_quote_prints_numbers(self):
        line = P.kelly_line({"landedOverExpected": 1.2, "quarterKelly": {"median": 0.05, "p95Drawdown": 0.1}, "halfKelly": {"median": 0.08, "p95Drawdown": 0.2}})
        self.assertIn("quarter Kelly: median +5.0%", line)


class ContextCheck(unittest.TestCase):
    """11 Nov 2026: the context check by verdict, and its pre-registered review
    at 30 settled "against" picks (claude/context-check-2026-11-11.md)."""
    def t(self, legs, landed, model, fair=0.7):
        return {"legs": legs, "landed": landed, "rate": round(landed / legs, 4), "model": model, "fair": fair, "zModel": 0.1}

    def test_table_and_waiting(self):
        body = post_with({"cardContext": {"clear": self.t(10, 8, 0.72), "against": self.t(4, 2, 0.70, None)}})
        self.assertIn("## The context check", body)
        self.assertIn("| clear | 10 | 8 (80%) | 72% | 70% | 0.1 |", body)
        self.assertIn("| against | 4 | 2 (50%) | 70% | n/a | 0.1 |", body)
        self.assertIn("(4 so far)", body)
        self.assertNotIn("tripwire fired", body)

    def test_fires_when_against_lands_at_or_above_model(self):
        body = post_with({"cardContext": {"against": self.t(30, 22, 0.70)}})
        self.assertIn("**Context tripwire fired: 30", body)
        self.assertIn("`CARD_CONTEXT = False`", body)

    def test_stays_when_against_lands_under(self):
        body = post_with({"cardContext": {"against": self.t(31, 15, 0.70)}})
        self.assertIn("so the veto stays", body)
        self.assertNotIn("tripwire fired", body)

    def test_no_section_without_reads(self):
        self.assertNotIn("context check", post_with({}))


class BothSidesOfTheGate(unittest.TestCase):
    """12 Nov 2026: the pool read beside the football-data seasons, so a pool
    lead the seasons refused is not read as a candidate."""
    REP = {"variants": {"live": {"legs": 24},
                        "m7under5": {"legs": 45, "vsLivePerDay": 2.1, "pWorse": 0.01},
                        "m7core": {"legs": 12, "vsLivePerDay": 0.9, "pWorse": 0.2},
                        "good": {"legs": 120, "vsLivePerDay": 0.5, "pWorse": 0.1},
                        "short": {"legs": 0, "vsLivePerDay": 0.44, "pWorse": 0.2}}}
    HIST = {"seasons": {"fit": {"season": "2025-26", "cardM7Paired": {
                "m7under5": {"perDay": -0.41, "pWorse": 0.96, "identical": False},
                "m7core": {"perDay": 0.0, "pWorse": None, "identical": True},
                "good": {"perDay": 0.2, "pWorse": 0.2, "identical": False}}},
            "check": {"season": "2026-27", "cardM7Paired": {
                "m7under5": {"perDay": -0.34, "pWorse": 0.62, "identical": False},
                "m7core": {"perDay": 0.0, "pWorse": None, "identical": True},
                "good": {"perDay": 0.1, "pWorse": 0.25, "identical": False}}}}}

    def test_refused_on_seasons(self):
        out = "\n".join(P.fd_gate_lines(self.REP, self.HIST))
        self.assertIn("| m7under5 | +2.10 | 0.01 | 45 | -0.41, 0.96 | -0.34, 0.62 | fails: pool 45 legs of 100, football-data 2025-26, 2026-27 |", out)
        self.assertIn("not a candidate however the pool reads: m7under5.", out)

    def test_identical_has_no_read(self):
        self.assertIn("| m7core | +0.90 | 0.2 | 12 | identical | identical | no football-data read", "\n".join(P.fd_gate_lines(self.REP, self.HIST)))

    def test_full_pass_says_act(self):
        out = "\n".join(P.fd_gate_lines(self.REP, self.HIST))
        self.assertIn("| good | +0.50 | 0.1 | 120 | +0.20, 0.2 | +0.10, 0.25 | **passes** |", out)
        self.assertIn("**Full gate passed: good.", out)

    def test_one_season_missing_fails(self):
        h = {"seasons": {"fit": self.HIST["seasons"]["fit"]}}
        self.assertIn("fit and check not both on file", "\n".join(P.fd_gate_lines(self.REP, h)))

    def test_nothing_on_file(self):
        self.assertIn("no paired season read on file yet", P.fd_gate_lines(self.REP, {})[0])

    def test_empty_variant_named_apart(self):
        v = {k: {"groups": 0, "won": 0, "expected": 0, "return": None, "emptyDays": 1, **r} for k, r in self.REP["variants"].items()}
        files = {"card-replay.json": {"from": "2026-11-01", "to": "2026-11-02", "days": 2, "variants": v}}
        posted = []
        with mock.patch.object(P, "load", side_effect=lambda p: files.get(p, {})), \
             mock.patch.object(P, "gh", side_effect=lambda *a: posted.append(a) or {}), \
             mock.patch.object(P, "funnel_section", return_value=[]), mock.patch.object(P, "edge_section", return_value=[]), \
             mock.patch("builtins.print"):
            P.main()
        body = next(x for a in posted for x in a if isinstance(x, str) and x.startswith("body="))
        self.assertIn("Built nothing on these days, so ahead of live only by live's losses (not a read): short.", body)
        watch = next(l for l in body.splitlines() if l.startswith("Ahead of live but under"))
        self.assertNotIn("short", watch)


class ContextPause(unittest.TestCase):
    """14 Nov 2026: a paused context check is said in bold."""
    def test_pause_line(self):
        from datetime import datetime, timezone
        now = datetime(2026, 11, 14, 3, 40, tzinfo=timezone.utc)
        out = P.context_pause_line({"2026-11-14": 6, "pausedUntil": "2026-12-01T00:00Z"}, now)
        self.assertTrue(out and out[0].startswith("**The context check is paused until 2026-12-01T00:00Z"))
        self.assertEqual(P.context_pause_line({"pausedUntil": "2026-11-01T00:00Z"}, now), [])
        self.assertEqual(P.context_pause_line({"2026-11-14": 6}, now), [])
        self.assertEqual(P.context_pause_line({}, now), [])


if __name__ == "__main__":
    unittest.main()
