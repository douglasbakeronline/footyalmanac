"""The results ledger (ledger.py) and the sports graded file
(sports.write_graded), 14 Nov 2026."""
import gzip, json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ledger as L
import sports as S


def fb(date, home, away, conf, pub, kickoff=None, lst=False, market=True, side="h"):
    p = {"h": conf, "d": 0.1, "a": round(0.9 - conf, 4)} if side == "h" else {"h": round(0.9 - conf, 4), "d": 0.1, "a": conf}
    g = {"league": "en.1", "date": date, "home": home, "away": away, "p": p, "confidence": conf,
         "celtic": False, "unrated": False, "list": lst, "reserve": False, "why": None,
         "kickoff": kickoff or f"{date}T15:00:00Z", "published": pub}
    if market:
        g["market"] = {"avg": [1.25, 6.0, 11.0], "best": [1.3, 6.5, 12.0], "books": 8, "src": "API-Football"}
    return g


def sp(gid, when, home, away, conf, pub, lst=False):
    return {"id": gid, "sport": "nba", "label": "NBA", "when": when, "home": home, "away": away,
            "pick": home, "confidence": conf, "list": lst, "reserve": False, "published": pub,
            "formH": ["W"] * 5, "eloH": 1600}


class Repo:
    """A throwaway repo folder with the files ledger.py reads."""
    def __init__(self):
        self.dir = tempfile.mkdtemp()
        for d in ("predictions", "predictions-tennis", "predictions-sports", "groupings-archive"):
            os.makedirs(os.path.join(self.dir, d))

    def put(self, rel, obj):
        with open(os.path.join(self.dir, rel), "w") as f: json.dump(obj, f)

    def close(self): shutil.rmtree(self.dir)


class Predictions(unittest.TestCase):
    def setUp(self): self.r = Repo()
    def tearDown(self): self.r.close()

    def test_latest_pre_start_copy_and_late_copy_ignored(self):
        self.r.put("predictions/2026-11-01.json", [fb("2026-11-02", "Arsenal", "Leeds United", 0.80, "2026-11-01T05:00:00Z")])
        self.r.put("predictions/2026-11-02.json", [fb("2026-11-02", "Arsenal", "Leeds United", 0.83, "2026-11-02T05:00:00Z"),
                                                   # published after kick-off: proves nothing
                                                   fb("2026-11-02", "Arsenal", "Leeds United", 0.99, "2026-11-02T16:00:00Z")])
        rows = L.predictions(self.r.dir)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["conf"], 0.83)
        self.assertEqual(len(rows[0]["_prices"]), 2)      # both pre-start copies' market

    def test_moved_fixture_counted_once_rematch_twice(self):
        self.r.put("predictions/2026-11-01.json", [fb("2026-11-02", "Arsenal", "Leeds United", 0.8, "2026-11-01T05:00:00Z"),
                                                   fb("2026-12-20", "Arsenal", "Leeds United", 0.8, "2026-11-01T05:00:00Z")])
        self.r.put("predictions/2026-11-03.json", [fb("2026-11-05", "Arsenal", "Leeds United", 0.8, "2026-11-03T05:00:00Z")])
        rows = sorted(L.predictions(self.r.dir), key=lambda r: r["start"])
        self.assertEqual([r["date"] for r in rows], ["2026-11-05", "2026-12-20"])
        self.assertEqual(rows[0]["_dates"], ["2026-11-02", "2026-11-05"])

    def test_us_sport_series_kept_apart_by_id(self):
        self.r.put("predictions-sports/2026-09-29.json", [
            sp("1", "2026-09-29T18:00Z", "Atlanta Braves", "Philadelphia Phillies", 0.6, "2026-09-29T05:00:00Z"),
            sp("2", "2026-09-30T18:00Z", "Atlanta Braves", "Philadelphia Phillies", 0.6, "2026-09-29T05:00:00Z")])
        self.assertEqual(len(L.predictions(self.r.dir)), 2)

    def test_tennis_rematch_with_new_id_is_a_second_match(self):
        t = lambda i, d, pub: {"id": i, "date": d, "time": "10:00", "tour": "ATP", "tournament": "X",
                               "playerA": "Jakub Mensik", "playerB": "Francisco Cerundolo", "pick": "Jakub Mensik",
                               "confidence": 0.8, "list": True, "reserve": False, "published": pub}
        self.r.put("predictions-tennis/2026-10-03.json", [t(None, "2026-10-03", "2026-10-03T05:00:00Z"),
                                                          t("1", "2026-10-03", "2026-10-03T06:00:00Z")])
        self.r.put("predictions-tennis/2026-10-11.json", [t("2", "2026-10-11", "2026-10-11T05:00:00Z")])
        rows = L.predictions(self.r.dir)
        self.assertEqual(sorted(r.get("id") for r in rows), ["1", "2"])


