"""24 Nov 2026: the review's Coverage line reads each record group against the
replay of the rule live on its day (card_review_post.rule_coverage), not every
group over the window against the live rule's replay."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import card_review_post as P


def rule(n, v, a, b, days):
    return {"rule": n, "variant": v, "from": a, "to": b, "groupDays": days}


REP = {"from": "2026-11-01", "to": "2026-11-25", "variants": {"live": {"groups": 2}},
       "rules": [rule(5, "rule5", "2026-10-31", "2026-11-05", {"2026-11-02": 1, "2026-11-20": 3}),
                 rule(14, "live", "2026-11-19", None, {"2026-11-20": 1, "2026-11-21": 1, "2026-11-24": 1})]}
REC = {"days": [
    {"date": "2026-11-02", "groups": [{"name": "Card 2x", "rule": 5, "status": "won"}, {"name": "Card 3x", "rule": 5, "status": "lost"},
                                      {"name": "Card 2x", "rule": 5, "status": "lost", "wide": True}]},
    {"date": "2026-11-20", "groups": [{"name": "Card 2x", "rule": 14, "status": "lost"}]},
    {"date": "2026-11-21", "groups": [{"name": "Card 2x", "rule": 14, "status": "pending"}]},
    {"date": "2026-11-24", "groups": [{"name": "Card 2x", "rule": 14, "status": "won"}]}]}


class RuleCoverage(unittest.TestCase):
    def line(self, rep=REP, rec=REC):
        out = P.rule_coverage(rep, rec, today_="2026-11-24")
        self.assertEqual(len(out), 1)
        return out[0]

    def test_each_rule_on_its_own_days(self):
        s = self.line()
        # rule 5's replay counts only its own span (not its 20 Nov groups);
        # rule 14's only settled days before today (21 Nov pending, 24 Nov today)
        self.assertIn("rule 5 2 v 1", s)
        self.assertIn("rule 14 1 v 1", s)
        self.assertIn("holds 3 settled", s)
        self.assertIn("rebuilt 2", s)

    def test_estimate_era_named_only_when_present(self):
        self.assertIn("2 of the record's groups fall before 2026-11-10", self.line())
        rec = {"days": [d for d in REC["days"] if d["date"] >= "2026-11-10"]}
        self.assertNotIn("estimates", self.line(rec=rec))

    def test_old_replay_falls_back(self):
        rep = dict(REP, rules=[{k: v for k, v in r.items() if k != "groupDays"} for r in REP["rules"]])
        self.assertIsNone(P.rule_coverage(rep, REC))
        out = P.coverage_lines(rep, {"days": [{"date": "2026-11-02", "groups": [{"name": "Card 2x"}] * 3}]})
        self.assertIn("holds **3**", out[0])

    def test_coverage_lines_uses_it(self):
        out = P.coverage_lines(REP, REC)
        self.assertTrue(out[0].startswith("Coverage, by the rule each day ran"))

    def test_rule_outside_replay(self):
        rec = {"days": [{"date": "2026-11-03", "groups": [{"name": "Card 2x", "rule": 9, "status": "won"}]}]}
        self.assertIn("rule 9 1 v not replayed", self.line(rec=rec))


if __name__ == "__main__":
    unittest.main()
