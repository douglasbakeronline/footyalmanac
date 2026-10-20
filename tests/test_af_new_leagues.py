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


if __name__ == "__main__":
    unittest.main()
