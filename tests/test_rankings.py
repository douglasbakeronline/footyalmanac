"""Tests for rankings.py: the FIFA / ATP adjustments, name mapping and the
refresh and fetch fallbacks. No network: _get and the file are patched."""
import json, math, os, sys, tempfile, unittest
from datetime import date, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rankings as R


# A release newer than write_men's file (30 days old). It was the literal
# 2026-10-22, which stopped being newer on 21 Nov 2026 and failed CI.
NEW_RELEASE = (date.today() - timedelta(days=1)).isoformat()

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
        # The ranking page is never fetched in a test unless a test says so.
        q = mock.patch.object(R, "_get_text", side_effect=OSError("page down"))
        q.start()
        self.addCleanup(q.stop)

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

    @staticmethod
    def fake_api(releases, calls, latest=None):
        """A FIFA API: `releases` maps id -> date string; the dateless
        overview names `latest`; other ids return no rankings."""
        def fake(url, timeout=20):
            if "dateId" not in url:
                calls.append("latest")
                if latest is None:
                    raise OSError("overview down")
                return {"dates": [{"dateId": f"id{latest}"}]}
            i = int(url.rsplit("dateId=id", 1)[1])
            calls.append(i)
            if i in releases:
                return {"rankings": [{"lastUpdateDate": f"{releases[i]}T00:00:00",
                                      "rankingItem": {"name": "Spain", "rank": 1, "totalPoints": 1900 + i}}]}
            return {"rankings": []}
        return fake

    def test_stale_file_takes_newest_release(self):
        base = R.FIFA_SEED
        self.write(30, id_=base)
        calls = []
        fake = self.fake_api({base + 3: "2026-10-03", base + 5: "2026-10-05"}, calls)
        log = []
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=10, log=log)
        self.assertEqual(new["id"], base + 5)
        self.assertEqual(new["date"], "2026-10-05")
        self.assertEqual(new["teams"]["Spain"], [1, 1900 + base + 5])
        self.assertEqual(min(i for i in calls if i != "latest"), base + 1)
        self.assertEqual(json.load(open(self.path))["id"], base + 5)
        self.assertIn("new release", log[0])

    def test_scan_starts_after_the_file_id_not_the_seed(self):
        # Bug 4: the file sat at the seed id, so a scan from the seed could
        # never pass it. The scan starts after max(seed, file id).
        base = R.FIFA_SEED + 40
        self.write(30, id_=base)
        calls = []
        fake = self.fake_api({base + 2: "2026-10-02"}, calls)
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=5)
        self.assertEqual(new["id"], base + 2)
        self.assertNotIn(R.FIFA_SEED + 1, calls)
        self.assertEqual(min(i for i in calls if i != "latest"), base + 1)

    def test_file_below_seed_scans_from_seed(self):
        self.write(30, id_=100)
        calls = []
        fake = self.fake_api({}, calls)
        with mock.patch.object(R, "_get", fake):
            R.refresh_fifa(scan=3)
        self.assertEqual(min(i for i in calls if i != "latest"), R.FIFA_SEED + 1)

    def test_overview_latest_id_beats_the_scan_window(self):
        # The dateless overview names a release far beyond the scan window.
        base = R.FIFA_SEED
        self.write(30, id_=base)
        calls = []
        fake = self.fake_api({base + 500: "2026-10-20"}, calls, latest=base + 500)
        log = []
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=5, log=log)
        self.assertEqual(new["id"], base + 500)
        self.assertEqual(calls[0], "latest")
        self.assertIn(base + 500, calls)
        self.assertEqual(json.load(open(self.path))["id"], base + 500)

    def test_release_answered_only_with_ranking_type(self):
        # 15 Nov 2026: ids after 15175 came back empty on the old URL. A
        # release answered only on the rankingType=football form is taken.
        base = R.FIFA_SEED
        self.write(30, id_=base)

        def fake(url, timeout=20):
            if "dateId" not in url:
                return {"x": 1}
            i = int(url.rsplit("dateId=id", 1)[1])
            if i == base + 2 and "rankingType=football" in url:
                return {"rankings": [{"lastUpdateDate": "2026-10-22T00:00:00",
                                      "rankingItem": {"name": "Spain", "rank": 1, "totalPoints": 1880}}]}
            return {"rankings": []}
        log = []
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=4, log=log)
        self.assertEqual((new["id"], new["date"]), (base + 2, "2026-10-22"))

    def test_overview_without_ids_logs_its_keys(self):
        self.write(30, id_=R.FIFA_SEED)
        fake = lambda url, timeout=20: {"rankings": []} if "dateId" in url else {"foo": [], "bar": 1}
        log = []
        with mock.patch.object(R, "_get", fake):
            R.refresh_fifa(scan=2, log=log)
        self.assertTrue(any("named no release id" in l and "bar" in l for l in log), log)

    def test_release_with_too_few_teams_is_refused(self):
        # A futsal or women's list under the same ids must not replace the
        # men's ranking (about 211 sides on file).
        base = R.FIFA_SEED
        d = (date.today() - timedelta(days=30)).isoformat()
        cur = {"id": base, "date": d, "teams": {f"T{k}": [k, 1000] for k in range(10)}}
        json.dump(cur, open(self.path, "w"))

        def fake(url, timeout=20):
            if "dateId" not in url:
                raise OSError("down")
            i = int(url.rsplit("dateId=id", 1)[1])
            n = {base + 1: 10, base + 3: 5}.get(i, 0)
            return {"rankings": [{"lastUpdateDate": f"2026-10-0{i - base}T00:00:00",
                                  "rankingItem": {"name": f"T{k}", "rank": k, "totalPoints": 1}}
                                 for k in range(n)]}
        log = []
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=4, log=log)
        self.assertEqual(new["id"], base + 1)
        self.assertTrue(any("refused id" in l and str(base + 3) in l for l in log), log)

    @staticmethod
    def rows(names, day):
        return {"rankings": [{"lastUpdateDate": f"{day}T00:00:00",
                              "rankingItem": {"name": n, "rank": k + 1, "totalPoints": 1900 - k}}
                             for k, n in enumerate(names)]}

    def write_men(self, days_old=30):
        d = (date.today() - timedelta(days=days_old)).isoformat()
        cur = {"id": R.FIFA_SEED, "date": d,
               "teams": {f"M{k}": [k + 1, 1800 - k] for k in range(40)}}
        json.dump(cur, open(self.path, "w"))
        return cur

    def test_overview_rows_without_an_id_are_the_new_release(self):
        # 15 Nov 2026 CI log: the dateless overview answers {"rankings": [...]}
        # and names no id, and no id after 15175 answers.
        cur = self.write_men()
        names = [f"M{k}" for k in (1, 0, 2, 3, 5, 4)] + [f"M{k}" for k in range(6, 40)]
        def fake(url, timeout=20):
            if "dateId" in url:
                return {"rankings": []}
            return self.rows(names, NEW_RELEASE)
        log = []
        with mock.patch.object(R, "_get", fake):
            new = R.refresh_fifa(scan=3, log=log)
        self.assertEqual(new["date"], NEW_RELEASE)
        self.assertEqual(new["id"], R.FIFA_SEED)
        self.assertEqual(new["teams"]["M1"], [1, 1900])
        self.assertEqual(json.load(open(self.path))["date"], NEW_RELEASE)
        self.assertTrue(any("from the dateless overview" in l for l in log), log)

    def test_overview_rows_older_than_the_file_are_ignored(self):
        cur = self.write_men(days_old=30)
        old = (date.today() - timedelta(days=60)).isoformat()
        fake = lambda url, timeout=20: {"rankings": []} if "dateId" in url else \
            self.rows([f"M{k}" for k in range(40)], old)
        with mock.patch.object(R, "_get", fake):
            self.assertEqual(R.refresh_fifa(scan=2), cur)

    def test_another_ranking_in_the_overview_is_refused(self):
        # A women's or futsal list: as many sides, a different top 20.
        cur = self.write_men()
        names = [f"W{k}" for k in range(25)] + [f"M{k}" for k in range(20, 40)]
        fake = lambda url, timeout=20: {"rankings": []} if "dateId" in url else \
            self.rows(names, NEW_RELEASE)
        log = []
        with mock.patch.object(R, "_get", fake):
            self.assertEqual(R.refresh_fifa(scan=2, log=log), cur)
        self.assertTrue(any("refused the overview" in l for l in log), log)

    def test_ranking_page_embedded_json_is_the_release(self):
        cur = self.write_men()
        names = [f"M{k}" for k in range(40)]
        blob = json.dumps({"props": {"pageProps": {"pageData": {"ranking": self.rows(names, NEW_RELEASE)["rankings"]}}}})
        html = (f'<a href="?dateId=id15400">Oct</a><script id="__NEXT_DATA__" type="application/json">{blob}</script>')
        calls = []
        def fake(url, timeout=20):
            calls.append(url)
            return {"rankings": []}
        log = []
        with mock.patch.object(R, "_get", fake), mock.patch.object(R, "_get_text", return_value=html):
            new = R.refresh_fifa(scan=2, log=log)
        self.assertEqual(new["date"], NEW_RELEASE)
        self.assertTrue(any("from the ranking page" in l for l in log), log)
        self.assertTrue(any("dateId=id15400" in u for u in calls))     # the page's id is asked first

    def test_page_without_rows_is_described(self):
        self.write_men()
        log = []
        with mock.patch.object(R, "_get", lambda url, timeout=20: {"rankings": []}), \
                mock.patch.object(R, "_get_text", return_value="<html>nothing</html>"):
            R.refresh_fifa(scan=2, log=log)
        self.assertTrue(any("page 20 chars" in l and "no ranking rows" in l for l in log), log)
        self.assertTrue(any("an empty rankings list" in l for l in log), log)

    def test_same_list(self):
        cur = {"teams": {f"M{k}": [k + 1, 1] for k in range(30)}}
        swapped = {"teams": {f"M{k}": [30 - k, 1] for k in range(30)}}
        self.assertTrue(R._same_list(cur, cur))
        self.assertTrue(R._same_list(cur, swapped))          # every top-20 side inside the top 30
        self.assertFalse(R._same_list(cur, {"teams": {f"W{k}": [k + 1, 1] for k in range(30)}}))
        self.assertTrue(R._same_list(None, cur))

    def test_release_ids_parsing(self):
        doc = {"dates": [{"dateId": "id15175"}, {"dateId": "id15190"}], "x": {"id": 7}, "s": "id15200"}
        self.assertEqual(R._release_ids(doc), {15175, 15190, 15200})
        self.assertEqual(R._release_ids({"rankings": []}), set())

    def test_nothing_newer_keeps_file_untouched(self):
        cur = self.write(30)
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            self.assertEqual(R.refresh_fifa(scan=5, log=log), cur)
        self.assertEqual(json.load(open(self.path)), cur)
        self.assertIn("no newer", log[0])

    def test_fetch_failure_is_logged_not_swallowed(self):
        self.write(30)
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            R.refresh_fifa(scan=5, log=log)
        failures = [l for l in log if "fetch failure" in l]
        self.assertEqual(len(failures), 1)
        self.assertIn("OSError: down", failures[0])

    def test_stale_file_warns_loudly(self):
        self.write(60)
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            R.refresh_fifa(scan=2, log=log)
        self.assertTrue(any(l.startswith("WARNING:") and "60 days old" in l for l in log), log)

    def test_file_under_45_days_does_not_warn(self):
        self.write(30)
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            R.refresh_fifa(scan=2, log=log)
        self.assertFalse(any(l.startswith("WARNING:") for l in log), log)

    def test_no_file_and_no_release(self):
        log = []
        with mock.patch.object(R, "_get", side_effect=OSError("down")):
            self.assertIsNone(R.refresh_fifa(scan=3, log=log))
        self.assertIn("none", log[0])
        self.assertFalse(os.path.exists(self.path))


