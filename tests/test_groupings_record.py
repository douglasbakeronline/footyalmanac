"""The groupings record after the 25 Oct 2026 review (groupings.grade):
graded rows keep wide / late / locked / lockAt, and the Card tallies the full
rule, the wider rule and late groups apart. Standard library only."""
import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G


def leg(pick, odds=1.50):
    return {"pick": pick, "event": f"{pick} v X", "sport": "football", "home": pick, "away": "X", "side": "h",
            "date": "2026-10-26", "when": "2026-10-26T15:00:00Z", "odds": odds, "best": odds, "p": 0.65}


def card(name, window, picks, **flags):
    g = {"name": name, "odds": 2.2, "p": 0.4, "window": window, "rank": window, "rule": G.CARD_RULE,
         "locked": True, "lockAt": "2026-10-26T07:00:00Z", "legs": [leg(p) for p in picks]}
    g.update(flags)
    return g


def graded(groups, statuses):
    """grade() on one archive day with every leg settled as given."""
    with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
        json.dump({"date": "2026-10-26", "groups": groups}, open(os.path.join(d, "2026-10-26.json"), "w"))
        it = iter(statuses)
        with mock.patch.object(G, "results_index", return_value=None), \
             mock.patch.object(G, "settle", side_effect=lambda l, idx, dead=None: (next(it), "1-0")):
            return G.grade()


class Flags(unittest.TestCase):
    def test_flags_travel_with_the_graded_row(self):
        rec = graded([card("Card 2x", "Daytime", ["A", "B", "C"], wide=True, late=True)], ["won"] * 3)
        g = rec["days"][0]["groups"][0]
        self.assertEqual((g["wide"], g["late"], g["locked"], g["lockAt"]), (True, True, True, "2026-10-26T07:00:00Z"))

    def test_old_rows_without_the_flags_still_grade(self):
        g = {"name": "Multiplier", "odds": 3.0, "p": 0.3, "legs": [leg("A"), leg("B")]}
        rec = graded([g], ["won", "lost"])
        r = rec["days"][0]["groups"][0]
        self.assertEqual((r["wide"], r["late"], r["locked"], r["lockAt"], r["status"]), (False, False, False, None, "lost"))


class Tallies(unittest.TestCase):
    def setUp(self):
        groups = [card("Card 2x", "Daytime", ["A", "B", "C"]),                       # full rule, on time: won
                  card("Card 3x", "Daytime", ["D", "E", "F"], wide=True),            # wider rule: won
                  card("Card 2x", "Evening", ["G", "H", "I"], late=True),            # late: lost
                  card("Card 3x", "Evening", ["J", "K", "L"], wide=True, late=True)]  # wide and late: won
        self.rec = graded(groups, ["won"] * 6 + ["lost", "won", "won"] + ["won"] * 3)

    def test_card_is_the_full_rule_locked_on_time(self):
        self.assertEqual((self.rec["card"]["groups"], self.rec["card"]["won"]), (1, 1))
        self.assertEqual(self.rec["cardByWindow"]["Daytime"]["groups"], 1)
        self.assertEqual(self.rec["cardByWindow"]["Evening"]["groups"], 0)

    def test_wide_and_late_have_their_own_lines(self):
        self.assertEqual((self.rec["cardWide"]["groups"], self.rec["cardWide"]["won"]), (1, 1))
        self.assertEqual((self.rec["cardLate"]["groups"], self.rec["cardLate"]["won"], self.rec["cardLate"]["lost"]), (2, 1, 1))

    def test_nothing_is_lost(self):
        self.assertEqual(self.rec["overall"]["groups"], 4)
        self.assertEqual(len(self.rec["days"][0]["groups"]), 4)


