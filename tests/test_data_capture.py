"""16 Nov 2026: the data kept for later (claude/data-capture-2026-11-16.md)."""
import gzip, json, os, sys, tempfile, unittest
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports, sources, markets, periods


def espn_event(final=True, odds=None):
    comp = {"date": "2026-11-16T00:00Z", "status": {"type": {"completed": final, "name": "STATUS_FINAL", "state": "post"}},
            "competitors": [
                {"homeAway": "home", "team": {"id": "1", "displayName": "Houston Rockets"}, "score": "147",
                 "linescores": [{"value": 40}, {"value": 35}, {"value": 38}, {"value": 34}]},
                {"homeAway": "away", "team": {"id": "2", "displayName": "Washington Wizards"}, "score": "119",
                 "linescores": [{"value": 30}, {"value": 29}, {"value": 31}, {"value": 29}]}]}
    if odds is not None:
        comp["odds"] = [odds]
    return {"id": "9", "season": {"type": 2}, "competitions": [comp]}


FEED = {"skip": (), "path": "basketball/nba", "label": "NBA", "pool": "nba"}


class SportsPeriodsAndLine(unittest.TestCase):
    def test_periods_kept_for_a_final_game(self):
        g = sports._game(espn_event(), FEED)
        self.assertEqual(g["hp"], [40, 35, 38, 34])
        self.assertEqual(sum(g["hp"]), g["hs"])

    def test_no_periods_before_the_end(self):
        self.assertNotIn("hp", sports._game(espn_event(final=False), FEED))

    def test_line_from_point_spread_close(self):
        o = {"provider": {"name": "DraftKings"},
             "pointSpread": {"home": {"close": {"line": "-9.5", "odds": "-110"}}},
             "total": {"over": {"close": {"line": "o241.5"}}},
             "moneyline": {"home": {"close": {"odds": "-400"}}, "away": {"close": {"odds": "+300"}}}}
        ln = sports._game(espn_event(odds=o), FEED)["line"]
        self.assertEqual(ln, {"spread": -9.5, "total": 241.5, "mlH": -400.0, "mlA": 300.0, "by": "DraftKings"})

    def test_line_from_the_bare_fields(self):
        o = {"details": "WAS -3.5", "spread": 3.5, "overUnder": 228.5, "homeTeamOdds": {"favorite": False, "moneyLine": 140}}
        ln = sports.line_of({"odds": [o]})
        self.assertEqual(ln["spread"], 3.5)
        self.assertEqual(ln["total"], 228.5)

    def test_no_odds_no_line(self):
        self.assertNotIn("line", sports._game(espn_event(), FEED))


class HalfTimeInTheDayCache(unittest.TestCase):
    def test_round_trip_and_old_files(self):
        f = {"league": {"id": 39, "season": 2026, "country": "England"},
             "fixture": {"id": 5, "date": "2026-11-15T15:00:00+00:00", "status": {"short": "FT"}},
             "teams": {"home": {"name": "Arsenal"}, "away": {"name": "Leeds"}},
             "score": {"fulltime": {"home": 2, "away": 1}, "halftime": {"home": 0, "away": 1}}}
        c = sources._compact(f)
        self.assertEqual(sources._expand(c)["score"]["halftime"], {"home": 0, "away": 1})
        self.assertNotIn("halftime", sources._expand(c[:10])["score"])


