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


if __name__ == "__main__":
    unittest.main()


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
