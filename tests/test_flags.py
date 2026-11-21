"""Every football competition has a flag the page's sprite draws, the new
flags change no club lookup, and the caution mark's league rule (21 Nov 2026)."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
import build  # noqa: E402
import engine as E  # noqa: E402

with open(os.path.join(ROOT, "index.html")) as _f:
    SPRITE = set(re.findall(r'<symbol id="f-([a-z]+)"', _f.read()))


class Flags(unittest.TestCase):
    def test_every_league_has_a_drawn_flag(self):
        missing = sorted((c, m.get("country")) for c, m in E.LEAGUES.items() if m.get("iso") not in SPRITE)
        self.assertEqual(missing, [], "a league with no flag in index.html's sprite")

    def test_every_cup_country_has_a_drawn_flag(self):
        path = os.path.join(ROOT, "current", "af-cups.json")
        if not os.path.exists(path):
            self.skipTest("no af-cups.json")
        with open(path) as f:
            doc = json.load(f)
        cups = doc.get("cups", doc) if isinstance(doc, dict) else doc
        missing = sorted({E.canon_country(e["country"]) for e in cups
                          if E.iso_of(e["country"], canon=True) not in SPRITE})
        self.assertEqual(missing, [], "a cup country with no flag")

    def test_flag_only_codes_stay_out_of_continental_cups(self):
        # before 21 Nov these leagues had no iso, so a club rated in one was
        # never eligible for a confederation's cup; a flag must not change that
        cont = [c for c, m in E.LEAGUES.items() if m.get("cup") and m["country"] in E._CONFED]
        self.assertTrue(E.FLAG_ONLY)
        if not cont:
            self.skipTest("no continental cup registered")
        for src in E.FLAG_ONLY:
            for comp in cont:
                self.assertFalse(E.eligible_league(src, comp), (src, comp))

    def test_spellings_reach_one_flag(self):
        self.assertEqual(E.iso_of("Macedonia"), "mkd")
        self.assertEqual(E.iso_of("United Arab Emirates"), "are")
        self.assertEqual(E.iso_of("Kazakhstan"), "kaz")
        self.assertEqual(E.iso_of("Nowhere"), "")


class Caution(unittest.TestCase):
    def test_rule(self):
        by = {"x.1": {"n": 66, "won": 21, "quoted": 0.4552},     # z -2.24
              "x.2": {"n": 91, "won": 34, "quoted": 0.4579},     # z -1.61
              "x.3": {"n": 98, "won": 48, "quoted": 0.4691},     # above quote
              "x.4": {"n": 40, "won": 5, "quoted": 0.5}}         # too few
        got = build.unpredictable_leagues(by)
        self.assertEqual(sorted(got), ["x.1", "x.2"])
        self.assertEqual(got["x.1"]["z"], -2.24)
        self.assertEqual(build.unpredictable_leagues(None), {})

    def test_summary_carries_it(self):
        rec = {"byLeague": {"x.1": {"n": 66, "won": 21, "quoted": 0.4552}}}
        self.assertIn("x.1", build.record_summary(rec)["caution"])


if __name__ == "__main__":
    unittest.main()
