"""Daily List picks at William Hill (10 Nov 2026): the UK-books pass for list
picks, the page's marks and the record's at-the-book tally. Display and tally
only; the list never sees a price."""
import gzip, json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

NOW = datetime(2026, 11, 10, 9, tzinfo=timezone.utc)
SPORTS = [{"key": "basketball_ncaab", "title": "NCAAB", "active": True},
          {"key": "basketball_nba", "title": "NBA", "active": True}]


def ncaab(home="Oklahoma Sooners", away="Mississippi Valley State Delta Devils", **kw):
    l = {"sport": "ncaab", "home": home, "away": away, "pick": home, "event": f"{home} v {away}",
         "when": "2026-11-10T00:30:00Z", "date": "2026-11-10", "pModel": 0.98, "list": True,
         "odds": 1.02, "est": True}
    l.update(kw); return l


def event(home, away, books):
    return {"home_team": home, "away_team": away, "commence_time": "2026-11-10T00:30:00Z",
            "bookmakers": [{"title": t, "markets": [{"key": "h2h", "outcomes": [
                {"name": home, "price": p}, {"name": away, "price": 15.0}]}]} for t, p in books]}


class ListBooksPass(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(); self.calls = []
        os.environ["ODDS_API_KEY"] = "test"
        self.events = [event("Oklahoma Sooners", "Mississippi Valley State Delta Devils",
                             [("William Hill", 1.01), ("Bet365", 1.02)]),
                       event("UCLA Bruins", "North Florida Ospreys", [("Bet365", 1.04)])]

    def tearDown(self):
        shutil.rmtree(self.dir); os.environ.pop("ODDS_API_KEY", None)

    def fetch(self, url):
        self.calls.append(url)
        if "/odds?" not in url: return SPORTS, None
        return (self.events if "basketball_ncaab" in url else []), 400

    def run_(self, L):
        r = {}
        G.price_odds_api(L, {"2026-11-10"}, r, cache_dir=self.dir, fetch=self.fetch, now=NOW, list_books=True)
        return r

    def test_marks_hill_not_hill_and_not_found(self):
        a, b = ncaab(), ncaab("UCLA Bruins", "North Florida Ospreys")
        c = ncaab("Kansas Jayhawks", "Howard Bison")
        self.run_([a, b, c])
        self.assertEqual(a["bookOdds"], {"William Hill": 1.01, "Bet365": 1.02})
        self.assertEqual(b["bookOdds"], {"Bet365": 1.04})
        self.assertNotIn("bookOdds", c)
        self.assertTrue(all(x["ukChecked"] for x in (a, b, c)))
        # display only: the leg's own price and estimate flag are untouched
        self.assertEqual((a["odds"], a["est"]), (1.02, True))
        self.assertEqual(G._lb_mark(a)["h"], 1.01)
        self.assertEqual(G._lb_mark(b), {"h": None, "b": 1, "x": ["Bet365", 1.04], "c": True})
        self.assertEqual(G._lb_mark(c), {"h": None, "b": 0, "x": None, "c": True})

    def test_one_credit_a_slate_and_off_list_picks_skipped(self):
        off = ncaab("Duke Blue Devils", "Army Black Knights", list=False)
        self.run_([ncaab(), ncaab("UCLA Bruins", "North Florida Ospreys"), off])
        self.assertEqual(sum("/odds?" in u for u in self.calls), 1)
        self.assertNotIn("ukChecked", off)

    def test_stops_at_the_list_cap(self):
        with open(os.path.join(self.dir, "oddsapi-ledger.json"), "w") as f:
            json.dump({"month": "2026-11", "used": 9, "days": {"2026-11-10": G.LIST_BOOK_DAY}, "left": 400}, f)
        l = ncaab(); r = self.run_([l])
        self.assertEqual(r["oddsApiList"]["skipped"], ["basketball_ncaab"])
        self.assertNotIn("ukChecked", l)            # never read: no mark at all


class ListAtBookRecord(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def pool(self, d, legs):
        with gzip.open(os.path.join(self.dir, f"pool-{d}.json.gz"), "wt", encoding="utf-8") as f:
            json.dump({"date": d, "legs": legs}, f)

    def test_splits_settled_list_picks_by_the_book(self):
        legs = [dict(ncaab(), id="1", lastBooks={"William Hill": 1.05}),
                dict(ncaab("UCLA Bruins", "North Florida Ospreys"), id="2", bookOdds={"Bet365": 1.04}),
                dict(ncaab("Kansas Jayhawks", "Howard Bison"), id="3", lastChecked=True),
                dict(ncaab("Duke Blue Devils", "Army Black Knights"), id="4"),
                dict(ncaab("Iowa Hawkeyes", "Chicago State Cougars"), id="5", list=False)]
        self.pool("2026-11-10", legs)
        self.pool("2026-11-09", [dict(ncaab(), id="9", lastBooks={"William Hill": 1.5})])   # before the pass
        sp = {"1": {"winner": "Oklahoma Sooners"}, "2": {"winner": "North Florida Ospreys"},
              "3": {"winner": "Kansas Jayhawks"}, "4": {"winner": "Duke Blue Devils"},
              "5": {"winner": "Iowa Hawkeyes"}, "9": {"winner": "Oklahoma Sooners"}}
        r = G.list_at_book(({}, {}, sp), now=NOW, pool_dir=self.dir)
        self.assertEqual(r["atBook"], {"n": 1, "won": 1, "rate": 1.0, "quoted": 0.98, "returned": 1.05, "ret": 0.05})
        self.assertEqual((r["notAtBook"]["n"], r["notAtBook"]["won"]), (2, 1))
        self.assertEqual((r["unchecked"]["n"], r["unchecked"]["won"]), (1, 1))
        self.assertEqual(r["picks"]["ncaab|oklahoma sooners|mississippi valley state delta devils|2026-11-10"], 1.05)
        self.assertEqual(r["picks"]["ncaab|ucla bruins|north florida ospreys|2026-11-10"], 0)
        self.assertEqual(r["picks"]["ncaab|kansas jayhawks|howard bison|2026-11-10"], -1)
        self.assertNotIn("ncaab|duke blue devils|army black knights|2026-11-10", r["picks"])
        self.assertEqual(r["bySport"]["ncaab"]["atBook"]["n"], 1)

    def test_tennis_rows_key_on_the_event(self):
        row = {"sport": "tennis", "event": "Jannik Sinner v Ben Shelton", "pick": "Jannik Sinner",
               "list": True, "bookOdds": {"William Hill": 1.2}}
        self.assertEqual(G._lb_key(row["sport"], *G._lb_sides(row)), "tennis|jannik sinner|ben shelton")


class ListAtBookWithoutId(unittest.TestCase):
    """11 Nov 2026 (#235): US-sport pool rows first archived days ahead carried
    no `id`, so settle left them pending and the tally read 1 settled pick of
    40. They now settle by names and date, as tools/card_replay.py does."""
    def test_rows_without_id_settle_by_names(self):
        d = tempfile.mkdtemp()
        try:
            with gzip.open(os.path.join(d, "pool-2026-11-10.json.gz"), "wt", encoding="utf-8") as f:
                json.dump({"date": "2026-11-10", "legs": [
                    dict(ncaab(), lastBooks={"William Hill": 1.04}),
                    dict(ncaab("UCLA Bruins", "North Florida Ospreys"), lastChecked=True)]}, f)
            sp = {"7": {"home": "Oklahoma Sooners", "away": "Mississippi Valley State Delta Devils",
                        "when": "2026-11-10T00:30Z", "winner": "Oklahoma Sooners"},
                  "8": {"home": "UCLA Bruins", "away": "North Florida Ospreys",
                        "when": "2026-11-10T00:30Z", "winner": "North Florida Ospreys"},
                  # same pairing a week later: never read for this leg
                  "9": {"home": "UCLA Bruins", "away": "North Florida Ospreys",
                        "when": "2026-11-17T00:30Z", "winner": "UCLA Bruins"}}
            r = G.list_at_book(({}, {}, sp), now=NOW, pool_dir=d)
            self.assertEqual((r["atBook"]["n"], r["atBook"]["won"], r["atBook"]["returned"]), (1, 1, 1.04))
            self.assertEqual((r["notAtBook"]["n"], r["notAtBook"]["won"]), (1, 0))
        finally:
            shutil.rmtree(d)

    def test_pool_row_takes_a_missing_id_from_a_later_build(self):
        d = tempfile.mkdtemp(); old = G.ARCHIVE; G.ARCHIVE = d
        try:
            l = ncaab(when="2026-11-11T00:30:00Z", date="2026-11-11")
            G.archive_pool([l], NOW, ["2026-11-11"])
            G.archive_pool([dict(l, id="401", odds=1.5)], NOW, ["2026-11-11"])
            with gzip.open(os.path.join(d, "pool-2026-11-11.json.gz"), "rt") as f:
                row = json.load(f)["legs"][0]
            self.assertEqual(row["id"], "401")
            self.assertEqual(row["odds"], 1.02)          # the first price is never changed
        finally:
            G.ARCHIVE = old; shutil.rmtree(d)


class PoolKeepsLaterBooks(unittest.TestCase):
    def test_last_books_and_checked_on_a_later_build(self):
        d = tempfile.mkdtemp(); old = G.ARCHIVE; G.ARCHIVE = d
        try:
            l = ncaab(when="2026-11-11T00:30:00Z", date="2026-11-11")
            G.archive_pool([l], NOW, ["2026-11-11"])
            l2 = dict(l, bookOdds={"William Hill": 1.01}, ukChecked=True)
            G.archive_pool([l2], NOW, ["2026-11-11"])
            with gzip.open(os.path.join(d, "pool-2026-11-11.json.gz"), "rt") as f:
                row = json.load(f)["legs"][0]
            self.assertEqual(row["lastBooks"], {"William Hill": 1.01})
            self.assertTrue(row["lastChecked"])
            self.assertNotIn("bookOdds", row)            # the first write is never changed
        finally:
            G.ARCHIVE = old; shutil.rmtree(d)



class ReviewSection(unittest.TestCase):
    def test_prints_the_three_lines(self):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
        import card_review_post as C
        out = C.list_book_section({"book": "William Hill", "from": "2026-11-10",
                                   "atBook": {"n": 4, "won": 4, "rate": 1.0, "quoted": 0.9, "ret": 0.05},
                                   "notAtBook": {"n": 0, "won": 0}, "unchecked": {"n": 0, "won": 0}, "bySport": {}})
        self.assertIn("| priced at William Hill | 4 | 4 (100%) | 90% | +5.0% |", out)
        self.assertEqual(C.list_book_section(None), [])


if __name__ == "__main__":
    unittest.main()
