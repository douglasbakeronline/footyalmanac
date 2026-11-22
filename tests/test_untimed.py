"""build.fill_untimed: board rows with no kick-off take API-Football's date
and time (19 Nov 2026, #417). All or nothing on names; one fixture only."""
import os, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build as B
import sources as S

START = date(2026, 11, 19)


def row(h, a, d, time=None, hg=None):
    return {"date": d, "time": time, "round": None, "home": h, "away": a, "hg": hg, "ag": hg}


def af(h, a, d, t):
    return {"date": d, "time": t, "utc": True, "home": h, "away": a, "hg": None, "ag": None}


class FillUntimed(unittest.TestCase):
    def rows(self):
        return [row("Athletic Club", "RCD Espanyol", "2026-11-22"),
                row("Real Madrid CF", "RC Celta de Vigo", "2026-11-22")]

    def test_takes_date_and_time(self):
        rows = self.rows()
        n, bad = B.fill_untimed(rows, [af("Athletic Club", "Espanyol", "2026-11-20", "20:00"),
                                       af("Real Madrid", "Celta Vigo", "2026-11-21", "15:15")], START)
        self.assertEqual((n, bad), (2, []))
        self.assertEqual((rows[0]["date"], rows[0]["time"], rows[0]["utc"]), ("2026-11-20", "20:00", True))
        self.assertEqual((rows[1]["date"], rows[1]["time"]), ("2026-11-21", "15:15"))
        self.assertEqual(rows[0]["timeFrom"], "apifootball")

    def test_unmatched_name_changes_nothing(self):
        rows = self.rows()
        n, bad = B.fill_untimed(rows, [af("Athletic Club", "Espanyol", "2026-11-20", "20:00"),
                                       af("Zzyzx Rovers", "Celta Vigo", "2026-11-21", "15:15")], START)
        self.assertEqual(n, 0)
        self.assertTrue(bad)
        self.assertIsNone(rows[0]["time"])
        self.assertEqual(rows[0]["date"], "2026-11-22")

    def test_timed_played_and_far_rows_untouched(self):
        rows = [row("Athletic Club", "RCD Espanyol", "2026-11-22", time="18:00"),
                row("Real Madrid CF", "RC Celta de Vigo", "2026-11-10", hg=1),
                row("Real Madrid CF", "RC Celta de Vigo", "2026-11-22")]
        n, _ = B.fill_untimed(rows, [af("Athletic Club", "Espanyol", "2026-11-20", "20:00"),
                                     af("Real Madrid", "Celta Vigo", "2026-12-20", "15:15")], START)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["date"], "2026-11-22")
        self.assertIsNone(rows[2]["time"])

    def test_pair_listed_twice_in_window_left_alone(self):
        rows = self.rows()
        n, _ = B.fill_untimed(rows, [af("Real Madrid", "Celta Vigo", "2026-11-21", "15:15"),
                                     af("Real Madrid", "Celta Vigo", "2026-11-23", "15:15"),
                                     af("Athletic Club", "Espanyol", "2026-11-20", "20:00")], START)
        self.assertEqual(n, 1)
        self.assertIsNone(rows[1]["time"])

    def test_no_af_rows(self):
        self.assertEqual(B.fill_untimed(self.rows(), [], START), (0, []))


