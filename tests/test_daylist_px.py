"""Each pinned and past pick's pre-start price from the results ledger (`px`,
28 Nov 2026): what the Prime filter reads on the days behind today
(claude/prime-filter-2026-11-28.md)."""
import gzip, json, os, sys, tempfile, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import daylist as DL

NOW = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)


def row(home, away, pick, start, first=None, last=None, **extra):
    return {"sport": "nba", "home": home, "away": away, "pick": pick, "start": start, "first": first, "last": last, **extra}


def ledger(d, rows):
    with gzip.open(os.path.join(d, "results-ledger.json.gz"), "wt", encoding="utf-8") as f:
        json.dump({"rows": rows}, f)


def item(home="A", away="B", pick="A", start="2026-10-03T23:00:00Z"):
    return {"sport": "nba", "home": home, "away": away, "pick": pick, "start": start}


class LedgerPrices(unittest.TestCase):
    def prices(self, rows):
        with tempfile.TemporaryDirectory() as d:
            ledger(d, rows)
            return DL.ledger_prices(d)

    def test_hill_before_average_and_last_before_first(self):
        p = self.prices([row("A", "B", "A", "2026-10-03T23:00:00Z", first={"o": 1.30, "h": 1.28}, last={"o": 1.22})])
        self.assertEqual(DL.price_of(item(), p), 1.22)          # the last read, its average (no Hill there)
        p = self.prices([row("A", "B", "A", "2026-10-03T23:00:00Z", first={"o": 1.30}, last={"o": 1.22, "h": 1.20})])
        self.assertEqual(DL.price_of(item(), p), 1.20)          # William Hill's when the read has it
        p = self.prices([row("A", "B", "A", "2026-10-03T23:00:00Z", first={"o": 1.30})])
        self.assertEqual(DL.price_of(item(), p), 1.30)          # only a first read on file

    def test_names_fold_case_and_the_pick_must_be_the_same_side(self):
        p = self.prices([row("a", "b", "B", "2026-10-03T23:00:00Z", last={"o": 3.4})])
        self.assertIsNone(DL.price_of(item(), p))               # the ledger's price is for the other side
        p = self.prices([row("a", "b", "A", "2026-10-03T23:00:00Z", last={"o": 1.4})])
        self.assertEqual(DL.price_of(item(), p), 1.4)

    def test_a_rematch_days_later_is_another_game(self):
        p = self.prices([row("A", "B", "A", "2026-10-08T23:00:00Z", last={"o": 1.9}),
                         row("A", "B", "A", "2026-10-04T01:00:00Z", last={"o": 1.15})])
        self.assertEqual(DL.price_of(item(), p), 1.15)          # the copy two hours off, not the one five days on
        p = self.prices([row("A", "B", "A", "2026-10-08T23:00:00Z", last={"o": 1.9})])
        self.assertIsNone(DL.price_of(item(), p))

    def test_duplicates_moved_rows_and_bad_prices_are_left_out(self):
        p = self.prices([row("A", "B", "A", "2026-10-03T23:00:00Z", last={"o": 1.5}, duplicate=True),
                         row("A", "B", "A", "2026-10-03T23:00:00Z", last={"o": 1.6}, movedTo="2026-10-20"),
                         row("A", "B", "A", "2026-10-03T23:00:00Z", last={"o": 0}),
                         row("A", "B", "A", "2026-10-03T23:00:00Z")])
        self.assertEqual(p, {})

    def test_no_ledger_is_no_prices(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(DL.ledger_prices(d), {})
        self.assertEqual(DL.attach_prices([item()], {}), [item()])


class PastDaysCarryThePrice(unittest.TestCase):
    def test_past_and_pinned_picks_take_px_only_when_there_is_one(self):
        # tests/test_daylist.py's shape: a list pick two days back, and a second player pair the same day
        t = lambda pid, a: {"id": pid, "tour": "ATP", "date": "2026-10-03", "time": "07:00", "tournament": "Japan Open",
                            "playerA": a, "playerB": "B", "p": {"a": 0.12, "b": 0.88}, "pick": "B", "confidence": 0.88,
                            "tier": "Strong", "accuracy": {"hit": 0.92, "n": 62}, "list": True, "reserve": False,
                            "published": "2026-10-03T04:00:00Z"}
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "predictions-tennis"))
            json.dump([t("7", "A"), t("8", "Z")], open(os.path.join(d, "predictions-tennis", "2026-10-03.json"), "w"))
            before = next(p for p in DL.build(NOW, here=d, fetch=False)["past"] if p["date"] == "2026-10-03")["list"]
            self.assertEqual(len(before), 2)
            self.assertTrue(all("px" not in i for i in before))        # no ledger: no key at all
            ledger(d, [{"sport": "tennis", "home": "A", "away": "B", "pick": "B", "start": before[0]["start"], "last": {"o": 1.25}}])
            after = next(p for p in DL.build(NOW, here=d, fetch=False)["past"] if p["date"] == "2026-10-03")["list"]
        got = {i["home"]: i.get("px") for i in after}
        self.assertEqual(got, {"A": 1.25, "Z": None})


if __name__ == "__main__":
    unittest.main()
