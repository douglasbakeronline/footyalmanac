import io
import os
import sys
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings


class Resp:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def http(code):
    return urllib.error.HTTPError("http://x", code, "err", {}, io.BytesIO(b""))


class Flaky:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), 0

    def __call__(self, req, timeout=0):
        self.calls += 1
        o = self.outcomes.pop(0) if self.outcomes else OSError("down")
        if isinstance(o, Exception):
            raise o
        return Resp(o)


class GetRetry(unittest.TestCase):
    def setUp(self):
        groupings._GET_DOWN["run"] = 0

    def run_get(self, flaky, **kw):
        with mock.patch("urllib.request.urlopen", flaky), mock.patch("time.sleep", lambda s: None):
            return groupings.get("http://x/y?k=1", **kw)

    def test_blip_then_success(self):
        f = Flaky(http(503), OSError("reset"), b'{"a": 1}')
        self.assertEqual(self.run_get(f), {"a": 1})
        self.assertEqual(f.calls, 3)

    def test_404_not_retried(self):
        f = Flaky(http(404))
        with self.assertRaises(urllib.error.HTTPError):
            self.run_get(f)
        self.assertEqual(f.calls, 1)

    def test_gives_up_loudly(self):
        f = Flaky()
        with self.assertRaises(OSError):
            self.run_get(f)
        self.assertEqual(f.calls, groupings.GET_TRIES)

    def test_outage_stops_retrying(self):
        for _ in range(groupings.GET_DOWN_AFTER):
            with self.assertRaises(OSError):
                self.run_get(Flaky())
        f = Flaky()
        with self.assertRaises(OSError):
            self.run_get(f)
        self.assertEqual(f.calls, 1)

    def test_success_resets_outage_count(self):
        groupings._GET_DOWN["run"] = groupings.GET_DOWN_AFTER - 1
        self.run_get(Flaky(b"{}"))
        self.assertEqual(groupings._GET_DOWN["run"], 0)


if __name__ == "__main__":
    unittest.main()
