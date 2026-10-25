"""build.accuracy_for quotes a tested rate only for a competition family
that has its own bands (25 Oct 2026, bug 12 of
claude/full-review-2026-10-25.md). Native cups, continental ties and the
not-yet-replayed leagues used to quote the core-league rate."""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B
import engine as E
import sources as S


def rate(code, conf=0.8):
    m = E.LEAGUES[code]
    return B.accuracy_for(conf, m.get("international"), False, code)


class NoBandsNoRate(unittest.TestCase):
    def test_native_cups_and_continental_ties(self):
        for code in ("en.fa", "en.faq", "efl.trophy", "eu.cl", "eu.clq", "eu.el", "uwcl", "caf.cl",
                     "sa.lib", "br.cup", "es.cup"):
            if code in E.LEAGUES:
                self.assertIsNone(rate(code), code)

    def test_every_cup_has_no_rate(self):
        for code, m in E.LEAGUES.items():
            if m.get("cup"):
                self.assertIsNone(rate(code), code)

    def test_af_new_leagues(self):
        for code in S.AF_NEW:
            self.assertIsNone(rate(code), code)
            self.assertIn(code, B.NEW_BOARD_ONLY)


class OwnBands(unittest.TestCase):
    def test_core_leagues_and_internationals_still_quote(self):
        self.assertIsNotNone(rate("en.1"))
        self.assertIsNotNone(rate("us.1"))
        self.assertIsNotNone(rate("en.w1"))
        intl = next(c for c, m in E.LEAGUES.items() if m.get("international"))
        self.assertIsNotNone(rate(intl))
        self.assertEqual(B.accuracy_for(0.8, True, True, intl)["season"], "2026, with FIFA ranking")

    def test_wider_and_step3_quote_their_own(self):
        afx = next(iter(S.AF_EXTRA))
        self.assertEqual(rate(afx)["season"], "2025, wider leagues")
        step3 = next(iter(B.NO_LIST))
        self.assertEqual(rate(step3)["season"], "2025-26, step 3")


if __name__ == "__main__":
    unittest.main()
