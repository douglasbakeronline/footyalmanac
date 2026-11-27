"""The Sports Almanac emails (mailer.py, 23 Nov 2026). No network: every call
goes through a stub, and every file is a fixture made here."""
import io, os, sys, unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mailer as M

UK = ZoneInfo("Europe/London")
DAY = "2026-11-23"
NOW = datetime(2026, 11, 23, 7, 5, tzinfo=timezone.utc)
TOK = "11111111-2222-3333-4444-555555555555"


def pick(sport, home, away, conf, list_=True, start="2026-11-23T19:00:00Z", **kw):
    return {"sport": sport, "home": home, "away": away, "side": "h", "pick": home, "confidence": conf,
            "accuracy": {"cumHit": 0.9}, "list": list_, "reserve": not list_, "start": start, "timed": True,
            "comp": "Comp", "status": "upcoming", **kw}


def src(list_=None, reserve=None, scale=True):
    L = list_ if list_ is not None else [pick("football", f"Home{i}", f"Away{i}", 0.95 - i * 0.02) for i in range(12)]
    return {"daylist": {"date": DAY, "list": L, "reserve": reserve or [pick("football", "ResHome", "ResAway", 0.78, False)], "past": []},
            "groupings": {"days": [{"date": DAY, "groups": [], "cardShort": {"kind": "Card 2x", "band": [2, 3], "picks": 1, "need": 3, "why": "few"}}],
                          "listBooks": {}, "prices": {}, "contexts": {}},
            "data": {"days": []},
            "scale": {"book": "William Hill", "sports": {}, "days": [{"date": DAY, "picks": [
                {"key": "k1", "sport": "football", "tier": "list", "start": "2026-11-23T19:00:00Z", "home": "Home0", "away": "Away0",
                 "pick": "Home0", "side": "h", "conf": 0.95, "bet": "And over 2.5 goals", "chance": 0.5, "price": None, "est": 1.7},
                {"key": "k2", "sport": "football", "tier": "reserve", "start": "2026-11-23T19:00:00Z", "home": "ScaleRes", "away": "X",
                 "pick": "ScaleRes", "side": "h", "conf": 0.7, "bet": "And over 2.5 goals", "chance": 0.4}],
                "groups": [{"name": "Scale double", "legs": ["k1"], "chance": 0.5, "est": 1.7}]}]} if scale else None,
            "slip": None, "sports": None, "ledger": {"rows": []}, "grecord": {"days": []}, "record": {}}


class Schedule(unittest.TestCase):
    def at(self, y, mo, d, h, mi):
        return datetime(y, mo, d, h, mi, tzinfo=UK)

    def test_window_daily(self):
        self.assertEqual(M.due(self.at(2026, 11, 23, 7, 0)), ["daily"])
        self.assertEqual(M.due(self.at(2026, 11, 23, 6, 59)), [])
        self.assertEqual(M.due(self.at(2026, 11, 23, 11, 59)), ["daily"])
        self.assertEqual(M.due(self.at(2026, 11, 23, 12, 0)), [])

    def test_weekly_on_saturday_only(self):
        self.assertEqual(M.due(self.at(2026, 11, 28, 7, 30)), ["daily", "weekly"])
        self.assertEqual(M.due(self.at(2026, 11, 29, 7, 30)), ["daily"])
        self.assertEqual(M.due(self.at(2026, 11, 28, 18, 0)), [])

    def test_bst_and_gmt(self):
        # 06:30 UTC in July is 07:30 BST (due); 06:30 UTC in November is 06:30 GMT (not due)
        self.assertEqual(M.due(datetime(2026, 7, 6, 6, 30, tzinfo=timezone.utc).astimezone(UK)), ["daily"])
        self.assertEqual(M.due(datetime(2026, 11, 23, 6, 30, tzinfo=timezone.utc).astimezone(UK)), [])

    def test_week_is_saturday_to_friday_before(self):
        self.assertEqual(M.week_of("2026-11-28"), ("2026-11-21", "2026-11-27"))
        self.assertEqual(M.week_of("2026-11-23"), ("2026-11-14", "2026-11-20"))


