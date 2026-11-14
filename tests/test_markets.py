"""Football markets beyond the match winner (markets.py, 14 Nov 2026): the
numbers, the settling, API-Football's labels, the archive and the gate."""
import gzip, json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import markets as M

P = {"h": 0.62, "d": 0.22, "a": 0.16}


def book(name, bets):
    return {"name": name, "bets": [{"id": i, "values": [{"value": v, "odd": str(o)} for v, o in vals.items()]} for i, vals in bets.items()]}


class Numbers(unittest.TestCase):
    def test_grid_agrees_with_the_published_chances(self):
        g = M.grid(1.8, 0.9, P)
        n = len(g)
        self.assertAlmostEqual(sum(g[x][y] for x in range(n) for y in range(n) if x > y), 0.62, places=6)
        self.assertAlmostEqual(sum(g[x][x] for x in range(n)), 0.22, places=6)
        self.assertAlmostEqual(sum(map(sum, g)), 1.0, places=6)

    def test_markets_are_coherent(self):
        side, m = M.numbers(1.8, 0.9, P)
        self.assertEqual(side, "h")
        # a winner always scores: win and both score + win to nil = win
        self.assertAlmostEqual(m["wbtts"]["p"] + m["wtn"]["p"], 0.62, places=3)
        self.assertAlmostEqual(m["dc"]["p"], 0.84, places=4)
        self.assertAlmostEqual(m["dnb"]["p"], 0.62 / 0.78, places=4)
        self.assertGreater(m["o15"]["p"], m["o25"]["p"] if m["o25"]["s"] == "over" else 0)
        self.assertLess(m["wo25"]["p"], 0.62)
        self.assertGreater(m["tts"]["p"], 0.62)

    def test_published_two_way_numbers_are_used_and_the_likelier_side_taken(self):
        _, m = M.numbers(1.8, 0.9, P, btts=0.44, over25=0.58)
        self.assertEqual(m["btts"], {"s": "no", "p": 0.56})
        self.assertEqual(m["o25"], {"s": "over", "p": 0.58})

    def test_away_pick(self):
        side, m = M.numbers(0.8, 1.9, {"h": 0.15, "d": 0.2, "a": 0.65})
        self.assertEqual((side, m["wbtts"]["s"], m["tts"]["s"]), ("a", "a", "a"))


class Settle(unittest.TestCase):
    def test_every_market(self):
        for mk, sel, score, want in (
                ("btts", "yes", (2, 1), True), ("btts", "no", (2, 1), False), ("btts", "no", (2, 0), True),
                ("o15", "over", (1, 1), True), ("o15", "under", (1, 0), True), ("o25", "over", (2, 0), False),
                ("o25", "under", (1, 1), True), ("o35", "under", (2, 2), False), ("o35", "over", (3, 1), True),
                ("wbtts", "h", (2, 1), True), ("wbtts", "h", (2, 0), False), ("wbtts", "a", (1, 1), False), ("wbtts", "a", (1, 3), True),
                ("wo25", "h", (2, 1), True), ("wo25", "h", (2, 0), False), ("wtn", "h", (1, 0), True), ("wtn", "a", (1, 2), False),
                ("dc", "h", (1, 1), True), ("dc", "h", (0, 1), False), ("dnb", "h", (1, 1), None), ("dnb", "a", (0, 1), True),
                ("tts", "h", (0, 0), False), ("tts", "a", (3, 1), True)):
            self.assertIs(M.settle(mk, sel, *score), want, (mk, sel, score))