class Retime(unittest.TestCase):
    """AF_RETIME leagues (19 Nov 2026): openfootball's Premier League times are
    nominal (every game Saturday 15:00 UK), so a timed row takes API-Football's
    date and time when its UTC kick-off differs."""
    def rows(self):
        return [row("Manchester City", "Fulham", "2026-11-21", time="15:00"),
                row("Liverpool", "Manchester United", "2026-11-21", time="15:00"),
                row("Chelsea", "Leeds United", "2026-11-21", time="15:00")]

    def afs(self):
        return [af("Manchester City", "Fulham", "2026-11-21", "12:30"),
                af("Liverpool", "Manchester United", "2026-11-22", "16:30"),
                af("Chelsea", "Leeds", "2026-11-21", "15:00")]

    def test_retime_takes_tv_times(self):
        rows = self.rows()
        n, bad = B.fill_untimed(rows, self.afs(), START, retime="eng")
        self.assertEqual((n, bad), (2, []))
        self.assertEqual((rows[0]["date"], rows[0]["time"], rows[0]["utc"]), ("2026-11-21", "12:30", True))
        self.assertEqual((rows[1]["date"], rows[1]["time"]), ("2026-11-22", "16:30"))
        # 15:00 UK in November is 15:00 UTC: already right, left as it was
        self.assertNotIn("utc", rows[2])
        self.assertEqual(S.kickoff_utc(rows[0], "eng"), "2026-11-21T12:30:00Z")

    def test_bst_time_that_agrees_is_left(self):
        rows = [row("Manchester City", "Fulham", "2026-09-26", time="15:00")]
        n, _ = B.fill_untimed(rows, [af("Manchester City", "Fulham", "2026-09-26", "14:00")],
                              date(2026, 9, 20), retime="eng")
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["time"], "15:00")

    def test_without_retime_timed_rows_untouched(self):
        rows = self.rows()
        n, _ = B.fill_untimed(rows, self.afs(), START)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["time"], "15:00")

    def test_retime_all_or_nothing_on_names(self):
        rows = self.rows()
        n, bad = B.fill_untimed(rows, self.afs() + [af("Zzyzx Rovers", "Fulham", "2026-11-28", "15:00")],
                                START, retime="eng")
        self.assertEqual(n, 0)
        self.assertTrue(bad)
        self.assertEqual(rows[0]["time"], "15:00")

    def test_leagues_registered(self):
        self.assertEqual(S.AF_RETIME.get("en.1"), 39)
        self.assertEqual(S.AF_RETIME.get("en.2"), 40)
        self.assertEqual(S.AF_RETIME.get("it.1"), 135)
        self.assertNotIn("it.1", S.AF_UNTIMED)
        self.assertFalse(set(S.AF_RETIME) & set(S.AF_UNTIMED))

    def test_retime_rome_time_and_untimed_row(self):
        """Serie A under retime (20 Nov 2026): a row at 18:00 Rome (17:00 UTC)
        takes API-Football's 14:00 UTC, and a row with no time is still filled."""
        rows = [row("Bologna FC 1909", "Udinese Calcio", "2026-11-22", time="18:00"),
                row("Inter", "Milan", "2026-11-29")]
        afs = [af("Bologna", "Udinese", "2026-11-22", "14:00"),
               af("Inter", "AC Milan", "2026-11-29", "19:45")]
        n, bad = B.fill_untimed(rows, afs, START, retime="ita")
        self.assertEqual((n, bad), (2, []))
        self.assertEqual(S.kickoff_utc(rows[0], "ita"), "2026-11-22T14:00:00Z")
        self.assertEqual(rows[1]["time"], "19:45")

    def test_championship_api_football_spellings(self):
        """20 Nov 2026: API-Football's "Sheffield Utd" and "QPR" kept every
        Championship row from AF_RETIME; both now map, and Sheffield United v
        Watford's stale 12:30 takes API-Football's 15:00."""
        pool = ["Sheffield United", "Watford", "Queens Park Rangers", "Wrexham",
                "Sheffield Wednesday", "West Bromwich Albion"]
        rows = [row("Sheffield United", "Watford", "2026-11-21", time="12:30"),
                row("Queens Park Rangers", "Wrexham", "2026-11-21", time="15:00")]
        afs = [af("Sheffield Utd", "Watford", "2026-11-21", "15:00"),
               af("QPR", "Wrexham", "2026-11-21", "15:00")]
        self.assertEqual(S.match_team("Sheffield Utd", pool), "Sheffield United")
        self.assertEqual(S.match_team("QPR", pool), "Queens Park Rangers")
        n, bad = B.fill_untimed(rows, afs, START, retime="eng")
        self.assertEqual((n, bad), (1, []))
        self.assertEqual(S.kickoff_utc(rows[0], "eng"), "2026-11-21T15:00:00Z")