class DailyList(unittest.TestCase):
    def test_list_not_reserve(self):
        m = M.daily_email(DAY, src(), now=NOW)
        self.assertIn("Home0", m["html"])
        self.assertNotIn("ResHome", m["html"])
        self.assertNotIn("ResHome", m["text"])

    def test_group_order(self):
        t = M.daily_email(DAY, src(), now=NOW)["text"]
        a, b = t.index("STRONGEST TODAY"), t.index("ALSO ON THE LIST")
        self.assertLess(a, t.index("Home0 "))
        self.assertLess(t.index("Home4 "), b)          # five at 85%+ in Strongest today
        self.assertLess(b, t.index("Home5 "))
        self.assertLess(b, t.index("Home10 "))
        self.assertNotIn("GROUP B", t)
        self.assertIn("STRONGEST TODAY · 5 picks at 85% or better", t)

    def test_group_a_never_padded(self):
        items = [{"confidence": c} for c in (0.9, 0.84, 0.83)]
        g = M.groups_of(items)
        self.assertEqual([(n, len(x)) for n, _, x in g], [("Strongest today", 1), ("Also on the list", 2)])

    def test_college_basketball_needs_a_price(self):
        L = [pick("ncaab", "Duke", "Rival", 0.9, start="2026-11-23T23:00:00Z", full={"line": {"spread": -15}, "neutral": False}),
             pick("ncaab", "Kansas", "Rival2", 0.9, start="2026-11-23T23:00:00Z", full={"line": {"spread": -15}, "neutral": False})]
        s = src(L)
        s["groupings"]["listBooks"] = {"ncaab|duke|rival": {"h": 1.06}}
        items, off = M.list_items(s, DAY, NOW)
        self.assertEqual([i["pick"] for i in items], ["Duke"])
        self.assertEqual(off, 1)
        # 27 Nov 2026: any price on file counts, not William Hill's alone
        s["groupings"]["prices"] = {"ncaab|kansas|rival2": {"o": 1.08}}
        items, off = M.list_items(s, DAY, NOW)
        self.assertEqual(sorted(i["pick"] for i in items), ["Duke", "Kansas"])
        self.assertEqual(off, 0)

    def test_empty_day_says_so(self):
        m = M.daily_email(DAY, src([]), now=NOW)
        self.assertIn("Nothing clears the Daily List's bar today", m["text"])
        self.assertIn("nothing clears the bar", m["subject"])

    def test_scale_only_for_scale_subscribers(self):
        s = src()
        plain, sc = M.daily_email(DAY, s, False, NOW), M.daily_email(DAY, s, True, NOW)
        self.assertNotIn("SCALE", plain["text"])
        self.assertIn("SCALE", sc["text"])
        self.assertIn("≈ 1.70 estimate", sc["text"])
        self.assertNotIn("ScaleRes", sc["text"])    # the Daily List tier only

    def test_card_reason_when_none(self):
        self.assertIn("No Card group today", M.daily_email(DAY, src(), now=NOW)["text"])


