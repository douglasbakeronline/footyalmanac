"""Prime, the Daily List's Show filter (28 Nov 2026, claude/prime-filter-2026-11-28.md).

The rule lives in index.html, so this pins its wiring: the constants the page
and the note quote, the option on the list alone, and that nothing run while
the page loads (itemPrice, listShown) was made to depend on it."""
import os, re, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
    PAGE = f.read()


def body(name):
    m = re.search(r"\nfunction " + name + r"\(.*?\n}\n", PAGE, re.S)
    return m.group(0) if m else ""


class PrimeFilter(unittest.TestCase):
    def test_constants(self):
        self.assertIn('const PRIME = {conf: 80, lo: 1.10, hi: 1.40, off: ["ncaab", "cfb"]};', PAGE)

    def test_label_and_views(self):
        self.assertRegex(PAGE, r'const SHOW_LABEL = \{[^}]*prime: "Prime"')
        views = re.search(r"const FVIEWS = \{(.*?)\n\};", PAGE, re.S).group(1)
        rows = [r for r in views.split("\n") if '"prime"' in r]
        self.assertEqual(len(rows), 1, "Prime is offered on one page")
        self.assertTrue(rows[0].strip().startswith("list:"))

    def test_rule_reads_list_confidence_sport_and_price(self):
        ok = body("primeOk")
        self.assertTrue(ok, "primeOk is a hoisted function")
        for needle in ("it.reserve", "it.g.list", "PRIME.off.includes(itemSport(it))",
                       "Math.round((it.g.confidence || 0) * 100) < PRIME.conf", "px >= PRIME.lo && px <= PRIME.hi"):
            self.assertIn(needle, ok)

    def test_load_time_functions_do_not_call_it(self):
        for name in ("itemPrice", "listShown", "listPriceMin"):
            self.assertNotIn("prime", body(name).lower(), name)

    def test_list_applies_it(self):
        r = body("renderList")
        self.assertIn('const primeOn = fShow("list") === "prime";', r)
        self.assertIn("(!primeOn || primeOk(it))", r)
        self.assertIn('{k: "prime", keep: true', r)


if __name__ == "__main__":
    unittest.main()
