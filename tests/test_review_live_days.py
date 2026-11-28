"""The nightly Card review's live-days section (tools/card_review_post.live_days_section, 13 Nov 2026)."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import card_review_post as C


def day(d, groups, folder):
    with open(os.path.join(folder, f"{d}.json"), "w") as f: json.dump({"date": d, "groups": groups}, f)


class TestLiveDays(unittest.TestCase):
    def test_run_of_empty_days_and_filters(self):
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-09", [{"name": "Card 2x", "rule": 6}, {"name": "Model 2x", "rule": 6}], t)
            day("2026-11-10", [{"name": "Card 2x", "rule": 6, "wide": True}, {"name": "Card 3x", "rule": 6}], t)
            day("2026-11-12", [{"name": "Model 3x", "rule": 8}], t)   # paper only: not a Card group
            day("2026-11-14", [{"name": "Card 2x", "rule": 11}], t)   # today, not finished: not read
            with open(os.path.join(t, "briefed.json"), "w") as f: json.dump({}, f)
            out = "\n".join(C.live_days_section(t, today_="2026-11-14", days=7))
        self.assertIn("2026-11-07 to 2026-11-13", out)
        self.assertIn("Days with a group: 2 of 7; groups 2;", out)
        self.assertIn("last group published for 2026-11-10", out)
        self.assertIn("**3 days running with no Card group (to 2026-11-13).**", out)

    def test_no_flag_under_three_days(self):
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-12", [{"name": "Card 2x", "rule": 11}], t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-14", days=7))
        self.assertNotIn("days running", out)
        self.assertIn("Rules: 11.", out)

    def test_missing_folder(self):
        out = "\n".join(C.live_days_section("/nonexistent", today_="2026-11-14", days=3))
        self.assertIn("Days with a group: 0 of 3", out)
        self.assertIn("no day on file", out)

    def test_two_day_groups_and_the_model_card_record(self):
        # 15 Nov 2026: span groups named; rules 7+ read on their own from the record
        rec = {"cardByRule": {"6": {"groups": 5, "settled": 5, "won": 3, "expected": 1.97, "unitsStaked": 10, "unitsReturned": 13.28},
                              "11": {"groups": 2, "settled": 1, "won": 1, "expected": 0.42, "unitsStaked": 2, "unitsReturned": 4.72}}}
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-13", [{"name": "Card 2x", "rule": 11, "span": ["2026-11-13", "2026-11-14"]}], t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-15", days=3, record=rec))
        self.assertIn("Two-day groups (`CARD_SPAN`): 1.", out)
        self.assertIn("The model's-picks Card (rules 11, from 11 Nov): 2 group(s), 1 settled, 1 won v 0.42 expected, +136.0% at the page's stakes.", out)

    def test_model_card_record_none_settled(self):
        rec = {"cardByRule": {"11": {"groups": 1, "settled": 0, "won": 0, "expected": 0, "unitsStaked": 0, "unitsReturned": 0}}}
        out = "\n".join(C.live_days_section("/nonexistent", today_="2026-11-15", days=3, record=rec))
        self.assertIn("1 group(s), 0 settled, 0 won v 0.00 expected; none settled yet.", out)
        self.assertNotIn("Two-day", out)
        out = "\n".join(C.live_days_section("/nonexistent", today_="2026-11-15", days=3, record={}))
        self.assertNotIn("model's-picks", out)


def pub(d, items, folder):
    os.makedirs(os.path.join(folder, "published"), exist_ok=True)
    with open(os.path.join(folder, "published", f"{d}.json"), "w") as f: json.dump({"day": d, "items": items}, f)


def leg(event, pick): return {"event": event, "pick": pick}


class TestShownNotArchived(unittest.TestCase):
    """26 Nov 2026: a Card group the page showed that never reached the
    archive (publog.py) is named, and its day is not counted as empty."""

    def test_lost_and_unarchived_groups_break_the_empty_run(self):
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-20", [{"name": "Card 2x", "rule": 14}], t)
            pub("2026-11-22", {"lost|Card 2x|1": {"kind": "card", "source": "build-log", "lost": True,
                                                   "name": "Card 2x", "picks": ["Golden State Warriors", "Toluca"]}}, t)
            # a build-logged Card group, its first pick long started, not in the (missing) day archive
            pub("2026-11-23", {"card|x": {"kind": "card", "source": "build", "start": "2026-11-23T15:00:00Z",
                                          "last": {"name": "Card 2x", "legs": [leg("A v B", "A"), leg("C v D", "D")]}}}, t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-25", days=5, now="2026-11-25T04:00:00Z", ledger=[]))
        self.assertIn("Days with a group: 1 of 5;", out)
        self.assertIn("The page also showed 2 Card group(s) that never reached the archive", out)
        self.assertIn("2026-11-22 Card 2x (Golden State Warriors pending, Toluca pending): not settled", out)
        self.assertIn("2026-11-23 Card 2x (A pending, D pending): not settled", out)
        self.assertIn("On the results ledger: 0 won, 0 lost, 2 not settled.", out)
        self.assertNotIn("days running", out)   # 24 Nov alone is empty

    def test_archived_withdrawn_paper_and_open_groups_are_not_named(self):
        g = {"name": "Card 2x", "rule": 14, "legs": [leg("A v B", "A"), leg("C v D", "D")]}
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-23", [g], t)
            pub("2026-11-23", {
                "card|in": {"kind": "card", "source": "build", "start": "2026-11-23T15:00:00Z", "last": g},
                "card|gone": {"kind": "card", "source": "build", "start": "2026-11-23T15:00:00Z", "gone": "2026-11-23T10:00:00Z",
                              "last": {"name": "Card 2x", "legs": [leg("E v F", "E")]}},
                "list|x": {"kind": "list", "source": "build", "start": "2026-11-23T15:00:00Z",
                           "last": {"name": "List 2x", "legs": [leg("G v H", "G")]}},
                "card|wide": {"kind": "card", "source": "build", "start": "2026-11-23T15:00:00Z",
                              "last": {"name": "Card 2x", "wide": True, "legs": [leg("I v J", "I")]}}}, t)
            # yesterday's group starting after the run: still open, its day not empty, not named as lost
            pub("2026-11-24", {"card|open": {"kind": "card", "source": "build", "start": "2026-11-25T05:30:00Z",
                                             "last": {"name": "Card 2x", "legs": [leg("K v L", "K")]}}}, t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-25", days=2, now="2026-11-25T04:00:00Z"))
        self.assertIn("Days with a group: 1 of 2;", out)
        self.assertNotIn("never reached the archive", out)
        self.assertIn("Still open from 2026-11-24: Card 2x (K), first start 2026-11-25T05:30:00Z.", out)


    def test_lost_groups_read_on_the_ledger(self):
        rows = [
            {"pick": "Golden State Warriors", "start": "2026-11-26T03:00:00Z", "result": "won"},
            {"pick": "Golden State Warriors", "start": "2026-11-24T03:00:00Z", "result": "lost"},   # the day before: not this group
            {"pick": "Memphis Grizzlies", "start": "2026-11-26T01:00:00Z", "result": "won"},
            {"pick": "Toluca", "start": "2026-11-26T01:00:00Z", "result": None},
            {"pick": "A", "start": "2026-11-23T15:00:00Z", "result": "won"},
            {"pick": "A", "start": "2026-11-23T19:00:00Z", "result": "lost"},   # same name, another start: the leg's own start wins
            {"pick": "D", "start": "2026-11-23T17:00:00Z", "result": "lost"},
            {"pick": "E", "start": "2026-11-24T12:00:00Z", "result": "won"},
            {"pick": "F", "start": "2026-11-24T13:00:00Z", "result": "void"},
        ]
        with tempfile.TemporaryDirectory() as t:
            day("2026-11-20", [{"name": "Card 2x", "rule": 14}], t)
            pub("2026-11-25", {"lost|Card 2x|1": {"kind": "card", "source": "build-log", "lost": True, "name": "Card 2x",
                                                   "picks": ["Golden State Warriors", "Memphis Grizzlies", "Toluca"]}}, t)
            pub("2026-11-23", {"card|x": {"kind": "card", "source": "build", "start": "2026-11-23T15:00:00Z",
                                          "last": {"name": "Card 2x", "legs": [dict(leg("A v B", "A"), when="2026-11-23T15:00:00Z"),
                                                                                leg("C v D", "D")]}}}, t)
            pub("2026-11-24", {"lost|Card 2x|2": {"kind": "card", "source": "build-log", "lost": True, "name": "Card 2x",
                                                   "picks": ["E", "F"]}}, t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-26", days=6, now="2026-11-26T12:00:00Z", ledger=rows))
        self.assertIn("2026-11-23 Card 2x (A won, D lost): lost", out)
        self.assertIn("2026-11-24 Card 2x (E won, F void): won", out)
        self.assertIn("2026-11-25 Card 2x (Golden State Warriors won, Memphis Grizzlies won, Toluca pending): not settled", out)
        self.assertIn("On the results ledger: 1 won, 1 lost, 1 not settled.", out)


class TestWithdrawn(unittest.TestCase):
    """28 Nov 2026: a Card group published and withdrawn before its first
    start is named with why and its result (claude/card-withdrawn-groups-2026-11-28.md)."""

    def _setup(self, t):
        day("2026-11-20", [{"name": "Card 2x", "rule": 14, "legs": [leg("X v Y", "X")]}], t)
        legs = [dict(leg("Q v F", "Q"), when="2026-11-27T14:20:00Z"), dict(leg("I v P", "P"), when="2026-11-28T00:30Z")]
        pub("2026-11-27", {
            "card|w": {"kind": "card", "source": "build", "firstSeen": "2026-11-26T20:11:46Z", "lastSeen": "2026-11-27T04:51:19Z",
                       "builds": 11, "start": "2026-11-27T14:20:00Z", "gone": "2026-11-27T07:10:16Z",
                       "last": {"name": "Card 2x", "odds": 2.43, "bookOdds": 2.55, "stake": 2, "p": 0.483, "legs": legs}},
            # off after its start: underway, not withdrawn
            "card|late": {"kind": "card", "source": "build", "start": "2026-11-27T12:00:00Z", "gone": "2026-11-27T13:00:00Z",
                          "last": {"name": "Card 2x", "legs": [leg("A v B", "A")]}},
            "daily|w": {"kind": "daily", "source": "build", "start": "2026-11-27T14:20:00Z", "gone": "2026-11-27T07:10:16Z",
                        "last": {"name": "Daily 2x", "legs": [leg("Q v F", "Q")]}}}, t)
        # withdrawn but the same picks were archived: it came back
        pub("2026-11-20", {"card|back": {"kind": "card", "source": "build", "start": "2026-11-20T15:00:00Z",
                                         "gone": "2026-11-20T09:00:00Z", "last": {"name": "Card 2x", "legs": [leg("X v Y", "X")]}}}, t)
        with open(os.path.join(t, "card-short.json"), "w") as f:
            json.dump({"2026-11-27": [
                {"at": "2026-11-27T04:50:43Z", "why": "built", "clear": [["Q", 1.19, 0.77], ["P", 1.65, 0.72]]},
                {"at": "2026-11-27T07:07:34Z", "why": "long", "clear": [["P", 1.65, 0.72], ["Z", 1.25, 0.86]]},
                {"at": "2026-11-27T12:57:01Z", "why": "long", "clear": []}]}, f)

    def test_named_with_why_result_and_return(self):
        rows = [{"pick": "Q", "start": "2026-11-27T14:20:00Z", "result": "won"},
                {"pick": "P", "start": "2026-11-28T00:30:00Z", "result": "won"}]   # seconds the log left out
        with tempfile.TemporaryDirectory() as t:
            self._setup(t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-28", days=8, now="2026-11-28T09:00:00Z", ledger=rows))
        self.assertIn("Withdrawn after publication: 1 Card group(s)", out)
        self.assertIn("2026-11-27 Card 2x (Q won, P won) at 2.55, shown 11-26 20:11 to its withdrawal 11-27 07:10 UTC "
                      "over 11 build(s): Q no longer clear of the rule: won", out)
        self.assertIn("1 won, 0 lost, 0 not settled; settled 1 won v 0.48 expected, +155.0% at the page's stakes", out)
        self.assertNotIn("never reached the archive", out)

    def test_pending_and_none(self):
        with tempfile.TemporaryDirectory() as t:
            self._setup(t)
            out = "\n".join(C.live_days_section(t, today_="2026-11-28", days=8, now="2026-11-28T09:00:00Z", ledger=[]))
            self.assertIn("(Q pending, P pending) at 2.55", out)
            self.assertIn("0 won, 0 lost, 1 not settled.", out)
            # before the withdrawal, nothing to name
            self.assertEqual(C.withdrawn_card_groups(t, ["2026-11-27"], now="2026-11-27T05:00:00Z"), [])
        out = "\n".join(C.live_days_section("/nonexistent", today_="2026-11-28", days=3, ledger=[]))
        self.assertNotIn("Withdrawn", out)

    def test_instant(self):
        self.assertEqual(C._instant("2026-11-28T00:30Z"), C._instant("2026-11-28T00:30:00Z"))
        self.assertIsNone(C._instant("not a time"))


if __name__ == "__main__":
    unittest.main()