class Periods(unittest.TestCase):
    def test_kept_when_full_time_agrees_refused_when_not(self):
        with tempfile.TemporaryDirectory() as here:
            cache = os.path.join(here, ".afcache")
            os.makedirs(cache)
            def fx(fid, h, a, ft, ht):
                return sources._compact({"league": {"id": 39, "season": 2026}, "fixture": {"id": fid, "date": "2026-11-15T15:00:00+00:00", "status": {"short": "FT"}},
                                         "teams": {"home": {"name": h}, "away": {"name": a}},
                                         "score": {"fulltime": {"home": ft[0], "away": ft[1]}, "halftime": {"home": ht[0], "away": ht[1]}}})
            with gzip.open(os.path.join(cache, "day-2026-11-15.json.gz"), "wt") as fh:
                json.dump({"final": True, "rows": [fx(1, "Arsenal", "Leeds United", (2, 1), (0, 1)),
                                                   fx(2, "Chelsea", "Fulham", (3, 0), (1, 0))]}, fh)
            graded = {"graded": [
                {"league": "en.1", "date": "2026-11-15", "home": "Arsenal", "away": "Leeds United", "result": [2, 1], "kickoff": "2026-11-15T15:00:00Z"},
                {"league": "en.1", "date": "2026-11-15", "home": "Chelsea", "away": "Fulham", "result": [2, 0], "kickoff": "2026-11-15T15:00:00Z"}]}
            json.dump(graded, open(os.path.join(here, "record-graded.json"), "w"))
            log = []
            want, found, files = periods.build(here, today=date(2026, 11, 16), cache_dir=cache, log=log)
            self.assertEqual((want, found), (2, 1), log)
            kept = json.load(open(files[0]))
            self.assertEqual(kept["en.1|2026-11-15|Arsenal|Leeds United"][:4], [0, 1, 2, 1])
            self.assertEqual(periods.check(here), (1, 0))
            # a second run looks only for what is missing and was not tried already (16 Nov 2026, QA:
            # the look-back is now the season, and matching every miss again on each build is slow)
            self.assertEqual(periods.build(here, today=date(2026, 11, 16), cache_dir=cache)[0], 0)

    def test_an_entry_whose_result_was_corrected_is_dropped_and_looked_for_again(self):
        # 17 Nov 2026: Quindio v Real Cartagena was kept at 0-1 and later regraded 0-2.
        with tempfile.TemporaryDirectory() as here:
            cache = os.path.join(here, ".afcache"); os.makedirs(cache); os.makedirs(os.path.join(here, "periods"))
            key = "en.1|2026-11-15|Arsenal|Leeds United"
            json.dump({key: [0, 0, 0, 1, 1]}, open(os.path.join(here, "periods", "football-2026-11.json"), "w"))
            json.dump({"graded": [{"league": "en.1", "date": "2026-11-15", "home": "Arsenal", "away": "Leeds United",
                                   "result": [0, 2], "kickoff": "2026-11-15T15:00:00Z"}]}, open(os.path.join(here, "record-graded.json"), "w"))
            periods.build(here, today=date(2026, 11, 16), cache_dir=cache)
            self.assertEqual(periods.check(here), (0, 0))      # stale entry gone, no day file to replace it yet
            row = sources._compact({"league": {"id": 39, "season": 2026}, "fixture": {"id": 1, "date": "2026-11-15T15:00:00+00:00", "status": {"short": "FT"}},
                                    "teams": {"home": {"name": "Arsenal"}, "away": {"name": "Leeds United"}},
                                    "score": {"fulltime": {"home": 0, "away": 2}, "halftime": {"home": 0, "away": 1}}})
            with gzip.open(os.path.join(cache, "day-2026-11-15.json.gz"), "wt") as fh:
                json.dump({"final": True, "rows": [row]}, fh)
            periods.build(here, today=date(2026, 11, 16), cache_dir=cache)
            kept = json.load(open(os.path.join(here, "periods", "football-2026-11.json")))
            self.assertEqual(kept[key][:4], [0, 1, 0, 2])

    def test_a_day_without_half_time_on_file_is_not_tried_yet(self):
        with tempfile.TemporaryDirectory() as here:
            cache = os.path.join(here, ".afcache")
            os.makedirs(cache)
            row = [39, 2026, 1, "2026-10-01T15:00:00+00:00", "FT", "Arsenal", "Leeds United", 2, 1, "England"]
            with gzip.open(os.path.join(cache, "day-2026-10-01.json.gz"), "wt") as fh:
                json.dump({"final": True, "rows": [row]}, fh)
            json.dump({"graded": [{"league": "en.1", "date": "2026-10-01", "home": "Arsenal", "away": "Leeds United",
                                   "result": [2, 1], "kickoff": "2026-10-01T15:00:00Z"}]}, open(os.path.join(here, "record-graded.json"), "w"))
            self.assertEqual(periods.build(here, today=date(2026, 11, 16), cache_dir=cache)[:2], (0, 0))
            with gzip.open(os.path.join(cache, "day-2026-10-01.json.gz"), "wt") as fh:
                json.dump({"final": True, "rows": [row + [1, 0]]}, fh)
            self.assertEqual(periods.build(here, today=date(2026, 11, 16), cache_dir=cache)[:2], (1, 1))


