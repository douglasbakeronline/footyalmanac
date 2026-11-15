"""The context check (11 Nov 2026, context_review.py, groupings.CARD_CONTEXT):
replies parsed, an unsourced "against" never vetoes, reads are due once and
again near the start, the veto keeps a pick off the Card. No network."""
import json, os, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import context_review as CX
import groupings as G

NOW = datetime(2026, 11, 14, 9, 0, tzinfo=timezone.utc)


def reply(obj):
    return {"content": [{"type": "server_tool_use", "name": "web_search"},
                        {"type": "text", "text": "Here you go:\n" + json.dumps(obj)}]}


SRC = [{"title": "BBC Sport", "url": "https://www.bbc.co.uk/sport/football/1"}]


def leg(pick="Almere City", when=NOW + timedelta(hours=6), pm=0.68):
    return {"sport": "football", "event": f"{pick} v Other", "pick": pick, "home": pick, "away": "Other",
            "comp": "Eerste Divisie", "when": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "date": when.date().isoformat(),
            "odds": 1.42, "pModel": pm}


class Parse(unittest.TestCase):
    def test_reads_the_json(self):
        v = CX.parse(reply({"verdict": "Against", "reason": "Top scorer out (BBC)", "numbers": "1st v 18th",
                            "news": "x", "sources": SRC}))
        self.assertEqual(v["verdict"], "against"); self.assertEqual(v["sources"][0]["url"], SRC[0]["url"])

    def test_unsourced_against_is_only_caution(self):
        self.assertEqual(CX.parse(reply({"verdict": "against", "reason": "feels off", "sources": []}))["verdict"], "caution")

    def test_unreadable_is_none(self):
        self.assertIsNone(CX.parse({"content": [{"type": "text", "text": "no json here"}]}))
        self.assertIsNone(CX.parse(reply({"verdict": "maybe"})))


class Due(unittest.TestCase):
    def test_first_read_then_one_near_the_start(self):
        l = leg()
        self.assertTrue(CX.due(None, l, NOW))
        old = {"at": "2026-11-14T09:00:00Z"}
        self.assertFalse(CX.due(old, l, NOW + timedelta(hours=1)))
        self.assertTrue(CX.due(old, l, NOW + timedelta(hours=4)))      # within 3 hours of a 15:00 start
        self.assertFalse(CX.due({"at": "2026-11-14T13:00:00Z"}, l, NOW + timedelta(hours=4, minutes=30)))

    def test_not_after_the_start_or_too_far_ahead(self):
        self.assertFalse(CX.due(None, leg(when=NOW - timedelta(minutes=5)), NOW))
        self.assertFalse(CX.due(None, leg(when=NOW + timedelta(hours=40)), NOW))


class Review(unittest.TestCase):
    def test_review_attaches_and_keeps_verdicts(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d):
            calls = []
            def post(body): calls.append(body); return reply({"verdict": "clear", "reason": "fine", "sources": SRC})
            L = [leg("A"), leg("B")]
            rep = {}
            self.assertEqual(CX.review(L, NOW, rep, post=post), 2)
            self.assertTrue(all(l["context"]["verdict"] == "clear" for l in L))
            self.assertEqual(rep["context"]["calls"], 2)
            L2 = [leg("A"), leg("B")]
            self.assertEqual(CX.review(L2, NOW + timedelta(minutes=30), {}, post=post), 0)   # kept, not re-read
            self.assertTrue(all(l["context"]["verdict"] == "clear" for l in L2))

    def test_silent_without_a_key(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d), mock.patch.dict(os.environ, {}, clear=True):
            L = [leg()]; rep = {}
            self.assertEqual(CX.review(L, NOW, rep), 0)
            self.assertNotIn("context", L[0]); self.assertFalse(rep["context"]["on"])

    def test_a_failed_call_is_logged_not_raised(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d):
            def post(body): raise TimeoutError("slow")
            rep = {}
            CX.review([leg()], NOW, rep, post=post)
            self.assertTrue(any("TimeoutError" in e for e in rep["errors"]))


