"""tools/staking.py: the Card's bankroll at the page's stakes (9 Nov 2026,
second pass). Standard library only."""
import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import staking as S


class Bankroll(unittest.TestCase):
    def test_every_group_lost_is_a_straight_drawdown(self):
        b = S.bankroll([(0.4, 2.5, False, 2)], 10, n=50)
        self.assertEqual((b["p95DrawdownUnits"], b["units"], b["staked"], b["medianPnlUnits"]), (20.0, 40, 20.0, -20.0))

    def test_every_group_won_needs_no_cushion(self):
        b = S.bankroll([(0.4, 2.5, True, 1)], 10, n=50)
        self.assertEqual((b["p95DrawdownUnits"], b["units"]), (0.0, 1))

    def test_scales_with_the_stake_not_inverted(self):
        gs = [(0.4, 2.5, w, 1) for w in (True, False, False)]
        one = S.bankroll(gs, 60, n=2000)["units"]
        S.random.seed(11)
        two = S.bankroll([(p, o, w, 2) for p, o, w, _ in gs], 60, n=2000)["units"]
        self.assertGreater(two, one * 1.6)   # double the stake, about double the bankroll


class Sources(unittest.TestCase):
    def test_history_reads_group_list_by_season(self):
        hist = {"seasons": {"fit": {"card": {"groupList": [
                    {"date": "2025-08-10", "name": "Card 2x", "p": 0.4, "odds": 2.2, "stake": 2, "won": True},
                    {"date": "2025-08-19", "name": "Card 3x", "p": 0.25, "odds": 3.4, "stake": 1, "won": False}]}},
                "check": {"card": {"groupList": [
                    {"date": "2026-08-10", "name": "Card 2x", "p": 0.4, "odds": 2.1, "stake": 2, "won": False}]}}}}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "HERE", d):
            json.dump(hist, open(os.path.join(d, "card-legs-history.json"), "w"))
            gs, rate, per_season = S.groups_from_history()
        self.assertEqual(gs, [(0.4, 2.2, True, 2), (0.25, 3.4, False, 1), (0.4, 2.1, False, 2)])
        self.assertAlmostEqual(rate, 3 / 11)       # 10 days and 1 day of replay
        self.assertEqual(per_season, 2)            # three groups over two seasons, rounded

    def test_record_leaves_out_wide_late_and_pending(self):
        rec = {"days": [{"date": "2026-11-01", "groups": [
                    {"name": "Card 2x", "p": 0.4, "odds": 2.2, "status": "won"},
                    {"name": "Card 3x", "p": 0.25, "odds": 3.4, "status": "lost"},
                    {"name": "Card 2x", "p": 0.4, "odds": 2.2, "status": "won", "wide": True},
                    {"name": "Card 2x", "p": 0.4, "odds": 2.2, "status": "won", "late": True},
                    {"name": "Card 2x", "p": 0.4, "odds": 2.2, "status": "pending"},
                    {"name": "Model 2x", "p": 0.4, "odds": 2.2, "status": "won"}]},
                {"date": "2026-11-04", "groups": [{"name": "Card 2x", "p": 0.4, "odds": 2.0, "status": "lost"}]}]}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(S, "HERE", d):
            json.dump(rec, open(os.path.join(d, "groupings-record.json"), "w"))
            gs, rate, per_season = S.groups_from_record()
        self.assertEqual(gs, [(0.4, 2.2, True, 2), (0.25, 3.4, False, 1), (0.4, 2.0, False, 2)])
        self.assertAlmostEqual(rate, 3 / 4)
        self.assertEqual(per_season, round(0.75 * 365))

    def test_report_says_too_few(self):
        r = S.report({"replay": ([], None, None)})
        self.assertEqual(r["replay"], {"groups": 0, "note": "too few groups"})


if __name__ == "__main__":
    unittest.main()


class FlatStakeVariant(unittest.TestCase):
    """The pre-registered `flatstake` replay variant: the same groups at one unit each."""

    def test_stakes_and_restore(self):
        import card_replay as CR
        G = CR.G
        def fake(L, used, after, name, wide=False):
            ev = f"{name} v X"
            if ev in used: return None
            return {"name": name, "odds": 2.2, "p": 0.4, "legs": [{"event": ev, "won": True}]}
        before = dict(G.CARD_STAKE)
        # both kinds built, as before CARD_RULE 8 (the 2x alone from 11 Nov 2026)
        with mock.patch.object(G, "best_card", side_effect=fake), mock.patch.object(G, "CARD_BUILD", ("Card 2x", "Card 3x")):
            live = CR.build([], "2026-11-10", "live")
            flat = CR.build([], "2026-11-10", "flatstake")
        self.assertEqual({g["name"]: g["stake"] for g in live}, {"Card 2x": 2, "Card 3x": 1})
        self.assertEqual({g["name"]: g["stake"] for g in flat}, {"Card 2x": 1, "Card 3x": 1})
        self.assertEqual(G.CARD_STAKE, before)
