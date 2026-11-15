"""tools/price_timing.py book_vs (13 Nov 2026, issue #156): each UK book
against CARD_BOOK on the legs both priced, paired and day-resampled, the
best UK price against it, the settled singles at each book, and the review
lines that name a book paying more as Douglas's call."""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import price_timing as PT
import card_review_post as C


def leg(i, hill, b365, day, won=True, last=None, sport="football"):
    bo = {"William Hill": hill}
    if b365: bo["Bet365"] = b365
    l = {"pick": f"P{i}", "sport": sport, "date": day, "odds": hill, "bookOdds": bo, "won": won}
    if last: l["lastBooks"] = last
    return l


class BookVs(unittest.TestCase):
    def test_paired_only_on_legs_both_priced(self):
        L = [leg(i, 1.40, 1.42, f"2026-11-{1 + i % 10:02d}") for i in range(60)] + [leg(100 + i, 1.40, None, "2026-11-01") for i in range(20)]
        r = PT.book_vs(L, L, base="William Hill")
        self.assertEqual(r["base"], "William Hill")
        b = r["books"]["Bet365"]
        self.assertEqual(b["first"]["n"], 60); self.assertEqual(b["first"]["days"], 10)
        self.assertAlmostEqual(b["first"]["meanPct"], 1.43, places=2)
        self.assertEqual(b["first"]["read"], "Bet365 pays more"); self.assertEqual(b["first"]["p"], 0.0)
        self.assertAlmostEqual(b["first"]["group3Pct"], round(((1.42 / 1.40) ** 3 - 1) * 100, 2), places=2)
        self.assertEqual(b["settled"]["n"], 60); self.assertEqual(b["settled"]["read"], "Bet365 pays more")
        self.assertEqual(b["last"], {"n": 0})                          # no last book prices on file
        self.assertEqual(b["sports"], {"football": 60})
        self.assertEqual(r["books"]["best UK price"]["first"]["n"], 60)   # a leg priced by Hill alone has nothing to shop

    def test_base_ahead_and_too_few(self):
        L = [leg(i, 1.50, 1.45, f"2026-11-{1 + i % 10:02d}", won=i % 3 > 0) for i in range(55)]
        b = PT.book_vs(L, L, base="William Hill")["books"]["Bet365"]
        self.assertEqual(b["first"]["read"], "William Hill pays more")
        few = PT.book_vs(L[:20], None, base="William Hill")["books"]["Bet365"]
        self.assertEqual(few["first"]["read"], "too few legs to read"); self.assertNotIn("settled", few)
        self.assertEqual(PT.book_vs(L[:5], None, base="William Hill")["books"], {})   # under MIN_BOOK paired legs: not reported

    def test_review_lines(self):
        L = [leg(i, 1.40, 1.42, f"2026-11-{1 + i % 10:02d}") for i in range(60)]
        lines = C.book_vs_lines(PT.book_vs(L, L, base="William Hill"))
        self.assertTrue(lines[0].startswith("- Bet365 v William Hill, the same picks: +1.43% a pick"))
        self.assertTrue(lines[1].startswith("- best UK price v William Hill"))           # the best price last, then the bold line
        self.assertIn("**Bet365 pays more than William Hill on 60 paired picks", lines[-1])
        self.assertIn("his call", lines[-1])
        L2 = [leg(i, 1.40, 1.40, f"2026-11-{1 + i % 10:02d}") for i in range(60)]
        tie = PT.book_vs(L2, L2, base="William Hill")["books"]["Bet365"]
        self.assertEqual(tie["first"]["read"], "no clear read"); self.assertEqual(tie["settled"]["read"], "no clear read")   # equal prices favour neither
        self.assertFalse(any("**" in x for x in C.book_vs_lines(PT.book_vs(L2, L2, base="William Hill"))))
        self.assertEqual(C.book_vs_lines(None), []); self.assertEqual(C.book_vs_lines({"base": "William Hill", "books": {}}), [])


if __name__ == "__main__":
    unittest.main()
