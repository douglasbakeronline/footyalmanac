"""Croatia, Hungary, Serbia, Ukraine and Korea from API-Football (21 Oct 2026)."""
import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import sources as S
import build as B
import tune


def fx(country, home="Dinamo Zagreb", away="Hajduk Split", lid=210):
    return {"league": {"id": lid, "country": country, "season": 2025},
            "fixture": {"date": "2026-03-01T15:00:00+00:00", "status": {"short": "FT"}},
            "teams": {"home": {"name": home}, "away": {"name": away}},
            "score": {"fulltime": {"home": 2, "away": 1}}}


class AfNew(unittest.TestCase):
    def test_registered_and_off_list(self):
        for code, lid in S.AF_NEW.items():
            self.assertEqual(S.AF[code], lid)
            self.assertIn(code, E.LEAGUES)
            self.assertIn(code, B.NEW_BOARD_ONLY)
            self.assertNotIn(code, tune.codes())
        self.assertEqual(set(S.AF_NEW), {"hrv.1", "hun.1", "srb.1", "ukr.1", "kr.1"})

    def test_no_duplicate_ids(self):
        ids = [S.AF[c] for c in S.AF_NEW]
        for c, i in S.AF.items():
            if c not in S.AF_NEW:
                self.assertNotIn(i, ids, c)

    def test_wrong_country_is_dropped(self):
        with mock.patch.object(S, "_af_season", return_value=[fx("Spain")]):
            self.assertEqual(S.af_rows("hrv.1", "2025-26"), [])

    def test_right_country_is_read(self):
        with mock.patch.object(S, "_af_season", return_value=[fx("Croatia")]):
            rows = S.af_rows("hrv.1", "2025-26")
        self.assertEqual((rows[0]["hg"], rows[0]["ag"]), (2, 1))

    def test_korea_spelling(self):
        with mock.patch.object(S, "_af_season", return_value=[fx("South-Korea", "Jeonbuk", "Ulsan", 292)]):
            self.assertEqual(len(S.af_rows("kr.1", "2025")), 1)

    # 20 Oct 2026: the current season reads the shared date pool, whose rows
    # pass through the day cache (_compact / _expand). The cache dropped the
    # country, so the guard threw away every current-season row of all five
    # leagues and Shakhtar went into a Champions League tie with no form.
    def pool_row(self, country, when="2026-10-25T15:00:00+00:00", st="NS", hg=None, ag=None):
        f = {"league": {"id": 333, "season": 2026, "country": country},
             "fixture": {"id": 1, "date": when, "status": {"short": st}},
             "teams": {"home": {"name": "Shakhtar Donetsk"}, "away": {"name": "Dynamo Kyiv"}},
             "score": {"fulltime": {"home": hg, "away": ag}}}
        return S._expand(S._compact(f))

    def test_country_survives_the_day_cache(self):
        self.assertEqual(self.pool_row("Ukraine")["league"]["country"], "Ukraine")

    def test_current_season_reads_through_the_pool(self):
        pool = {333: [self.pool_row("Ukraine", "2026-09-20T15:00:00+00:00", "FT", 2, 1),
                      self.pool_row("Ukraine")]}
        with mock.patch.object(S, "af_season_pool", return_value=pool):
            rows = S.af_rows("ukr.1", E.LEAGUES["ukr.1"]["season"])
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["hg"] for r in rows], [2, None])

    def test_old_cache_rows_judged_by_new_ones(self):
        old = S._expand(S._compact(self.pool_row("Ukraine"))[:9])   # nine-field day file
        self.assertNotIn("country", old["league"])
        pool = {333: [old, self.pool_row("Ukraine")]}
        with mock.patch.object(S, "af_season_pool", return_value=pool):
            self.assertEqual(len(S.af_rows("ukr.1", E.LEAGUES["ukr.1"]["season"])), 2)
        with mock.patch.object(S, "af_season_pool", return_value={333: [old]}):
            self.assertEqual(S.af_rows("ukr.1", E.LEAGUES["ukr.1"]["season"]), [])
        with mock.patch.object(S, "af_season_pool", return_value={333: [self.pool_row("Spain")]}):
            self.assertEqual(S.af_rows("ukr.1", E.LEAGUES["ukr.1"]["season"]), [])


if __name__ == "__main__":
    unittest.main()