class Schedule(unittest.TestCase):
    """The endpoint FIFA's page calls (15 Nov 2026): schedule ids, not dateIds."""
    PAGE = ('<script type="application/json">{"dates":[{"year":"2026","dates":['
            '{"id":"FRS_Male_Football_20260720","iso":"2026-10-07T10:10:08.375Z"},'
            '{"id":"FRS_Male_Football_20260611","iso":"2026-07-20T08:37:28.979Z"}]}]}</script>')

    def test_dates_newest_first(self):
        self.assertEqual(R._schedule_dates(self.PAGE)[0], ("FRS_Male_Football_20260720", "2026-10-07"))
        self.assertEqual(R._schedule_dates("<html></html>"), [])

    def test_parse_maps_names_back_to_file_spelling(self):
        doc = {"rankings": [{"teamName": "Spain", "rank": 1, "totalPoints": 2011.571862},
                            {"teamName": "Hong Kong", "rank": 150, "totalPoints": 900.123456},
                            {"teamName": "Unranked", "rank": None, "totalPoints": 0}]}
        rel = R._parse_schedule(doc, "2026-10-07")
        self.assertEqual(rel["teams"], {"Spain": [1, 2011.57], "Hong Kong, China": [150, 900.12]})
        self.assertEqual(rel["date"], "2026-10-07")
        self.assertIsNone(R._parse_schedule({"rankings": []}, "2026-10-07"))

    def test_fetch_uses_newest_schedule(self):
        seen = []
        def fake(url, timeout=20):
            seen.append(url)
            return {"rankings": [{"teamName": "Spain", "rank": 1, "totalPoints": 2000.0}]}
        with mock.patch.object(R, "_get", fake):
            rel = R._fifa_schedule(self.PAGE)
        self.assertIn("scheduleId=FRS_Male_Football_20260720", seen[0])
        self.assertEqual(rel["date"], "2026-10-07")



