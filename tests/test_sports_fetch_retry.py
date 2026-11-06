import io
import os
import sys
import unittest
import urllib.error
from datetime import date
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports
import build_tennis


class Resp:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body


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


D = date(2026, 11, 5)
OK = b'{"events": [{"id": "1"}]}'


def call(fn, flaky, *args):
    errs = []
    with mock.patch("urllib.request.urlopen", flaky), mock.patch("time.sleep", lambda s: None):
        out = fn(*args, errs)
    return out, errs


class SportsDayRetry(unittest.TestCase):
    def test_blip_on_every_host_is_retried(self):
        n = len(sports.ESPN_HOSTS)
        f = Flaky(*[OSError("reset")] * n, OK)
        out, errs = call(lambda p, d, e: sports._day(p, d, e), f, "football/nfl", D)
        self.assertEqual(out, [{"id": "1"}])
        self.assertEqual(len(errs), n)

    def test_persistent_failure_is_none_not_empty(self):
        f = Flaky()
        out, errs = call(lambda p, d, e: sports._day(p, d, e), f, "football/nfl", D)
        self.assertIsNone(out)
        self.assertEqual(f.calls, 2 * len(sports.ESPN_HOSTS))
        self.assertTrue(errs)

    def test_404_not_retried(self):
        n = len(sports.ESPN_HOSTS)
        f = Flaky(*[http(404)] * n)
        out, _ = call(lambda p, d, e: sports._day(p, d, e), f, "football/nfl", D)
        self.assertIsNone(out)
        self.assertEqual(f.calls, n)


class TennisDayRetry(unittest.TestCase):
    def test_blip_then_success(self):
        n = len(build_tennis.ESPN_HOSTS)
        f = Flaky(*[http(503)] * n, OK)
        out, errs = call(lambda t, d, e: build_tennis._get_day(t, d, 5, e), f, "atp", D)
        self.assertEqual(out, [{"id": "1"}])
        self.assertEqual(len(errs), n)

    def test_404_not_retried(self):
        n = len(build_tennis.ESPN_HOSTS)
        f = Flaky(*[http(404)] * n)
        out, _ = call(lambda t, d, e: build_tennis._get_day(t, d, 5, e), f, "atp", D)
        self.assertEqual(out, [])
        self.assertEqual(f.calls, n)


if __name__ == "__main__":
    unittest.main()
