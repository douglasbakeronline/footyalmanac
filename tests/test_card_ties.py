import gzip, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_ties as CT


def fx(lg, d, h, a, **kw):
    return dict({"league": lg, "date": d, "home": h, "away": a}, **kw)


class TieIndex(unittest.TestCase):
    def write(self, files):
        tmp = tempfile.mkdtemp()
        for name, rows in files.items():
            json.dump(rows, open(os.path.join(tmp, name), "w"))
        return tmp

    def test_reverse_within_days_is_a_tie(self):
        d = self.write({"2026-11-25.json": [fx("mx.1", "2026-11-26", "Toluca", "Atlas"),
                                            fx("mx.1", "2026-11-29", "Atlas", "Toluca")]})
        idx = CT.tie_index(d, since="2026-11-01")
        self.assertEqual(idx[("mx.1", "2026-11-26", "Toluca", "Atlas")], {"leg": 1, "other": "2026-11-29"})
        self.assertEqual(idx[("mx.1", "2026-11-29", "Atlas", "Toluca")], {"leg": 2, "other": "2026-11-26"})

    def test_regular_season_reverse_months_apart_is_not(self):
        d = self.write({"2026-09-12.json": [fx("mx.1", "2026-09-12", "Toluca", "Atlas")],
                        "2026-11-25.json": [fx("mx.1", "2026-11-26", "Atlas", "Toluca")]})
        self.assertEqual(CT.tie_index(d, since="2026-09-01"), {})

    def test_other_league_or_same_direction_is_not(self):
        d = self.write({"2026-11-25.json": [fx("mx.1", "2026-11-26", "Toluca", "Atlas"),
                                            fx("mx.2", "2026-11-29", "Atlas", "Toluca"),
                                            fx("mx.1", "2026-11-28", "Toluca", "Atlas")]})
        self.assertEqual(CT.tie_index(d, since="2026-11-01"), {})

    def test_tie_of_reads_pool_and_card_shapes(self):
        idx = {("mx.1", "2026-11-26", "Toluca", "Atlas"): {"leg": 1, "other": "2026-11-29"}}
        self.assertTrue(CT.tie_of({"sport": "football", "code": "mx.1", "date": "2026-11-26", "home": "Toluca", "away": "Atlas"}, idx))
        self.assertTrue(CT.tie_of({"code": "mx.1", "when": "2026-11-26T01:00:00Z", "home": "Toluca", "away": "Atlas"}, idx))
        self.assertIsNone(CT.tie_of({"sport": "nba", "code": "mx.1", "date": "2026-11-26", "home": "Toluca", "away": "Atlas"}, idx))


class Report(unittest.TestCase):
    def leg(self, h, a, won, d="2026-11-26", code="mx.1", p=0.7):
        return {"sport": "football", "code": code, "date": d, "home": h, "away": a, "pick": h, "won": won, "pModel": p, "fair": 0.65}

    def test_split_and_clear(self):
        idx = {("mx.1", "2026-11-26", "Toluca", "Atlas"): {"leg": 1, "other": "2026-11-29"},
               ("mx.1", "2026-11-29", "Atlas", "Toluca"): {"leg": 2, "other": "2026-11-26"}}
        by = {"2026-11-26": [self.leg("Toluca", "Atlas", False), self.leg("Pachuca", "Leon", True),
                             self.leg("Low", "Side", True, p=0.55)],
              "2026-11-29": [self.leg("Atlas", "Toluca", True, d="2026-11-29")]}
        rep = CT.report(by, idx, fault=lambda l: "no" if l["home"] == "Atlas" else None)
        self.assertEqual(rep["all"]["tie"]["n"], 2)
        self.assertEqual(rep["all"]["first"]["landed"], 0)
        self.assertEqual(rep["all"]["second"]["landed"], 1)
        self.assertEqual(rep["all"]["other"]["n"], 1)           # the 55% leg is under the 60% floor
        self.assertEqual(rep["clear"]["tie"]["n"], 1)
        self.assertEqual(rep["clear"]["second"]["n"], 0)
        body = "\n".join(CT.lines(rep))
        self.assertIn("second leg | 0 | | | |  |", body)      # an empty row keeps the table's columns

    def test_open_ties_finds_late_kickoff_in_next_pool_file(self):
        tmp = tempfile.mkdtemp()
        json.dump({"2026-11-25": [{"at": "2026-11-25T20:00:00Z", "why": "built", "groups": [["Golden State Warriors", "Toluca"]]}]},
                  open(os.path.join(tmp, "card-short.json"), "w"))
        with gzip.open(os.path.join(tmp, "pool-2026-11-26.json.gz"), "wt") as f:
            json.dump({"date": "2026-11-26", "legs": [{"sport": "football", "pick": "Toluca", "event": "Toluca v Atlas", "code": "mx.1",
                                                       "date": "2026-11-26", "when": "2026-11-26T01:00:00Z", "home": "Toluca", "away": "Atlas"}]}, f)
        idx = {("mx.1", "2026-11-26", "Toluca", "Atlas"): {"leg": 1, "other": "2026-11-29"}}
        self.assertEqual(CT.open_ties(idx, "2026-11-25T21:00:00Z", archive=tmp),
                         [("2026-11-25", "Toluca", "Toluca v Atlas", 1, "2026-11-29")])
        self.assertEqual(CT.open_ties(idx, "2026-11-26T02:00:00Z", archive=tmp), [])   # started: not open


if __name__ == "__main__":
    unittest.main()