class Sending(unittest.TestCase):
    def mails(self):
        return M.build("daily", DAY, src(), NOW)

    def test_one_email_per_recipient_with_its_own_unsubscribe(self):
        m = M.message("a@example.com", TOK, self.mails()["plain"])
        self.assertEqual(m["to"], ["a@example.com"])
        self.assertEqual(m["headers"]["List-Unsubscribe"], f"<{M.UNSUB_URL.format(t=TOK)}>")
        self.assertEqual(m["headers"]["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click")
        self.assertIn(f"#mailer?manage={TOK}", m["html"])
        self.assertNotIn(M.MANAGE_MARK, m["html"] + m["text"])
        self.assertNotIn(M.UNSUB_MARK, m["html"] + m["text"])

    def test_batches_of_100(self):
        calls = []
        post = lambda url, body, h: (calls.append(len(body)) or (200, {}))
        recips = [{"email": f"r{i}@example.com", "manage_token": TOK, "scale": i % 2 == 0} for i in range(250)]
        out = io.StringIO()
        sent, failed = M.send("k", "daily", DAY, recips, self.mails(), post, lambda s: None, lambda *a: print(*a, file=out))
        self.assertEqual(calls, [100, 100, 50])
        self.assertEqual((sent, failed), (250, 0))
        self.assertNotIn("@example.com", out.getvalue())

    def test_retry_then_stop_on_success(self):
        seen = []
        codes = iter([429, 503, 200])
        post = lambda url, body, h: (seen.append(h["Idempotency-Key"]) or (next(codes), {}))
        self.assertEqual(M.send_batch("k", [{}], "id-1", post, lambda s: None), 200)
        self.assertEqual(seen, ["id-1"] * 3)

    def test_no_retry_on_client_error(self):
        n = []
        self.assertEqual(M.send_batch("k", [{}], "i", lambda u, b, h: (n.append(1) or (422, None)), lambda s: None), 422)
        self.assertEqual(len(n), 1)

    def test_scale_variant_goes_to_scale_subscribers(self):
        bodies = []
        post = lambda url, body, h: (bodies.extend(body) or (200, {}))
        recips = [{"email": "s@example.com", "manage_token": TOK, "scale": True}, {"email": "p@example.com", "manage_token": TOK, "scale": False}]
        M.send("k", "daily", DAY, recips, self.mails(), post, lambda s: None, lambda *a: None)
        self.assertIn("SCALE", bodies[0]["text"])
        self.assertNotIn("SCALE", bodies[1]["text"])


class Run(unittest.TestCase):
    def setUp(self):   # 25 Nov 2026: a sent daily email is kept (mailer.keep); never in the repo's folder from a test
        import tempfile
        self._tmp = tempfile.TemporaryDirectory(); self._old = M.MAIL_ARCHIVE; M.MAIL_ARCHIVE = self._tmp.name

    def tearDown(self):
        M.MAIL_ARCHIVE = self._old; self._tmp.cleanup()

    def test_silent_without_secrets(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(M.run(now=NOW, env={}, post=lambda *a: self.fail("no network")), 0)
            self.assertEqual(M.run(now=NOW, env={"RESEND_API_KEY": "x"}, post=lambda *a: self.fail("no network")), 0)
        self.assertIn("not configured", out.getvalue())

    def test_full_run_claims_once_and_never_prints_an_address(self):
        calls = []

        def post(url, body, h):
            calls.append(url)
            if url.endswith("almanac_mail_list"): return 200, [{"email": "who@example.com", "manage_token": TOK, "scale": True}]
            if url.endswith("almanac_mail_claim"): return 200, True
            return 200, {"data": []}
        out = io.StringIO()
        with redirect_stdout(out):
            M.run(now=NOW, env={"RESEND_API_KEY": "k", "MAILER_SECRET": "s"}, post=post, sleep=lambda s: None, src=src())
        self.assertEqual([u.rsplit("/", 1)[-1] for u in calls], ["almanac_mail_list", "almanac_mail_claim", "batch"])
        self.assertIn("1 sent", out.getvalue())
        self.assertNotIn("who@example.com", out.getvalue())

    def test_claimed_elsewhere_sends_nothing(self):
        calls = []

        def post(url, body, h):
            calls.append(url)
            if url.endswith("almanac_mail_list"): return 200, [{"email": "who@example.com", "manage_token": TOK, "scale": False}]
            return 200, False
        with redirect_stdout(io.StringIO()):
            M.run(now=NOW, env={"RESEND_API_KEY": "k", "MAILER_SECRET": "s"}, post=post, sleep=lambda s: None, src=src())
        self.assertFalse(any(u.endswith("/emails/batch") for u in calls))

    def test_outside_window_and_stale_daylist(self):
        out = io.StringIO()
        with redirect_stdout(out):
            M.run(now=datetime(2026, 11, 23, 13, 0, tzinfo=timezone.utc), env={"RESEND_API_KEY": "k", "MAILER_SECRET": "s"},
                  post=lambda *a: self.fail("no network"), src=src())
            s = src(); s["daylist"]["date"] = "2026-11-22"
            M.run(now=NOW, env={"RESEND_API_KEY": "k", "MAILER_SECRET": "s"}, post=lambda *a: self.fail("no network"), src=s)
        self.assertIn("outside the 07:00-11:59", out.getvalue())
        self.assertIn("daily skipped", out.getvalue())


if __name__ == "__main__":
    unittest.main()


class SevenToSeven(unittest.TestCase):
    """24 Nov 2026 (Douglas: "Some of the games on the mailer already played ...
    can it be a 07.00-07.00 24 hour period"): the 07:00 email carries the picks
    starting from 07:00 UK that day to 07:00 UK the next, the overnight games of
    the next UK day included (daylist.json "early")."""
    def test_window(self):
        L = [pick("nba", "Played", "X", 0.9, start="2026-11-23T03:00:00Z"),
             pick("football", "Evening", "Y", 0.88, start="2026-11-23T19:00:00Z"),
             pick("tennis", "Untimed", "Z", 0.86, start="2026-11-23T12:00:00Z", timed=False)]
        s = src(L)
        s["daylist"]["early"] = [pick("nba", "Overnight", "W", 0.87, start="2026-11-24T01:00:00Z"),
                                 pick("nba", "TooLate", "V", 0.9, start="2026-11-24T07:30:00Z")]
        items, _ = M.list_items(s, DAY, NOW)
        self.assertEqual(sorted(i["pick"] for i in items), ["Evening", "Overnight", "Untimed"])

    def test_window_in_summer_time(self):
        self.assertEqual(M.window(DAY), (datetime(2026, 11, 23, 7, tzinfo=timezone.utc), datetime(2026, 11, 24, 7, tzinfo=timezone.utc)))
        self.assertEqual(M.window("2026-07-01")[0], datetime(2026, 7, 1, 6, tzinfo=timezone.utc))
