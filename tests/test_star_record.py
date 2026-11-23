import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import star_record as SR


class StarRule(unittest.TestCase):
    def fb(self, **k):
        row = {"p": {"h": 0.86, "d": 0.09, "a": 0.05}, "confidence": 0.86, "list": True,
               "market": {"best": [1.25, 6.0, 12.0], "p": [0.80, 0.13, 0.07]}}
        row.update(k)
        return row

    def test_football(self):
        self.assertTrue(SR.football_star(self.fb())[0])
        self.assertFalse(SR.football_star(self.fb(list=False))[0])
        self.assertFalse(SR.football_star(self.fb(celtic=True))[0])
        self.assertFalse(SR.football_star(self.fb(market={"best": [1.45, 4, 6], "p": [0.66, 0.2, 0.14]}))[0])   # 1.40+
        self.assertFalse(SR.football_star(self.fb(market={"best": [1.30, 4, 6], "p": [0.74, 0.16, 0.10]}))[0])  # 12 points above
        self.assertTrue(SR.football_star(self.fb(market={}))[0])                                                 # unpriced passes

    def test_college_side(self):
        g = {"sport": "ncaab", "home": "A", "away": "B", "pick": "B", "confidence": 0.9}
        self.assertFalse(SR.sport_star(g))
        g.update(pick="A", neutral=True)
        self.assertFalse(SR.sport_star(g))
        g.update(neutral=False)
        self.assertTrue(SR.sport_star(g))

    def test_strict(self):
        self.assertFalse(SR.strict({"sport": "football", "star": True, "conf": 0.84}))
        self.assertTrue(SR.strict({"sport": "football", "star": True, "conf": 0.85}))
        self.assertTrue(SR.strict({"sport": "nfl", "star": True, "conf": 0.81}))


if __name__ == "__main__":
    unittest.main()