class Prices(unittest.TestCase):
    ITEM = {"fixture": {"id": 77}, "bookmakers": [
        book("William Hill", {8: {"Yes": 1.80, "No": 1.95}, 12: {"Home/Draw": 1.20, "Draw/Away": 2.40, "Home/Away": 1.25},
                              24: {"Home/Yes": 3.50, "Home/No": 3.00, "Draw/Yes": 5.0, "Draw/No": 12.0, "Away/Yes": 9.0, "Away/No": 11.0},
                              36: {"Home": 3.20, "Away": 12.0}, 43: {"Yes": 1.10, "No": 6.50}}),
        book("Bet365", {8: {"Yes": 1.83, "No": 1.90}, 5: {"Over 2.5": 1.90, "Under 2.5": 1.90, "Over 2.75": 2.10, "Over 1.5": 1.28, "Under 1.5": 3.60},
                        16: {"Over 0.5": 1.12, "Under 0.5": 6.00, "Over 1.5": 1.70}, 2: {"Home": 1.30, "Away": 3.40}}),
        book("1xBet", {8: {"Yes": 1.90, "No": 1.99}, 1: {"Home": 1.6}})]}

    def setUp(self):
        self.row = M.parse_odds([self.ITEM])["77"]

    def test_average_best_uk_and_hill(self):
        y = self.row["btts"]["yes"]
        self.assertEqual((y["n"], y["b"], y["bb"], y["h"]), (3, 1.83, "Bet365", 1.80))
        self.assertAlmostEqual(y["o"], round((1.80 + 1.83 + 1.90) / 3, 3))
        self.assertNotIn("h", self.row["o25"]["over"])          # Hill did not price the goals line
        self.assertNotIn("o275", self.row)                      # only the tracked lines are read

    def test_team_to_score_merges_hills_bet_with_the_team_total(self):
        t = self.row["tts"]["h"]
        self.assertEqual((t["n"], t["h"], t["b"], t["bb"]), (2, 1.10, 1.12, "Bet365"))

    def test_fair_chance_takes_the_margin_out(self):
        b = M.price_of(self.row, "btts", "yes")
        imp = 1 / b["o"] + 1 / self.row["btts"]["no"]["o"]
        self.assertAlmostEqual(b["f"], round((1 / b["o"]) / imp, 4))
        dc = M.price_of(self.row, "dc", "h")                    # three outcomes whose chances sum to 2
        self.assertAlmostEqual(dc["f"], round((1 / 1.20) * 2 / (1 / 1.20 + 1 / 2.40 + 1 / 1.25), 4))
        w = M.price_of(self.row, "wbtts", "h")
        self.assertAlmostEqual(w["f"], round((1 / 3.5) / sum(1 / o for o in (3.5, 3.0, 5.0, 12.0, 9.0, 11.0)), 4))
        self.assertNotIn("f", M.price_of(self.row, "wtn", "h"))  # only the yes is priced: no fair chance
        self.assertIsNone(M.price_of(self.row, "wo25", "h"))
        self.assertIsNone(M.price_of(None, "btts", "yes"))


def pred(home, away, kickoff, date="2026-11-15", pub="2026-11-14T05:00:00Z", **kw):
    return {"league": "en.1", "date": date, "home": home, "away": away, "p": dict(P), "xg": [1.8, 0.9],
            "btts": 0.52, "over25": 0.55, "celtic": False, "unrated": False, "kickoff": kickoff, "published": pub, **kw}


class Archive(unittest.TestCase):
    NOW = datetime(2026, 11, 15, 12, tzinfo=timezone.utc)

    def test_unrated_and_unpriced_fixtures(self):
        self.assertIsNone(M.row_for(pred("A", "B", None, unrated=True)))
        r = M.row_for(pred("A", "B", "2026-11-15T15:00:00Z"), None, "x")
        self.assertEqual(set(r["m"]), set(M.MARKETS))
        self.assertNotIn("o", r["m"]["btts"])

    def test_replaced_before_kick_off_kept_after_and_price_carried(self):
        priced = M.row_for(pred("A", "B", "2026-11-15T15:00:00Z"), M.parse_odds([Prices.ITEM])["77"], "2026-11-15T08:00:00Z")
        started = M.row_for(pred("C", "D", "2026-11-15T11:00:00Z"), None, "2026-11-15T08:00:00Z")
        new = [M.row_for(pred("A", "B", "2026-11-15T15:00:00Z"), None, "2026-11-15T12:00:00Z"),
               M.row_for(pred("C", "D", "2026-11-15T11:00:00Z"), None, "2026-11-15T12:00:00Z"),
               M.row_for(pred("E", "F", "2026-11-15T10:00:00Z"), None, "2026-11-15T12:00:00Z")]
        out = {r["home"]: r for r in M.merge_rows([priced, started], new, self.NOW)}
        self.assertEqual(out["A"]["published"], "2026-11-15T12:00:00Z")
        self.assertEqual(out["A"]["m"]["btts"]["h"], 1.80)            # the earlier price, same selection
        self.assertEqual(out["C"]["published"], "2026-11-15T08:00:00Z")  # started: as it stood
        self.assertNotIn("E", out)                                    # a first row after the start is refused


