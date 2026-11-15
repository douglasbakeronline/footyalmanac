"""The briefing watchdog (15 Nov 2026): tools/briefing_watch.decide dispatches
a deploy when a briefing slot is due, unsent, past its grace, no deploy is
queued or running, and the watchdog has not already kicked this slot."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import briefing_watch as W


def at(s): return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def run(created, status="completed", event="schedule"):
    return {"created_at": created, "status": status, "event": event}


class Decide(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.p = os.path.join(self.d, "briefed.json")

    def brief(self, date, slots):
        with open(self.p, "w") as f: json.dump({"date": date, "slots": slots}, f)

    def test_kicks_when_morning_unsent_and_no_build(self):
        self.brief("2026-11-15", [])
        go, why = W.decide(at("2026-11-15T07:20:00"), [run("2026-11-15T06:15:51Z")], self.p)
        self.assertTrue(go, why)
        self.assertIn("morning", why)

    def test_waits_for_the_grace(self):
        self.brief("2026-11-15", [])
        go, _ = W.decide(at("2026-11-15T07:05:00"), [], self.p)
        self.assertFalse(go)

    def test_nothing_due_before_the_first_slot(self):
        go, why = W.decide(at("2026-11-15T05:30:00"), [], self.p)
        self.assertFalse(go); self.assertIn("no slot", why)

    def test_already_sent(self):
        self.brief("2026-11-15", ["morning"])
        go, _ = W.decide(at("2026-11-15T08:00:00"), [], self.p)
        self.assertFalse(go)

    def test_yesterdays_file_does_not_count(self):
        self.brief("2026-11-14", ["morning", "lunch", "evening", "night"])
        go, _ = W.decide(at("2026-11-15T07:30:00"), [], self.p)
        self.assertTrue(go)

    def test_a_build_in_flight_will_send_it(self):
        self.brief("2026-11-15", [])
        for st in ("queued", "in_progress", "waiting", "pending", "requested"):
            go, why = W.decide(at("2026-11-15T07:30:00"), [run("2026-11-15T07:25:00Z", st, "push")], self.p)
            self.assertFalse(go, st); self.assertIn("running", why)

    def test_kicks_at_most_twice_a_slot(self):
        self.brief("2026-11-15", [])
        runs = [run("2026-11-15T07:16:00Z", event="workflow_dispatch")]
        self.assertTrue(W.decide(at("2026-11-15T07:40:00"), runs, self.p)[0])
        runs.append(run("2026-11-15T07:41:00Z", event="workflow_dispatch"))
        go, why = W.decide(at("2026-11-15T08:00:00"), runs, self.p)
        self.assertFalse(go); self.assertIn("already", why)

    def test_dispatches_before_the_slot_are_not_counted(self):
        self.brief("2026-11-15", ["morning"])
        runs = [run("2026-11-15T09:00:00Z", event="workflow_dispatch"), run("2026-11-15T10:30:00Z", event="workflow_dispatch")]
        self.assertTrue(W.decide(at("2026-11-15T11:20:00"), runs, self.p)[0])

    def test_summer_time_slot_is_uk_hour(self):
        self.brief("2026-07-01", [])
        self.assertFalse(W.decide(at("2026-07-01T05:50:00"), [], self.p)[0])   # 06:50 BST
        self.assertTrue(W.decide(at("2026-07-01T06:20:00"), [], self.p)[0])    # 07:20 BST

    def test_every_slot_hour_is_inside_a_cron_window(self):
        # GMT and BST: the slot's UTC hour (and the next) must be watched
        hours = W.watched_utc_hours()
        for _, h in W.N.SLOTS:
            for utc in (h, h - 1):
                self.assertIn(utc, hours)
                self.assertIn(utc + 1, hours)


if __name__ == "__main__":
    unittest.main()
