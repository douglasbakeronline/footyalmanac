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


if __name__ == "__main__":
    unittest.main()