class Veto(unittest.TestCase):
    def model_leg(self):
        l = {"sport": "football", "event": "Ajax v Other", "pick": "Ajax", "code": "en.1", "comp": "Premier League",
             "odds": 1.50, "est": False, "fair": 0.64, "pModel": 0.68, "why": None, "hit": 0.8}
        return l

    def test_against_keeps_the_pick_off_the_card(self):
        self.assertTrue(G.core_league("en.1"))
        l = self.model_leg()
        self.assertIsNone(G.card_fault(l))
        l["context"] = {"verdict": "against", "reason": "five starters rested (BBC)"}
        self.assertIn("context check reads against", G.card_fault(l))
        l["context"] = {"verdict": "caution", "reason": "x"}
        self.assertIsNone(G.card_fault(l))
        with mock.patch.object(G, "CARD_CONTEXT", False):
            l["context"] = {"verdict": "against"}
            self.assertIsNone(G.card_fault(l))

    def test_rule_is_9_or_later(self):
        self.assertGreaterEqual(G.CARD_RULE, 9); self.assertTrue(G.CARD_CONTEXT)
        self.assertIn("context", G.POOL_KEYS)


if __name__ == "__main__":
    unittest.main()


class CardPicks(unittest.TestCase):
    """11 Nov 2026: the day's backed picks with their verdicts, for the page."""
    def test_lists_backed_picks_and_the_vetoed(self):
        base = {"sport": "football", "code": "en.1", "comp": "Premier League", "odds": 1.50, "est": False,
                "fair": 0.64, "pModel": 0.68, "why": None, "hit": 0.8, "date": "2026-11-14"}
        ok = dict(base, event="A v B", pick="A", when="2026-11-14T15:00:00Z", context={"verdict": "clear"})
        off = dict(base, event="C v D", pick="C", when="2026-11-14T17:30:00Z", context={"verdict": "against", "reason": "x"})
        low = dict(base, event="E v F", pick="E", when="2026-11-14T15:00:00Z", pModel=0.50)
        done = dict(base, event="G v H", pick="G", when="2026-11-14T08:00:00Z")
        ps = G.card_picks([ok, off, low, done], "2026-11-14", NOW)
        self.assertEqual([p["pick"] for p in ps], ["A", "C"])
        self.assertEqual(ps[1]["context"]["verdict"], "against")


class Budget(unittest.TestCase):
    """12 Nov 2026: Daily List reads within a daily cap, by priority."""
    def test_priority_card_then_sport_then_strongest(self):
        a = dict(leg("A"), sport="ncaab", pModel=0.95)
        b = dict(leg("B"), sport="football", pModel=0.76)
        c = dict(leg("C"), sport="nba", pModel=0.90, cxCard=True)
        d = dict(leg("D"), sport="football", pModel=0.88)
        self.assertEqual([x["pick"] for x in sorted([a, b, c, d], key=CX.priority)], ["C", "D", "B", "A"])

    def test_models_by_sport(self):
        self.assertEqual(CX.model_for({"sport": "football"}), CX.MODEL)
        self.assertEqual(CX.model_for({"sport": "nba"}), CX.MODEL)
        self.assertEqual(CX.model_for({"sport": "tennis"}), CX.CHEAP_MODEL)
        self.assertEqual(CX.model_for({"sport": "tennis", "cxCard": True}), CX.MODEL)

    def test_daily_cap_holds_across_builds(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d), mock.patch.object(CX, "DAILY_READS", 3):
            post = lambda body: reply({"verdict": "clear", "reason": "ok", "sources": SRC})
            self.assertEqual(CX.review([leg(f"P{i}") for i in range(5)], NOW, {}, post=post), 3)
            self.assertEqual(CX.review([leg(f"Q{i}") for i in range(5)], NOW + timedelta(hours=1), {}, post=post), 0)
            self.assertEqual(CX.review([leg(f"R{i}") for i in range(5)], NOW + timedelta(days=1), {}, post=post), 0)  # those picks have started by then


