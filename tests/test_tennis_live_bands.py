"""The tennis "tested" chip quotes the live own-band record, not the archive
walk (26 Oct 2026). score_tennis.live_bands tallies graded picks per tour in
5-point bands from 55%; build_tennis.accuracy_for quotes a band only once it
holds LIVE_MIN_N picks and marks the row's rateSource, otherwise nothing."""
import os, sys, unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_tennis as ST
import build_tennis as B


def row(tour, conf, ok, void=False):
    return {"tour": tour, "confidence": conf, "ok": ok, "void": void}


class LiveBands(unittest.TestCase):
    def test_band_of(self):
        self.assertIsNone(ST.live_band_of(0.54))
        self.assertEqual(ST.live_band_of(0.55), (0.55, 0.6))
        self.assertEqual(ST.live_band_of(0.5999), (0.55, 0.6))
        self.assertEqual(ST.live_band_of(0.6), (0.6, 0.65))
        self.assertEqual(ST.live_band_of(0.7), (0.7, 0.75))
        self.assertEqual(ST.live_band_of(0.749), (0.7, 0.75))
        self.assertEqual(ST.live_band_of(0.95), (0.95, 1.0))
        self.assertEqual(ST.live_band_of(1.0), (0.95, 1.0))

    def test_tally_per_tour_graded_only(self):
        rows = ([row("ATP", 0.72, True)] * 3 + [row("ATP", 0.74, False)]
                + [row("WTA", 0.71, False)] * 2 + [row("WTA", 0.73, True)]
                + [row("ATP", 0.72, True, void=True)]        # void: never counted
                + [row("ATP", 0.52, True)])                  # under 55%: no band
        lb = ST.live_bands(rows)
        atp = next(b for b in lb["ATP"] if b["from"] == 0.7)
        self.assertEqual((atp["to"], atp["n"], atp["correct"], atp["hit"]), (0.75, 4, 3, 0.75))
        self.assertAlmostEqual(atp["quoted"], 0.725, places=4)
        wta = next(b for b in lb["WTA"] if b["from"] == 0.7)
        self.assertEqual((wta["n"], wta["correct"], wta["hit"]), (3, 1, 0.3333))
        empty = next(b for b in lb["WTA"] if b["from"] == 0.9)
        self.assertEqual((empty["n"], empty["hit"], empty["quoted"]), (0, None, None))
        self.assertEqual([b["from"] for b in lb["ATP"]],
                         [0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])


LIVE = {"ATP": [{"from": 0.7, "to": 0.75, "n": 38, "correct": 26, "hit": 0.6842, "quoted": 0.7231},
                {"from": 0.75, "to": 0.8, "n": 12, "correct": 10, "hit": 0.8333, "quoted": 0.77}],
        "WTA": [{"from": 0.7, "to": 0.75, "n": 54, "correct": 34, "hit": 0.6296, "quoted": 0.721}]}


class Stamping(unittest.TestCase):
    def test_live_band_with_enough_picks_is_quoted_as_live(self):
        with mock.patch.object(B, "LIVE_BANDS", LIVE):
            a = B.accuracy_for(0.72, "atp")
        self.assertEqual(a["rateSource"], "live")
        self.assertEqual((a["from"], a["to"], a["hit"], a["n"]), (0.7, 0.75, 0.6842, 38))
        self.assertEqual(a["cumHit"], a["hit"])       # no cumulative figure to borrow
        with mock.patch.object(B, "LIVE_BANDS", LIVE):
            w = B.accuracy_for(0.7, "WTA")
        self.assertEqual((w["rateSource"], w["hit"]), ("live", 0.6296))

    def test_thin_or_missing_band_shows_nothing_not_the_archive_walk(self):
        with mock.patch.object(B, "LIVE_BANDS", LIVE):
            self.assertIsNone(B.accuracy_for(0.77, "atp"))      # 12 picks: under LIVE_MIN_N
            self.assertIsNone(B.accuracy_for(0.88, "wta"))      # no live band at all
            self.assertIsNone(B.accuracy_for(0.72, "atp", ranked=True))   # ranked ATP has no live band
        with mock.patch.object(B, "LIVE_BANDS", {}):
            self.assertIsNone(B.accuracy_for(0.72, "atp"))      # no record on disk: nothing

    def test_archive_walk_bands_are_never_quoted(self):
        with mock.patch.object(B, "LIVE_BANDS", {}):
            for conf in (0.6, 0.72, 0.8, 0.9):
                self.assertIsNone(B.accuracy_for(conf, "ATP"))
                self.assertIsNone(B.accuracy_for(conf, "WTA"))

    def test_rate_source_on_the_row(self):
        with mock.patch.object(B, "LIVE_BANDS", LIVE):
            self.assertEqual(B.rate_source(B.accuracy_for(0.72, "atp")), "live")
            self.assertEqual(B.rate_source(B.accuracy_for(0.77, "atp")), "none")

    def test_no_rate_cannot_qualify_a_row(self):
        # the list and reserve rules read confidence and the round, never the
        # rate; a None rate leaves them where they were
        with mock.patch.object(B, "LIVE_BANDS", {}):
            self.assertFalse(B.list_eligible(0.9, "ATP", "Final", 20, 20))     # LIST_ON is off
            self.assertTrue(B.list_reserve(0.9, "ATP", "Final", 20, 20))
            self.assertFalse(B.list_reserve(0.6, "ATP", "Final", 20, 20))
        with mock.patch.object(B, "LIST_ON", {"ATP": True, "WTA": False}), \
                mock.patch.object(B, "LIVE_BANDS", {}):
            self.assertTrue(B.list_eligible(0.8, "ATP", "Final", 20, 20))
            self.assertFalse(B.list_eligible(0.8, "ATP", "Qualifying", 20, 20))
            self.assertFalse(B.list_eligible(0.8, "WTA", "Final", 20, 20))


if __name__ == "__main__":
    unittest.main()


class PlaceholderDay(unittest.TestCase):
    def test_midnight_new_york_is_a_placeholder(self):
        import build_tennis as BT
        self.assertTrue(BT.time_placeholder("2026-10-26", "04:00"))   # EDT
        self.assertTrue(BT.time_placeholder("2026-12-01", "05:00"))   # EST
        self.assertFalse(BT.time_placeholder("2026-10-26", "12:30"))
        self.assertFalse(BT.time_placeholder("2026-10-26", None))

    def test_card_refuses_a_leg_with_no_order_of_play(self):
        import groupings as G
        leg = {"pick": "A", "odds": 1.5, "fair": 0.7, "pModel": 0.7, "timeEst": True}
        self.assertIn("order of play", G.card_fault(leg))
        self.assertIn("order of play", G.mult_fault(leg))
        leg["timeEst"] = False
        self.assertIsNone(G.card_fault(leg))

    def test_unconfirmed_day_never_lists_or_reserves(self):
        import build_tennis as BT
        src = open(BT.__file__, encoding="utf-8").read()
        self.assertIn('"list": (not time_placeholder(r["date"], r["time"])', src)
        self.assertIn('"reserve": (not time_placeholder(r["date"], r["time"])', src)