class Pick(unittest.TestCase):
    def fx(self, status, country="Spain"):
        return {"fixture": {"date": "2026-11-20T20:00:00+00:00", "status": {"short": status}},
                "league": {"country": country}, "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
                "score": {"fulltime": {}}}

    def test_tbd_dropped(self):
        self.assertEqual(S.af_untimed_pick("es.1", [self.fx("TBD")]), [])
        self.assertEqual(len(S.af_untimed_pick("es.1", [self.fx("NS")])), 1)

    def test_wrong_country_dropped(self):
        self.assertEqual(S.af_untimed_pick("es.1", [self.fx("NS", "Italy")]), [])




class BeforeWindow(unittest.TestCase):
    """22 Nov 2026: a round dated on its nominal Saturday (the Premier League's
    21 Nov, Brazil's) whose games are played on the Sunday or Monday fell
    before the window on the Sunday's build and never reached fill_untimed:
    Liverpool v Manchester United (22 Nov 16:30), Hull v Brighton and Brentford
    v Everton were off the board. An unplayed row up to `window` days before
    the start now takes API-Football's date when that date is in the window."""
    SUN = date(2026, 11, 22)

    def test_nominal_saturday_moves_into_window(self):
        rows = [row("Liverpool", "Manchester United", "2026-11-21", time="15:00"),
                row("Brentford", "Everton", "2026-11-21", time="15:00")]
        n, bad = B.fill_untimed(rows, [af("Liverpool", "Manchester United", "2026-11-22", "16:30"),
                                       af("Brentford", "Everton", "2026-11-23", "20:00")],
                                self.SUN, retime="eng")
        self.assertEqual((n, bad), (2, []))
        self.assertEqual((rows[0]["date"], rows[0]["time"]), ("2026-11-22", "16:30"))
        self.assertEqual((rows[1]["date"], rows[1]["time"]), ("2026-11-23", "20:00"))

    def test_untimed_league_before_window(self):
        rows = [row("CA Paranaense", "Clube do Remo", "2026-11-21")]
        n, _ = B.fill_untimed(rows, [af("Athletico Paranaense", "Remo", "2026-11-22", "19:00")], self.SUN)
        self.assertEqual(n, 1)
        self.assertEqual((rows[0]["date"], rows[0]["time"]), ("2026-11-22", "19:00"))

    def test_before_window_played_day_left_alone(self):
        # API-Football lists it before the start: played or postponed, not ours to move
        rows = [row("Liverpool", "Manchester United", "2026-11-21", time="15:00")]
        n, _ = B.fill_untimed(rows, [af("Liverpool", "Manchester United", "2026-11-21", "17:30")],
                              self.SUN, retime="eng")
        self.assertEqual(n, 0)
        self.assertEqual((rows[0]["date"], rows[0]["time"]), ("2026-11-21", "15:00"))

    def test_older_unplayed_row_is_a_rescheduled_game(self):
        # 22 Nov 2026 (afternoon): an unplayed row older than the window whose
        # ordered pair API-Football lists once in the window is the postponed
        # game replayed (these leagues play each ordered pair once a season)
        rows = [row("Rayo Vallecano de Madrid", "Athletic Club", "2026-10-10"),
                row("Liverpool", "Manchester United", "2026-11-18", time="15:00")]
        n, bad = B.fill_untimed(rows, [af("Rayo Vallecano", "Athletic Club", "2026-11-25", "20:00"),
                                       af("Liverpool", "Manchester United", "2026-11-22", "16:30")],
                                self.SUN)
        self.assertEqual((n, bad), (2, []))
        self.assertEqual((rows[0]["date"], rows[0]["time"]), ("2026-11-25", "20:00"))
        self.assertEqual(rows[0]["rescheduledFrom"], "2026-10-10")
        self.assertEqual(rows[1]["date"], "2026-11-22")

    def test_postponed_row_left_when_listed_before_window(self):
        rows = [row("Rayo Vallecano de Madrid", "Athletic Club", "2026-10-10")]
        n, _ = B.fill_untimed(rows, [af("Rayo Vallecano", "Athletic Club", "2026-11-20", "20:00")],
                              self.SUN)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["date"], "2026-10-10")

    def test_postponed_row_left_when_source_relisted_it(self):
        # the source already holds the new date as a second row: that row is
        # the one placed; the stale first copy stays where it is
        rows = [row("Rayo Vallecano de Madrid", "Athletic Club", "2026-10-10"),
                row("Rayo Vallecano de Madrid", "Athletic Club", "2026-11-25")]
        n, _ = B.fill_untimed(rows, [af("Rayo Vallecano", "Athletic Club", "2026-11-25", "20:00")],
                              self.SUN)
        self.assertEqual(n, 1)
        self.assertEqual(rows[0]["date"], "2026-10-10")
        self.assertEqual((rows[1]["date"], rows[1]["time"]), ("2026-11-25", "20:00"))

    def test_postponed_row_left_when_pair_listed_twice(self):
        rows = [row("Rayo Vallecano de Madrid", "Athletic Club", "2026-10-10")]
        n, _ = B.fill_untimed(rows, [af("Rayo Vallecano", "Athletic Club", "2026-11-23", "20:00"),
                                     af("Rayo Vallecano", "Athletic Club", "2026-11-25", "20:00")],
                              self.SUN)
        self.assertEqual(n, 0)

    def test_played_old_row_untouched(self):
        rows = [row("Rayo Vallecano de Madrid", "Athletic Club", "2026-10-10", hg=1)]
        n, _ = B.fill_untimed(rows, [af("Rayo Vallecano", "Athletic Club", "2026-11-25", "20:00")],
                              self.SUN)
        self.assertEqual(n, 0)


