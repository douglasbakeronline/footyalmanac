"""11 Nov 2026 evening: model_fault (the Card's rule 7/8) reads CARD_CORE_ONLY,
as card_fault does, so the replay (`m7wide`) and the funnel (the "league"
relief) can admit the wider API-Football leagues. Live stays core only."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import groupings as G
import card_replay as R
import card_funnel as CF


def leg(code):
    l = {"event": "a v b", "pick": "a", "sport": "football", "comp": "c", "odds": 1.40, "p": 0.76, "pModel": 0.76,
         "when": "2026-11-12T15:00:00Z", "est": False, "margin": 1.0, "date": "2026-11-12", "code": code, "opp": 9.0}
    return G.honest(l)


class M7Wide(unittest.TestCase):
    def setUp(self): self.saved = G.CARD_CORE_ONLY

    def tearDown(self): G.CARD_CORE_ONLY = self.saved

    def test_live_admits_wider_leagues(self):
        # 11 Nov 2026 (CARD_RULE 11): wider leagues on, at Douglas's call
        self.assertFalse(G.CARD_CORE_ONLY)
        self.assertIsNone(G.model_fault(leg("af.311")))
        self.assertIsNone(G.model_fault(leg("en.1")))
        G.CARD_CORE_ONLY = True
        self.assertIn("outside the core leagues", G.model_fault(leg("af.311")))

    def test_relaxed_admits_wider_league(self):
        G.CARD_CORE_ONLY = False
        self.assertIsNone(G.model_fault(leg("af.311")))

    def test_relaxed_still_keeps_cups_out(self):
        G.CARD_CORE_ONLY = False
        self.assertIn("outside the core leagues", G.model_fault(leg("afc.101")))

    def test_registered(self):
        self.assertEqual(R.VARIANTS["m7wide"], {"CARD_CORE_ONLY": False})
        self.assertNotIn("m7wide", R.RULE6_FAMILY)
        self.assertEqual(CF.MODEL_RELIEF["league"], {"CARD_CORE_ONLY": False})


if __name__ == "__main__":
    unittest.main()
