"""The nightly Card review's pre-registered decisions table (tools/card_review_post.decisions_section, 18 Nov 2026)."""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import card_review_post as C


def row(out, name):
    return next(l for l in out if l.startswith(f"| {name}"))


def tally(settled, won, expected, z, us=0, ur=0):
    return {"groups": settled, "settled": settled, "won": won, "expected": expected, "z": z, "unitsStaked": us, "unitsReturned": ur}


class TestDecisions(unittest.TestCase):
    def test_quiet_record(self):
        out = C.decisions_section({}, {}, {}, today_="2026-11-18")
        self.assertEqual(out[0], "## Pre-registered decisions (2026-11-30 review in 12 day(s))")
        self.assertIn("Nothing due or fired; every trigger is copied from the note behind it.", out)
        self.assertTrue(all("**" not in l for l in out if l.startswith("| ")))

    def test_tennis_tripwire_fired(self):
        rec = {"cardLegsBySport": {"tennis": {"tripwire": True, "atFloor": {"legs": 52, "z": -2.3}},
                                   "football": {"tripwire": False, "legs": 40, "z": 0.3}}}
        out = C.decisions_section(rec, {}, {}, today_="2026-11-18")
        r = row(out, "Tennis off the Card")
        self.assertIn("52 legs, z -2.3", r)
        self.assertIn("**fired**", r)
        self.assertFalse(any(l.startswith("| Football off") for l in out))   # only a fired sport besides tennis
        self.assertIn("**1 decision(s) due or fired", out[-2])

    def test_floor_line_needs_fifty_groups(self):
        out = C.decisions_section({"card": tally(49, 5, 17.0, -3.4)}, {}, {}, today_="2026-11-18")
        self.assertIn("| waiting |", row(out, "The Card's floor line"))
        out = C.decisions_section({"card": tally(50, 5, 17.0, -3.4, 75, 30)}, {}, {}, today_="2026-11-18")
        r = row(out, "The Card's floor line")
        self.assertIn("**fired**", r)
        self.assertIn("-60.0% at the page's stakes", r)

    def test_rule13_due_on_the_day_or_at_fifty(self):
        rec = {"cardByRule": {"13": tally(4, 1, 1.5, -0.4)}}
        rep = {"variants": {"rule12": {"vsLivePerDay": 0.4, "pWorse": 0.2, "legs": 60}}}
        r = row(C.decisions_section(rec, rep, {}, today_="2026-11-18"), "Rule 13")
        self.assertIn("| waiting |", r)
        self.assertIn("rule 12 ahead on the pool", r)
        out = C.decisions_section(rec, rep, {}, today_="2026-11-30")
        self.assertIn("**due**", row(out, "Rule 13"))
        self.assertEqual(out[0], "## Pre-registered decisions (the 2026-11-30 review is due)")
        rec = {"cardByRule": {"13": tally(50, 20, 19.0, 0.3)}}
        self.assertIn("**due**", row(C.decisions_section(rec, {}, {}, today_="2026-11-20"), "Rule 13"))

    def test_tennis75_counts_rule10_tennis_legs(self):
        legs = [{"sport": "tennis", "status": "won"}] * 20 + [{"sport": "tennis", "status": "pending"}]
        days = [{"groups": [{"name": "Card 2x", "rule": 13, "legs": legs},
                            {"name": "Card 2x", "rule": 9, "legs": [{"sport": "tennis", "status": "lost"}] * 9},   # before rule 10
                            {"name": "Card 2x", "rule": 13, "wide": True, "legs": [{"sport": "tennis", "status": "lost"}] * 9},
                            {"name": "Card 2x", "rule": 11, "legs": [{"sport": "tennis", "status": "lost"}] * 10}]}]
        self.assertEqual(C.card_tennis_since({"days": days}), 30)
        rep = {"variants": {"tennis75": {"vsLivePerDay": 0.2, "pWorse": 0.25, "legs": 120}}}
        self.assertIn("**due**", row(C.decisions_section({"days": days}, rep, {}, today_="2026-11-18"), "Tennis floor back"))
        rep = {"variants": {"tennis75": {"vsLivePerDay": 0.2, "pWorse": 0.45, "legs": 120}}}
        self.assertIn("| waiting |", row(C.decisions_section({"days": days}, rep, {}, today_="2026-11-18"), "Tennis floor back"))

    def test_opposition_floor_needs_both_seasons(self):
        rep = {"variants": {"m7opp5": {"vsLivePerDay": 0.5, "pWorse": 0.1, "legs": 140}}}
        one = {"seasons": {"a": {"season": "2025-26", "cardM7Paired": {"m7opp5": {"perDay": 0.1, "pWorse": 0.2}}},
                           "b": {"season": "2026-27", "cardM7Paired": {"m7opp5": {"perDay": -0.1, "pWorse": 0.7}}}}}
        r = row(C.decisions_section({}, rep, one, today_="2026-11-18"), "Opposition floor `m7opp5`")
        self.assertIn("football-data ahead in 1 of 2 season(s)", r)
        self.assertIn("| waiting |", r)
        both = {"seasons": {"a": {"season": "2025-26", "cardM7Paired": {"m7opp5": {"perDay": 0.1, "pWorse": 0.2}}},
                            "b": {"season": "2026-27", "cardM7Paired": {"m7opp5": {"perDay": 0.3, "pWorse": 0.1}}}}}
        r = row(C.decisions_section({}, rep, both, today_="2026-11-18"), "Opposition floor `m7opp5`")
        self.assertIn("**due**", r)
        self.assertIn("Douglas", r)

    def test_context_and_lists(self):
        rec = {"cardContext": {"against": {"legs": 30, "landed": 24, "rate": 0.8, "model": 0.75}},
               "cardList": tally(30, 18, 15.0, 1.1, 30, 36), "cardDaily": tally(50, 15, 25.0, -2.8, 50, 30)}
        out = C.decisions_section(rec, {}, {}, today_="2026-11-18")
        self.assertIn("**fired**", row(out, "Context veto off"))
        self.assertIn("80% v 75%", row(out, "Context veto off"))
        self.assertIn("**due**", row(out, "The List 2x as a method"))
        self.assertIn("| waiting |", row(out, "The List long dropped"))
        self.assertIn("**fired**", row(out, "The Daily 2x's rule"))


if __name__ == "__main__":
    unittest.main()
