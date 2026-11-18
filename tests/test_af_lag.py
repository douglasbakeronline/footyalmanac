"""The Czech First League scored from API-Football (sources.AF_LAG,
sources.af_lag_pick, build.fill_lagging source=, 18 Nov 2026): openfootball's
Czech 2026-27 file stopped scoring after 20 Sep and ESPN's cze.1 slug answers
nothing, so the table was flagged under Celtic's Law from 14 Nov. See
claude/czech-results-api-football-2026-11-18.md."""
import os, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B
import sources as S

# openfootball's spellings for the 2026-27 Czech First League
OPENFOOTBALL = ["1.FC Slovácko", "Artis Brno", "Baník Ostrava", "Bohemians 1905",
                "FC Fastav Zlín", "FK Jablonec", "FK Mlada Boleslav", "FK Pardubice",
                "FK Teplice", "Hradec Kralove", "Sigma Olomouc", "Slavia Praha",
                "Slovan Liberec", "Sparta Praha", "Viktoria Plzeň", "Zbrojovka Brno"]


def af(fid, when, home, away, hg, ag, season=2026, country="Czech-Republic", st="FT"):
    return {"league": {"id": 345, "season": season, "country": country},
            "fixture": {"id": fid, "date": when, "status": {"short": st}},
            "teams": {"home": {"name": home}, "away": {"name": away}},
            "score": {"fulltime": {"home": hg, "away": ag}}}


class CzechNames(unittest.TestCase):
    def test_czech_letters_fold(self):
        self.assertEqual(S.match_team("Viktoria Plzen", OPENFOOTBALL), "Viktoria Plzeň")
        self.assertEqual(S.match_team("Plzen", OPENFOOTBALL), "Viktoria Plzeň")

    def test_short_spellings_match_one_club_each(self):
        short = ["Slavia Praha", "Sparta Praha", "Plzen", "Banik Ostrava", "Sigma Olomouc",
                 "Mlada Boleslav", "Slovan Liberec", "Bohemians 1905", "Hradec Kralove",
                 "Jablonec", "Teplice", "Pardubice", "Zlin", "Slovacko", "Zbrojovka Brno",
                 "Artis Brno"]
        got = [S.match_team(n, OPENFOOTBALL) for n in short]
        self.assertNotIn(None, got)
        self.assertEqual(len(set(got)), len(short))

    def test_brno_clubs_kept_apart(self):
        self.assertEqual(S.match_team("Artis Brno", OPENFOOTBALL), "Artis Brno")
        self.assertEqual(S.match_team("Zbrojovka Brno", OPENFOOTBALL), "Zbrojovka Brno")


class Pick(unittest.TestCase):
    def test_played_rows_of_the_season_only(self):
        src = [af(1, "2026-10-18T15:00:00+00:00", "Slavia Praha", "Plzen", 2, 0),
               af(2, "2026-11-29T15:00:00+00:00", "Teplice", "Zlin", None, None, st="NS"),
               af(3, "2025-10-18T15:00:00+00:00", "Teplice", "Zlin", 1, 1, season=2025)]
        rows, why = S.af_lag_pick("cze.1", "2026-27", src)
        self.assertIsNone(why)
        self.assertEqual([(r["date"], r["home"], r["away"], r["hg"], r["ag"]) for r in rows],
                         [("2026-10-18", "Slavia Praha", "Plzen", 2, 0)])

    def test_wrong_country_uses_nothing(self):
        src = [af(1, "2026-10-18T15:00:00+00:00", "A", "B", 2, 0, country="Slovakia"),
               af(2, "2026-10-19T15:00:00+00:00", "C", "D", 1, 0)]
        rows, why = S.af_lag_pick("cze.1", "2026-27", src)
        self.assertEqual(rows, [])
        self.assertIn("Slovakia", why)

    def test_rows_without_country_judged_by_the_rest(self):
        src = [af(1, "2026-10-18T15:00:00+00:00", "A", "B", 2, 0, country=None),
               af(2, "2026-10-19T15:00:00+00:00", "C", "D", 1, 0)]
        rows, why = S.af_lag_pick("cze.1", "2026-27", src)
        self.assertIsNone(why)
        self.assertEqual(len(rows), 2)

    def test_no_key_reads_nothing(self):
        old = os.environ.pop("API_FOOTBALL_KEY", None)
        try:
            self.assertEqual(S.af_lag_results("cze.1", "2026-27"), ([], None))
        finally:
            if old is not None:
                os.environ["API_FOOTBALL_KEY"] = old


class Fill(unittest.TestCase):
    def test_fills_under_openfootball_spelling_marked_apifootball(self):
        rows = [{"date": "2026-10-18", "home": "Slavia Praha", "away": "Viktoria Plzeň",
                 "hg": None, "ag": None, "time": None, "round": None}]
        res, _ = S.af_lag_pick("cze.1", "2026-27",
                               [af(1, "2026-10-18T15:00:00+00:00", "Slavia Praha", "Plzen", 2, 0)])
        n, bad, un = B.fill_lagging(rows, res, date(2026, 11, 18), source="apifootball")
        self.assertEqual((n, bad, un), (1, [], 0))
        self.assertEqual((rows[0]["hg"], rows[0]["ag"], rows[0]["filledFrom"]),
                         (2, 0, "apifootball"))
        self.assertEqual(rows[0]["away"], "Viktoria Plzeň")


if __name__ == "__main__":
    unittest.main()
