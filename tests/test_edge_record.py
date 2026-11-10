"""score.edge_of / edge_record (10 Nov 2026): the green Edge flag graded.
A row archived with an "edge" key is live (None there means not flagged, and
is never replayed); an older row is flagged from its archived prices."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import score as S
import build as B

FLAG = {"side": "h", "odds": 1.2, "best": 1.25, "fair": 0.8, "opp": 11.0, "model": 0.8, "rule": 1}


class EdgeRecord(unittest.TestCase):
    def test_live_and_replayed(self):
        self.assertEqual(S.edge_of({"edge": FLAG}, lambda g: None)["live"], True)
        self.assertIsNone(S.edge_of({"edge": None}, lambda g: FLAG))           # published unflagged stays unflagged
        self.assertEqual(S.edge_of({}, lambda g: FLAG)["live"], False)          # before 10 Nov: replayed
        self.assertIsNone(S.edge_of({}, lambda g: None))

    def test_tally(self):
        rows = [{"date": "2026-11-01", "actual": "h", "edge": dict(S.edge_of({"edge": FLAG}, None))},
                {"date": "2026-11-02", "actual": "d", "edge": dict(S.edge_of({}, lambda g: FLAG))},
                {"date": "2026-11-03", "actual": "a", "edge": None}]
        r = S.edge_record(rows)
        a = r["all"]
        self.assertEqual((a["n"], a["won"], a["expected"]), (2, 1, 1.6))
        self.assertAlmostEqual(a["return"], 1.2 / 2 - 1, places=4)
        self.assertAlmostEqual(a["returnBest"], 1.25 / 2 - 1, places=4)
        self.assertEqual(r["live"]["n"], 1)
        self.assertEqual(S.edge_record([])["all"], {"n": 0})

    def test_summary_carries_it(self):
        self.assertIn("edge", B.SUMMARY_KEYS)


if __name__ == "__main__":
    unittest.main()
