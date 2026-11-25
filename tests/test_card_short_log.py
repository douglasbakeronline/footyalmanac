"""The page's own read of each Card day, build by build (25 Nov 2026,
groupings.short_entry / log_short, card_review_post._page_read): the pool
replay built groups on 23 and 24 Nov the page never published, and nothing
kept what the page saw at each build."""
import json, os, sys, tempfile, unittest
from datetime import timedelta
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import groupings as G
import card_review_post as C
from test_card_span import D1, NOW, leg


class Entry(unittest.TestCase):
    def test_short_day_names_reason_and_clear_picks(self):
        L = [leg(i, D1, 15 + i) for i in range(2)]
        e = G.short_entry(L, D1.isoformat(), NOW, [])
        self.assertEqual(e["why"], "few")
        self.assertEqual([c[0] for c in e["clear"]], ["h0", "h1"])
        self.assertEqual(e["clear"][0][1:], [1.40, 0.76])

    def test_built_day_names_its_groups(self):
        L = [leg(i, D1, 15 + i) for i in range(3)]
        gs = G.build_card(L, D1.isoformat(), NOW, log=[])
        self.assertTrue(gs)
        e = G.short_entry(L, D1.isoformat(), NOW, gs)
        self.assertEqual(e["why"], "built")
        self.assertEqual(e["groups"], [["h0", "h1", "h2"]])

    def test_other_cards_do_not_count_as_built(self):
        L = [leg(i, D1, 15 + i) for i in range(2)]
        e = G.short_entry(L, D1.isoformat(), NOW, [{"name": "Daily 2x", "legs": [{"pick": "h0"}]}])
        self.assertEqual(e["why"], "few")


class Log(unittest.TestCase):
    def test_appends_only_on_change_and_trims(self):
        with tempfile.TemporaryDirectory() as t:
            d = D1.isoformat()
            a = {"at": "2026-11-24T06:00:00Z", "why": "few", "clear": [["X", 1.4, 0.7]]}
            G.log_short({d: a}, NOW, archive=t)
            G.log_short({d: dict(a, at="2026-11-24T12:00:00Z")}, NOW, archive=t)       # unchanged
            G.log_short({d: dict(a, at="2026-11-24T17:00:00Z", why="long")}, NOW, archive=t)
            old = (NOW.date() - timedelta(days=G.SHORT_LOG_DAYS + 1)).isoformat()
            log = G.log_short({old: a}, NOW, archive=t)
            self.assertEqual([e["why"] for e in log[d]], ["few", "long"])
            self.assertNotIn(old, log)
            with open(os.path.join(t, G.SHORT_LOG)) as f: self.assertEqual(json.load(f), log)

    def test_bad_file_starts_afresh(self):
        with tempfile.TemporaryDirectory() as t:
            with open(os.path.join(t, G.SHORT_LOG), "w") as f: f.write("not json")
            log = G.log_short({D1.isoformat(): {"at": "x", "why": "few", "clear": []}}, NOW, archive=t)
            self.assertEqual(list(log), [D1.isoformat()])


class PageRead(unittest.TestCase):
    def write(self, t, es):
        with open(os.path.join(t, "card-short.json"), "w") as f: json.dump({"2026-11-24": es}, f)

    def test_never_together(self):
        with tempfile.TemporaryDirectory() as t:
            self.write(t, [{"at": "2026-11-24T06:00:00Z", "why": "few", "clear": [["Salisbury", 1.44, 0.69], ["Torquay", 1.53, 0.67]]},
                           {"at": "2026-11-24T12:00:00Z", "why": "few", "clear": [["Salisbury", 1.5, 0.69]]}])
            out = C._page_read("2026-11-24", ["Boston Celtics", "Salisbury", "Torquay"], t)
        self.assertEqual(out, "the page's own reads, 2 logged from 11-24 06:00 UTC: never all clear together "
                              "(clear in: Boston Celtics 0, Salisbury 2, Torquay 1); last read few")

    def test_together(self):
        with tempfile.TemporaryDirectory() as t:
            self.write(t, [{"at": "2026-11-24T06:00:00Z", "why": "chance", "clear": [["A", 1.3, 0.8], ["B", 1.3, 0.8], ["C", 1.3, 0.8]]}])
            out = C._page_read("2026-11-24", ["A", "B", "C"], t)
        self.assertIn("all clear together at 1", out)

    def test_no_log_is_silent(self):
        self.assertIsNone(C._page_read("2026-11-24", ["A"], "/nonexistent"))
        with tempfile.TemporaryDirectory() as t:
            self.write(t, [])
            self.assertIsNone(C._page_read("2026-11-23", ["A"], t))

    def test_fidelity_why_carries_it(self):
        rec = {"cardLiveRule": 14, "days": [{"date": "2026-11-24", "groups": []}]}
        first = {"from": "2026-10-29", "to": "2026-11-24", "rules": [{"rule": 14, "from": "2026-11-19"}],
                 "variants": {"live": {"groupList": [{"date": "2026-11-24", "picks": ["A", "B", "C"]}],
                                       "legFaults": {"2026-11-24": {"A": "", "B": "", "C": ""}}}}}
        with tempfile.TemporaryDirectory() as t:
            self.write(t, [{"at": "2026-11-24T06:00:00Z", "why": "few", "clear": [["A", 1.3, 0.8]]}])
            out = C.fidelity_why(rec, first, None, today_="2026-11-25", archive=t)
        self.assertEqual(out, ["- replay at first prices, not on the page: 11-24 A, B, C: the page's own reads, 1 logged from "
                               "11-24 06:00 UTC: never all clear together (clear in: A 1, B 0, C 0); last read few"])


if __name__ == "__main__":
    unittest.main()
