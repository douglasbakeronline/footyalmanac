"""Why the page's Card and the replay's live row differ (card_review_post.
fidelity_why, card_replay.leg_faults, 24 Nov 2026 evening)."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import card_review_post as C
import card_replay as R


def grp(picks, rule=14, status="won", **kw):
    return dict(name="Card 2x", rule=rule, status=status, legs=[{"pick": p} for p in picks], **kw)


REC = {"cardLiveRule": 14, "days": [
    {"date": "2026-11-21", "groups": [grp(["A", "B", "C"]), grp(["D", "E", "F"], status="lost"), grp(["G", "H", "I"])]},
    {"date": "2026-11-23", "groups": []},
    {"date": "2026-11-24", "groups": [grp(["J", "K", "L"], status="pending")]},
]}


def rep(groups, faults):
    return {"from": "2026-10-29", "to": "2026-11-24", "rules": [{"rule": 14, "from": "2026-11-19"}],
            "variants": {"live": {"groupList": [{"date": d, "picks": p} for d, p in groups], "legFaults": faults}}}


FIRST = rep([("2026-11-21", ["A", "B", "C"]), ("2026-11-21", ["A", "D", "Q"]), ("2026-11-23", ["M", "N", "O"])],
            {"2026-11-21": {"A": "", "B": "", "C": "", "D": "", "E": "no value", "F": "", "G": "", "H": "", "Q": ""},
             "2026-11-23": {"M": "", "N": "", "O": ""}})
CLOSE = rep([("2026-11-21", ["A", "B", "C"])],
            {"2026-11-21": {"A": "", "B": "", "C": "", "D": "", "E": "", "F": "", "G": "", "H": ""},
             "2026-11-23": {"M": "no value", "N": "", "O": ""}})


class TestFidelityWhy(unittest.TestCase):
    def test_classifies_each_page_group(self):
        with tempfile.TemporaryDirectory() as t:
            with open(os.path.join(t, "2026-11-21.json"), "w") as f:
                json.dump({"groups": [{"name": "Card 2x", "first": "2026-11-20T19:07:07Z", "legs": [{"pick": p} for p in "DEF"]}]}, f)
            out = C.fidelity_why(REC, FIRST, CLOSE, today_="2026-11-24", archive=t)
        self.assertIn("did not rebuild 2 of the page's group(s), read at first prices: 1 a pick refused at that price, "
                      "0 every pick clear", out[0])
        self.assertIn("1 a pick not in the pool", out[0])
        self.assertIn("- page: 11-21 D, E, F (first published 11-20 19:07 UTC): at first prices E no value; "
                      "at last pre-start prices every pick clear", out)
        self.assertIn("- page: 11-21 G, H, I: at first prices not in the pool: I; at last pre-start prices not in the pool: I", out)
        self.assertIn("- replay at first prices, not on the page: 11-21 A, D, Q: at last pre-start prices not in the pool: Q", out)
        self.assertIn("- replay at first prices, not on the page: 11-23 M, N, O: at last pre-start prices M no value", out)
        self.assertFalse(any("J, K, L" in x for x in out))      # a pending day is left out

    def test_all_clear_is_choice(self):
        r = rep([("2026-11-21", ["A", "B", "Q"])], {"2026-11-21": {"A": "", "B": "", "C": "", "Q": ""}})
        rec = {"cardLiveRule": 14, "days": [{"date": "2026-11-21", "groups": [grp(["A", "B", "C"])]}]}
        out = C.fidelity_why(rec, r, None, today_="2026-11-24", archive="/nonexistent")
        self.assertIn("0 a pick refused at that price, 1 every pick clear", out[0])
        self.assertIn("- page: 11-21 A, B, C: at first prices every pick clear", out)

    def test_silent_without_leg_faults_or_differences(self):
        old = rep([("2026-11-21", ["A", "B", "C"])], {}); del old["variants"]["live"]["legFaults"]
        self.assertEqual(C.fidelity_why(REC, old, None, today_="2026-11-24"), [])
        same = rep([("2026-11-21", ["A", "B", "C"]), ("2026-11-21", ["D", "E", "F"]), ("2026-11-21", ["G", "H", "I"])], {})
        self.assertEqual(C.fidelity_why(REC, same, None, today_="2026-11-24"), [])
        self.assertEqual(C.fidelity_why({}, FIRST, CLOSE, today_="2026-11-24"), [])


class TestLegFaults(unittest.TestCase):
    def test_reason_without_the_name_and_sport_off_left_out(self):
        G = R.G
        legs = [{"pick": "Clear FC", "sport": "football"}, {"pick": "Bad FC", "sport": "football"},
                {"pick": "Off", "sport": next(iter(G.CARD_SPORTS_OFF))}, {"pick": "Listless", "sport": "nba", "listOff": True}]
        old = G.card_fault
        G.card_fault = lambda l, wide=False: f"{l['pick']}: the model sees no value" if l["pick"] == "Bad FC" else None
        try:
            out = R.leg_faults({"2026-11-18": legs, "2026-11-21": legs}, ["2026-11-18", "2026-11-21"], since="2026-11-19")
        finally:
            G.card_fault = old
        self.assertEqual(out, {"2026-11-21": {"Clear FC": "", "Bad FC": "the model sees no value"}})

    def test_live_rule_from_is_the_open_row(self):
        self.assertEqual(R.live_rule_from(), next(a for n, v, a, b, w in R.RULES if b is None))


if __name__ == "__main__":
    unittest.main()
