"""API-Football: a used-up daily allowance stops calls for the run, a burst limit is retried."""
import io, json, os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sources as S


def reply(doc):
    return mock.MagicMock(read=lambda: json.dumps(doc).encode())


class Allowance(unittest.TestCase):
    def setUp(self):
        S._AF_SPENT[0] = False
        S._AF_CACHE.clear()
        S._AF_NEXT[0] = 0.0

    tearDown = setUp

    @mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"})
    def test_daily_limit_stops_further_calls(self):
        daily = {"errors": {"requests": "You have reached the request limit for the day"}, "response": []}
        with mock.patch.object(S.urllib.request, "urlopen", return_value=reply(daily)) as op, \
             mock.patch.object(S.time, "sleep"), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(S._af_get("/fixtures?league=1&season=2026"), [])
            self.assertEqual(S._af_get("/fixtures?league=2&season=2026"), [])
        self.assertEqual(op.call_count, 1)
        self.assertTrue(S._AF_SPENT[0])

    @mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "k"})
    def test_burst_limit_is_retried(self):
        burst = {"errors": {"rateLimit": "Too many requests"}, "response": []}
        ok = {"errors": [], "response": [{"id": 1}]}
        with mock.patch.object(S.urllib.request, "urlopen", side_effect=[reply(burst), reply(ok)]), \
             mock.patch.object(S.time, "sleep"):
            self.assertEqual(S._af_get("/fixtures?league=3&season=2026"), [{"id": 1}])
        self.assertFalse(S._AF_SPENT[0])


if __name__ == "__main__":
    unittest.main()
