"""Tests for build_tennis.py's pure core: Elo pricing, shrink, tiers, the
ESPN event parser, walkover / retirement detection and the archive key.
No network."""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import build_tennis as BT


def _comp(cid, a, b, state="post", winner=0, date="2026-10-20T09:30Z", note=None, rnd="Round of 16"):
    sides = [{"id": "1", "athlete": {"displayName": a}, "winner": winner == 0},
             {"id": "2", "athlete": {"displayName": b}, "winner": winner == 1}]
    return {"id": cid, "date": date, "competitors": sides,
            "status": {"type": {"state": state, "name": "STATUS_FINAL"}},
            "round": {"displayName": rnd},
            "notes": [{"text": note}] if note else []}


class PriceMatch(unittest.TestCase):
    def test_equal_ratings_are_a_coin_flip(self):
        r = {"overall": 1600}
        self.assertAlmostEqual(BT.price_match(r, dict(r), "Hard", 0.5), 0.5)

    def test_symmetric(self):
        a, b = {"overall": 1700}, {"overall": 1550}
        self.assertAlmostEqual(BT.price_match(a, b, "Clay", 0.3) + BT.price_match(b, a, "Clay", 0.3), 1.0)

    def test_400_points_is_ten_to_one(self):
        self.assertAlmostEqual(BT.price_match({"overall": 1900}, {"overall": 1500}, "Hard", 0.0), 10 / 11)

    def test_missing_surface_falls_back_to_overall(self):
        a = {"overall": 1700}
        b = {"overall": 1500, "surface_Grass": 1500}
        self.assertAlmostEqual(BT.price_match(a, b, "Grass", 0.7), BT.price_match(a, b, "Grass", 0.0))

    def test_surface_weight_blends(self):
        a = {"overall": 1500, "surface_Clay": 1700}
        b = {"overall": 1500, "surface_Clay": 1500}
        self.assertAlmostEqual(BT.price_match(a, b, "Clay", 0.0), 0.5)
        self.assertGreater(BT.price_match(a, b, "Clay", 0.5), 0.5)


class SmallHelpers(unittest.TestCase):
    def test_dampen(self):
        self.assertAlmostEqual(BT.dampen(0.9, 0.9), 0.86)
        self.assertAlmostEqual(BT.dampen(0.5, 0.3), 0.5)
        self.assertAlmostEqual(BT.dampen(0.2, 1.0), 0.2)
        self.assertAlmostEqual(BT.dampen(0.9, 0.0), 0.5)

    def test_tier_boundaries(self):
        for p, name in [(0.70, "Strong"), (0.699, "Firm"), (0.62, "Firm"), (0.619, "Lean"),
                        (0.55, "Lean"), (0.549, "No read"), (0.5, "No read")]:
            self.assertEqual(BT.tier_of(p), name, p)

    def test_walkover(self):
        self.assertTrue(BT.is_walkover({"note": "A bt B w/o"}))
        self.assertTrue(BT.is_walkover({"note": "A bt B (Walkover)"}))
        self.assertFalse(BT.is_walkover({"note": "A bt B 6-4 6-3"}))
        self.assertFalse(BT.is_walkover({"note": None}))
        self.assertFalse(BT.is_walkover({}))

    def test_retirement_word_only(self):
        self.assertTrue(BT.is_retirement("A bt B 5-7 5-3 ret"))
        self.assertTrue(BT.is_retirement("A bt B 5-7 5-3 retired"))
        self.assertFalse(BT.is_retirement("Berrettini bt X 6-4 6-4"))
        self.assertFalse(BT.is_retirement(""))

    def test_pred_key(self):
        self.assertEqual(BT.pred_key({"id": "55", "tour": "atp"}), "55")
        m = {"id": None, "tour": "atp", "date": "2026-10-20", "playerA": "A", "playerB": "B"}
        self.assertEqual(BT.pred_key(m), "atp|2026-10-20|A|B")


class EventParser(unittest.TestCase):
    def ev(self, *groups):
        return {"name": "Basel Open", "groupings": list(groups)}

    def grp(self, slug, *comps):
        return {"grouping": {"slug": slug}, "competitions": list(comps)}

    def test_completed_match(self):
        rows = BT._matches_from_event(
            self.ev(self.grp("mens-singles", _comp("9", "A One", "B Two", winner=1, note="B Two bt A One 6-4 6-3"))), "atp")
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["p0"], r["p1"], r["winner"], r["completed"]), ("A One", "B Two", "B Two", True))
        self.assertEqual((r["date"], r["time"], r["tournament"], r["round"]), ("2026-10-20", "09:30", "Basel Open", "Round of 16"))
        self.assertEqual(r["tour"], "atp")

    def test_scheduled_match_has_no_winner(self):
        r = BT._matches_from_event(self.ev(self.grp("womens-singles", _comp("1", "A", "B", state="pre", winner=0))), "wta")[0]
        self.assertFalse(r["completed"])
        self.assertIsNone(r["winner"])

    def test_completed_without_winner_flag(self):
        c = _comp("1", "A", "B")
        for s in c["competitors"]:
            s["winner"] = False
        self.assertIsNone(BT._matches_from_event(self.ev(self.grp("mens-singles", c)), "atp")[0]["winner"])

    def test_doubles_and_malformed_are_skipped(self):
        bad_one = _comp("2", "A", "B"); bad_one["competitors"] = bad_one["competitors"][:1]
        no_name = _comp("3", "A", "B"); no_name["competitors"][0]["athlete"] = {}
        rows = BT._matches_from_event(self.ev(
            self.grp("mens-doubles", _comp("1", "A", "B")),
            self.grp("mens-singles", bad_one, no_name)), "atp")
        self.assertEqual(rows, [])

    def test_empty_event(self):
        self.assertEqual(BT._matches_from_event({}, "atp"), [])

    def test_short_date_has_no_time(self):
        r = BT._matches_from_event(self.ev(self.grp("mens-singles", _comp("1", "A", "B", date="2026-10-20"))), "atp")[0]
        self.assertEqual((r["date"], r["time"]), ("2026-10-20", None))


if __name__ == "__main__":
    unittest.main()