class TennisRanksFailure(unittest.TestCase):
    DOC = {"items": [{"$ref": "http://x/ref"}]}
    RANKS = {"ranks": [{"athlete": {"$ref": "http://x/athletes/42?lang=en"}, "current": 3}]}

    def run_ranks(self, get, cache):
        with mock.patch.object(R, "_get", get), mock.patch.object(R, "RANKS_CACHE_DIR", cache), \
                mock.patch.object(R.time, "sleep"):
            return R.tennis_ranks("atp")

    def test_retry_then_success_writes_copy(self):
        calls = []
        def get(url, timeout=20):
            calls.append(url)
            if len(calls) == 1:
                raise OSError("blip")
            return self.DOC if "rankings" in url and "ref" not in url else self.RANKS
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_ranks(get, d), {"42": 3})
            self.assertTrue(os.path.exists(os.path.join(d, "tennis-ranks-atp.json")))

    def test_outage_uses_last_good_copy(self):
        def down(url, timeout=20):
            raise OSError("down")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "tennis-ranks-atp.json"), "w") as fh:
                json.dump({"7": 1}, fh)
            self.assertEqual(self.run_ranks(down, d), {"7": 1})

    def test_outage_without_copy_is_empty(self):
        def down(url, timeout=20):
            raise OSError("down")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_ranks(down, d), {})

if __name__ == "__main__":
    unittest.main()
