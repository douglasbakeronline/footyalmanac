"""The pool archive's first real price and the pool-based Card replay
(9 Nov 2026, issue #154). A leg archived as the model's estimate, before any
bookmaker priced it, takes a `priced` block once from the first build that
carries a real price; tools/card_replay.py reads the pool from POOL_FROM and
settles every sport. Synthetic pool files only; nothing on disk is read."""
import gzip, json, os, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as CR

DAY = "2026-11-21"      # a Saturday after POOL_FROM; the window is 07:00 UK to 07:00 next day
T0 = datetime(2026, 11, 18, 1, 0, tzinfo=timezone.utc)


def fb(event, pick, home, away, odds, model, est=False, opp=10.0, when=f"{DAY}T15:00:00Z", code="en.1"):
    l = {"sport": "football", "event": event, "pick": pick, "home": home, "away": away, "side": "h" if pick == home else "a",
         "comp": "Premier League", "code": code, "when": when, "date": DAY, "odds": odds, "est": est,
         "pModel": model, "p": model, "pTested": model, "hit": 0.8, "n": 200, "list": True, "multOnly": False}
    if not est:
        l.update(margin=1.04, best=round(odds + 0.05, 2), bestBook="William Hill", bookOdds={"William Hill": round(odds + 0.05, 2)},
                 opp=opp, draw=4.5, src="API-Football average", pricedAt=G.iso(T0))
    else:
        l["src"] = "estimate: the model's price less a typical bookmaker margin, no bookmaker price found"
    return G.honest(l)


class PricedBlock(unittest.TestCase):
    """archive_pool: an estimate-first leg gets `priced` once; a real-first
    leg never does; lastFair and lastOpp follow the last price."""

    def setUp(self):
        self.saved = G.ARCHIVE; G.ARCHIVE = tempfile.mkdtemp()

    def tearDown(self):
        G.ARCHIVE = self.saved

    def read(self):
        with gzip.open(os.path.join(G.ARCHIVE, f"pool-{DAY}.json.gz"), "rt") as f: return json.load(f)

    def test_estimate_then_real_price(self):
        est = fb("Arsenal v Burnley", "Arsenal", "Arsenal", "Burnley", 1.22, 0.78, est=True)
        self.assertEqual(G.archive_pool([est], T0, [DAY]), 1)
        row = self.read()["legs"][0]
        self.assertTrue(row["est"]); self.assertNotIn("priced", row); self.assertNotIn("fair", row)
        real = fb("Arsenal v Burnley", "Arsenal", "Arsenal", "Burnley", 1.25, 0.72, opp=12.0)
        self.assertEqual(G.archive_pool([real], T0 + timedelta(days=1), [DAY]), 0)
        row = self.read()["legs"][0]
        self.assertTrue(row["est"]); self.assertEqual(row["odds"], 1.22)          # what was first written stands
        self.assertEqual(row["lastOdds"], 1.25); self.assertEqual(row["lastOpp"], 12.0); self.assertEqual(row["lastFair"], real["fair"])
        pr = row["priced"]
        self.assertEqual(pr["odds"], 1.25); self.assertEqual(pr["fair"], real["fair"]); self.assertEqual(pr["opp"], 12.0)
        self.assertEqual(pr["bookOdds"], {"William Hill": 1.3}); self.assertEqual(pr["at"], G.iso(T0 + timedelta(days=1)))
        # a later, different price moves last* but not priced
        later = fb("Arsenal v Burnley", "Arsenal", "Arsenal", "Burnley", 1.30, 0.72, opp=11.0)
        G.archive_pool([later], T0 + timedelta(days=2), [DAY])
        row = self.read()["legs"][0]
        self.assertEqual(row["priced"]["odds"], 1.25); self.assertEqual(row["lastOdds"], 1.30); self.assertEqual(row["lastOpp"], 11.0)

    def test_real_first_has_no_block_and_estimate_update_ignored(self):
        real = fb("Leeds v Fulham", "Leeds", "Leeds", "Fulham", 1.60, 0.56)
        G.archive_pool([real], T0, [DAY])
        est = fb("Leeds v Fulham", "Leeds", "Leeds", "Fulham", 1.55, 0.56, est=True)
        G.archive_pool([est], T0 + timedelta(hours=6), [DAY])
        row = self.read()["legs"][0]
        self.assertNotIn("priced", row); self.assertNotIn("lastOdds", row); self.assertEqual(row["fair"], real["fair"])

    def test_moved_start_kept_as_when_last(self):
        # 9 Nov 2026 (#156): a later build with a different start records whenLast; `when` stands
        real = fb("Leeds v Fulham", "Leeds", "Leeds", "Fulham", 1.60, 0.56)
        G.archive_pool([real], T0, [DAY])
        first_when = self.read()["legs"][0]["when"]
        same = dict(real); G.archive_pool([same], T0 + timedelta(hours=1), [DAY])
        self.assertNotIn("whenLast", self.read()["legs"][0])
        moved = dict(real, when=f"{DAY}T19:45:00Z"); G.archive_pool([moved], T0 + timedelta(hours=2), [DAY])
        row = self.read()["legs"][0]
        self.assertEqual(row["when"], first_when); self.assertEqual(row["whenLast"], f"{DAY}T19:45:00Z")

    def test_pool_keys_carry_id_and_flags(self):
        for k in ("id", "listOff", "timeEst"): self.assertIn(k, G.POOL_KEYS)
        t = {"sport": "tennis", "event": "A v B", "pick": "B", "when": f"{DAY}T12:00:00Z", "date": DAY, "odds": 1.3, "est": False,
             "margin": 1.05, "pModel": 0.8, "p": 0.8, "hit": 0.8, "n": 50, "id": "m77", "listOff": False}
        G.archive_pool([G.honest(t)], T0, [DAY])
        self.assertEqual(self.read()["legs"][0]["id"], "m77")


