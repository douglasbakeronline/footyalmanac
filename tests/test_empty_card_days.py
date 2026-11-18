"""tools/card_review_post.py empty_card_days (18 Nov 2026): the started days
the live Card published no group, read from day files in a synthetic archive."""
import json, os, sys, tempfile, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_review_post as P


class EmptyCardDays(unittest.TestCase):
    def test_days_without_a_full_rule_group(self):
        d = tempfile.mkdtemp()
        def day(date, groups):
            with open(os.path.join(d, f"{date}.json"), "w") as f: json.dump({"date": date, "groups": groups}, f)
        day("2026-11-10", [{"name": "Card 2x"}])
        day("2026-11-11", [{"name": "Card 2x", "wide": True}])   # the filler is not the Card
        day("2026-11-12", [{"name": "Daily 2x"}])                # nor the Daily 2x
        day("2026-11-14", [{"name": "Card 2x"}])                 # today: not started-and-finished
        self.assertEqual(P.empty_card_days("2026-11-10", "2026-11-14", archive=d),
                         {"2026-11-11", "2026-11-12", "2026-11-13"})

    def test_no_archive_means_every_day_empty(self):
        self.assertEqual(P.empty_card_days("2026-11-10", "2026-11-12", archive="/nonexistent"),
                         {"2026-11-10", "2026-11-11"})


if __name__ == "__main__":
    unittest.main()
