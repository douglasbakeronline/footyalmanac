"""The domestic-cup list gate (build.cup_gate, 8 Oct 2026)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B


def rows(n, hit_rate, conf=0.82, date="2026-08-10", flags=(), thin=False, pick="h"):
    k = round(n * hit_rate)
    return [{"date": date, "cup": "afc.1", "conf": conf, "pick": pick, "hit": int(i < k),
             "flags": list(flags), "thin": thin} for i in range(n)]


class CupGate(unittest.TestCase):
    def setUp(self):
        self.saved = dict(B.CUP_LIST)

    def tearDown(self):
        B.CUP_LIST.clear(); B.CUP_LIST.update(self.saved)

    def test_pass_at_lowest_bar(self):
        d = B.cup_gate(rows(40, 0.85, conf=0.77) + rows(40, 0.85, conf=0.77, date="2026-03-01"))
        self.assertTrue(d["pass"]); self.assertEqual(d["bar"], 0.75)

    def test_too_few(self):
        self.assertFalse(B.cup_gate(rows(29, 1.0))["pass"])

    def test_one_window_failing(self):
        d = B.cup_gate(rows(40, 0.9) + rows(40, 0.7, date="2026-03-01"))
        self.assertFalse(d["pass"])

    def test_small_window_clearly_failing(self):
        d = B.cup_gate(rows(40, 0.9) + rows(10, 0.5, date="2026-03-01"))
        self.assertFalse(d["pass"])

    def test_flagged_thin_and_draw_excluded(self):
        r = rows(40, 0.9) + rows(40, 0.0, flags=["moved"]) + rows(40, 0.0, thin=True) + rows(40, 0.0, pick="d")
        self.assertTrue(B.cup_gate(r)["pass"])

    def test_cross(self):
        r = rows(40, 0.9) + rows(40, 0.9, flags=["cross"])
        d = B.cup_gate(r)
        self.assertTrue(d["crossPass"]); self.assertEqual(d["crossBar"], 0.75)
        d = B.cup_gate(rows(40, 0.9) + rows(80, 0.6, flags=["cross"]))
        self.assertTrue(d["pass"]); self.assertFalse(d["crossPass"])

    def _g(self, conf, reasons=None):
        lg = next(c for c in sorted(B.S.AF_CUPS) if not B.CUP_OTHER_RE.search(B.E.LEAGUES[c]["name"]))
        return {"league": lg, "p": {"h": conf, "d": (1 - conf) / 2, "a": (1 - conf) / 2},
                "celtic": {"reasons": reasons} if reasons else None, "unrated": False,
                "home": {"name": "Alpha", "played": 5, "last": {"P": 30}}, "away": {"name": "Beta", "played": 5, "last": {"P": 30}}}

    def test_list_reason(self):
        if not B.S.AF_CUPS:
            self.skipTest("no cups registered")
        B.CUP_LIST.update({"pass": False, "cross": False})
        self.assertEqual(B.list_reason(self._g(0.9)), "cup")
        B.CUP_LIST.update({"pass": True, "bar": 0.8, "cross": False, "crossBar": None})
        self.assertIsNone(B.list_reason(self._g(0.85)))
        self.assertEqual(B.list_reason(self._g(0.78)), "below")
        cross = ["cup tie across divisions (A v B), priced entirely off league strength coefficients"]
        self.assertEqual(B.list_reason(self._g(0.85, cross)), "celtic")
        B.CUP_LIST.update({"cross": True, "crossBar": 0.8})
        self.assertIsNone(B.list_reason(self._g(0.85, cross)))
        self.assertEqual(B.list_reason(self._g(0.85, cross + ["X came up from the Y"])), "celtic")
        g = self._g(0.9); g["home"]["name"] = "Arsenal W"
        self.assertEqual(B.list_reason(g), "cup")

    def test_other(self):
        self.assertTrue(B.cup_other("x", "Arsenal W", "Chelsea"))
        self.assertTrue(B.cup_other("x", "Flamengo U20", "Vasco"))
        self.assertFalse(B.cup_other("x", "Wigan", "West Ham"))


if __name__ == "__main__":
    unittest.main()
