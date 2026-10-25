"""The wider API-Football leagues take their season from the API's
seasons[].current, not from the static strings in af-leagues.json
(25 Oct 2026, bug 5 of claude/full-review-2026-10-25.md). No network."""
import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stderr
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import sources as S


def league(lid, seasons):
    return {"league": {"id": lid, "name": f"L{lid}", "type": "League"},
            "country": {"name": "Albania"},
            "seasons": [{"year": y, "current": cur, "start": f"{y}-08-01", "end": f"{y + (1 if split else 0)}-05-30"}
                        for y, cur, split in seasons]}


class Labels(unittest.TestCase):
    def test_label_and_prev(self):
        self.assertEqual(E.season_label(2026, True), "2026-27")
        self.assertEqual(E.season_label(2026, False), "2026")
        self.assertEqual(E.season_prev("2026-27"), ["2025-26", "2024-25"])
        self.assertEqual(E.season_prev("2026"), ["2025", "2024"])


class Refresh(unittest.TestCase):
    def setUp(self):
        self.codes = [c for c in S.af_season_codes() if c in E.LEAGUES][:3]
        self.assertTrue(self.codes)
        self.saved = {c: dict(E.LEAGUES[c]) for c in self.codes}

    def tearDown(self):
        for c, m in self.saved.items():
            E.LEAGUES[c].clear()
            E.LEAGUES[c].update(m)
        E.AF_SEASON_CODES.difference_update(self.codes)

    def test_current_season_from_api_rolls_the_league(self):
        a, b, c = self.codes
        resp = [league(S.AF[a], [(2024, False, True), (2025, False, True), (2026, True, True)]),
                league(S.AF[b], [(2025, False, False), (2026, True, False)]),
                league(S.AF[c], [(2024, False, True), (2025, False, True)])]   # nothing current
        E.LEAGUES[a]["season"] = "2024-25"          # a rolled static season
        log = []
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "_af_get", return_value=resp) as g:
            path = os.path.join(d, "af-seasons.json")
            doc = S.af_refresh_seasons(path=path, log=log)
            self.assertEqual(g.call_count, 1)
            self.assertEqual(json.load(open(path))["seasons"][a]["current"], 2026)
            # fresh: no second call inside three days
            S.af_refresh_seasons(path=path)
            self.assertEqual(g.call_count, 1)
        self.assertEqual(doc["seasons"][a], {"current": 2026, "split": True, "years": [2024, 2025, 2026]})
        self.assertEqual(doc["seasons"][b]["split"], False)
        self.assertNotIn(c, doc["seasons"])
        self.assertIn(f"WARNING: {c} no current season", log)

        changed = E.apply_af_seasons(doc)
        self.assertEqual(changed[a], ("2024-25", "2026-27"))
        self.assertEqual(E.LEAGUES[a]["season"], "2026-27")
        self.assertEqual(E.LEAGUES[a]["prev"], ["2025-26", "2024-25"])
        self.assertEqual(E.LEAGUES[a]["seasonSource"], "api")
        self.assertEqual(E.LEAGUES[b]["season"], "2026")
        self.assertEqual(E.LEAGUES[c]["season"], self.saved[c]["season"])   # untouched, warned
        self.assertIn(a, E.AF_SEASON_CODES)
        self.assertNotIn(c, E.AF_SEASON_CODES)

    def test_no_key_no_call(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(S, "_af_get") as g:
            self.assertEqual(S.af_refresh_seasons(path=os.path.join(d, "x.json")), {})
            g.assert_not_called()

    def test_empty_answer_keeps_file(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "_af_get", return_value=[]):
            path = os.path.join(d, "x.json")
            json.dump({"checked": 1, "seasons": {"af.1": {"current": 2020}}}, open(path, "w"))
            self.assertEqual(S.af_refresh_seasons(path=path)["seasons"]["af.1"]["current"], 2020)

    def test_apply_ignores_cups_and_unknown(self):
        self.assertEqual(E.apply_af_seasons({"seasons": {"nope.9": {"current": 2026}}}), {})
        self.assertEqual(E.apply_af_seasons({}), {})


class PoolFallback(unittest.TestCase):
    """The configured season has no fixtures in the window but the API is
    already playing a newer one: af_rows uses the newer one and says so."""

    def row(self, lid, year, when="2026-10-25T15:00:00+00:00"):
        f = {"league": {"id": lid, "season": year, "country": "Albania"},
             "fixture": {"id": 1, "date": when, "status": {"short": "NS"}},
             "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
             "score": {"fulltime": {"home": None, "away": None}}}
        return S._expand(S._compact(f))

    def test_newer_season_in_pool_is_used_and_logged(self):
        code = next(c for c in S.AF_EXTRA if "-" in E.LEAGUES[c]["season"])
        lid = S.AF[code]
        season = E.LEAGUES[code]["season"]
        year = int(season[:4])
        pool = {lid: [self.row(lid, year + 1)]}
        err = io.StringIO()
        with mock.patch.object(S, "af_season_pool", return_value=pool), redirect_stderr(err):
            rows = S.af_rows(code, season)
        self.assertEqual(len(rows), 1)
        self.assertIn(f"{code}: configured season {season} has no fixtures", err.getvalue())

    def test_configured_season_still_wins_when_present(self):
        code = next(c for c in S.AF_EXTRA if "-" in E.LEAGUES[c]["season"])
        lid = S.AF[code]
        season = E.LEAGUES[code]["season"]
        year = int(season[:4])
        pool = {lid: [self.row(lid, year), self.row(lid, year + 1)]}
        err = io.StringIO()
        with mock.patch.object(S, "af_season_pool", return_value=pool), redirect_stderr(err):
            rows = S.af_rows(code, season)
        self.assertEqual(len(rows), 1)
        self.assertEqual(err.getvalue(), "")

    def test_rolled_static_season_reads_the_pool_not_a_finished_fetch(self):
        # A split season two years back is over by the calendar; the API is
        # playing this year's. The finished-season call must not be made.
        code = next(c for c in S.AF_EXTRA if "-" in E.LEAGUES[c]["season"])
        lid = S.AF[code]
        saved = dict(E.LEAGUES[code])
        try:
            E.LEAGUES[code]["season"] = "2024-25"
            pool = {lid: [self.row(lid, 2026)]}
            err = io.StringIO()
            with mock.patch.object(S, "af_day_pool", return_value=pool), \
                 mock.patch.object(S, "_af_season", side_effect=AssertionError("fetched a finished season")), \
                 redirect_stderr(err):
                rows = S.af_rows(code, "2024-25")
            self.assertEqual(len(rows), 1)
            self.assertIn("API-Football is playing 2026", err.getvalue())
        finally:
            E.LEAGUES[code].clear()
            E.LEAGUES[code].update(saved)


if __name__ == "__main__":
    unittest.main()