class Record(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.dir, "predictions-markets")); os.makedirs(os.path.join(self.dir, "predictions"))

    def tearDown(self): shutil.rmtree(self.dir)

    def test_live_priced_and_replayed_rows(self):
        row = M.row_for(pred("A", "B", "2026-11-15T15:00:00Z"), M.parse_odds([Prices.ITEM])["77"], "2026-11-15T08:00:00Z")
        late = M.row_for(pred("A", "B", "2026-11-15T15:00:00Z"), None, "2026-11-15T16:00:00Z")   # after the start: not graded
        with gzip.open(os.path.join(self.dir, "predictions-markets", "2026-11-15.json.gz"), "wt") as f: json.dump([row], f)
        with gzip.open(os.path.join(self.dir, "predictions-markets", "2026-11-16.json.gz"), "wt") as f: json.dump([late], f)
        old = pred("G", "H", "2026-10-01T15:00:00Z", date="2026-10-01", pub="2026-10-01T05:00:00Z")
        with open(os.path.join(self.dir, "predictions", "2026-10-01.json"), "w") as f:
            json.dump([old, dict(old, published="2026-09-30T05:00:00Z", xg=[9, 9])], f)
        with open(os.path.join(self.dir, "record-graded.json"), "w") as f:
            json.dump({"graded": [{"league": "en.1", "date": "2026-11-15", "home": "A", "away": "B", "result": [2, 1], "published": "x"},
                                  {"league": "en.1", "date": "2026-10-01", "home": "G", "away": "H", "result": [0, 0],
                                   "published": "2026-10-01T05:00:00Z"}]}, f)
        rec = M.record(self.dir, now=datetime(2026, 11, 16, tzinfo=timezone.utc))
        self.assertEqual((rec["live"]["fixtures"], rec["replay"]["fixtures"]), (1, 1))
        b = rec["markets"]["btts"]
        self.assertEqual((b["live"]["n"], b["live"]["landed"], b["live"]["priced"]), (1, 1, 1))
        self.assertAlmostEqual(b["live"]["retBest"], 0.83)
        self.assertEqual(b["live"]["atHill"], 1)
        self.assertEqual((b["replay"]["n"], b["replay"]["landed"]), (1, 0))       # 0-0: both to score missed
        self.assertNotIn("priced", b["replay"])
        self.assertEqual(rec["markets"]["dnb"]["replay"].get("void"), 1)
        self.assertEqual(b["gate"]["all"]["verdict"], "wait")
        self.assertEqual(rec["markets"]["wbtts"]["live"]["landed"], 1)


class Gate(unittest.TestCase):
    def picks(self, n, hit_every, price, fair):
        return [(f"2026-11-{1 + i % 28:02d}", i % hit_every != 0, {"o": price, "b": price, "f": fair}) for i in range(n)]

    def test_waits_under_the_count(self):
        self.assertEqual(M.gate(self.picks(149, 4, 1.6, 0.6))["verdict"], "wait")

    def test_passes_only_when_it_beats_the_bookmakers_and_pays(self):
        self.assertEqual(M.gate(self.picks(400, 4, 1.6, 0.6))["verdict"], "pass")     # lands 75% at 1.60
        self.assertEqual(M.gate(self.picks(400, 2, 1.6, 0.6))["verdict"], "fail")     # lands 50% at 1.60
        self.assertEqual(M.gate(self.picks(400, 4, 1.6, 0.8))["verdict"], "fail")     # pays, but under the bookmakers' chance

    def test_review_section_says_a_pass_in_bold(self):
        import card_review_post as CP
        rec = {"live": {"fixtures": 3, "from": "2026-11-15"}, "replay": {"fixtures": 9}, "gate": {"n": 150, "pLoss": 0.1, "edge": 0.05},
               "markets": {"btts": {"name": "Both teams to score", "all": {"n": 12, "rate": 0.5, "quoted": 0.52, "z": -0.1},
                                    "live": {"priced": 3, "ret": -0.02, "retBest": 0.01},
                                    "gate": {"value": {"n": 200, "need": 150, "verdict": "pass", "retBest": 0.06, "pLoss": 0.04},
                                             "all": {"n": 3, "need": 150, "verdict": "wait", "retBest": 0.01}}}}}
        text = "\n".join(CP.markets_section(rec))
        self.assertIn("**passes**", text); self.assertIn("**Passed the value gate: Both teams to score", text)
        self.assertIn("3 of 150", text)
        self.assertEqual(CP.markets_section({}), [])


