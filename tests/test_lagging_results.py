"""Scoring a lagging primary source from ESPN (build.fill_lagging,
build.lagging_codes, 13 Nov 2026): openfootball's 2026-27 files stopped
scoring matches after 20 Sep 2026, so the core leagues' current-season tables
were seven weeks old. See claude/openfootball-lag-2026-11-13.md."""
import os, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B
import sources as S


def fx(d, h, a, hg=None, ag=None):
    return {"date": d, "home": h, "away": a, "hg": hg, "ag": ag, "time": None, "round": None}


def res(d, h, a, hg, ag):
    return {"date": d, "home": h, "away": a, "hg": hg, "ag": ag}


BEFORE = date(2026, 11, 13)


class FillLagging(unittest.TestCase):
    def rows(self):
        return [fx("2026-09-20", "Manchester City", "Sunderland", 5, 3),
                fx("2026-10-11", "Liverpool", "Manchester City"),
                fx("2026-10-17", "Everton", "Chelsea"),
                fx("2026-11-21", "Chelsea", "Everton"),
                fx("2027-03-01", "Sunderland", "Manchester City")]

    def test_fills_under_primary_spelling(self):
        rows = self.rows()
        n, bad, un = B.fill_lagging(rows, [res("2026-10-11", "Liverpool", "Man City", 2, 1),
                                           res("2026-10-17", "Everton", "Chelsea", 0, 0)], BEFORE)
        self.assertEqual((n, bad, un), (2, [], 0))
        self.assertEqual((rows[1]["hg"], rows[1]["ag"]), (2, 1))
        self.assertEqual(rows[1]["home"], "Liverpool")
        self.assertEqual(rows[1]["away"], "Manchester City")
        self.assertEqual(rows[1]["filledFrom"], "espn")

    def test_never_overwrites_primary(self):
        rows = self.rows()
        n, _, _ = B.fill_lagging(rows, [res("2026-09-20", "Man City", "Sunderland", 0, 0)], BEFORE)
        self.assertEqual(n, 0)
        self.assertEqual((rows[0]["hg"], rows[0]["ag"]), (5, 3))

    def test_window_and_future_left_alone(self):
        rows = self.rows()
        # the reverse fixture is in the window; a result for it after the cut is ignored
        n, _, un = B.fill_lagging(rows, [res("2026-11-21", "Chelsea", "Everton", 1, 0)], BEFORE)
        self.assertEqual((n, un), (0, 0))
        self.assertIsNone(rows[3]["hg"])
        # a result far from any scheduled date of that pair fills nothing
        n, _, un = B.fill_lagging(rows, [res("2026-11-10", "Sunderland", "Man City", 1, 1)], BEFORE)
        self.assertEqual((n, un), (0, 1))
        self.assertIsNone(rows[4]["hg"])

    def test_moved_match_takes_played_date(self):
        rows = self.rows()
        n, _, _ = B.fill_lagging(rows, [res("2026-10-28", "Everton", "Chelsea", 3, 2)], BEFORE)
        self.assertEqual(n, 1)
        self.assertEqual(rows[2]["date"], "2026-10-28")
        rows = self.rows()
        B.fill_lagging(rows, [res("2026-10-18", "Everton", "Chelsea", 3, 2)], BEFORE)
        self.assertEqual(rows[2]["date"], "2026-10-17")   # a day apart is the time zone

    def test_one_unmatched_name_fills_nothing(self):
        rows = self.rows()
        n, bad, _ = B.fill_lagging(rows, [res("2026-10-11", "Liverpool", "Man City", 2, 1),
                                          res("2026-10-17", "Real Madrid", "Chelsea", 0, 0)], BEFORE)
        self.assertEqual(n, 0)
        self.assertEqual(bad, ["Real Madrid"])
        self.assertIsNone(rows[1]["hg"])

    def test_two_names_on_one_club_fills_nothing(self):
        rows = self.rows()
        n, bad, _ = B.fill_lagging(rows, [res("2026-10-11", "Liverpool", "Man City", 2, 1),
                                          res("2026-10-12", "Liverpool", "Manchester City", 2, 1)], BEFORE)
        self.assertEqual(n, 0)
        self.assertEqual(len(bad), 1)
        self.assertIn("Manchester City", bad[0])


