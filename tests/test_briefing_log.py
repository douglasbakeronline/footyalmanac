"""Briefing send times (13 Nov 2026): notify.mark_sent logs each slot's
lateness and any slot a late build skipped; the nightly Card review
summarises the log (card_review_post.briefing_section)."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import notify as N
import card_review_post as P


def at(s): return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


class Log(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.p = os.path.join(self.d, "briefed.json")

    def read(self):
        with open(self.p) as f: return json.load(f)

    def test_lateness_in_minutes_after_the_slot(self):
        N.mark_sent(at("2026-11-12T07:06:22"), "morning", self.p)   # GMT: UK = UTC
        N.mark_sent(at("2026-11-12T13:18:43"), "lunch", self.p)
        st = self.read()
        self.assertEqual(st["slots"], ["morning", "lunch"])
        self.assertEqual([(e["slot"], e["late"]) for e in st["log"]], [("morning", 6), ("lunch", 138)])

    def test_summer_time_reads_uk_hour(self):
        N.mark_sent(at("2026-07-01T06:10:00"), "morning", self.p)   # 07:10 BST
        self.assertEqual(self.read()["log"][0]["late"], 10)

    def test_skipped_slot_logged_once(self):
        N.mark_sent(at("2026-11-12T07:06:00"), "morning", self.p)
        N.mark_sent(at("2026-11-12T16:20:00"), "evening", self.p)   # lunch never went
        log = self.read()["log"]
        self.assertEqual([e for e in log if e.get("skipped")], [{"date": "2026-11-12", "slot": "lunch", "skipped": True}])
        N.mark_sent(at("2026-11-12T21:30:00"), "night", self.p)
        self.assertEqual(sum(1 for e in self.read()["log"] if e.get("skipped")), 1)

    def test_old_file_without_log_and_trimming(self):
        with open(self.p, "w") as f: json.dump({"date": "2026-11-11", "slots": ["morning"], "at": "x"}, f)
        N.mark_sent(at("2026-11-12T07:01:00"), "morning", self.p)
        self.assertEqual(len(self.read()["log"]), 1)
        N.mark_sent(at("2026-12-20T07:01:00"), "morning", self.p)
        self.assertEqual([e["date"] for e in self.read()["log"]], ["2026-12-20"])

    def test_due_slot_unchanged(self):
        N.mark_sent(at("2026-11-12T07:06:00"), "morning", self.p)
        self.assertIsNone(N.due_slot(at("2026-11-12T08:00:00"), self.p))
        self.assertEqual(N.due_slot(at("2026-11-12T13:00:00"), self.p), "lunch")


class Section(unittest.TestCase):
    def test_late_slot_named(self):
        st = {"log": [{"date": "2026-11-12", "slot": "morning", "late": 6},
                      {"date": "2026-11-12", "slot": "lunch", "late": 138},
                      {"date": "2026-11-12", "slot": "evening", "skipped": True}]}
        out = "\n".join(P.briefing_section(st, today_="2026-11-13"))
        self.assertIn("| lunch | 1 | 138 | 138 | 0 |", out)
        self.assertIn("| evening | 0 | n/a | n/a | 1 |", out)
        self.assertIn("Late or skipped: lunch, evening", out)
        self.assertNotIn("morning,", out)

    def test_on_time_and_empty(self):
        self.assertEqual(P.briefing_section({}), [])
        out = "\n".join(P.briefing_section({"log": [{"date": "2026-11-12", "slot": "night", "late": 20}]}))
        self.assertIn("within 60 minutes", out)

    def test_window(self):
        st = {"log": [{"date": "2026-10-01", "slot": "lunch", "late": 200}]}
        self.assertEqual(P.briefing_section(st, today_="2026-11-13"), [])


if __name__ == "__main__":
    unittest.main()
