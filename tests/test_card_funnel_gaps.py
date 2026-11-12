"""tools/card_funnel.py price_gaps (12 Nov 2026): the legs a missing
bookmaker price alone keeps off the Card, split into days already started
and days still to come. Synthetic pool files; nothing is fitted."""
import gzip, json, os, sys, tempfile, unittest
from unittest import mock
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_funnel as CF

_LIVE = [mock.patch.object(G, "CARD_MODEL_RULE", True), mock.patch.object(G, "CARD_RULE", 11),
         mock.patch.object(G, "CARD_SPORTS_OFF", {"cfb", "nfl", "ncaab"}), mock.patch.object(G, "CARD_CORE_ONLY", False)]
def setUpModule():
    for p in _LIVE: p.start()
def tearDownModule():
    for p in _LIVE: p.stop()


def leg(i, day, sport="nba", model=0.78, est=True, priced=None):
    r = {"sport": sport, "event": f"Home{i} v Away{i}", "pick": f"Home{i}", "comp": "NBA", "when": f"{day}T19:00:00Z",
         "date": day, "pModel": model, "pTested": model, "hit": 0.8, "p": model, "est": est}
    if not est: r.update(odds=1.40, best=1.42, fair=0.69, margin=1.04, opp=3.0)
    if priced: r["priced"] = priced
    return r


class PriceGaps(unittest.TestCase):
    def pool(self, legs_by_day):
        d = tempfile.mkdtemp()
        for day, legs in legs_by_day.items():
            with gzip.open(os.path.join(d, f"pool-{day}.json.gz"), "wt", encoding="utf-8") as f:
                json.dump({"date": day, "legs": legs}, f)
        return d

    def test_unpriced_leg_that_would_qualify_counts(self):
        self.assertTrue(CF.unpriced_ok(leg(1, "2026-11-20")))

    def test_unpriced_leg_failing_another_condition_does_not(self):
        self.assertFalse(CF.unpriced_ok(leg(1, "2026-11-20", model=0.50)))       # under the model floor
        self.assertFalse(CF.unpriced_ok(leg(1, "2026-11-20", sport="cfb")))       # sport off the Card
        self.assertFalse(CF.unpriced_ok(dict(leg(1, "2026-11-20"), pModel=None)))

    def test_split_past_and_to_come_and_priced_left_out(self):
        d = self.pool({"2026-11-18": [leg(1, "2026-11-18"), leg(2, "2026-11-18", est=False)],
                       "2026-11-20": [leg(3, "2026-11-20"), leg(4, "2026-11-20", model=0.4)]})
        g = CF.price_gaps("2026-11-10", None, "2026-11-19", pool_dir=d)
        self.assertEqual(g["legs"], 2)
        self.assertEqual(g["past"], 1)
        self.assertEqual(g["bySport"], {"nba|past": 1, "nba|to come": 1})
        self.assertEqual(g["days"], {"2026-11-18": 1})

    def test_leg_priced_later_is_not_a_gap(self):
        d = self.pool({"2026-11-18": [leg(1, "2026-11-18", priced={"odds": 1.4, "fair": 0.69, "margin": 1.04})]})
        self.assertEqual(CF.price_gaps("2026-11-10", None, "2026-11-19", pool_dir=d)["legs"], 0)

    def test_lines(self):
        self.assertIn("No leg", CF.gap_lines({"legs": 0})[0])
        d = self.pool({"2026-11-18": [leg(1, "2026-11-18")]})
        txt = "\n".join(CF.gap_lines(CF.price_gaps("2026-11-10", None, "2026-11-19", pool_dir=d)))
        self.assertIn("**1**", txt); self.assertIn("| nba | 1 | 0 |", txt)


if __name__ == "__main__":
    unittest.main()