class Ledger(unittest.TestCase):
    NOW = datetime(2026, 11, 14, 12, tzinfo=timezone.utc)

    def setUp(self):
        self.r = Repo()
        self.r.put("predictions/2026-11-01.json", [
            fb("2026-11-02", "Arsenal", "Leeds United", 0.86, "2026-11-01T05:00:00Z", lst=True),
            fb("2026-11-02", "Chelsea", "Everton", 0.70, "2026-11-01T05:00:00Z", market=False),
            fb("2026-11-03", "Fulham", "Wolves", 0.81, "2026-11-01T05:00:00Z", lst=True, market=False)])
        self.r.put("record-graded.json", {"graded": [
            {"date": "2026-11-02", "league": "en.1", "home": "Arsenal", "away": "Leeds United", "result": [2, 0], "won": True},
            {"date": "2026-11-02", "league": "en.1", "home": "Chelsea", "away": "Everton", "result": [1, 1], "won": False}]})
        self.r.put("predictions-sports/2026-11-05.json", [sp("9", "2026-11-05T00:00Z", "Boston Celtics", "Utah Jazz", 0.9, "2026-11-04T05:00:00Z", lst=True)])
        self.r.put("sports-graded.json", {"graded": [{"id": "9", "ok": True, "score": [120, 99]}]})
        self.r.put("tennis-record.json", {"graded": []})

    def tearDown(self): self.r.close()

    def test_results_prices_and_ungraded(self):
        out = L.write(now=self.NOW, here=self.r.dir)
        rows = {r["key"]: r for r in out["rows"]}
        ars = rows["football|arsenal|leeds united|2026-11-02"]
        self.assertEqual((ars["result"], ars["score"]), ("won", "2-0"))
        self.assertEqual(ars["last"]["o"], 1.25)
        self.assertEqual(ars["last"]["b"], 1.3)
        self.assertEqual(rows["football|chelsea|everton|2026-11-02"]["result"], "lost")
        self.assertIsNone(rows["football|chelsea|everton|2026-11-02"]["last"])
        self.assertEqual(rows["nba|id|9"]["result"], "won")
        ug = out["ungraded"]
        self.assertEqual(ug["chase"], {"n": 1, "list": 1, "reserve": 0})
        self.assertEqual(ug["listPicks"], ["2026-11-03 football Fulham v Wolves"])
        s = out["summary"]["football|list|85-90"]
        self.assertEqual((s["n"], s["won"], s["priced"]), (1, 1, 1))
        self.assertAlmostEqual(s["ret"], 0.25)
        self.assertAlmostEqual(s["retBest"], 0.30)

    def test_kept_when_its_sources_are_gone(self):
        path = os.path.join(self.r.dir, "results-ledger.json.gz")
        L.write(now=self.NOW, here=self.r.dir, path=path)
        for d in ("predictions", "predictions-sports"):
            shutil.rmtree(os.path.join(self.r.dir, d)); os.makedirs(os.path.join(self.r.dir, d))
        self.r.put("record-graded.json", {"graded": []})
        out = L.write(now=self.NOW, here=self.r.dir, path=path)
        rows = {r["key"]: r for r in out["rows"]}
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows["football|arsenal|leeds united|2026-11-02"]["result"], "won")
        with gzip.open(path, "rt") as f: self.assertEqual(json.load(f)["n"], 4)

    def test_price_other_side_or_after_start_not_kept(self):
        self.r.put("predictions/2026-11-01.json", [
            fb("2026-11-02", "Arsenal", "Leeds United", 0.6, "2026-11-01T05:00:00Z", side="a"),
            fb("2026-11-02", "Arsenal", "Leeds United", 0.6, "2026-11-01T09:00:00Z", side="h", market=False)])
        out = L.write(now=self.NOW, here=self.r.dir)
        ars = [r for r in out["rows"] if r["home"] == "Arsenal"][0]
        self.assertEqual(ars["side"], "h")
        self.assertIsNone(ars["last"])                  # the only market copy priced the away side
        self.assertIsNone(L._pre_start({"o": 1.5, "t": "2026-11-02T16:00:00Z"},
                                       L.parse_utc("2026-11-02T15:00:00Z")))


