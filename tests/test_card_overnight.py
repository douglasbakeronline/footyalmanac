"""The Card's day after midnight (26 Nov 2026, groupings.card_dates): the day
runs 07:00 to 07:00 UK, so a group whose picks all start between midnight and
07:00 must still be built, held and locked by the builds in those hours, and
archived under its own day. Before this the build began at today's UK date and
dropped the day before at midnight (25 Nov: Warriors, Grizzlies, Toluca)."""
import os, sys, json, tempfile, unittest
from datetime import date, datetime, timedelta, timezone
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G


def _day():
    d = date.today() + timedelta(days=7)
    if 4 <= d.month <= 10: d = date(d.year, 11, 1)      # GMT: UK time is UTC
    while d.weekday() != 2: d += timedelta(days=1)
    return d
D1 = _day(); D2 = D1 + timedelta(days=1)


def at(d, h, m=0):
    return datetime(d.year, d.month, d.day, h, m, tzinfo=timezone.utc)


def leg(i, d, hour, odds=1.40, model=0.76):
    l = {"event": f"h{i} v a{i}", "pick": f"h{i}", "home": f"h{i}", "away": f"a{i}", "sport": "football",
         "comp": f"league{i}", "code": "en.1", "odds": odds, "p": model, "pModel": model, "est": False,
         "margin": 1.04, "date": d.isoformat(), "when": f"{d.isoformat()}T{hour:02d}:00:00Z", "why": None,
         "opp": 8.0, "hit": 0.8}
    return G.honest(l)


class CardDates(unittest.TestCase):
    def test_day_before_kept_until_seven(self):
        dates = [D2.isoformat(), (D2 + timedelta(days=1)).isoformat()]
        self.assertEqual(G.card_dates(dates, at(D2, 0, 10)), [D1.isoformat()] + dates)
        self.assertEqual(G.card_dates(dates, at(D2, 6, 59)), [D1.isoformat()] + dates)

    def test_day_before_gone_from_seven(self):
        dates = [D2.isoformat()]
        self.assertEqual(G.card_dates(dates, at(D2, 7, 0)), dates)
        self.assertEqual(G.card_dates(dates, at(D2, 22, 15)), dates)


class OvernightGroup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        for k, v in (("ARCHIVE", self.tmp.name), ("CARD_SPAN", False)):
            p = mock.patch.object(G, k, v); p.start(); self.addCleanup(p.stop)
        # three picks starting 01:00 to 03:00 on the next calendar day: the first day's overnight
        self.L = [leg(i, D2, 1 + i) for i in range(3)]
        for l in self.L: self.assertIsNone(G.card_fault(l), l["pick"])
        self.assertEqual({G.uk_slot(l)[0] for l in self.L}, {D1.isoformat()})

    def test_held_then_locked_and_archived(self):
        first = G.build_card(self.L, D1.isoformat(), at(D1, 21, 0), log=[])
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["status"], "new")
        # the first build after midnight: the day is still built, the group holds
        held = G.build_card(self.L, D1.isoformat(), at(D2, 0, 10), prev=first, log=[])
        self.assertEqual(len(held), 1)
        self.assertFalse(held[0].get("locked"))
        self.assertEqual(held[0]["status"], "holding")
        # a build after its first kick-off: locked, and archived under its own day
        late = G.build_card(self.L, D1.isoformat(), at(D2, 5, 15), prev=held, log=[])
        self.assertTrue(late[0]["locked"])
        n = G.archive_locked({"date": D1.isoformat(), "groups": late}, G.iso(at(D2, 5, 15)))
        self.assertEqual(n, 1)
        with open(os.path.join(self.tmp.name, f"{D1.isoformat()}.json")) as f:
            a = json.load(f)
        self.assertEqual([l["pick"] for l in a["groups"][0]["legs"]], [l["pick"] for l in held[0]["legs"]])

    def test_nothing_new_once_the_window_ends(self):
        self.assertEqual(G.build_card(self.L, D1.isoformat(), at(D2, 7, 0), log=[]), [])


if __name__ == "__main__":
    unittest.main()