class PoolReplay(unittest.TestCase):
    """card_replay.pool_legs on a synthetic pool file: first real price from
    the row or its `priced` block, estimate-only legs left out, results by
    names for football, by id or names for tennis and US sport."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        real = fb("Arsenal v Burnley", "Arsenal", "Arsenal", "Burnley", 1.25, 0.70, opp=12.0)   # 7 points under the bookmakers' 77%
        real["firstAt"] = G.iso(T0)
        est_priced = dict(fb("Leeds v Fulham", "Leeds", "Leeds", "Fulham", 1.50, 0.58, est=True), firstAt=G.iso(T0),
                          lastOdds=1.60, lastBest=1.65, lastOpp=9.5, lastFair=0.6,
                          priced={"odds": 1.55, "best": 1.60, "bestBook": "Bet365", "bookOdds": {"Bet365": 1.60}, "margin": 1.04,
                                  "fair": 0.62, "implied": 0.6452, "opp": 9.2, "draw": 4.2, "src": "API-Football average", "at": G.iso(T0 + timedelta(days=1))})
        est_only = dict(fb("Spurs v Everton", "Spurs", "Spurs", "Everton", 1.40, 0.65, est=True), firstAt=G.iso(T0), lastOdds=1.45, lastBest=1.5)
        tennis_id = G.honest({"sport": "tennis", "event": "Ann Lee v Bea Roy", "pick": "Bea Roy", "comp": "Open", "when": f"{DAY}T11:00:00Z", "date": DAY,
                              "odds": 1.30, "est": False, "margin": 1.05, "pModel": 0.8, "p": 0.8, "pTested": 0.8, "hit": 0.8, "n": 60, "id": "t1", "firstAt": G.iso(T0)})
        tennis_names = G.honest({"sport": "tennis", "event": "Cara Fox v Dee Hill", "pick": "Cara Fox", "comp": "Open", "when": f"{DAY}T13:00:00Z", "date": DAY,
                                 "odds": 1.40, "est": False, "margin": 1.05, "pModel": 0.78, "p": 0.78, "pTested": 0.78, "hit": 0.8, "n": 60, "firstAt": G.iso(T0)})
        nba_names = G.honest({"sport": "nba", "event": "Boston Celtics v Utah Jazz", "pick": "Boston Celtics", "home": "Boston Celtics", "away": "Utah Jazz",
                              "comp": "NBA", "when": f"{DAY}T23:30Z", "date": DAY, "odds": 1.30, "est": False, "margin": 1.04, "pModel": 0.76, "p": 0.76,
                              "pTested": 0.76, "hit": 0.7, "n": 300, "firstAt": G.iso(T0)})
        with gzip.open(os.path.join(self.dir, f"pool-{DAY}.json.gz"), "wt") as f:
            json.dump({"date": DAY, "legs": [real, est_priced, est_only, tennis_id, tennis_names, nba_names]}, f)
        # an older file, before POOL_FROM, is never read
        with gzip.open(os.path.join(self.dir, "pool-2026-10-01.json.gz"), "wt") as f:
            json.dump({"date": "2026-10-01", "legs": [dict(real, date="2026-10-01", when="2026-10-01T15:00:00Z")]}, f)
        fbres = {(DAY, G.norm("Arsenal"), G.norm("Burnley")): (2, 0), (DAY, G.norm("Leeds"), G.norm("Fulham")): (1, 1),
                 (DAY, G.norm("Spurs"), G.norm("Everton")): (3, 0)}
        tn = {"t1": {"key": f"WTA|{DAY}|Ann Lee|Bea Roy", "playerA": "Ann Lee", "playerB": "Bea Roy", "winner": "Bea Roy", "date": DAY, "note": "Bea Roy bt Ann Lee 6-1 6-1"},
              "t2": {"key": f"WTA|{DAY}|Cara Fox|Dee Hill", "playerA": "Cara Fox", "playerB": "Dee Hill", "winner": "Dee Hill", "date": DAY}}
        sp = {"401": {"id": "401", "sport": "nba", "home": "Boston Celtics", "away": "Utah Jazz", "when": f"{DAY}T23:30Z", "winner": "Boston Celtics", "score": [110, 99]}}
        self.idx = (fbres, tn, sp)

    def test_legs_settled_and_estimates_left_out(self):
        by, skipped = CR.pool_legs(pool_dir=self.dir, idx=self.idx)
        self.assertEqual(list(by), [DAY])
        legs = {l["pick"]: l for l in by[DAY]}
        self.assertEqual(set(legs), {"Arsenal", "Leeds", "Bea Roy", "Cara Fox", "Boston Celtics"})
        self.assertEqual(skipped, {"estimate only": 1})
        self.assertTrue(legs["Arsenal"]["won"]); self.assertEqual(legs["Arsenal"]["odds"], 1.25); self.assertEqual(legs["Arsenal"]["opp"], 12.0)
        # the estimate-first leg replays on its first real price, not the estimate or the last price
        ld = legs["Leeds"]
        self.assertFalse(ld["won"]); self.assertFalse(ld["est"]); self.assertEqual(ld["odds"], 1.55); self.assertEqual(ld["fair"], 0.62)
        self.assertEqual(ld["opp"], 9.2); self.assertEqual(ld["best"], 1.60); self.assertEqual(ld["p"], min(0.58, 0.62))
        self.assertTrue(legs["Bea Roy"]["won"])                # tennis by id
        self.assertFalse(legs["Cara Fox"]["won"])              # tennis by names, no id on the row
        self.assertTrue(legs["Boston Celtics"]["won"])         # NBA by names
        self.assertIsNone(G.card_fault(legs["Arsenal"]))       # the rule reads the replayed leg as a live one

    def test_closing_prices(self):
        by, _ = CR.pool_legs(pool_dir=self.dir, idx=self.idx, closing=True)
        ld = {l["pick"]: l for l in by[DAY]}["Leeds"]
        self.assertEqual(ld["odds"], 1.60); self.assertEqual(ld["fair"], 0.6); self.assertEqual(ld["opp"], 9.5); self.assertEqual(ld["best"], 1.65)

    def test_recover_takes_estimate_only_legs_at_the_last_price(self):
        by, skipped = CR.pool_legs(pool_dir=self.dir, idx=self.idx, recover=True)
        legs = {l["pick"]: l for l in by[DAY]}
        self.assertIn("Spurs", legs); self.assertEqual(legs["Spurs"]["odds"], 1.45)
        self.assertEqual(legs["Spurs"]["fair"], round(1 / 1.45 / G.MARGIN, 4)); self.assertTrue(legs["Spurs"]["recovered"])
        self.assertEqual(skipped, {"recovered, counted at the last price": 1})

    def test_pending_left_out(self):
        fbres, tn, sp = self.idx
        by, skipped = CR.pool_legs(pool_dir=self.dir, idx=({}, tn, sp))
        self.assertEqual(skipped, {"estimate only": 1, "pending": 2})
        self.assertEqual({l["pick"] for l in by[DAY]}, {"Bea Roy", "Cara Fox", "Boston Celtics"})

    def test_pool_market_prefers_row_then_block(self):
        self.assertIsNone(CR.pool_market({"est": True, "odds": 1.3}))
        self.assertEqual(CR.pool_market({"est": True, "odds": 1.3, "priced": {"odds": 1.4, "fair": 0.7}})["odds"], 1.4)
        self.assertEqual(CR.pool_market({"est": False, "odds": 1.3, "fair": 0.75, "priced": {"odds": 1.4, "fair": 0.7}})["odds"], 1.3)


if __name__ == "__main__":
    unittest.main()


class IntegrityUnpriced(unittest.TestCase):
    """tools/card_integrity.py `pool-unpriced`: an estimate-first leg written
    from PRICED_FROM with a real last price and no `priced` block is a
    finding; one first written before PRICED_FROM is not."""

    def test_finding(self):
        import card_integrity as CI
        here, now = CI.HERE, CI.now
        CI.HERE = tempfile.mkdtemp(); CI.now = datetime(2026, 11, 21, 3, 40, tzinfo=timezone.utc)
        try:
            os.makedirs(os.path.join(CI.HERE, "groupings-archive"))
            json.dump({"days": [], "generated": G.iso(CI.now)}, open(os.path.join(CI.HERE, "groupings-record.json"), "w"))
            for i in range(-2, 2):
                day = (CI.now + timedelta(days=i)).date().isoformat()
                legs = [{"est": True, "lastOdds": 1.3, "firstAt": "2026-11-01T00:00:00Z"}]          # before PRICED_FROM: not a finding
                if day == DAY:
                    legs += [{"est": True, "lastOdds": 1.3, "firstAt": "2026-11-18T00:00:00Z"},     # the finding
                             {"est": True, "lastOdds": 1.3, "firstAt": "2026-11-18T00:00:00Z", "priced": {"odds": 1.3, "fair": 0.7}},
                             {"est": True, "firstAt": "2026-11-18T00:00:00Z"}]                          # never priced: nothing to record
                with gzip.open(os.path.join(CI.HERE, "groupings-archive", f"pool-{day}.json.gz"), "wt") as f:
                    json.dump({"date": day, "legs": legs}, f)
            import io, contextlib
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = CI.main()
            self.assertEqual(rc, 1)
            self.assertIn(f"check=pool-unpriced date={DAY} legs=1", out.getvalue())
            self.assertIn("1 finding(s)", out.getvalue())
        finally:
            CI.HERE, CI.now = here, now
