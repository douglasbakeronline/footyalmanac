"""The green edge flag (10 Nov 2026, groupings.edge_flag): a football-data
league, clean for the Daily List, the model's pick also the bookmakers'
favourite at 1.15-1.90, the bookmakers 60%+, the opposition 9+, the model no
more than 5 points above the market. Display only."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G


def fx(**kw):
    g = {"league": "sco.1", "p": {"h": 0.80, "d": 0.13, "a": 0.07}, "celtic": False, "unrated": False, "why": None,
         "market": {"avg": [1.15, 7.7, 12.3], "best": [1.18, 8.0, 13.0], "p": [0.80, 0.12, 0.08]}}
    for k, v in kw.items():
        if k in ("avg", "best", "fair"): g["market"]["p" if k == "fair" else k] = v
        else: g[k] = v
    return g


class EdgeFlag(unittest.TestCase):
    def test_flags_the_celtic_case(self):
        e = G.edge_flag(fx())
        self.assertEqual((e["side"], e["odds"], e["best"], e["opp"], e["rule"]), ("h", 1.15, 1.18, 12.3, G.EDGE_RULE))

    def test_away_favourite(self):
        e = G.edge_flag(fx(p={"h": 0.07, "d": 0.13, "a": 0.80}, avg=[12.3, 7.7, 1.15], best=[13, 8, 1.18], fair=[0.08, 0.12, 0.80]))
        self.assertEqual((e["side"], e["opp"]), ("a", 12.3))

    def test_each_condition_refuses(self):
        self.assertIsNone(G.edge_flag(fx(avg=[1.15, 7.7, 4.5])))                     # opposition under 4/1 (5.0, rule 2)
        self.assertEqual(G.edge_flag(fx(avg=[1.15, 7.7, 8.5]))["rule"], 2)           # 8.5 cleared rule 2, not rule 1
        self.assertIsNone(G.edge_flag(fx(avg=[1.10, 9.0, 21.0])))                    # too short
        self.assertIsNone(G.edge_flag(fx(avg=[1.95, 4.0, 9.5])))                     # too long
        self.assertIsNone(G.edge_flag(fx(fair=[0.58, 0.25, 0.17])))                  # bookmakers under 60%
        self.assertIsNone(G.edge_flag(fx(p={"h": 0.87, "d": 0.08, "a": 0.05})))      # model 7 points above
        self.assertIsNone(G.edge_flag(fx(celtic=True)))
        self.assertIsNone(G.edge_flag(fx(unrated=True)))
        self.assertIsNone(G.edge_flag(fx(why="cup")))
        self.assertIsNone(G.edge_flag(fx(league="en.w1")))                            # never tested on price
        self.assertIsNone(G.edge_flag(fx(market=None)))
        self.assertIsNone(G.edge_flag(fx(p={"h": 0.30, "d": 0.40, "a": 0.30})))      # a draw read

    def test_model_pick_must_be_the_favourite(self):
        self.assertIsNone(G.edge_flag(fx(p={"h": 0.45, "d": 0.10, "a": 0.45 + 0.001}, avg=[1.15, 7.7, 12.3])))

    def test_leagues_are_the_football_data_divisions(self):
        import odds as O
        self.assertEqual(G.edge_leagues(), set(O.DIVS.values()))
        self.assertTrue(G.edge_leagues() <= {c for c in G.edge_leagues() if G.core_league(c)})


if __name__ == "__main__":
    unittest.main()
