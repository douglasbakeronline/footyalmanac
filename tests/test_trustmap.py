"""Where to trust the model (10 Nov 2026): the grid counts graded picks by
family and band, landed against quoted, with z."""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import trustmap


class Grid(unittest.TestCase):
    def test_bands_all_and_z(self):
        rs = [("nba", 0.60, True)] * 8 + [("nba", 0.60, False)] * 2 + [("nba", 0.90, True)] * 3 + [("nfl", 0.70, False)]
        g = trustmap.grid(rs)
        fam = {f["key"]: f["cells"] for f in g["families"]}
        self.assertEqual([f["key"] for f in g["families"]], ["nba", "nfl"])     # busiest first
        self.assertEqual((fam["nba"]["0"]["n"], fam["nba"]["0"]["won"]), (10, 8))
        self.assertAlmostEqual(fam["nba"]["0"]["quoted"], 0.60)
        self.assertGreater(fam["nba"]["0"]["z"], 0)
        self.assertEqual(fam["nba"]["3"]["n"], 3)
        self.assertEqual(fam["nba"]["all"]["n"], 13)
        self.assertLess(fam["nfl"]["all"]["z"], 0)
        self.assertEqual(g["bands"][-1], [0.95, 1.0])

    def test_under_55_and_unbanded_are_left_out(self):
        self.assertEqual(trustmap.grid([("nba", 0.5, True)])["families"], [])

    def test_football_families(self):
        self.assertEqual(trustmap._family_football("af.123"), "football-wider")
        self.assertEqual(trustmap._family_football("en.1"), "football")
        self.assertEqual(trustmap._family_football("nope.9"), "football-cups")


if __name__ == "__main__":
    unittest.main()
