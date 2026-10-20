"""Regression tests for the office sprint's task picker (agents/pick_task.py).

    python3 -m unittest tests.test_pick_task -v

Standard library only, no network: the HQ backlog is read from a temporary file.
"""
import json, os, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "agents"))
import pick_task as T


def backlog_file(tasks, age_h=1):
    made = (datetime.now(timezone.utc) - timedelta(hours=age_h)).isoformat(timespec="minutes")
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"generated": made, "tasks": tasks}, f); f.close()
    return "file://" + f.name


class TestHQBacklog(unittest.TestCase):
    def tearDown(self): T.HQ_BACKLOG = os.environ.get("HQ_BACKLOG", T.HQ_BACKLOG)

    def test_reads_valid_tasks(self):
        T.HQ_BACKLOG = backlog_file([{"key": "hq-list-cfb", "owner": "sports", "title": "CFB", "brief": "b"}])
        got = T.hq_backlog()
        self.assertEqual([c[0] for c in got], ["hq-list-cfb"]); self.assertEqual(got[0][1], "sports")

    def test_drops_unknown_owner_and_foreign_keys(self):
        T.HQ_BACKLOG = backlog_file([{"key": "hq-x", "owner": "nobody", "title": "t", "brief": "b"},
                                     {"key": "build-failure", "owner": "engineer", "title": "t", "brief": "b"}])
        self.assertEqual(T.hq_backlog(), [])

    def test_stale_backlog_is_ignored(self):
        T.HQ_BACKLOG = backlog_file([{"key": "hq-a", "owner": "calib", "title": "t", "brief": "b"}], age_h=72)
        self.assertEqual(T.hq_backlog(), [])

    def test_missing_backlog_is_ignored(self):
        T.HQ_BACKLOG = "file:///nonexistent/backlog.json"
        self.assertEqual(T.hq_backlog(), [])


class TestAgentPick(unittest.TestCase):
    CANDS = [("hq-a", "sports", "A", "a"), ("hq-b", "sports", "B", "b"), ("hq-c", "calib", "C", "c")]

    def test_first_free_task_in_order(self):
        self.assertEqual(T.agent_pick("sports", self.CANDS, set())[1][0], "hq-a")
        self.assertEqual(T.agent_pick("sports", self.CANDS, {"hq-a"})[1][0], "hq-b")

    def test_standing_task_ranks_after_live_work(self):
        i, c = T.agent_pick("engineer", self.CANDS, set())
        self.assertEqual(c[0], T.STANDING["engineer"][0]); self.assertGreaterEqual(i, len(self.CANDS))

    def test_nothing_free(self):
        self.assertEqual(T.agent_pick("engineer", [], {T.STANDING["engineer"][0]}), (None, None))


if __name__ == "__main__":
    unittest.main()