if __name__ == "__main__":
    unittest.main()


class Sweep(unittest.TestCase):
    """odds_day against a stubbed feed: paging, the cache, a sweep cut short
    by a low allowance resuming where it stopped."""
    def setUp(self):
        import sources as S
        self.S, self.dir = S, tempfile.mkdtemp()
        self.keep = (S.AF_CACHE_DIR, S._af_get, dict(S.AF_USAGE), os.environ.get("API_FOOTBALL_KEY"), os.environ.get("AF_FRUGAL"))
        S.AF_CACHE_DIR = self.dir
        os.environ["API_FOOTBALL_KEY"] = "x"; os.environ.pop("AF_FRUGAL", None)
        self.calls = []

        def fake(q):
            self.calls.append(q)
            page = int(q.split("page=")[1])
            S.AF_PAGING[q] = {"current": page, "total": 3}
            S._AF_CACHE[q] = "kept"
            item = json.loads(json.dumps(Prices.ITEM)); item["fixture"]["id"] = 1000 + page
            return [item]
        S._af_get = fake

    def tearDown(self):
        S = self.S
        S.AF_CACHE_DIR, S._af_get = self.keep[0], self.keep[1]
        S.AF_USAGE.clear(); S.AF_USAGE.update(self.keep[2])
        for k, v in (("API_FOOTBALL_KEY", self.keep[3]), ("AF_FRUGAL", self.keep[4])):
            os.environ.pop(k, None)
            if v is not None: os.environ[k] = v
        shutil.rmtree(self.dir)

    def test_reads_every_page_once_and_caches(self):
        from datetime import date
        self.S.AF_USAGE["left"] = None
        rows = M.odds_day(date(2026, 11, 15), now=1000.0)
        self.assertEqual((sorted(rows), len(self.calls)), (["1001", "1002", "1003"], 3))
        self.assertNotIn(self.calls[0], self.S._AF_CACHE)          # the big response is not held for the run
        M.odds_day(date(2026, 11, 15), now=1000.0 + M.ODDS_TTL - 1)
        self.assertEqual(len(self.calls), 3)
        M.odds_day(date(2026, 11, 15), now=1000.0 + M.ODDS_TTL + 1)
        self.assertEqual(len(self.calls), 6)

    def test_stands_down_on_a_low_allowance_and_resumes(self):
        from datetime import date
        self.S.AF_USAGE["left"] = 100
        log = []
        rows = M.odds_day(date(2026, 11, 16), log=log, now=1000.0)
        self.assertEqual((sorted(rows), len(self.calls)), (["1001"], 1))
        self.assertIn("stood down", log[0])
        self.S.AF_USAGE["left"] = 5000
        self.assertEqual(len(M.odds_day(date(2026, 11, 16), now=1500.0)), 1)        # inside the partial TTL: the copy
        rows = M.odds_day(date(2026, 11, 16), now=1000.0 + M.ODDS_PARTIAL_TTL + 1)
        self.assertEqual(sorted(rows), ["1001", "1002", "1003"])
        self.assertEqual([c.split("page=")[1] for c in self.calls], ["1", "2", "3"])  # picked up at page 2
