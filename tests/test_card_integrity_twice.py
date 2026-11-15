"""card_integrity.picks_twice (15 Nov 2026): one fixture in two Card groups."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import card_integrity as CI


def g(name, events, seq=1, first="t", span=None):
    return {"name": name, "seq": seq, "first": first, "span": span, "legs": [{"event": e} for e in events]}


class Twice(unittest.TestCase):
    def test_span_and_next_day_group(self):
        by = {"2026-11-20": [g("Card 2x", ["a", "b", "c"], span=["2026-11-20", "2026-11-21"])],
              "2026-11-21": [g("Card 2x", ["b", "d", "e"], first="u")]}
        f = CI.picks_twice(by)
        self.assertEqual([(x["date"], x["event"]) for x in f], [("2026-11-21", "b")])

    def test_same_day_two_groups(self):
        by = {"2026-11-20": [g("Card 2x", ["a", "b"]), g("Card 2x", ["a", "c"], seq=2)]}
        self.assertEqual(len(CI.picks_twice(by)), 1)

    def test_clean_and_not_card(self):
        by = {"2026-11-20": [g("Card 2x", ["a", "b"]), g("Model 2x", ["a", "b"]), g("Card 2x", ["c"], seq=2)]}
        self.assertEqual(CI.picks_twice(by), [])

    def test_before_from_is_ignored(self):
        by = {"2026-11-14": [g("Card 2x", ["p"], span=["2026-11-14", "2026-11-15"])],
              "2026-11-15": [g("Card 2x", ["p"], first="u")]}
        self.assertEqual(CI.picks_twice(by), [])
        self.assertEqual(len(CI.picks_twice(by, since="2026-11-01")), 1)


if __name__ == "__main__":
    unittest.main()
