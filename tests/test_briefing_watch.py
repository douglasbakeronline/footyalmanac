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


class NextWait(unittest.TestCase):
    """--wait (16 Nov 2026): the deploy that ends a build starts a watchdog that
    sleeps until the next unsent slot, so no briefing waits on a shed cron."""
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.p = os.path.join(self.d, "briefed.json")

    def brief(self, date, slots):
        with open(self.p, "w") as f: json.dump({"date": date, "slots": slots}, f)

    def test_build_before_the_morning_slot_waits_for_it(self):
        # 16 Nov: the 05:15 cron ran at 06:14 UTC, before the 07:00 slot
        self.brief("2026-11-15", ["morning", "lunch", "evening", "night"])
        slot, secs = W.next_wait(at("2026-11-16T06:21:00"), self.p)
        self.assertEqual(slot, "morning")
        self.assertEqual(secs, (39 + W.GRACE_MIN) * 60)

    def test_due_and_unsent_waits_only_the_grace(self):
        self.brief("2026-11-16", [])
        self.assertEqual(W.next_wait(at("2026-11-16T07:30:00"), self.p), ("morning", 0))
        self.assertEqual(W.next_wait(at("2026-11-16T07:04:00"), self.p), ("morning", 6 * 60))

    def test_sent_slot_moves_to_the_next(self):
        self.brief("2026-11-16", ["morning"])
        slot, secs = W.next_wait(at("2026-11-16T07:20:00"), self.p)
        self.assertEqual(slot, "lunch")
        self.assertEqual(secs, (3 * 60 + 40 + W.GRACE_MIN) * 60)

    def test_too_far_ahead_is_left_to_the_crons(self):
        self.brief("2026-11-16", ["morning", "lunch"])
        self.assertIsNone(W.next_wait(at("2026-11-16T10:50:00"), self.p))   # 16:10 is 5h20 away

    def test_build_after_lunch_reaches_the_evening(self):
        self.brief("2026-11-16", ["morning", "lunch"])
        self.assertEqual(W.next_wait(at("2026-11-16T11:20:00"), self.p)[0], "evening")   # 4h50

    def test_long_missed_slot_is_skipped(self):
        self.brief("2026-11-16", [])
        slot, _ = W.next_wait(at("2026-11-16T08:30:00"), self.p)   # morning 90 min past
        self.assertEqual(slot, "lunch")

    def test_nothing_after_the_night_slot(self):
        self.brief("2026-11-16", ["morning", "lunch", "evening", "night"])
        self.assertIsNone(W.next_wait(at("2026-11-16T22:00:00"), self.p))

    def test_wait_fits_the_job_limit(self):
        self.assertLessEqual(W.MAX_WAIT_MIN + W.LOOP_MIN + W.POLL_MIN, 350)
        with open(W.WATCH_FILE) as f:
            self.assertIn("inputs.wait && 355", f.read())


class WaitAndKick(unittest.TestCase):
    def setUp(self):
        self.t = [at("2026-11-16T06:21:00")]
        self.posts, self.state = [], {"date": "2026-11-15", "slots": []}
        self.runs = []
        def sleep(s): self.t[0] = self.t[0] + W.timedelta(seconds=s)
        def brief(repo, token, path):
            with open(path, "w") as f: json.dump(self.state, f)
            return path
        def api(method, url, token, body=None):
            if method == "POST": self.posts.append(url); return {}
            return {"workflow_runs": list(self.runs)}
        self.sleep = sleep
        self._b, self._a = W._brief_now, W._api
        W._brief_now, W._api = brief, api
    def tearDown(self):
        W._brief_now, W._api = self._b, self._a

    def go(self, dry=False):
        return W.wait_and_kick("o/r", "t", "https://x/deploy.yml", dry, sleep=self.sleep, clock=lambda: self.t[0])

    def test_sleeps_then_dispatches(self):
        self.go()
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.t[0], at("2026-11-16T07:10:00"))

    def test_dry_run_does_not_dispatch(self):
        self.go(dry=True)
        self.assertEqual(self.posts, [])

    def test_a_running_build_is_left_to_send_then_stops(self):
        self.runs = [run("2026-11-16T07:05:00Z", "in_progress", "push")]
        calls = {"n": 0}
        orig = self.sleep
        def sleep(s):
            orig(s); calls["n"] += 1
            if calls["n"] == 2:   # the build sent it during the first poll gap
                self.state = {"date": "2026-11-16", "slots": ["morning"]}; self.runs = []
        self.sleep = sleep
        self.go()
        self.assertEqual(self.posts, [])
        self.assertLess(self.t[0], at("2026-11-16T07:30:00"))

    def test_gives_up_after_the_loop(self):
        self.runs = [run("2026-11-16T07:05:00Z", "in_progress", "push")]   # never finishes
        self.go()
        self.assertEqual(self.posts, [])
        self.assertLessEqual(self.t[0], at("2026-11-16T07:45:00"))
