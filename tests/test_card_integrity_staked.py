"""card_integrity.staked (17 Nov 2026): the pending checks read every slip
Douglas stakes, not only the names that start "Card"."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import card_integrity as CI
import groupings as G


class Staked(unittest.TestCase):
    def test_staked_slips(self):
        for n in ("Card 2x", "Card 3x", G.DAILY_NAME, "List 2x", "List long"):
            self.assertTrue(CI.staked(n), n)

    def test_paper_and_retired(self):
        for n in ("Model 2x", "Model 3x", "Wider Treble", "Steady", "Multiplier", "", None):
            self.assertFalse(CI.staked(n), n)


if __name__ == "__main__":
    unittest.main()


class FullLeg(unittest.TestCase):
    """17 Nov 2026: the record's slim legs crashed settle() (KeyError 'date')."""
    def setUp(self):
        import json, tempfile
        self.dir = tempfile.mkdtemp()
        json.dump({"groups": [{"name": "Card 2x", "legs": [{"event": "A v B", "pick": "A", "date": "2026-11-14",
                   "home": "A", "away": "B", "side": "h", "id": "77", "sport": "football"}]}]},
                  open(os.path.join(self.dir, "2026-11-14.json"), "w"))
        CI._ARCH.clear()

    def test_from_archive_including_day_before(self):
        slim = {"event": "A v B", "pick": "A", "sport": "football", "status": "pending", "when": "2026-11-15T13:30:00Z"}
        f = CI.full_leg("2026-11-15", slim, self.dir)
        self.assertEqual((f["date"], f["home"], f["away"], f["side"], f["id"], f["status"]),
                         ("2026-11-14", "A", "B", "h", "77", "pending"))

    def test_fallback_from_event(self):
        slim = {"event": "C v D", "pick": "D", "sport": "football", "when": "2026-11-15T13:30:00Z"}
        f = CI.full_leg("2026-11-15", slim, self.dir)
        self.assertEqual((f["date"], f["home"], f["away"], f["side"]), ("2026-11-15", "C", "D", "a"))

    def test_settles_without_keyerror(self):
        slim = {"event": "C v D", "pick": "D", "sport": "football", "when": "2026-11-15T13:30:00Z"}
        self.assertEqual(G.settle(CI.full_leg("2026-11-15", slim, self.dir), ({}, {}, {})), ("pending", None))