class ExtraFootballLines(unittest.TestCase):
    def test_handicap_kept_with_hill(self):
        items = [{"fixture": {"id": 7}, "bookmakers": [
            {"name": "William Hill", "bets": [{"id": 4, "name": "Asian Handicap", "values": [{"value": "Home -1.5", "odd": "2.40"}]},
                                              {"id": 8, "name": "Both Teams Score", "values": [{"value": "Yes", "odd": "1.80"}, {"value": "No", "odd": "1.95"}]}]},
            {"name": "Unibet", "bets": [{"id": 4, "name": "Asian Handicap", "values": [{"value": "Home -1.5", "odd": "2.50"}]}]}]}]
        row = markets.parse_odds(items)["7"]
        self.assertEqual(row["x"]["Asian Handicap"]["Home -1.5"], [2.45, 2.4])
        self.assertIn("btts", row)
        g = {"league": "en.1", "date": "2026-11-16", "home": "A", "away": "B", "xg": [2.0, 0.8], "p": {"h": 0.7, "d": 0.18, "a": 0.12}}
        self.assertEqual(markets.row_for(g, row, "x")["x"]["Asian Handicap"]["Home -1.5"][0], 2.45)


class HalfTimeBackfill(unittest.TestCase):
    """16 Nov 2026 (QA): a finished day cached before the half time was kept
    is asked for once more, so the season's half-time scores fill in."""

    def _write(self, d, path, n):
        row = [39, 2026, 1, f"{path}T15:00:00+00:00", "FT", "A", "B", 2, 1, "England", 1, 0][:n]
        with gzip.open(os.path.join(d, f"day-{path}.json.gz"), "wt") as fh:
            json.dump({"final": True, "rows": [row]}, fh)

    def _fx(self, day):
        return [{"league": {"id": 39, "season": 2026, "country": "England"},
                 "fixture": {"id": 1, "date": f"{day}T15:00:00+00:00", "status": {"short": "FT"}},
                 "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
                 "score": {"fulltime": {"home": 2, "away": 1}, "halftime": {"home": 1, "away": 0}}}]

    def test_an_old_final_day_without_half_time_is_asked_once(self):
        from unittest import mock
        from datetime import timedelta
        day = date.today() - timedelta(days=20)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(sources, "AF_CACHE_DIR", d), \
                mock.patch.dict(sources._HT_REFETCH, {"n": 0}), mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AF_FRUGAL", None)
            self._write(d, day.isoformat(), 10)
            with mock.patch.object(sources, "_af_get", return_value=self._fx(day.isoformat())) as g:
                f = sources._af_day(day)[0]
                sources._af_day(day)
                self.assertEqual(g.call_count, 1)
            self.assertEqual(f["score"]["halftime"], {"home": 1, "away": 0})

    def test_too_old_or_over_the_cap_is_left_alone(self):
        from unittest import mock
        from datetime import timedelta
        old = date.today() - timedelta(days=sources.HT_BACK_DAYS + 5)
        recent = date.today() - timedelta(days=20)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(sources, "AF_CACHE_DIR", d), \
                mock.patch.dict(sources._HT_REFETCH, {"n": sources.HT_REFETCH_MAX}):
            os.environ.pop("AF_FRUGAL", None)
            self._write(d, old.isoformat(), 10)
            self._write(d, recent.isoformat(), 10)
            with mock.patch.object(sources, "_af_get") as g:
                sources._af_day(old); sources._af_day(recent)
                g.assert_not_called()

    def test_a_push_build_never_backfills(self):
        from unittest import mock
        from datetime import timedelta
        day = date.today() - timedelta(days=20)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(sources, "AF_CACHE_DIR", d), \
                mock.patch.dict(sources._HT_REFETCH, {"n": 0}), mock.patch.dict(os.environ, {"AF_FRUGAL": "1"}):
            self._write(d, day.isoformat(), 10)
            with mock.patch.object(sources, "_af_get") as g:
                sources._af_day(day)
                g.assert_not_called()


if __name__ == "__main__":
    unittest.main()
