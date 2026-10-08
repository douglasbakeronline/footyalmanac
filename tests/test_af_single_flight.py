"""API-Football: one call per question, however many threads ask (7 Oct 2026).

Unlocked, parallel league threads each built the same day pool, and the
first build of 7 Oct spent 2,717 calls in nametest.py alone."""
import json, os, sys, tempfile, threading, time, unittest
from datetime import date, timedelta
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sources as S


class _Resp:
    def __init__(self, doc): self._b, self.headers = json.dumps(doc).encode(), {"x-ratelimit-requests-remaining": "7000"}
    def read(self): return self._b


class SingleFlight(unittest.TestCase):
    def _patches(self, d, opener):
        return [mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}),
                mock.patch.object(S, "_spent_marker", return_value=os.path.join(d, "spent")),
                mock.patch.object(S, "_AF_SPENT", [False]), mock.patch.object(S, "_AF_CACHE", {}),
                mock.patch.object(S, "_AF_PATH_LOCKS", {}), mock.patch.object(S, "_AF_POOL", {}),
                mock.patch.object(S, "_AF_PACE", 0), mock.patch.object(S, "AF_CACHE_DIR", d),
                mock.patch.object(S, "AF_USAGE", {"calls": 0, "left": None}),
                mock.patch.object(S.urllib.request, "urlopen", side_effect=opener)]

    def _run(self, patches, fn, n=8):
        for p in patches: p.start()
        try:
            ts = [threading.Thread(target=fn) for _ in range(n)]
            [t.start() for t in ts]; [t.join() for t in ts]
        finally:
            for p in reversed(patches): p.stop()

    def test_same_path_is_one_call(self):
        calls = []
        def opener(req, timeout=None):
            calls.append(req.full_url); time.sleep(0.05)
            return _Resp({"response": [1], "errors": []})
        with tempfile.TemporaryDirectory() as d:
            self._run(self._patches(d, opener), lambda: S._af_get("/fixtures?date=2026-10-07"))
        self.assertEqual(len(calls), 1)

    def test_pool_built_once_each_day_once(self):
        calls = []
        def opener(req, timeout=None):
            calls.append(req.full_url); time.sleep(0.01)
            return _Resp({"response": [], "errors": []})
        end = date.today(); start = end - timedelta(days=9)
        with tempfile.TemporaryDirectory() as d:
            self._run(self._patches(d, opener), lambda: S.af_day_pool(start, end))
        self.assertEqual(len(calls), 10)
        self.assertEqual(len(set(calls)), 10)
        # newest day asked first: the pool fetches on 4 threads, so it is among
        # the first 4 requests; which one lands first is a race (it failed
        # 15 in 40 runs asserting calls[0], 8 Oct 2026)
        self.assertTrue(any(end.isoformat() in c for c in calls[:4]), calls[:4])

    def test_spent_reads_zero_left(self):
        def opener(req, timeout=None):
            return _Resp({"response": [], "errors": {"requests": "You have reached the request limit for the day"}})
        with tempfile.TemporaryDirectory() as d:
            ps = self._patches(d, opener)
            for p in ps: p.start()
            try:
                S._af_get("/fixtures?date=2026-10-07")
                self.assertEqual(S.AF_USAGE["left"], 0)
            finally:
                for p in reversed(ps): p.stop()


if __name__ == "__main__":
    unittest.main()
