"""groupings.pool_rows (13 Nov 2026): one pool row a fixture. A fixture the
source moves to another day keeps the row of its latest placement; a rematch
(different ids, or starts more than POOL_MOVE_DAYS apart) stays two rows.
Synthetic pool files; nothing is fitted."""
import gzip, json, os, sys, tempfile, unittest
from unittest import mock
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_funnel as CF


def row(day, hour="19:00", first="2026-11-10T01:00:00Z", sport="nba", event="Knicks v Pacers", pick="Knicks", **kw):
    r = {"sport": sport, "event": event, "pick": pick, "when": f"{day}T{hour}:00Z", "date": day, "firstAt": first,
         "pModel": 0.75, "pTested": 0.75, "hit": 0.8, "p": 0.75, "est": True, "comp": "NBA"}
    r.update(kw)
    return r


def pool(by_day):
    d = tempfile.mkdtemp()
    for day, legs in by_day.items():
        with gzip.open(os.path.join(d, f"pool-{day}.json.gz"), "wt", encoding="utf-8") as f:
            json.dump({"date": day, "legs": legs}, f)
    return d


class PoolRows(unittest.TestCase):
    def test_moved_later_keeps_new_day(self):
        # tennis placed a day early, then on its real day
        d = pool({"2026-11-02": [row("2026-11-02", first="2026-11-01T00:00:00Z")],
                  "2026-11-03": [row("2026-11-03", first="2026-11-02T00:00:00Z", est=False, odds=1.4, fair=0.69)]})
        out = G.pool_rows(d)
        self.assertEqual([x[0] for x in out], ["2026-11-03"])
        self.assertFalse(out[0][1]["est"])

    def test_moved_earlier_keeps_new_day(self):
        # Drina Zvornik: first on 14 Nov, then the source moved it to 13 Nov
        d = pool({"2026-11-13": [row("2026-11-13", "12:00", first="2026-11-12T22:38:18Z")],
                  "2026-11-14": [row("2026-11-14", "12:00", first="2026-11-10T22:11:40Z")]})
        self.assertEqual([x[0] for x in G.pool_rows(d)], ["2026-11-13"])

    def test_different_ids_are_two_fixtures(self):
        d = pool({"2026-11-12": [row("2026-11-12", id="1")], "2026-11-13": [row("2026-11-13", id="2")]})
        self.assertEqual(len(G.pool_rows(d)), 2)

    def test_same_id_is_one_fixture(self):
        d = pool({"2026-11-11": [row("2026-11-11", id="7", first="2026-11-09T00:00:00Z")],
                  "2026-11-12": [row("2026-11-12", id="7", first="2026-11-10T00:00:00Z")],
                  "2026-11-13": [row("2026-11-13", id="7", first="2026-11-11T00:00:00Z")]})
        self.assertEqual([x[0] for x in G.pool_rows(d)], ["2026-11-13"])

    def test_far_apart_is_a_rematch(self):
        d = pool({"2026-11-04": [row("2026-11-04")], "2026-11-15": [row("2026-11-15", first="2026-11-12T00:00:00Z")]})
        self.assertEqual(len(G.pool_rows(d)), 2)

    def test_other_picks_untouched(self):
        d = pool({"2026-11-12": [row("2026-11-12"), row("2026-11-12", event="Nets v Heat", pick="Heat")]})
        self.assertEqual(len(G.pool_rows(d)), 2)

    def test_missing_dir(self):
        self.assertEqual(G.pool_rows(os.path.join(tempfile.mkdtemp(), "none")), [])

    def test_funnel_reads_the_moved_row(self):
        # the funnel's old (event, pick) dedup kept the first, stale, unpriced row
        with mock.patch.object(G, "CARD_MODEL_RULE", True), mock.patch.object(G, "CARD_RULE", 11):
            d = pool({"2026-11-12": [row("2026-11-12", first="2026-11-10T00:00:00Z")],
                      "2026-11-13": [row("2026-11-13", first="2026-11-11T00:00:00Z", est=False, odds=1.40, best=1.42,
                                         fair=0.69, margin=1.04, opp=3.0)]})
            by, unpriced = CF.pool_days("2026-11-10", None, pool_dir=d)
        self.assertEqual(sum(len(v) for v in by.values()), 1)
        self.assertEqual(sum(unpriced.values()), 0)


if __name__ == "__main__":
    unittest.main()