class LaggingCodes(unittest.TestCase):
    def test_picks_leagues_with_blank_past_fixtures(self):
        fixtures = {
            "en.1": [fx("2026-09-20", "A", "B", 1, 0), fx("2026-10-10", "B", "A")],
            "es.1": [fx("2026-11-08", "A", "B", 1, 0), fx("2026-11-20", "B", "A")],
        }
        out = B.lagging_codes(fixtures, BEFORE, gaps=set())
        self.assertEqual(out, {"en.1": date(2026, 9, 21)})

    def test_skips_gaps_and_leagues_without_slug(self):
        fixtures = {"en.1": [fx("2026-10-10", "B", "A")]}
        self.assertEqual(B.lagging_codes(fixtures, BEFORE, gaps={"en.1"}), {})
        self.assertEqual(B.lagging_codes(fixtures, BEFORE, gaps=set()), {"en.1": None})
        saved = S.ESPN_SLUGS.pop("en.1")
        try:
            self.assertEqual(B.lagging_codes(fixtures, BEFORE, gaps=set()), {})
        finally:
            S.ESPN_SLUGS["en.1"] = saved


class LagWalk(unittest.TestCase):
    """A lagging league's first walk that fails on every day is not marked done."""
    def walk(self, since, fail):
        import json, tempfile
        tmp = tempfile.mkdtemp()
        saved = (S.CURRENT_DIR, S._espn_day)

        def fake(slug, day, timeout, errs, pause=1.0):
            if fail:
                errs.append("down")
            return []
        S.CURRENT_DIR, S._espn_day = tmp, fake
        try:
            S.topup_current("en.1", "2026-27", until=date(2026, 9, 25), sleep=0, since=since)
            return json.load(open(os.path.join(tmp, "en.1-2026-27.json")))["through"]
        finally:
            S.CURRENT_DIR, S._espn_day = saved

    def test_failed_lag_walk_retries(self):
        self.assertEqual(self.walk(date(2026, 9, 21), fail=True), "2026-09-20")

    def test_clean_lag_walk_marked(self):
        self.assertEqual(self.walk(date(2026, 9, 21), fail=False), "2026-09-25")

    def test_gap_walk_unchanged(self):
        # no `since`: a competition that never answered is saved as before
        self.assertEqual(self.walk(None, fail=True), "2026-09-25")


class Aliases(unittest.TestCase):
    def test_new_spellings(self):
        self.assertEqual(S.match_team("AEK Athens", {"AEK", "PAOK", "OFI"}), "AEK")
        self.assertEqual(S.match_team("OFI Crete", {"AEK", "PAOK", "OFI"}), "OFI")
        self.assertEqual(S.match_team("SC Rheindorf Altach", {"SCR Altach", "WSG Tirol"}), "SCR Altach")
        self.assertEqual(S.match_team("WSG Swarovski Tirol", {"SCR Altach", "WSG Tirol"}), "WSG Tirol")
        self.assertEqual(S.match_team("St Johnstone", {"Saint Johnstone", "St. Mirren"}), "Saint Johnstone")
        self.assertIsNone(S.match_team("AEK Larnaca", {"AEK", "PAOK"}))

    def test_first_ci_build_misses(self):
        pairs = [("Athletico-PR", "CA Paranaense"), ("Atlético-MG", "CA Mineiro"),
                 ("Red Bull Bragantino", "RB Bragantino"), ("Deportivo", "RC Deportivo La Coruña"),
                 ("NEC Nijmegen", "NEC"), ("FC Famalicao", "FC Famalicão"),
                 ("Vitória de Guimaraes", "Vitória Guimarães"), ("Erzurum BB", "BB Erzurumspor"),
                 ("Istanbul Basaksehir", "İstanbul Başakşehir")]
        pool = {b for _, b in pairs} | {"Deportivo Alavés", "SC Internacional", "Gaziantep FK"}
        for a, b in pairs:
            self.assertEqual(S.match_team(a, pool), b, a)


