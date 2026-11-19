"""racing.py (19 Nov 2026): the race reader, the model, the tip rule and grading."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import racing  # noqa: E402


def card(n=8, name="Sample Handicap Chase", odds=None, form=None, nr=()):
    odds = odds or [4.5, 3.25, 5.5, 7.0, 9.0, 13.0, 15.0, 17.0][:n]
    form = form or ["1-2311", "3P-142", "21-1U2", "52-43F", "9-2214", "6-7543", "4-3356", "1-3124"][:n]
    runners = []
    for i in range(n):
        runners.append({"horse_id": f"h{i}", "horse": f"Horse {i} (IRE)", "number": str(i + 1),
                        "ofr": str(128 - 3 * i), "form": form[i], "last_run": str(14 + 7 * i),
                        "jockey": f"J{i}", "trainer": f"T{i}",
                        "trainer_14_days": {"percent": str(25 - 2 * i)},
                        "odds": [{"bookmaker": "Book A", "decimal": str(odds[i])},
                                 {"bookmaker": "Book B", "decimal": str(round(odds[i] * 0.95, 2))}],
                        **({"status": "NR"} if i in nr else {})})
    return {"race_id": "rac_1", "course": "Wetherby", "region": "GB", "off_dt": "2026-11-19T14:00:00+00:00",
            "race_name": name, "type": "Chase", "race_class": "Class 3", "distance": "2m3½f",
            "going": "Good To Soft", "runners": runners}


class RaceReading(unittest.TestCase):
    def test_fields_and_names(self):
        r = racing.race_of(card())
        self.assertEqual(r["off"], "14:00")
        self.assertEqual(r["date"], "2026-11-19")
        self.assertEqual(r["going"], "Good To Soft")
        self.assertTrue(r["handicap"])
        self.assertEqual(r["runners"][0]["horse"], "Horse 0")      # country suffix dropped
        self.assertEqual(r["runners"][0]["or"], 128.0)

    def test_non_runner_changes_place_terms(self):
        self.assertEqual(racing.race_of(card(8))["places"], 3)
        r = racing.race_of(card(8, nr=(7,)))
        self.assertEqual(r["field"], 7)
        self.assertEqual((r["places"], r["frac"]), (2, 0.25))

    def test_each_way_terms(self):
        self.assertEqual(racing.ew_terms(4, False), (1, 1.0))
        self.assertEqual(racing.ew_terms(6, True), (2, 0.25))
        self.assertEqual(racing.ew_terms(10, False), (3, 0.2))
        self.assertEqual(racing.ew_terms(13, True), (3, 0.25))
        self.assertEqual(racing.ew_terms(18, True), (4, 0.25))

    def test_form(self):
        self.assertEqual(racing.form_runs("3P-142"), [3, "P", 1, 4, 2])
        self.assertGreater(racing.form_score("111"), racing.form_score("999"))
        self.assertIsNone(racing.form_score(""))


class Model(unittest.TestCase):
    def test_chances_sum_to_one(self):
        rows = racing.chances(racing.race_of(card()))
        for key in ("fund", "mkt", "p"):
            self.assertAlmostEqual(sum(x[key] for x in rows), 1.0, places=6)

    def test_no_price_falls_back_to_the_model(self):
        c = card()
        for r in c["runners"]:
            r["odds"] = []
        rows = racing.chances(racing.race_of(c))
        self.assertTrue(all(x["mkt"] is None for x in rows))
        self.assertAlmostEqual(sum(x["p"] for x in rows), 1.0, places=6)

    def test_place_chance(self):
        ps = [0.4, 0.3, 0.2, 0.1]
        self.assertAlmostEqual(racing.place_chance(ps, 0, 1), 0.4)
        self.assertEqual(racing.place_chance(ps, 3, 4), 1.0)
        tot2 = sum(racing.place_chance(ps, i, 2) for i in range(4))
        self.assertAlmostEqual(tot2, 2.0, places=6)          # two places are filled
        tot3 = sum(racing.place_chance([.3, .25, .2, .15, .1], i, 3) for i in range(5))
        self.assertAlmostEqual(tot3, 3.0, places=6)


class Tips(unittest.TestCase):
    def test_tip_needs_value(self):
        # the favourite priced short: no edge, no tip
        r = racing.read_race(racing.race_of(card(odds=[1.5, 6, 8, 10, 12, 15, 20, 25])))
        self.assertIsNone(r["tip"])
        self.assertIn("priced about right", r["skip"])

    def test_tip_when_price_beats_chance(self):
        # a strong top-rated horse at a generous price
        r = racing.read_race(racing.race_of(card(odds=[3.4, 6, 8, 10, 12, 15, 20, 25])))
        t = r["tip"]
        self.assertIsNotNone(t)
        self.assertEqual(t["horse"], r["runners"][0]["horse"])
        self.assertGreaterEqual(t["edge"], racing.TIP_MIN_EDGE)
        self.assertLessEqual(t["take"], t["price"])
        self.assertIsNotNone(t["danger"])

    def test_big_field_no_tip(self):
        c = card()
        c["runners"] = c["runners"] * 3
        for i, r in enumerate(c["runners"]):
            r["horse_id"] = f"x{i}"
        r = racing.read_race(racing.race_of(c))
        self.assertIsNone(r["tip"])
        self.assertIn("too big a field", r["skip"])

    def test_day_cap_keeps_most_likely(self):
        races = []
        for i in range(racing.MAX_TIPS + 3):
            c = card(odds=[3.0 + 0.1 * i, 6, 8, 10, 12, 15, 20, 25])
            c["race_id"] = f"r{i}"
            races.append(racing.read_race(racing.race_of(c)))
        kept = racing.day_tips(races)
        self.assertEqual(len(kept), racing.MAX_TIPS)
        ps = [r["tip"]["p"] for r in kept]
        self.assertEqual(ps, sorted(ps, reverse=True))
        self.assertEqual(sum(1 for r in races if r["tip"]), racing.MAX_TIPS)


class Grading(unittest.TestCase):
    def test_settle_win_and_each_way(self):
        win = {"bet": "win", "price": 4.5}
        ew = {"bet": "each-way", "price": 5.0}
        self.assertEqual(racing.settle(win, 1, 3, 0.2), 3.5)
        self.assertEqual(racing.settle(win, 2, 3, 0.2), -1.0)
        self.assertAlmostEqual(racing.settle(ew, 1, 3, 0.2), 0.5 * 4 + 0.5 * 4 * 0.2)
        self.assertAlmostEqual(racing.settle(ew, 3, 3, 0.2), -0.5 + 0.5 * 4 * 0.2)
        self.assertEqual(racing.settle(ew, 4, 3, 0.2), -1.0)
        self.assertIsNone(racing.settle(win, None, 3, 0.2, nr=True))

    def test_grade_and_summary(self):
        race = racing.read_race(racing.race_of(card(odds=[3.4, 6, 8, 10, 12, 15, 20, 25])))
        finish = {f"h{i}": i + 1 for i in range(8)}
        sp = {"h0": 3.0}
        runners, tips = racing.grade({"2026-11-19": [race]}, {"rac_1": (finish, sp)})
        self.assertEqual(len(runners), 8)
        self.assertEqual(len(tips), 1)
        self.assertEqual(tips[0]["state"], "won")
        self.assertTrue(tips[0]["beatClose"])
        s = racing.summarise(runners, tips)
        self.assertEqual(s["won"], 1)
        self.assertEqual(sum(b["n"] for b in s["bands"]), 8)
        self.assertEqual(s["byDay"]["2026-11-19"][0]["state"], "won")

    def test_withdrawn_tip_is_void(self):
        race = racing.read_race(racing.race_of(card(odds=[3.4, 6, 8, 10, 12, 15, 20, 25])))
        finish = {f"h{i}": i for i in range(1, 8)}       # h0 never ran
        _, tips = racing.grade({"2026-11-19": [race]}, {"rac_1": (finish, {})})
        self.assertEqual(tips[0]["state"], "void")


class EndToEnd(unittest.TestCase):
    def test_sample_build_writes_page_and_archive(self):
        here = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            try:
                c = card(odds=[3.4, 6, 8, 10, 12, 15, 20, 25])
                with open("cards.json", "w") as fh:
                    json.dump({"racecards": [c]}, fh)
                with open("results.json", "w") as fh:
                    json.dump({"results": [{"race_id": "rac_1", "runners": [
                        {"horse_id": f"h{i}", "position": str(i + 1), "sp_dec": "3.0"} for i in range(8)]}]}, fh)
                self.assertEqual(racing.main(["--sample", "cards.json", "--results-sample", "results.json"]), 0)
                text = open("racing.js").read()
                self.assertTrue(text.startswith("window.RACING = "))
                page = json.loads(text[len("window.RACING = "):-2])
                self.assertEqual(page["status"], "live")
                self.assertTrue(page["trial"])
                self.assertTrue(os.path.exists("predictions-racing/2026-11-19.json"))
                rec = json.load(open("racing-record.json"))
                self.assertEqual(rec["summary"]["runners"], 8)
            finally:
                os.chdir(here)

    def test_no_secrets_writes_waiting_page(self):
        here = os.getcwd()
        env = {k: os.environ.pop(k) for k in ("RACING_API_USERNAME", "RACING_API_PASSWORD") if k in os.environ}
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            try:
                self.assertEqual(racing.main([]), 0)
                page = json.loads(open("racing.js").read()[len("window.RACING = "):-2])
                self.assertEqual(page["status"], "waiting")
            finally:
                os.chdir(here)
                os.environ.update(env)


class FeedFallback(unittest.TestCase):
    def test_refused_endpoint_falls_back(self):
        import urllib.error
        calls = []

        def fake(path, params, key, auth):
            calls.append(path)
            if path != "racecards/free":
                raise urllib.error.HTTPError(path, 401, "Unauthorized", {}, None)
            return {"racecards": []}
        old = racing.fetch_region
        racing.fetch_region = fake
        racing._card_path[0] = None
        try:
            self.assertEqual(racing.fetch_cards([("day", "today")], "x"), {"racecards": []})
            self.assertEqual(calls, list(racing.CARD_PATHS))
            # the second day asks only the endpoint that answered
            racing.fetch_cards([("day", "tomorrow")], "x")
            self.assertEqual(calls[-1], "racecards/free")
            self.assertEqual(len(calls), len(racing.CARD_PATHS) + 1)
        finally:
            racing.fetch_region = old
            racing._card_path[0] = None

    def test_other_errors_raise(self):
        import urllib.error

        def fake(path, params, key, auth):
            raise urllib.error.HTTPError(path, 500, "Server", {}, None)
        old = racing.fetch_region
        racing.fetch_region = fake
        racing._card_path[0] = None
        try:
            with self.assertRaises(urllib.error.HTTPError):
                racing.fetch_cards([], "x")
        finally:
            racing.fetch_region = old


if __name__ == "__main__":
    unittest.main()
