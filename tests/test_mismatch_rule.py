"""Douglas's mismatch rule (#224, 11 Nov 2026): card_legs_history builds the
table from earlier dates only, applies the pre-registered conditions, keeps
the 1.15-1.60 home price band, splits by games played and gates on 4 of 5
seasons ahead of the price."""
import os, sys, unittest
from datetime import date, timedelta

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import card_legs_history as H

HEAD = "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR,AvgH,AvgD,AvgA,MaxH,MaxD,MaxA"


def season_csv(final_price=1.40, final_result=(2, 0), rounds=7):
    """Eight teams, A strongest to H weakest; A beats everyone 3-0 and H loses
    to everyone 0-2, the rest draw 1-1. Then A v H at home on the last day."""
    teams = list("ABCDEFGH")
    lines, d = [HEAD], date(2025, 8, 2)
    for rnd in range(rounds):
        for i in range(0, 8, 2):
            # a rotating pairing keeps every team playing once a round
            order = teams[:1] + teams[1:][rnd % 7:] + teams[1:][:rnd % 7]
            h, a = order[i], order[i + 1]
            if "A" in (h, a): hg, ag = (3, 0) if h == "A" else (0, 3)
            elif "H" in (h, a): hg, ag = (0, 2) if h == "H" else (2, 0)
            else: hg, ag = 1, 1
            ftr = "H" if hg > ag else "A" if ag > hg else "D"
            lines.append(f"E0,{d.strftime('%d/%m/%Y')},15:00,{h},{a},{hg},{ag},{ftr},2.5,3.2,2.9,2.6,3.3,3.0")
        d += timedelta(days=7)
    hg, ag = final_result
    ftr = "H" if hg > ag else "A" if ag > hg else "D"
    lines.append(f"E0,{d.strftime('%d/%m/%Y')},15:00,A,H,{hg},{ag},{ftr},{final_price},4.5,9.0,{final_price + 0.04},4.8,9.5")
    return "\n".join(lines) + "\n", d.isoformat()


class MismatchRule(unittest.TestCase):
    def test_strong_home_v_weak_away_is_a_leg(self):
        text, day = season_csv()
        M = H.mismatch_legs([text])
        self.assertEqual([(l["home"], l["away"], l["date"]) for l in M], [("A", "H", day)])
        l = M[0]
        self.assertTrue(l["won"]); self.assertEqual(l["gp"], 7); self.assertAlmostEqual(l["best"], 1.44)
        self.assertFalse(l["edge"])

    def test_price_band_and_games_played(self):
        self.assertEqual(H.mismatch_legs([season_csv(final_price=1.75)[0]]), [])
        self.assertEqual(H.mismatch_legs([season_csv(rounds=5)[0]]), [])     # five games each: under the minimum

    def test_same_day_games_never_count(self):
        text, day = season_csv()
        st, size = H.table_before(H.results_rows(text), day)
        self.assertEqual(size, 8)
        self.assertEqual(st["A"]["gp"], 7)          # the A v H game itself is not in the table
        self.assertEqual((st["A"]["pos"], st["H"]["pos"]), (1, 8))
        self.assertTrue(st["A"]["gfTop"] and st["A"]["gaFew"] and st["H"]["gfBottom"] and st["H"]["gaMany"])

    def test_edge_overlap_and_report(self):
        text, day = season_csv(final_result=(0, 1))
        M = H.mismatch_legs([text], frozenset({("en.1", day, "A", "H")}))
        self.assertTrue(M[0]["edge"]); self.assertFalse(M[0]["won"])
        r = H.mismatch_report(M)
        self.assertEqual((r["singles"]["n"], r["edgeCaught"], r["notEdge"]["n"]), (1, 1, 0))
        self.assertEqual(r["byGamesPlayed"]["6-10"]["n"], 1)
        self.assertEqual(r["byGamesPlayed"]["21+"]["n"], 0)

    def test_verdict_needs_four_seasons_and_the_best_price(self):
        ahead = {"n": 50, "landed": 0.85, "quoted": 0.80}
        behind = {"n": 50, "landed": 0.75, "quoted": 0.80}
        band = lambda r: {"singles": r, "byGamesPlayed": {b: r for b, _, _ in H.MM_GP_BANDS}}
        pooled = band({"n": 250, "pRoiBestNotPositive": 0.2})
        v = H.mismatch_verdict([band(ahead)] * 4 + [band(behind)], pooled)
        self.assertTrue(v["all"]["passes"]); self.assertEqual(v["all"]["aheadOfPrice"], 4)
        v = H.mismatch_verdict([band(ahead)] * 3 + [band(behind)] * 2, pooled)
        self.assertFalse(v["all"]["passes"])
        v = H.mismatch_verdict([band(ahead)] * 5, band({"n": 250, "pRoiBestNotPositive": 0.4}))
        self.assertFalse(v["21+"]["passes"])


if __name__ == "__main__":
    unittest.main()