MSG = ('{"type":"error","error":{"type":"invalid_request_error","message":"You have reached your specified API '
       'usage limits. You will regain access on 2026-12-01 at 00:00 UTC."}}')


class UsageLimitPause(unittest.TestCase):
    """14 Nov 2026: the API key's monthly limit stops the check until the
    time the API names, and says so, instead of failing every pick."""

    def test_limit_until_reads_the_time(self):
        self.assertEqual(CX.limit_until(MSG, NOW), "2026-12-01T00:00Z")
        self.assertEqual(CX.limit_until("usage limit reached", NOW), "2026-11-15T09:00Z")
        self.assertIsNone(CX.limit_until("tool web_search_20250305 not supported", NOW))

    def test_http_limit_raises_usage_limit(self):
        import io, urllib.error
        err = urllib.error.HTTPError(CX.API, 400, "Bad Request", {}, io.BytesIO(MSG.encode()))
        with mock.patch("urllib.request.urlopen", side_effect=err) as up:
            with self.assertRaises(CX.UsageLimit):
                CX.call(leg(), "k")
            self.assertEqual(up.call_count, 1)          # no retry with another tool

    def test_pause_stops_calls_and_resumes(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d):
            calls = []
            def limited(body): calls.append(1); raise CX.UsageLimit(MSG)
            rep = {}
            self.assertEqual(CX.review([leg(f"P{i}") for i in range(4)], NOW, rep, post=limited), 0)
            self.assertEqual(len(calls), 1)                              # stopped after the first refusal
            self.assertEqual(rep["context"]["paused"], "2026-12-01T00:00Z")
            self.assertTrue(any("paused until" in e for e in rep["errors"]))
            self.assertEqual(CX.ledger_load()[CX.PAUSE_KEY], "2026-12-01T00:00Z")
            rep2 = {}
            self.assertEqual(CX.review([leg(f"Q{i}") for i in range(4)], NOW + timedelta(hours=1), rep2, post=limited), 0)
            self.assertEqual(len(calls), 2)                              # one probe a build while paused
            self.assertEqual(rep2["context"]["paused"], "2026-12-01T00:00Z")
            ok = lambda body: (calls.append(1), reply({"verdict": "clear", "reason": "ok", "sources": SRC}))[1]
            later = datetime(2026, 12, 1, 9, 0, tzinfo=timezone.utc)
            rep3 = {}
            self.assertEqual(CX.review([leg("R", when=later + timedelta(hours=3))], later, rep3, post=ok), 1)
            self.assertIsNone(rep3["context"]["paused"])
            self.assertNotIn(CX.PAUSE_KEY, CX.ledger_load())

    def test_ledger_keeps_fourteen_days_and_the_pause(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d):
            led = {f"2026-10-{i:02d}": 1 for i in range(1, 21)}; led[CX.PAUSE_KEY] = "2026-12-01T00:00Z"
            CX.ledger_save(led)
            got = CX.ledger_load()
            self.assertEqual(len([k for k in got if k[:1].isdigit()]), 14)
            self.assertEqual(got[CX.PAUSE_KEY], "2026-12-01T00:00Z")

    def test_probe_resumes_when_the_limit_is_raised(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(CX, "ARCHIVE", d):
            CX.ledger_save({CX.PAUSE_KEY: "2026-12-01T00:00Z"})
            ok = lambda body: reply({"verdict": "clear", "reason": "ok", "sources": SRC})
            rep = {}
            self.assertEqual(CX.review([leg(f"P{i}") for i in range(3)], NOW, rep, post=ok), 3)
            self.assertIsNone(rep["context"]["paused"])
            self.assertNotIn(CX.PAUSE_KEY, CX.ledger_load())
