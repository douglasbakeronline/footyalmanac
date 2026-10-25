import unittest
import re
import score


class Ladder(unittest.TestCase):
    def test_record_ladder_matches_tiers(self):
        lad = score.ladder()
        self.assertEqual([(t["min"], t["k"], t["name"]) for t in lad], score.TIERS)
        self.assertTrue(all(t["was"] for t in lad))

    def test_page_fallback_matches_score(self):
        html = open("index.html", encoding="utf-8").read()
        m = re.search(r"const TIERS = \(window.__RECORD__ && window.__RECORD__.ladder\) \|\| \[(.*?)\];", html, re.S)
        self.assertIsNotNone(m)
        rows = re.findall(r'min:([\d.]+), k:(\d), name:"([^"]+)",\s*was:"([^"]+)"', m.group(1))
        self.assertEqual([(float(a), int(b), c) for a, b, c, _ in rows], score.TIERS)
        self.assertEqual([w for *_, w in rows], [t["was"] for t in score.ladder()])


if __name__ == "__main__":
    unittest.main()