class RescheduleOnly(unittest.TestCase):
    """22 Nov 2026 (evening): the Primeira Liga (sources.AF_RESCHEDULE) has
    real dates and times, so only a postponed game is moved: Braga v Gil
    Vicente (16 Aug) and Estoril v Maritimo (8 Nov) were off the board."""
    SUN = date(2026, 11, 22)

    def test_registered_apart(self):
        self.assertEqual(S.AF_RESCHEDULE.get("pt.1"), 94)
        self.assertFalse(set(S.AF_RESCHEDULE) & (set(S.AF_RETIME) | set(S.AF_UNTIMED)))

    def test_postponed_row_moves(self):
        rows = [row("Sporting Clube de Braga", "Gil Vicente FC", "2026-08-16"),
                row("GD Estoril Praia", "CS Marítimo", "2026-11-08", time="15:30")]
        n, bad = B.fill_untimed(rows, [af("SC Braga", "Gil Vicente", "2026-11-25", "19:45"),
                                       af("Estoril", "Maritimo", "2026-11-26", "18:00")],
                                self.SUN, postponed_only=True)
        self.assertEqual((n, bad), (2, []))
        self.assertEqual((rows[0]["date"], rows[0]["time"]), ("2026-11-25", "19:45"))
        self.assertEqual(rows[0]["rescheduledFrom"], "2026-08-16")
        self.assertEqual(rows[1]["date"], "2026-11-26")

    def test_rows_in_the_window_untouched(self):
        # a timed or untimed row inside the look-back keeps its own date and time
        rows = [row("FC Porto", "Sport Lisboa e Benfica", "2026-11-23", time="20:30"),
                row("Rio Ave FC", "FC Arouca", "2026-11-21"),
                row("Sporting Clube de Braga", "Gil Vicente FC", "2026-08-16")]
        n, _ = B.fill_untimed(rows, [af("FC Porto", "Benfica", "2026-11-23", "19:00"),
                                     af("Rio Ave", "Arouca", "2026-11-22", "15:30"),
                                     af("SC Braga", "Gil Vicente", "2026-11-25", "19:45")],
                              self.SUN, postponed_only=True)
        self.assertEqual(n, 1)
        self.assertEqual((rows[0]["date"], rows[0]["time"]), ("2026-11-23", "20:30"))
        self.assertEqual((rows[1]["date"], rows[1]["time"]), ("2026-11-21", None))
        self.assertEqual(rows[2]["date"], "2026-11-25")

    def test_guards_still_hold(self):
        # listed twice, or the source relisted it: nothing moves
        rows = [row("Sporting Clube de Braga", "Gil Vicente FC", "2026-08-16")]
        n, _ = B.fill_untimed(rows, [af("SC Braga", "Gil Vicente", "2026-11-23", "19:45"),
                                     af("SC Braga", "Gil Vicente", "2026-11-25", "19:45")],
                              self.SUN, postponed_only=True)
        self.assertEqual(n, 0)
        rows = [row("Sporting Clube de Braga", "Gil Vicente FC", "2026-08-16"),
                row("Sporting Clube de Braga", "Gil Vicente FC", "2026-11-25", time="19:45")]
        n, _ = B.fill_untimed(rows, [af("SC Braga", "Gil Vicente", "2026-11-25", "19:45")],
                              self.SUN, postponed_only=True)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["date"], "2026-08-16")

    def test_api_football_spellings_match(self):
        # every 2026-27 club under API-Football's usual short forms (unprobed: the
        # sandbox has no key; the first CI build names any miss), against openfootball's file
        of = ["Académico de Viseu FC", "CD Nacional", "CD Santa Clara", "CF Estrela da Amadora",
              "CS Marítimo", "Casa Pia AC", "FC Alverca", "FC Arouca", "FC Famalicão", "FC Porto",
              "GD Estoril Praia", "Gil Vicente FC", "Moreirense FC", "Rio Ave FC",
              "Sport Lisboa e Benfica", "Sporting Clube de Braga", "Sporting Clube de Portugal",
              "Vitória Guimarães"]
        api = ["Academico Viseu", "Nacional", "Santa Clara", "Estrela", "Maritimo", "Casa Pia",
               "Alverca", "Arouca", "Famalicao", "FC Porto", "Estoril", "Gil Vicente", "Moreirense",
               "Rio Ave", "Benfica", "SC Braga", "Sporting CP", "Guimaraes"]
        rows = [row(of[i], of[(i + 1) % len(of)], "2026-12-01") for i in range(len(of))]
        mapping, bad = B._map_names(rows, [af(a, api[(i + 1) % len(api)], "2026-12-01", "20:00")
                                           for i, a in enumerate(api)])
        self.assertEqual(bad, [])
        self.assertEqual(mapping["SC Braga"], "Sporting Clube de Braga")
        self.assertEqual(mapping["Sporting CP"], "Sporting Clube de Portugal")