class PostponedLegs(unittest.TestCase):
    """25 Oct 2026: a postponed, cancelled or abandoned football leg is void
    and drops out of the price; so is one with no result 72 hours after
    kick-off once every other leg has settled."""

    def idx(self, results):
        fb = {(d, G.norm(h), G.norm(a)): r for (d, h, a), r in results.items()}
        return fb, {}, {}

    def test_source_marked_postponed_is_void(self):
        l = leg("A"); idx = self.idx({("2026-10-26", "B", "X"): (2, 0)})
        self.assertEqual(G.settle(l, idx), ("pending", None))
        self.assertEqual(G.settle(l, idx, {("2026-10-26", "a", "x")}), ("void", "postponed"))
        self.assertEqual(G.settle(leg("B"), idx, {("2026-10-26", "a", "x")}), ("won", "2-0"))

    def test_dead_fixtures_read_from_the_cached_day_file_only(self):
        import gzip, sources as S
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "AF_CACHE_DIR", d), \
             mock.patch.object(S, "_af_get", side_effect=AssertionError("no calls while grading")):
            rows = [S._compact({"league": {"id": 1, "season": 2026}, "fixture": {"id": 5, "date": "2026-10-26T15:00:00+00:00", "status": {"short": "PST"}},
                                "teams": {"home": {"name": "Alpha FC"}, "away": {"name": "Beta"}}, "score": {"fulltime": {}}}),
                    S._compact({"league": {"id": 1, "season": 2026}, "fixture": {"id": 6, "date": "2026-10-26T15:00:00+00:00", "status": {"short": "FT"}},
                                "teams": {"home": {"name": "Gamma"}, "away": {"name": "Delta"}}, "score": {"fulltime": {"home": 1, "away": 0}}})]
            with gzip.open(os.path.join(d, "day-2026-10-26.json.gz"), "wt", encoding="utf-8") as fh:
                json.dump({"final": True, "rows": rows}, fh)
            dead = G.dead_fixtures({"2026-10-26", "2026-10-27"})
        self.assertIn(("2026-10-26", "alpha", "beta"), dead)
        self.assertNotIn(("2026-10-26", "gamma", "delta"), dead)

    def grade_at(self, groups, results, now):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(G, "ARCHIVE", d), mock.patch.object(G, "HERE", d):
            json.dump({"date": "2026-10-26", "groups": groups}, open(os.path.join(d, "2026-10-26.json"), "w"))
            with mock.patch.object(G, "results_index", return_value=self.idx(results)), \
                 mock.patch.object(G, "dead_fixtures", return_value=set()):
                return G.grade(now=now)

    def test_no_result_72_hours_on_is_void_and_the_group_pays_on_the_rest(self):
        from datetime import datetime, timedelta, timezone
        g = {"name": "Card 2x", "window": "Daytime", "odds": 3.0, "p": 0.35, "locked": True,
             "legs": [leg("A", 1.50), leg("B", 1.40), leg("C", 1.43)]}
        results = {("2026-10-26", "A", "X"): (1, 0), ("2026-10-26", "B", "X"): (3, 1)}
        ko = datetime(2026, 10, 26, 15, 0, tzinfo=timezone.utc)
        soon = self.grade_at([g], results, ko + timedelta(hours=20))["days"][0]["groups"][0]
        self.assertEqual(soon["status"], "pending")
        later = self.grade_at([g], results, ko + timedelta(hours=73))["days"][0]["groups"][0]
        self.assertEqual(later["status"], "won")
        self.assertEqual(later["legs"][2]["status"], "void")
        self.assertEqual(later["paid"], 2.1)                 # 1.50 x 1.40, C out of the price

    def test_not_voided_while_another_leg_is_still_pending(self):
        from datetime import datetime, timedelta, timezone
        g = {"name": "Card 2x", "window": "Daytime", "odds": 3.0, "p": 0.35, "locked": True,
             "legs": [leg("A", 1.50), leg("B", 1.40), leg("C", 1.43)]}
        ko = datetime(2026, 10, 26, 15, 0, tzinfo=timezone.utc)
        r = self.grade_at([g], {("2026-10-26", "A", "X"): (1, 0)}, ko + timedelta(hours=100))["days"][0]["groups"][0]
        self.assertEqual(r["status"], "pending")
        self.assertEqual([l["status"] for l in r["legs"]], ["won", "pending", "pending"])


if __name__ == "__main__":
    unittest.main()
