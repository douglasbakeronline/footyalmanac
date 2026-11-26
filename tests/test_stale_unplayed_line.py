"""build.stale_unplayed_line: newest first, old leftovers counted apart (26 Nov 2026)."""
import os, sys, unittest
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build


class StaleLine(unittest.TestCase):
    def test_newest_first_and_old_counted(self):
        rows = [("af.118", "2024-05-03", "Arsenal II", "Dinamo Brest II"),
                ("es.1", "2026-10-10", "Rayo", "Athletic"),
                ("ukr.1", "2026-11-20", "Shakhtar Donetsk", "Livyi Bereh")]
        s = build.stale_unplayed_line(rows, date(2026, 11, 26))
        self.assertTrue(s.startswith("::warning::3 unplayed"))
        self.assertLess(s.index("Shakhtar"), s.index("Rayo"))
        self.assertNotIn("Arsenal II", s)
        self.assertIn("1 more dated over 180 days back", s)

    def test_more_than_shown(self):
        rows = [("x", f"2026-11-{d:02d}", f"H{d}", "A") for d in range(1, 16)]
        s = build.stale_unplayed_line(rows, date(2026, 11, 26))
        self.assertIn("H15 v A", s)
        self.assertNotIn("H3 v A", s)
        self.assertIn("and 3 more", s)
        self.assertNotIn("days back", s)

    def test_only_old(self):
        s = build.stale_unplayed_line([("x", "2024-01-01", "H", "A")], date(2026, 11, 26))
        self.assertIn("none recent", s)


if __name__ == "__main__":
    unittest.main()
