"""Place now, the top of the Bets tab (10 Nov 2026): only open bets that pass
a tested rule. Run in node on the page's own functions with stub data: an
Edge single and a full-rule Card group are listed soonest first, a started
group and a late group are left out, the wider-rule filler is never a
signal, and the copied slip carries the stake and William Hill's prices."""
import json, os, shutil, subprocess, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def page_functions():
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    return src[src.index("const SIG_HOURS = 24;"):src.index("function sigWire(host){")]


STUBS = """
const pct = x => Math.round(x*100);
const ogEsc = s => String(s ?? "");
const ogStake = () => 10;
const compName = g => g.leagueName;
const ogDate = l => l.when ? new Date(l.when) : null;
const RS = null;
"""


@unittest.skipUnless(shutil.which("node"), "node not installed")
class PlaceNow(unittest.TestCase):
    def run_js(self, D, OG):
        js = STUBS + f"const D = {json.dumps(D)}, OG = {json.dumps(OG)};\n" + page_functions() + """
const now = Date.parse("2026-11-10T09:00:00Z");
const r = sigList(now);
console.log(JSON.stringify({out: r.out.map(s => [s.kind, s.title, s.units, +s.odds.toFixed(2)]),
  skip: r.skip.map(s => s.kind), slip: r.out.length ? sigSlip(r.out[r.out.length - 1]) : ""}));
"""
        return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)

    def leg(self, pick, when, odds, hill=None):
        return {"pick": pick, "event": f"{pick} v Other", "when": when, "odds": odds,
                "bookOdds": {"William Hill": hill} if hill else {}}

    def test_lists_open_signals_only(self):
        D = {"days": [{"games": [
            {"kickoff": "2026-11-10T12:00:00Z", "leagueName": "Premier League", "home": {"name": "Arsenal"}, "away": {"name": "Leeds"},
             "edge": {"side": "h", "odds": 1.40, "best": 1.45, "opp": 9.5, "fair": 0.68, "model": 0.66}},
            {"kickoff": "2026-11-10T08:00:00Z", "leagueName": "Premier League", "home": {"name": "A"}, "away": {"name": "B"},
             "edge": {"side": "a", "odds": 1.4, "best": 1.4, "opp": 9.5, "fair": 0.68, "model": 0.66}}]}]}
        card = {"name": "Card 2x", "stake": 2, "odds": 2.0, "p": 0.45, "status": "holding",
                "legs": [self.leg("X", "2026-11-10T19:00:00Z", 1.4, 1.38), self.leg("Y", "2026-11-10T20:00:00Z", 1.43, 1.44)]}
        started = dict(card, name="Card 3x", status="underway")
        late = dict(card, late=True)
        wide = dict(card, name="Card 3x", wide=True, stake=1)
        r = self.run_js(D, {"rules": {"card": {"book": "William Hill"}}, "record": {},
                            "days": [{"groups": [card, started, late, wide]}]})
        self.assertEqual(r["out"], [["edge", "Edge single", 1, 1.45], ["card", "Card 2x", 2, 1.99]])
        self.assertEqual(r["skip"], ["wide"])
        self.assertIn("Card 2x · 2 units (£20) · William Hill 1.99", r["slip"])
        self.assertIn("X to win v Other · 1.38", r["slip"])

    def test_nothing_open(self):
        r = self.run_js({"days": []}, {"rules": {}, "record": {}, "days": []})
        self.assertEqual(r["out"], []); self.assertEqual(r["skip"], [])


if __name__ == "__main__":
    unittest.main()
