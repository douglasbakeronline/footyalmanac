"""Tests for rankings.py: the FIFA / ATP adjustments, name mapping and the
refresh and fetch fallbacks. No network: _get and the file are patched."""
import json, math, os, sys, tempfile, unittest
from datetime import date, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rankings as R


class Maths(unittest.TestCase):
    def test_sig_logit_roundtrip(self):
        for p in (0.1, 0.5, 0.8, 0.95):
            self.assertAlmostEqual(R._sig(R._logit(p)), p, places=9)

    def test_extremes_do_not_overflow(self):
        self.assertTrue(0 < R._sig(1e9) <= 1)
        self.assertTrue(0 <= R._sig(-1e9) < 1)
        self.assertTrue(math.isfinite(R._logit(0)) and math.isfinite(R._logit(1)))


class FifaAdjust(unittest.TestCase):
    def test_missing_side_keeps_confidence(self):
        self.assertEqual(R.adjust_fifa(0.7, None, [5, 1500]), 0.7)
        self.assertEqual(R.adjust_fifa(0.7, [5, 1500], None), 0.7)

    def test_formula_equal_points(self):
        w = R.FIFA_W
        want = R._sig(w[0] + w[1] * R._logit(0.7) + w[3])
        self.assertAlmostEqual(R.adjust_fifa(0.7, [5, 1500], [9, 1500]), want)

    def test_bigger_points_gap_raises_pick(self):
        lo = R.adjust_fifa(0.7, [5, 1500], [9, 1450])
        hi = R.adjust_fifa(0.7, [5, 1500], [9, 1300])
        self.assertGreater(hi, lo)

    def test_stays_a_probability(self):
        for c in (0.0, 0.5, 1.0):
            self.assertTrue(0 < R.adjust_fifa(c, [1, 1900], [200, 800]) < 1)


class FifaTeam(unittest.TestCase):
    fifa = {"teams": {"USA": [11, 1650], "Korea Republic": [22, 1500], "Spain": [3, 1850],
                      "Côte d'Ivoire": [40, 1400]}}

    def test_mapped_names(self):
        self.assertEqual(R.fifa_team(self.fifa, "United States"), [11, 1650])
        self.assertEqual(R.fifa_team(self.fifa, "South Korea"), [22, 1500])
        self.assertEqual(R.fifa_team(self.fifa, "Ivory Coast"), [40, 1400])

    def test_direct_name_and_unknown(self):
        self.assertEqual(R.fifa_team(self.fifa, "Spain"), [3, 1850])
        self.assertIsNone(R.fifa_team(self.fifa, "Martinique"))

    def test_no_file(self):
        self.assertIsNone(R.fifa_team(None, "Spain"))

    def test_mapping_targets_are_not_identity(self):
        for k, v in R.FIFA_NAMES.items():
            self.assertNotEqual(k, v)


class AtpAdjust(unittest.TestCase):
    def test_both_unranked_keeps_confidence(self):
        self.assertEqual(R.adjust_atp(0.66, None, None), 0.66)
        self.assertEqual(R.adjust_atp(0.66, 0, 0), 0.66)

    def test_equal_ranks_no_gap_term(self):
        w = R.ATP_W
        self.assertAlmostEqual(R.adjust_atp(0.7, 20, 20), R._sig(w[0] + w[1] * R._logit(0.7)))

    def test_unranked_counts_as_cap(self):
        self.assertAlmostEqual(R.adjust_atp(0.7, 10, None), R.adjust_atp(0.7, 10, R.ATP_CAP))

    def test_rank_above_cap_is_capped(self):
        self.assertAlmostEqual(R.adjust_atp(0.7, 10, 900), R.adjust_atp(0.7, 10, R.ATP_CAP))

    def test_better_ranked_favourite_gets_more(self):
        self.assertGreater(R.adjust_atp(0.7, 5, 100), R.adjust_atp(0.7, 50, 100))


class TennisRanks(unittest.TestCase):
    def test_parses_ranks(self):
        idx = {"items": [{"$ref": "http://x/ref"}]}
        doc = {"ranks": [
            {"athlete": {"$ref": "http://a/athletes/111?lang=en"}, "current": 1},
            {"athlete": {"$ref": "http://a/athletes/222"}, "current": 2},
            {"athlete": {"$ref": "http://a/athletes/333"}, "current": 0},
            {"athlete": {}, "current": 4},
        ]}
        seen = []

        def fake(url, timeout=20):
            seen.append(url)
            return idx if len(seen) == 1 else doc
        with mock.patch.object(R, "_get", fake):
            out = R.tennis_ranks("atp")
        self.assertEqual(out, {"111": 1, "222": 2})
        self.assertTrue(seen[1].startswith("https://"))

    def test_failure_gives_empty(self):
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            self.assertEqual(R.tennis_ranks("wta"), {})


class Refresh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "fifa.json")
        p = mock.patch.object(R, "FIFA_FILE", self.path)
        p.start()
        self.addCleanup(p.stop)

    def write(self, days_old, id_=100):
        d = (date.today() - timedelta(days=days_old)).isoformat()
        cur = {"id": id_, "date": d, "teams": {"Spain": [1, 1800]}}
        json.dump(cur, open(self.path, "w"))
        return cur

    def test_load_missing_or_corrupt(self):
        self.assertIsNone(R.load_fifa())
        open(self.path, "w").write("{nope")
        self.assertIsNone(R.load_fifa())

    def test_fresh_file_makes_no_requests(self):
        cur = self.write(3)
        with mock.patch.object(R, "_get", side_effect=AssertionError("fetched")):
            self.assertEqual(R.refresh_fifa(), cur)

    def test_stale_file_takes_newest_release(self):
        self.write(30, id_=100)
        calls = []

        def fake(url, timeout=20):
            i = int(url.rsplit("id", 1)[1])
            calls.append(i)
            if i in (103, 105):
                return {"rankings": [{"lastUpdateDate": f"2026-10-{i - 100:02d}T00:00:00",
                                      "rankingItem": {"name": "Spain", "rank": 1, "totalPoints": 1900 + i}}]}
            return {"rankings": []}
        log = []
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=10, log=log)
        self.assertEqual(new["id"], 105)
        self.assertEqual(new["date"], "2026-10-05")
        self.assertEqual(new["teams"]["Spain"], [1, 2005])
        self.assertEqual(min(calls), 101)
        self.assertEqual(json.load(open(self.path))["id"], 105)
        self.assertIn("new release", log[0])

    def test_nothing_newer_keeps_file_untouched(self):
        cur = self.write(30)
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            self.assertEqual(R.refresh_fifa(scan=5, log=log), cur)
        self.assertEqual(json.load(open(self.path)), cur)
        self.assertIn("no newer", log[0])

    def test_no_file_and_no_release(self):
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            self.assertIsNone(R.refresh_fifa(scan=3, log=log))
        self.assertIn("none", log[0])
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
