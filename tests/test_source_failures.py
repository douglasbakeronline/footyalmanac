import io
import os
import sys
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sources


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
        o = self.outcomes.pop(0)
        if isinstance(o, Exception):
            raise o
        return Resp(o)


@mock.patch.object(sources.time, "sleep", lambda s: None)
class SourceFailureTests(unittest.TestCase):
    def setUp(self):
        sources._FDX_CACHE.clear()

    def test_retries_then_succeeds(self):
        f = Flaky(TimeoutError("slow"), http(503), b"ok")
        with mock.patch.object(sources.urllib.request, "urlopen", f):
            self.assertEqual(sources._open("http://x", 5), b"ok")
        self.assertEqual(f.calls, 3)

    def test_404_not_retried(self):
        f = Flaky(http(404))
        with mock.patch.object(sources.urllib.request, "urlopen", f):
            with self.assertRaises(urllib.error.HTTPError):
                sources._open("http://x", 5)
        self.assertEqual(f.calls, 1)

    def test_gives_up_loudly(self):
        f = Flaky(*[OSError("down")] * 3)
        with mock.patch.object(sources.urllib.request, "urlopen", f), \
                mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            with self.assertRaises(OSError):
                sources._open("http://x", 5)
        self.assertIn("source failed after 3 tries", err.getvalue())

    def test_fdx_outage_not_cached_as_empty(self):
        down = Flaky(*[OSError("down")] * 3)
        with mock.patch.object(sources.urllib.request, "urlopen", down), \
                mock.patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(sources._fdx_text("POL.csv"), "")
        self.assertNotIn("POL.csv", sources._FDX_CACHE)
        up = Flaky(b"Date,Home\n")
        with mock.patch.object(sources.urllib.request, "urlopen", up):
            self.assertEqual(sources._fdx_text("POL.csv"), "Date,Home\n")

    def test_fdx_missing_file_cached(self):
        f = Flaky(http(404))
        with mock.patch.object(sources.urllib.request, "urlopen", f):
            self.assertEqual(sources._fdx_text("NOPE.csv"), "")
            self.assertEqual(sources._fdx_text("NOPE.csv"), "")
        self.assertEqual(f.calls, 1)


if __name__ == "__main__":
    unittest.main()
