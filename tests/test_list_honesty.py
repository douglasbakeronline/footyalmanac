""""Is the list honest?" (10 Nov 2026): the page's Wilson range and the
chart's guards, run in node on the functions from index.html."""
import json, os, shutil, subprocess, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def page(start, end):
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    return src[src.index(start):src.index(end)]


@unittest.skipUnless(shutil.which("node"), "node not installed")
class Honesty(unittest.TestCase):
    def js(self, body):
        code = ("const pct = x => Math.round(x*100); const fmtShort = s => s;\n"
                + page("const HON_BANDS", "function listReview(){") + body)
        return subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout.strip()

    def test_wilson_range(self):
        lo, hi = json.loads(self.js("console.log(JSON.stringify(wilson(45, 50)))"))
        self.assertTrue(0.8 < lo < 0.83 and 0.95 < hi < 0.97, (lo, hi))
        self.assertEqual(json.loads(self.js("console.log(JSON.stringify(wilson(0, 0)))")), [0, 1])

    def test_needs_twenty_settled_picks(self):
        day = lambda d, k: {"date": d, "items": [{"conf": .9, "status": "won" if i < k else "lost"} for i in range(10)]}
        self.assertEqual(self.js(f"console.log(listHonesty({json.dumps([day('2026-11-02', 9)])}) === '')"), "true")
        out = self.js(f"console.log(listHonesty({json.dumps([day('2026-11-02', 9), day('2026-11-01', 9)])}))")
        self.assertIn("18 of 20", out)
        self.assertIn("on quote", out)


if __name__ == "__main__":
    unittest.main()
