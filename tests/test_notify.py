"""notify.py (29 Oct 2026): one push per Card group this build created."""
import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import notify as N


def group(status, first, name="Card 2x"):
    return {"name": name, "status": status, "first": first, "odds": 2.18, "bestOdds": 2.26, "stake": 2, "book": "William Hill",
            "legs": [{"pick": "Melgar", "when": "2026-10-30T19:00:00Z", "odds": 1.30, "best": 1.32, "bestBook": "Bet365", "bookOdds": {"William Hill": 1.29}},
                     {"pick": "Lens", "when": "2026-10-30T20:05:00Z", "odds": 1.28, "best": 1.30, "bestBook": "Bet365", "bookOdds": {}},
                     {"pick": "Mainz", "when": "2026-10-30T19:30:00Z", "odds": 1.31, "best": 1.33, "bestBook": "Betfair", "bookOdds": {"William Hill": 1.30}}],
            "bench": [{"pick": "x"}]}


class Notify(unittest.TestCase):
    def test_sends_new_groups_of_this_build_only(self):
        og = {"generated": "T1", "days": [{"date": "2026-10-30", "groups": [group("new", "T1"), group("holding", "T0"), group("new", "T0", "Card 3x"),
                                                                            {"name": "Multiplier", "status": "new", "first": "T1", "legs": [], "odds": 3}]}]}
        sent = []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(N, "HERE", d), \
             mock.patch.dict(os.environ, {"NTFY_TOPIC": "t"}), mock.patch.object(N, "send", lambda topic, title, body, tags="x": sent.append((title, body))):
            json.dump(og, open(os.path.join(d, "groupings.json"), "w"))
            N.main()
        self.assertEqual(len(sent), 1)
        title, body = sent[0]
        self.assertTrue(title.startswith("Card 2x, Fri 30 Oct, 2.18"))
        self.assertTrue(title.isascii())
        self.assertIn("Melgar  1.29 William Hill", body)
        self.assertIn("Lens  1.30 Bet365", body)         # no Hill price: best and who
        self.assertIn("open until Fri 19:00", body)
        self.assertIn("2 units", body)

    def test_silent_without_topic(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(N, "send", side_effect=AssertionError("must not send")):
            self.assertEqual(N.main(), 0)


if __name__ == "__main__":
    unittest.main()


class Replacement(unittest.TestCase):
    def test_replacement_is_flagged_in_title_and_tag(self):
        og = {"generated": "T1", "days": [{"date": "2026-10-30", "groups": [dict(group("replacement", "T1"))]}]}
        sent = []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(N, "HERE", d), \
             mock.patch.dict(os.environ, {"NTFY_TOPIC": "t"}), mock.patch.object(N, "send", lambda topic, title, body, tags="x": sent.append((title, body, tags))):
            json.dump(og, open(os.path.join(d, "groupings.json"), "w"))
            N.main()
        title, body, tags = sent[0]
        self.assertTrue(title.startswith("REPLACEMENT: Card 2x"))
        self.assertEqual(tags, "warning")
        self.assertIn("your bet stands", body)
