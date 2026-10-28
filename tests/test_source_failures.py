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

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = mock.patch.object(sources, "AF_CACHE_DIR", self.tmp.name)
        p.start()
        self.addCleanup(p.stop)
        for k in ("POL.csv", "GOOD.csv"):
            sources._FDX_CACHE.pop(k, None)

    def test_fdx_outage_uses_last_good_copy_loudly(self):
        up = Flaky(b"Date,Home\nx,y\n")
        with mock.patch.object(sources.urllib.request, "urlopen", up):
            self.assertEqual(sources._fdx_text("GOOD.csv"), "Date,Home\nx,y\n")
        sources._FDX_CACHE.pop("GOOD.csv")          # a new build
        down = Flaky(*[OSError("down")] * 3)
        with mock.patch.object(sources.urllib.request, "urlopen", down), \
                mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            self.assertEqual(sources._fdx_text("GOOD.csv"), "Date,Home\nx,y\n")
        self.assertIn("last good copy", err.getvalue())
        self.assertNotIn("GOOD.csv", sources._FDX_CACHE)

    def test_fdx_outage_without_copy_warns(self):
        down = Flaky(*[OSError("down")] * 3)
        with mock.patch.object(sources.urllib.request, "urlopen", down), \
                mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            self.assertEqual(sources._fdx_text("GOOD.csv"), "")
        self.assertIn("no earlier copy", err.getvalue())

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


class EspnDayTests(unittest.TestCase):
    DAY = __import__("datetime").date(2026, 10, 12)

    def setUp(self):
        sources._ESPN_DOWN["run"] = 0

    def run_day(self, *outcomes):
        f = Flaky(*outcomes)
        errs = []
        with mock.patch.object(sources.urllib.request, "urlopen", f):
            rows = sources._espn_day("eng.1", self.DAY, 5, errs, pause=0)
        return rows, errs, f.calls

    def test_blip_on_every_host_is_retried(self):
        rows, errs, calls = self.run_day(TimeoutError("a"), TimeoutError("b"),
                                         b'{"events": [{"id": 1}]}')
        self.assertEqual(rows, [{"id": 1}])
        self.assertEqual((errs, calls), ([], 3))

    def test_persistent_failure_is_reported_not_swallowed(self):
        rows, errs, calls = self.run_day(*[http(503)] * 4)
        self.assertEqual((rows, calls), ([], 4))
        self.assertEqual(len(errs), 1)
        self.assertIn("eng.1", errs[0])

    def test_404_not_retried(self):
        rows, errs, calls = self.run_day(http(404), http(404))
        self.assertEqual((rows, calls), ([], 2))
        self.assertEqual(len(errs), 1)

    def test_blocked_network_skips_retry(self):
        sources._ESPN_DOWN["run"] = sources._ESPN_DOWN_AT
        rows, errs, calls = self.run_day(OSError("x"), OSError("y"))
        self.assertEqual((rows, calls), ([], 2))


if __name__ == "__main__":
    unittest.main()
