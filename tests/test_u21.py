"""Premier League 2 ratings for U21 sides in the EFL Trophy (6 Oct 2026)."""
import json, os, random, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E
import sources as S
import build as B

DOC = {"leagues": [{"code": "afu.99702", "id": 99702, "name": "Premier League 2 Division One",
                    "current": 2026, "years": [2023, 2024, 2025, 2026]}],
       "trophy": {"id": 99046, "years": [2024, 2025, 2026]}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fitfile = os.path.join(self.tmp.name, "u21-fit.json")
        self.p = mock.patch.object(E, "U21_FIT_FILE", self.fitfile)
        self.p.start()
        S.register_u21(DOC)

    def tearDown(self):
        self.p.stop()
        self.tmp.cleanup()
        E.LEAGUES.pop("afu.99702", None)
        S.AF.pop("afu.99702", None)
        S.AF_U21.discard("afu.99702")


class Register(Base):
    def test_entry(self):
        m = E.LEAGUES["afu.99702"]
        self.assertEqual((m["season"], m["prev"], m["country"]), ("2026-27", ["2025-26", "2024-25"], "England"))
        self.assertTrue(m["u21"])
        self.assertFalse(m["u21Fitted"])
        self.assertEqual(S.AF["afu.99702"], 99702)

    def test_unfitted_u21_not_priced_against_seniors(self):
        self.assertFalse(B.u21_cup_ok("afu.99702", "efl.trophy"))
        self.assertTrue(B.u21_cup_ok("afu.99702", "afu.99702"))   # its own league games
        self.assertTrue(B.u21_cup_ok("en.3", "efl.trophy"))


def synthetic(n_clubs=16, s_true=0.40, seed=3):
    """Ties drawn from the model itself at a known PL2 strength."""
    rnd = random.Random(seed)
    young = {f"Club{i} U21": {"att": rnd.uniform(0.8, 1.2), "def": rnd.uniform(0.8, 1.2)} for i in range(n_clubs)}
    old = {f"Town{i}": {"att": rnd.uniform(0.8, 1.2), "def": rnd.uniform(0.8, 1.2)} for i in range(n_clubs)}
    prior = {"afu.99702": young, "en.3": old}
    mu = {"afu.99702": 1.5, "en.3": 1.35}
    rows = []
    for k in range(400):
        y, o = rnd.choice(list(young)), rnd.choice(list(old))
        home_young = rnd.random() < 0.5
        if home_young:
            p = E.cup_match(young[y], s_true, old[o], E.LEAGUES["en.3"]["strength"], 1.425, tier=3)
        else:
            p = E.cup_match(old[o], E.LEAGUES["en.3"]["strength"], young[y], s_true, 1.425, tier=3)
        u = rnd.random()
        res = "h" if u < p["home"] else ("d" if u < p["home"] + p["draw"] else "a")
        hg, ag = {"h": (1, 0), "d": (1, 1), "a": (0, 1)}[res]
        h, a = (y, o) if home_young else (o, y)
        rows.append({"date": "2025-09-02", "home": h, "away": a, "hg": hg, "ag": ag})
    return rows, prior, mu


class Fit(Base):
    def dom(self, prior):
        return lambda team, comp=None: (("en.3", team) if team in prior["en.3"] else (None, team))

    def test_recovers_strength_and_passes(self):
        rows, prior, mu = synthetic()
        with mock.patch.object(S, "af_season_by_id", return_value=[]), \
             mock.patch.object(S, "af_rows_from", return_value=rows):
            fit = B.fit_u21(DOC, prior, mu, self.dom(prior), path=self.fitfile)
        self.assertEqual(fit["ties"], 400)
        self.assertTrue(fit["pass"], fit)
        self.assertLess(abs(fit["strength"] - 0.40), 0.08)
        self.assertTrue(E.LEAGUES["afu.99702"]["u21Fitted"])
        self.assertEqual(E.LEAGUES["afu.99702"]["strength"], fit["strength"])
        self.assertTrue(B.u21_cup_ok("afu.99702", "efl.trophy"))
        self.assertEqual(json.load(open(self.fitfile))["strength"], fit["strength"])

    def test_too_few_ties_stays_unpriced(self):
        rows, prior, mu = synthetic()
        with mock.patch.object(S, "af_season_by_id", return_value=[]), \
             mock.patch.object(S, "af_rows_from", return_value=rows[:10]):
            fit = B.fit_u21(DOC, prior, mu, self.dom(prior), path=self.fitfile)
        self.assertFalse(fit["pass"])
        self.assertFalse(E.LEAGUES["afu.99702"]["u21Fitted"])

    def test_senior_v_senior_and_youth_v_youth_ignored(self):
        rows, prior, mu = synthetic()
        rows = [{"date": "x", "home": "Town1", "away": "Town2", "hg": 1, "ag": 0},
                {"date": "x", "home": "Club1 U21", "away": "Club2 U21", "hg": 1, "ag": 0}]
        self.assertEqual(B.u21_ties(rows, ["afu.99702"], prior, mu, self.dom(prior)), [])


class Refresh(unittest.TestCase):
    def test_finds_pl2_and_trophy(self):
        resp = [{"league": {"id": 702, "name": "Premier League 2 Division One", "type": "League"},
                 "seasons": [{"year": 2025}, {"year": 2026, "current": True}]},
                {"league": {"id": 46, "name": "EFL Trophy", "type": "Cup"}, "seasons": [{"year": 2025}]},
                {"league": {"id": 39, "name": "Premier League", "type": "League"}, "seasons": []}]
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"API_FOOTBALL_KEY": "x"}), \
             mock.patch.object(S, "_af_get", return_value=resp):
            doc = S.af_refresh_u21(path=os.path.join(d, "u.json"))
        self.assertEqual([e["code"] for e in doc["leagues"]], ["afu.702"])
        self.assertEqual(doc["trophy"]["id"], 46)
        self.assertEqual(doc["leagues"][0]["current"], 2026)


if __name__ == "__main__":
    unittest.main()
