"""The model's record on every team (teamrecord.py, 28 Nov 2026).

What must hold: a side's tally counts each graded fixture once, two clubs are
never joined on a name alone when the record shows them apart, and the page
finds a side under the spelling on its row.
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import teamrecord as T


def fb(code, d, home, away, pick, actual, conf=0.6):
    return {"league": code, "date": d, "home": home, "away": away, "pick": pick, "actual": actual,
            "confidence": conf, "result": [1, 0], "kickoff": d + "T15:00:00Z"}


def clubs(rows, board=()):
    return T.Clubs([(g["league"], g["date"], g["home"], g["away"]) for g in rows] + list(board))


class Scope(unittest.TestCase):
    def test_kinds(self):
        for code, want in (("en.1", ("dom", "eng")), ("en.w1", ("dom", "eng-w")), ("en.fa", ("cup", "eng")),
                           ("eu.cl", ("cont", "cont")), ("uwcl", ("cont", "cont-w")), ("afc.cl", ("cont", "cont")),
                           ("friendly", ("int", "int")), ("afu.702", ("solo", "afu.702")),
                           ("fifa.wwc.u20", ("solo", "fifa.wwc.u20")), ("u21.uefa.q", ("solo", "u21.uefa.q")),
                           ("no.such.code", ("solo", "no.such.code"))):
            self.assertEqual(T.scope_of(code), want, code)


class Identity(unittest.TestCase):
    def test_men_and_women_apart(self):
        rows = [fb("en.1", "2026-09-05", "Arsenal", "Chelsea", "h", "h"),
                fb("en.w1", "2026-09-06", "Arsenal", "Chelsea", "h", "h")]
        c = clubs(rows)
        self.assertNotEqual(c.id("en.1", "Arsenal"), c.id("en.w1", "Arsenal"))

    def test_two_spellings_one_club(self):
        # one source a matchday: the club is written one way or the other, never both
        rows = [fb("en.5", "2026-09-05", "Southend United", "Woking", "h", "h"),
                fb("en.5", "2026-09-12", "Rochdale", "Southend", "h", "a"),
                fb("en.5", "2026-09-19", "Southend United", "Altrincham", "h", "h"),
                fb("en.5", "2026-09-26", "Yeovil Town", "Southend", "a", "a")]
        c = clubs(rows)
        self.assertEqual(c.id("en.5", "Southend"), c.id("en.5", "Southend United"))
        self.assertIn(("spelling", "eng", "en.5"), [j[:3] for j in c.joined])

    def test_two_clubs_sharing_a_word_stay_apart(self):
        # both play the same weekend against different sides: two clubs
        rows = [fb("ar.1", "2026-09-05", "Independiente", "Boca Juniors", "h", "h"),
                fb("ar.1", "2026-09-06", "Independiente Rivadavia", "River Plate", "a", "a"),
                fb("ar.1", "2026-09-12", "Lanús", "Independiente", "h", "h"),
                fb("ar.1", "2026-09-13", "Racing Club", "Independiente Rivadavia", "h", "h")]
        c = clubs(rows)
        self.assertNotEqual(c.id("ar.1", "Independiente"), c.id("ar.1", "Independiente Rivadavia"))

    def test_league_under_two_codes_counted_once(self):
        rows = [fb("tr.1", "2026-10-10", "Samsunspor", "Trabzonspor", "a", "a", 0.45),
                fb("af.203", "2026-10-10", "Samsunspor", "Trabzonspor", "a", "a", 0.45),
                fb("tr.1", "2026-10-17", "Trabzonspor", "Kasimpasa", "h", "d", 0.6)]
        out = T.build(football=rows, tennis=[], sports=[],
                      board=[("tr.1", "2026-11-28", "Trabzonspor", "Samsunspor"),
                             ("af.203", "2026-11-28", "Trabzonspor", "Samsunspor")])   # the same game, both codes
        self.assertEqual(out["keys"]["f|tr.1|Samsunspor"], out["keys"]["f|af.203|Samsunspor"])   # one club, either code
        row = out["rows"][out["keys"]["f|tr.1|Trabzonspor"]]
        self.assertEqual(row[:2], [2, 1])                 # two fixtures, not three
        self.assertEqual(out["rows"][out["keys"]["f|af.203|Samsunspor"]][0], 1)

    def test_same_name_two_clubs_in_a_country(self):
        # FC Andorra (LaLiga 2) and Andorra CF (Tercera) play different sides the same weekend
        rows = [fb("es.2", "2026-10-03", "Andorra", "Granada", "a", "a"),
                fb("af.455", "2026-10-04", "Andorra", "Utebo", "h", "h"),
                fb("es.cup", "2026-10-27", "Andorra", "Getafe", "a", "a")]
        c = clubs(rows)
        self.assertNotEqual(c.id("es.2", "Andorra"), c.id("af.455", "Andorra"))
        cup = c.id("es.cup", "Andorra")
        self.assertNotIn(cup, (c.id("es.2", "Andorra"), c.id("af.455", "Andorra")))   # stands alone

    def test_cup_and_europe_join_the_league_club(self):
        rows = [fb("de.1", "2026-08-28", "FC Bayern München", "VfB Stuttgart", "h", "h"),
                fb("de.cup", "2026-10-28", "Bayern Munich", "1. FC Magdeburg", "h", "h"),
                fb("eu.cl", "2026-10-21", "Bayern Munich", "Arsenal", "h", "d")]
        c = clubs(rows)
        home = c.id("de.1", "FC Bayern München")
        self.assertEqual(c.id("de.cup", "Bayern Munich"), home)
        self.assertEqual(c.id("eu.cl", "Bayern Munich"), home)

    def test_exact_spelling_settles_a_shared_name(self):
        # AC Milan and Serie D's Club Milano both reduce to "milano"; Europe writes "AC Milan"
        rows = [fb("it.1", "2026-09-05", "AC Milan", "Roma", "h", "h"),
                fb("af.427", "2026-09-06", "Club Milano", "Varesina", "h", "h"),
                fb("eu.el", "2026-09-17", "AC Milan", "Lyon", "h", "h")]
        c = clubs(rows)
        self.assertNotEqual(c.id("it.1", "AC Milan"), c.id("af.427", "Club Milano"))
        self.assertEqual(c.id("eu.el", "AC Milan"), c.id("it.1", "AC Milan"))

    def test_europe_stands_alone_when_two_countries_carry_the_name(self):
        rows = [fb("en.1", "2026-09-05", "Rangers", "Chelsea", "a", "a"),
                fb("sco.1", "2026-09-05", "Rangers", "Celtic", "h", "h"),
                fb("eu.el", "2026-09-17", "Rangers", "Lyon", "h", "h")]
        c = clubs(rows)
        self.assertNotIn(c.id("eu.el", "Rangers"), (c.id("en.1", "Rangers"), c.id("sco.1", "Rangers")))


class Tallies(unittest.TestCase):
    def test_backed_against_and_draw_calls(self):
        rows = [fb("en.1", "2026-09-05", "Arsenal", "Chelsea", "h", "h", 0.6),     # backed Arsenal, right
                fb("en.1", "2026-09-12", "Everton", "Arsenal", "h", "a", 0.5),     # picked against, wrong
                fb("en.1", "2026-09-19", "Arsenal", "Fulham", "d", "d", 0.4),      # a draw call, right
                fb("en.1", "2026-09-26", "Arsenal", "Brentford", "h", "d", 0.7)]   # backed, wrong
        out = T.build(football=rows, tennis=[], sports=[], board=[("en.1", "2026-11-28", "Arsenal", "Chelsea")])
        n, right, quoted, backed, bwon, against, aright, last, first, to = out["rows"][out["keys"]["f|en.1|Arsenal"]]
        self.assertEqual((n, right, backed, bwon, against, aright), (4, 2, 2, 1, 1, 0))
        self.assertAlmostEqual(quoted, 2.2)
        self.assertEqual(last, "1010")                    # oldest first
        self.assertEqual((first, to), ("2026-09-05", "2026-09-26"))
        self.assertEqual(out["since"], "2026-09-05")

    def test_last_keeps_ten(self):
        rows = [fb("en.1", f"2026-09-{d:02d}", "Arsenal", f"Side {d}", "h", "h" if d % 2 else "a") for d in range(1, 15)]
        out = T.build(football=rows, tennis=[], sports=[], board=[("en.1", "2026-11-28", "Arsenal", "Chelsea")])
        row = out["rows"][out["keys"]["f|en.1|Arsenal"]]
        self.assertEqual(len(row[7]), T.LAST)
        self.assertEqual(row[7][-1], "0")                 # the 14th, newest last
        self.assertEqual(row[0], 14)

    def test_only_names_on_the_page_are_written(self):
        rows = [fb("en.1", "2026-09-05", "Arsenal", "Chelsea", "h", "h")]
        out = T.build(football=rows, tennis=[], sports=[], board=[("en.1", "2026-11-28", "Arsenal", "Fulham")])
        self.assertIn("f|en.1|Arsenal", out["keys"])
        self.assertNotIn("f|en.1|Chelsea", out["keys"])   # tallied, not on the page
        self.assertNotIn("f|en.1|Fulham", out["keys"])    # on the page, nothing graded
        self.assertEqual(out["teams"]["football"], 2)

    def test_other_sports_and_tennis(self):
        sports = [{"id": "1", "sport": "nba", "when": "2026-11-01T00:00Z", "home": "Boston Celtics", "away": "Miami Heat",
                   "pick": "Boston Celtics", "confidence": 0.7, "ok": True},
                  {"id": "2", "sport": "nba", "when": "2026-11-03T00:00Z", "home": "Miami Heat", "away": "Boston Celtics",
                   "pick": "Miami Heat", "confidence": 0.55, "ok": False},
                  {"id": "3", "sport": "nba", "when": "2026-11-05T00:00Z", "home": "Miami Heat", "away": "Boston Celtics",
                   "pick": "Miami Heat", "confidence": 0.55, "ok": None, "void": True}]
        tennis = [{"date": "2026-11-02", "playerA": "A Player", "playerB": "B Player", "pick": "B Player",
                   "confidence": 0.8, "ok": True, "void": False}]
        out = T.build(football=[], tennis=tennis, sports=sports, board=[])
        celtics = out["rows"][out["keys"]["nba|Boston Celtics"]]
        self.assertEqual(celtics[:7], [2, 1, 1.25, 1, 1, 1, 0])     # the void game left out
        self.assertEqual(out["rows"][out["keys"]["tennis|A Player"]][:7], [1, 1, 0.8, 0, 0, 1, 1])
        self.assertEqual(out["teams"], {"tennis": 2, "sports": 2})


class Page(unittest.TestCase):
    def test_the_page_reads_it(self):
        page = open(os.path.join(HERE, "index.html")).read()
        for bit in ('["team-record.js", "__TEAM_RECORD__"]', "function teamRecBlock(",
                    'teamRecBlock("football", g.league, g.home.name, g.away.name)',
                    'teamRecBlock(g.sport, "", g.home, g.away)'):
            self.assertIn(bit, page, bit)
        self.assertEqual(page.count('teamRecBlock("football"'), 2)   # the winner board and Both to score


if __name__ == "__main__":
    unittest.main()