class ExhaustedLeague(unittest.TestCase):
    """A primary source that dates only its first rounds (Belgium 2026-27:
    rounds 8 to 34 "datum TBC", dropped by the parser), 14 Nov 2026."""
    START = date(2026, 11, 14)

    def rows(self):
        return [fx("2026-08-07", "Club Brugge", "KV Kortrijk", 3, 0),
                fx("2026-08-08", "KRC Genk", "STVV"),
                fx("2026-09-20", "STVV", "Club Brugge")]

    def test_only_a_league_with_nothing_ahead(self):
        fixtures = {"be.1": self.rows(),
                    "en.1": [fx("2026-09-20", "Liverpool", "Everton", 1, 0),
                             fx("2026-11-21", "Everton", "Liverpool")]}
        self.assertEqual(B.exhausted_codes(fixtures, self.START, set()), ["be.1"])
        self.assertEqual(B.exhausted_codes(fixtures, self.START, {"be.1"}), [])

    def test_undated_round_result_appended(self):
        rows = self.rows()
        results = [res("2026-08-08", "Racing Genk", "Sint-Truidense", 2, 2),
                   # a round the file lists as TBC: no row for this pair at all
                   res("2026-10-25", "KV Kortrijk", "Racing Genk", 0, 1),
                   # a listed pair far from its date: not added, the file has it
                   res("2026-11-08", "Sint-Truidense", "Club Brugge", 1, 3)]
        n, bad, un = B.fill_lagging(rows, results, self.START, append=True)
        self.assertEqual((n, bad, un), (2, [], 1))
        new = [r for r in rows if r["date"] == "2026-10-25"]
        self.assertEqual(len(new), 1)
        self.assertEqual((new[0]["home"], new[0]["away"], new[0]["hg"], new[0]["ag"]),
                         ("KV Kortrijk", "KRC Genk", 0, 1))
        self.assertEqual(new[0]["filledFrom"], "espn")
        self.assertIsNone(rows[2]["hg"])

    def test_append_off_by_default(self):
        rows = self.rows()
        n, _, un = B.fill_lagging(rows, [res("2026-10-25", "KV Kortrijk", "Racing Genk", 0, 1)],
                                  self.START)
        self.assertEqual((n, un, len(rows)), (0, 1, 3))

    def test_append_needs_every_name(self):
        rows = self.rows()
        n, bad, _ = B.fill_lagging(rows, [res("2026-10-25", "KV Kortrijk", "Racing Genk", 0, 1),
                                          res("2026-10-26", "Nowhere United", "STVV", 1, 1)],
                                   self.START, append=True)
        self.assertEqual((n, len(rows)), (0, 3))
        self.assertIn("Nowhere United", bad)

    def test_window_fixtures_added_under_primary_spelling(self):
        rows = self.rows()
        espn = [dict(fx("2026-11-21", "Racing Genk", "Club Brugge"), time="17:30", utc=True),
                # the file already lists this pair within three weeks: not added twice
                dict(fx("2026-10-04", "Sint-Truidense", "Club Brugge"), utc=True)]
        added, bad = B.fill_window(rows, espn)
        self.assertEqual((added, bad), (1, []))
        new = rows[-1]
        self.assertEqual((new["home"], new["away"], new["date"], new["time"]),
                         ("KRC Genk", "Club Brugge", "2026-11-21", "17:30"))
        self.assertTrue(new["utc"])
        self.assertEqual(new["filledFrom"], "espn")

    def test_window_needs_every_name(self):
        rows = self.rows()
        added, bad = B.fill_window(rows, [fx("2026-11-21", "Racing Genk", "Club Brugge"),
                                          fx("2026-11-22", "Nowhere United", "STVV")])
        self.assertEqual((added, len(rows)), (0, 3))
        self.assertEqual(bad, ["Nowhere United"])


if __name__ == "__main__":
    unittest.main()


class StaleLeagues(unittest.TestCase):
    """A league table still missing results after the lagging fill is flagged
    (build.stale_leagues, 14 Nov 2026): the Czech First League, scored by
    openfootball to early October and not at all by ESPN."""
    START = date(2026, 11, 14)

    def test_many_unplayed_flags_a_few_do_not(self):
        cz = [fx(f"2026-10-{d:02d}", f"H{d}", f"A{d}") for d in range(9, 14)]
        es = [fx("2026-10-10", "Rayo", "Athletic"), fx("2026-11-01", "A", "B"),
              fx("2026-11-21", "B", "A")]
        flag, watch = B.stale_leagues({"cze.1": cz, "es.1": es}, self.START)
        self.assertEqual(flag, {"cze.1": (5, "2026-10-09")})
        self.assertEqual(watch, {})

    def test_grace_days_and_played_rows_ignored(self):
        rows = [fx("2026-11-12", "A", "B"), fx("2026-11-13", "C", "D"),
                fx("2026-11-12", "E", "F"), fx("2026-11-13", "G", "H"),
                fx("2026-10-01", "I", "J", 1, 0), fx("2026-11-01", "K", "L")]
        self.assertEqual(B.stale_leagues({"cze.1": rows}, self.START), ({}, {}))

    def test_cups_skipped_af_and_fdx_only_watched(self):
        rows = [fx(f"2026-10-{d:02d}", f"H{d}", f"A{d}") for d in range(1, 8)]
        cup = next(c for c, m in B.E.LEAGUES.items() if m.get("cup"))
        af = next(c for c in sorted(S.AF) if not B.E.LEAGUES.get(c, {}).get("cup"))
        flag, watch = B.stale_leagues({cup: list(rows), af: list(rows)}, self.START)
        self.assertEqual(flag, {})
        self.assertEqual(set(watch), {af})

    def test_reason_names_the_league(self):
        why = B.stale_reason("cze.1", {"cze.1": (41, "2026-10-09")})
        self.assertIn("First League (Czechia)", why)
        self.assertIn("41 results from 9 Oct on", why)
        self.assertIsNone(B.stale_reason("en.1", {"cze.1": (41, "2026-10-09")}))