class Merge(unittest.TestCase):
    def test_result_never_lost_prices_widen(self):
        old = [{"key": "k", "result": "won", "score": "1-0", "first": {"o": 1.4, "t": "2026-11-01T00:00:00Z"},
                "last": {"o": 1.3, "t": "2026-11-02T00:00:00Z"}}]
        new = [{"key": "k", "result": None, "score": None, "first": {"o": 1.5, "t": "2026-11-01T06:00:00Z"},
                "last": {"o": 1.2, "t": "2026-11-02T06:00:00Z"}}]
        m = L.merge(old, new)[0]
        self.assertEqual((m["result"], m["score"]), ("won", "1-0"))
        self.assertEqual((m["first"]["o"], m["last"]["o"]), (1.4, 1.2))

    def test_band(self):
        self.assertEqual([L.band(c) for c in (0.97, 0.85, 0.8499, 0.62, 0.5)], ["95+", "85-90", "80-85", "62-70", "0-62"])


class Report(unittest.TestCase):
    def test_warning_only_when_asked(self):
        import io, contextlib
        out = {"n": 1, "rows": [{"result": None}], "priceCover": {}, "book": "William Hill",
               "ungraded": {"days": 3, "staleDays": 14, "chase": {"n": 2, "list": 1, "reserve": 0},
                            "stale": {"n": 0, "list": 0, "reserve": 0}, "byComp": {"football|en.1": {"n": 2}},
                            "listPicks": ["2026-11-03 football Fulham v Wolves"]}}
        for warn, want in ((True, 2), (False, 0)):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf): L.report(out, warn=warn)
            self.assertEqual(buf.getvalue().count("::warning::"), want)


class SportsGraded(unittest.TestCase):
    def test_merge_keeps_old_rows_and_drops_detail(self):
        old = [{"id": "1", "when": "2026-10-01T00:00Z", "ok": True}]
        graded = [{"id": "2", "when": "2026-11-01T00:00Z", "ok": False, "formH": ["W"], "h2h": []},
                  {"id": "1", "when": "2026-10-01T00:00Z", "ok": False}]
        rows = S.merge_graded(old, graded, [{"id": "3", "when": "2026-11-02T00:00Z", "void": True}])
        self.assertEqual([r["id"] for r in rows], ["1", "2", "3"])
        self.assertFalse(rows[0]["ok"])                 # a regrade wins
        self.assertNotIn("formH", rows[1])

    def test_write_graded_survives_a_missing_file(self):
        d = tempfile.mkdtemp()
        try:
            path = os.path.join(d, "sports-graded.json")
            S.write_graded([{"id": "1", "when": "2026-10-01T00:00Z", "ok": True}], [], "now", path=path)
            S.write_graded([], [], "later", path=path)
            with open(path) as f: self.assertEqual(len(json.load(f)["graded"]), 1)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