class RescheduleSplit(unittest.TestCase):
    """22 Nov 2026 (night): Scotland, Greece and Czechia (sources.AF_SPLIT)
    split after a regular season their openfootball files hold whole, so a
    postponed row moves only to a date on or before the file's last fixture:
    Dundee United v Hearts (31 Oct) and Atromitos v AEK (17 Oct) were off
    the board."""
    SUN = date(2026, 11, 22)

    def season(self):
        return [row("Dundee United", "Heart of Midlothian", "2026-10-31"),
                row("Celtic", "Rangers", "2026-11-29", time="12:00"),
                row("Aberdeen", "Hibernian", "2027-04-10", time="15:00")]

    def test_registered(self):
        self.assertEqual({c: S.AF_RESCHEDULE[c] for c in S.AF_SPLIT},
                         {"sco.1": 179, "gr.1": 197, "cze.1": 345})
        self.assertLessEqual(S.AF_SPLIT, set(S.AF_RESCHEDULE))

    def test_postponed_row_moves_in_the_regular_season(self):
        rows = self.season()
        n, bad = B.fill_untimed(rows, [af("Dundee Utd", "Heart Of Midlothian", "2026-11-25", "19:45")],
                                self.SUN, postponed_only=True, split=True)
        self.assertEqual((n, bad), (1, []))
        self.assertEqual((rows[0]["date"], rows[0]["rescheduledFrom"]), ("2026-11-25", "2026-10-31"))
        self.assertEqual(rows[1]["date"], "2026-11-29")

    def test_never_past_the_files_last_fixture(self):
        # a listing after the regular season is the split's game, not this one
        rows = self.season()
        n, _ = B.fill_untimed(rows, [af("Dundee Utd", "Heart Of Midlothian", "2027-04-25", "15:00")],
                              date(2027, 4, 24), postponed_only=True, split=True)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["date"], "2026-10-31")
        # without the split flag (Portugal) the same listing would move it
        rows = self.season()
        n, _ = B.fill_untimed(rows, [af("Dundee Utd", "Heart Of Midlothian", "2027-04-25", "15:00")],
                              date(2027, 4, 24), postponed_only=True)
        self.assertEqual(n, 1)

    def test_repeat_pair_in_the_file_refused(self):
        # Scotland's 33 rounds repeat 66 ordered pairs before the split
        rows = self.season() + [row("Dundee United", "Heart of Midlothian", "2027-02-14", time="15:00")]
        n, _ = B.fill_untimed(rows, [af("Dundee Utd", "Heart Of Midlothian", "2026-11-25", "19:45")],
                              self.SUN, postponed_only=True, split=True)
        self.assertEqual(n, 0)
        self.assertEqual(rows[0]["date"], "2026-10-31")

    def test_api_football_spellings_match(self):
        # API-Football's usual short forms (unprobed: the first CI build names any
        # miss) against openfootball's 2026-27 files; "Dundee Utd" had reduced to Dundee
        cases = {
            "sco": (["Aberdeen", "Celtic", "Dundee", "Dundee United", "Falkirk",
                     "Heart of Midlothian", "Hibernian", "Kilmarnock", "Motherwell", "Rangers",
                     "Saint Johnstone", "St. Mirren"],
                    ["Aberdeen", "Celtic", "Dundee", "Dundee Utd", "Falkirk", "Heart Of Midlothian",
                     "Hibernian", "Kilmarnock", "Motherwell", "Rangers", "ST Johnstone", "ST Mirren"]),
            "gr": (["AEK", "Aris Thessaloniki", "Asteras Tripolis", "Atromitos", "Iraklis 1908",
                    "Kalamata", "Kifisia", "Levadiakos", "OFI", "Olympiakos Piraeus", "PAOK",
                    "Panathinaikos", "Panetolikos", "Volos"],
                   ["AEK Athens FC", "Aris", "Asteras Tripolis", "Atromitos", "Iraklis", "Kalamata",
                    "Kifisia", "Levadiakos", "OFI", "Olympiakos Piraeus", "PAOK", "Panathinaikos",
                    "Panetolikos", "Volos NFC"]),
        }
        for key, (of, api) in cases.items():
            rows = [row(of[i], of[(i + 1) % len(of)], "2026-12-01") for i in range(len(of))]
            mapping, bad = B._map_names(rows, [af(a, api[(i + 1) % len(api)], "2026-12-01", "20:00")
                                               for i, a in enumerate(api)])
            self.assertEqual(bad, [], key)
            self.assertEqual(len(set(mapping.values())), len(of), key)
        self.assertEqual(S.match_team("Dundee Utd", {"Dundee", "Dundee United"}), "Dundee United")


if __name__ == "__main__":
    unittest.main()
