"""The Card review read at last pre-start prices and the replay's fidelity to
the published Card (tools/card_review_post, 24 Nov 2026)."""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import card_review_post as C


def row(out, name):
    return next(l for l in out if l.startswith(f"| {name}"))


def grp(picks, rule=14, status="won", name="Card 2x", **kw):
    return dict(name=name, rule=rule, status=status, legs=[{"pick": p} for p in picks], **kw)


REC = {"cardLiveRule": 14, "days": [
    {"date": "2026-11-18", "groups": [grp(["X", "Y", "Z"], rule=13)]},          # before rule 14
    {"date": "2026-11-19", "groups": []},
    {"date": "2026-11-21", "groups": [grp(["A", "B", "C"]), grp(["D", "E", "F"], status="lost"),
                                      grp(["W1", "W2", "W3"], wide=True)]},   # the filler is not the rule
    {"date": "2026-11-22", "groups": [grp(["G", "H", "I"], status="lost")]},
    {"date": "2026-11-23", "groups": []},
    {"date": "2026-11-24", "groups": [grp(["J", "K", "L"], status="pending")]},  # not settled: left out
]}


def rep(groups, rules=True):
    r = {"from": "2026-10-29", "to": "2026-11-24",
         "variants": {"live": {"groupList": groups}, "rule13": {"vsLivePerDay": -0.31, "pWorse": 0.694, "legs": 117},
                      "rule12": {"vsLivePerDay": 0.19, "pWorse": 0.411, "legs": 63}}}
    if rules: r["rules"] = [{"rule": 13, "from": "2026-11-17"}, {"rule": 14, "from": "2026-11-19", "to": None}]
    return r


class TestFidelity(unittest.TestCase):
    def test_counts_matches_and_one_sided_days(self):
        first = rep([{"date": "2026-11-21", "picks": ["A", "B", "C"]}, {"date": "2026-11-21", "picks": ["A", "D", "Q"]},
                     {"date": "2026-11-22", "picks": ["G", "H", "I"]}, {"date": "2026-11-23", "picks": ["M", "N", "O"]},
                     {"date": "2026-11-18", "picks": ["X", "Y", "Z"]}])
        close = rep([{"date": "2026-11-21", "picks": ["A", "B", "C"]}, {"date": "2026-11-22", "picks": ["G", "H", "I"]}])
        out = C.fidelity_lines(REC, first, close, today_="2026-11-24")
        self.assertEqual(len(out), 1)
        t = out[0]
        self.assertIn("rule 14, 2026-11-19 to 2026-11-23, 4 settled day(s)", t)
        self.assertIn("the page published 3 group(s)", t)
        self.assertIn("at first prices 4 group(s), 2 with the page's picks, a group on one side only on 11-23", t)
        self.assertIn("at last pre-start prices 2 group(s), 2 with the page's picks.", t)

    def test_needs_picks_and_the_rule_start(self):
        old = rep([{"date": "2026-11-21", "name": "Card 2x"}])            # a replay written before 24 Nov
        self.assertEqual(C.fidelity_lines(REC, old, {}, today_="2026-11-24"), [])
        self.assertEqual(C.fidelity_lines(REC, rep([], rules=False), {}, today_="2026-11-24"), [])
        self.assertEqual(C.fidelity_lines({}, rep([]), {}, today_="2026-11-24"), [])

    def test_decision_row_reads_last_prices_when_given(self):
        rec = {"cardLiveRule": 14}
        r = row(C.decisions_section(rec, rep([]), {}, today_="2026-11-24"), "Rule 14")
        self.assertNotIn("last pre-start price", r)
        close = {"variants": {"rule13": {"vsLivePerDay": -0.31, "pWorse": 0.694, "legs": 117},
                              "rule12": {"vsLivePerDay": 0.19, "pWorse": 0.411, "legs": 63}}}
        r = row(C.decisions_section(rec, rep([]), {}, today_="2026-11-24", rep_close=close), "Rule 14")
        self.assertIn("at the last pre-start price: `rule13` v live -0.31 a day, p(worse) 0.694, 117 legs; "
                      "`rule12` v live +0.19 a day, p(worse) 0.411, 63 legs", r)


if __name__ == "__main__":
    unittest.main()
