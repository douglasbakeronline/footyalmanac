"""score.drop_duplicates: a match archived under two spellings is graded
once (21 Nov 2026, #464), and two clubs `match_team` would join are kept
apart when the archive shows them as two (Managua and UNAN Managua)."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ledger as LG  # noqa: E402
import score as SC  # noqa: E402


def row(code, d, h, a, res, published, lst=False, reserve=False):
    return {"league": code, "date": d, "home": h, "away": a, "result": res,
            "published": published, "list": lst, "reserve": reserve}


class DropDuplicates(unittest.TestCase):
    def test_southend_same_day_graded_once_earliest_kept(self):
        rows = [row("en.5", "2026-10-03", "Southend United", "AFC Fylde", (3, 1), "2026-10-02T20:00:00Z"),
                row("en.5", "2026-10-03", "Southend", "AFC Fylde", (3, 1), "2026-10-02T09:00:00Z")]
        kept, pairs = SC.drop_duplicates(rows)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["home"], "Southend")
        self.assertEqual(pairs[0][1]["home"], "Southend United")

    def test_besiktas_round_date_apart(self):
        rows = [row("tr.1", "2026-10-10", "Besiktas", "Kocaelispor", (2, 1), "2026-10-09T20:00:00Z"),
                row("tr.1", "2026-10-11", "Beşiktaş", "Kocaelispor", (2, 1), "2026-10-09T21:00:00Z")]
        kept, pairs = SC.drop_duplicates(rows)
        self.assertEqual([r["date"] for r in kept], ["2026-10-10"])

    def test_list_copy_kept_over_earlier_board_copy(self):
        rows = [row("en.5", "2026-10-03", "Southend", "AFC Fylde", (3, 1), "2026-10-02T09:00:00Z"),
                row("en.5", "2026-10-03", "Southend United", "AFC Fylde", (3, 1), "2026-10-02T20:00:00Z", lst=True)]
        kept, _ = SC.drop_duplicates(rows)
        self.assertEqual(len(kept), 1)
        self.assertTrue(kept[0]["list"])

    def test_different_score_or_far_apart_or_reversed_kept(self):
        rows = [row("en.5", "2026-10-03", "Southend", "AFC Fylde", (3, 1), "2026-10-02T09:00:00Z"),
                row("en.5", "2026-10-03", "Southend United", "AFC Fylde", (1, 1), "2026-10-02T20:00:00Z"),
                row("en.5", "2026-10-20", "Southend United", "AFC Fylde", (3, 1), "2026-10-19T20:00:00Z"),
                row("en.5", "2026-10-04", "AFC Fylde", "Southend United", (3, 1), "2026-10-03T20:00:00Z")]
        kept, pairs = SC.drop_duplicates(rows)
        self.assertEqual(len(kept), 4)
        self.assertEqual(pairs, [])

    def test_two_clubs_match_team_joins_kept_apart(self):
        # the same build published both, against different opponents, and
        # they met on 2 Nov: two clubs, so both San Marcos results stand
        stamp = "2026-10-14T22:29:44Z"
        rows = [row("af.396", "2026-10-14", "UNAN Managua", "Diriangén", (1, 3), stamp),
                row("af.396", "2026-10-15", "Managua", "San Marcos", (3, 2), stamp),
                row("af.396", "2026-10-17", "UNAN Managua", "San Marcos", (3, 2), "2026-10-17T21:36:11Z"),
                row("af.396", "2026-11-02", "Managua", "UNAN Managua", (4, 0), "2026-11-01T22:59:26Z")]
        kept, pairs = SC.drop_duplicates(rows)
        self.assertEqual(len(kept), 4)
        self.assertEqual(pairs, [])

    def test_three_spellings_one_kept(self):
        rows = [row("in.1", "2026-10-18", "Churchill Brothers", n, (0, 4), f"2026-10-17T1{i}:00:00Z")
                for i, n in enumerate(["SC East Bengal", "East Bengal", "EAST BENGAL"])]
        kept, pairs = SC.drop_duplicates(rows)
        self.assertEqual([r["away"] for r in kept], ["SC East Bengal"])
        self.assertEqual(len(pairs), 2)


class LedgerReadsDuplicates(unittest.TestCase):
    def test_dropped_copy_marked_not_ungraded(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "record-graded.json"), "w") as f:
                json.dump({"graded": [{"date": "2026-10-03", "league": "en.5", "home": "Southend", "away": "AFC Fylde",
                                   "result": [3, 1], "won": True}],
                       "duplicates": [{"league": "en.5", "date": "2026-10-03", "home": "Southend United",
                                       "away": "AFC Fylde", "kept": ["2026-10-03", "Southend", "AFC Fylde"]}]},
                          f)
            look = LG.results(d)
            kept = {"sport": "football", "comp": "en.5", "date": "2026-10-03", "home": "Southend", "away": "AFC Fylde"}
            dup = dict(kept, home="Southend United")
            self.assertEqual(LG.result_of(kept, look), ("won", "3-1"))
            self.assertEqual(LG.result_of(dup, look), ("duplicate", None))


if __name__ == "__main__":
    unittest.main()
