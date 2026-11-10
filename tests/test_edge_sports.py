"""tools/edge_sports.py (10 Nov 2026): the Edge flag tested on every sport.
Favourites only, the candidate and short-favourite filters, the gate, and the
review section's table on a stubbed pool."""
import os, sys, unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import edge_sports as ES
import card_review_post as P


def leg(sport="nba", odds=1.25, opp=4.0, fair=0.78, model=0.78, won=True, day="2026-11-12"):
    return {"sport": sport, "odds": odds, "best": odds + 0.02, "opp": opp, "fair": fair, "pModel": model, "won": won, "day": day}


class EdgeSports(unittest.TestCase):
    def test_favourites_only(self):
        by = {"2026-11-12": [leg(), leg(odds=3.0, opp=1.4)]}
        self.assertEqual(len(ES.favourites(by)), 1)

    def test_candidate_and_short(self):
        self.assertTrue(ES.candidate(leg()))
        self.assertFalse(ES.candidate(leg(fair=0.55)))                 # bookmakers under 60%
        self.assertFalse(ES.candidate(leg(model=0.90)))                # model 12 points above
        self.assertFalse(ES.candidate(leg(odds=1.10)))                 # outside CARD_ODDS
        self.assertTrue(ES.short(leg(odds=1.15)))
        self.assertFalse(ES.short(leg(odds=1.30)))                     # 1.30 is the next band

    def test_gate(self):
        win = [leg(day=f"2026-11-{d:02d}") for d in range(11, 21) for _ in range(11)]
        self.assertTrue(ES.passes(ES.summary(win)))
        self.assertFalse(ES.passes(ES.summary(win[:90])))              # under 100 legs
        lose = [leg(won=i % 2 == 0, day=f"2026-11-{11 + i % 10:02d}") for i in range(120)]
        self.assertFalse(ES.passes(ES.summary(lose)))

    def test_report_has_every_sport_and_all(self):
        rep = ES.report([leg(), leg(sport="tennis"), leg(sport="football", opp=11.0)])
        self.assertEqual(set(rep), {"nba", "tennis", "football", "_all"})
        self.assertIn("liveFlag", rep["football"])

    def test_review_section(self):
        import card_replay as CR
        with mock.patch.object(CR, "pool_legs", lambda since=None, **k: ({"2026-11-12": [leg()]}, {})):
            out = P.edge_section()
        self.assertTrue(out[0].startswith("## Edge flag, every sport"))
        self.assertTrue(any(x.startswith("| nba | 1 |") for x in out), out)
        self.assertTrue(any(x.startswith("| all sports |") for x in out))


if __name__ == "__main__":
    unittest.main()
