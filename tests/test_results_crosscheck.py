"""A second source for the graded football results (25 Nov 2026, #472):
periods.py names the graded results API-Football's day file scores another
way (periods/disagree.json), drops them when the record is regraded, and
tools/card_integrity.py raises one when it is a leg Douglas staked."""
import gzip, json, os, sys, tempfile, unittest
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import periods, sources
import card_integrity as CI

KEY = "en.1|2026-11-15|Chelsea|Fulham"


def day_file(cache, ft, ht=(1, 0)):
    row = sources._compact({"league": {"id": 39, "season": 2026},
                            "fixture": {"id": 2, "date": "2026-11-15T15:00:00+00:00", "status": {"short": "FT"}},
                            "teams": {"home": {"name": "Chelsea"}, "away": {"name": "Fulham"}},
                            "score": {"fulltime": {"home": ft[0], "away": ft[1]}, "halftime": {"home": ht[0], "away": ht[1]}}})
    with gzip.open(os.path.join(cache, "day-2026-11-15.json.gz"), "wt") as fh:
        json.dump({"final": True, "rows": [row]}, fh)


def graded(here, result):
    json.dump({"graded": [{"league": "en.1", "date": "2026-11-15", "home": "Chelsea", "away": "Fulham",
                           "result": list(result), "kickoff": "2026-11-15T15:00:00Z"}]},
              open(os.path.join(here, "record-graded.json"), "w"))


class Disagreements(unittest.TestCase):
    def test_named_and_kept_then_dropped_on_regrade(self):
        with tempfile.TemporaryDirectory() as here:
            cache = os.path.join(here, ".afcache"); os.makedirs(cache)
            day_file(cache, (3, 0)); graded(here, (2, 0))
            log = []
            periods.build(here, today=date(2026, 11, 16), cache_dir=cache, log=log)
            dis = json.load(open(os.path.join(here, "periods", "disagree.json")))
            self.assertEqual(dis[KEY]["graded"], [2, 0]); self.assertEqual(dis[KEY]["af"], [3, 0])
            self.assertEqual(dis[KEY]["fid"], 2); self.assertEqual(dis[KEY]["sim"], [1.0, 1.0])
            self.assertNotIn(KEY, json.load(open(os.path.join(here, "periods", "missed.json"))))
            self.assertTrue(any("graded 2-0, API-Football 3-0" in l for l in log), log)
            self.assertIn(("2026-11-15", "Chelsea", "Fulham"), periods.disagreements(here))
            # a second run with the record unchanged does not look again
            self.assertEqual(periods.build(here, today=date(2026, 11, 16), cache_dir=cache)[0], 0)
            # regraded to agree: the disagreement goes and the half time is kept
            graded(here, (3, 0))
            want, found, _ = periods.build(here, today=date(2026, 11, 16), cache_dir=cache)
            self.assertEqual((want, found), (1, 1))
            self.assertEqual(json.load(open(os.path.join(here, "periods", "disagree.json"))), {})
            self.assertEqual(periods.check(here), (1, 0))


class Integrity(unittest.TestCase):
    def rec(self, name="Card 2x", status="won", sport="football"):
        return [{"date": "2026-11-25", "groups": [{"name": name, "legs": [
            {"event": "Chelsea v Fulham", "pick": "Chelsea", "sport": sport, "status": status, "when": "2026-11-25T15:00:00Z"}]}]}]

    def dis(self, sim=(1.0, 1.0)):
        return {("2026-11-25", "Chelsea", "Fulham"): {"graded": [2, 0], "af": [3, 0], "fid": 9, "sim": list(sim)}}

    def test_staked_leg_raised(self):
        out = CI.result_disagrees(self.rec(), self.dis())
        self.assertEqual(len(out), 1)
        self.assertEqual((out[0]["check"], out[0]["graded"], out[0]["apiFootball"]), ("result-disagrees", "2-0", "3-0"))

    def test_not_raised(self):
        self.assertEqual(CI.result_disagrees(self.rec(), self.dis(sim=(1.0, 0.6))), [])   # loose names: maybe another fixture
        self.assertEqual(CI.result_disagrees(self.rec(name="Model 2x"), self.dis()), [])  # paper, not staked
        self.assertEqual(CI.result_disagrees(self.rec(status="pending"), self.dis()), [])
        self.assertEqual(CI.result_disagrees(self.rec(sport="nba"), self.dis()), [])
        self.assertEqual(CI.result_disagrees(self.rec(), self.dis(), since="2026-11-26"), [])


if __name__ == "__main__":
    unittest.main()
