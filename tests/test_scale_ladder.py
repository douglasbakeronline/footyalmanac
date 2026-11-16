import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scale_ladder as L


class Football(unittest.TestCase):
    def test_a_three_nil_win(self):
        r = L.football_landed(3, 0)
        self.assertTrue(r["w_o25"] and r["wtn"] and r["by3"] and r["t_o25"])
        self.assertFalse(r["w_o35"] or r["wbtts"])

    def test_a_draw(self):
        r = L.football_landed(1, 1)
        self.assertTrue(r["dc"])
        self.assertFalse(r["win"] or r["by2"] or r["w_o15"])


class Tennis(unittest.TestCase):
    def row(self, note, ok=True, **kw):
        return dict({"note": note, "ok": ok}, **kw)

    def test_the_winner_in_three_sets(self):
        sets = L.tennis_sets(self.row("(3) Ben Shelton (USA) bt (6) Arthur Fils (FRA) 6-2 3-6 6-3"))
        r = L.tennis_landed(sets)
        self.assertTrue(r["win"] and r["fs_win"] and r["g35"])
        self.assertFalse(r["straight"] or r["g55"])

    def test_the_pick_lost(self):
        sets = L.tennis_sets(self.row("A (GER) bt B (ESP) 6-4 6-4", ok=False))
        self.assertEqual(sets, [(4, 6), (4, 6)])
        self.assertFalse(L.tennis_landed(sets)["win"])

    def test_a_retirement_is_void(self):
        self.assertIsNone(L.tennis_sets(self.row("A bt B 6-4 2-1", retired=True)))


class Margins(unittest.TestCase):
    def test_rockets_by_28(self):
        r = L.margin_landed("nba", 28)
        self.assertTrue(all(r[k] for k in r))

    def test_a_three_point_nfl_win(self):
        r = L.margin_landed("nfl", 3)
        self.assertTrue(r["win"] and r["by3"])
        self.assertFalse(r["by4"] or r["by7"])


class Build(unittest.TestCase):
    def test_tallies_by_band_tier_and_needs(self):
        f = {"graded": [{"confidence": 0.9, "pick": "h", "result": [3, 0], "list": True, "date": "2026-11-10"},
                        {"confidence": 0.9, "pick": "a", "result": [1, 1], "date": "2026-11-10"}]}
        rows = list(L.rows(f, {}, {}))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][3], "list")
        self.assertEqual(L.band_of(0.9), "85+")
        self.assertEqual(L._done({"n": 4, "landed": 2}), {"n": 4, "landed": 2, "rate": 0.5, "needs": 2.0})


if __name__ == "__main__":
    unittest.main()
