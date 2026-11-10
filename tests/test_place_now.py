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
const localDay = iso => new Date(iso).toLocaleDateString("en-CA", {timeZone: "Europe/London"});
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

    def test_edge_double_from_the_two_most_likely_of_a_day(self):
        g = lambda h, when, fair, best: {"kickoff": when, "leagueName": "L", "home": {"name": h}, "away": {"name": "Z"},
                                         "edge": {"side": "h", "odds": best - 0.05, "best": best, "opp": 10, "fair": fair, "model": fair}}
        D = {"days": [{"games": [g("A", "2026-11-10T12:00:00Z", 0.70, 1.40), g("B", "2026-11-10T15:00:00Z", 0.80, 1.25),
                                 g("C", "2026-11-10T17:00:00Z", 0.75, 1.30), g("D", "2026-11-11T15:00:00Z", 0.9, 1.10)]}]}
        r = self.run_js(D, {"rules": {}, "record": {}, "days": []})
        doubles = [o for o in r["out"] if o[1] == "Edge double"]
        self.assertEqual(doubles, [["edge", "Edge double", 1, 1.63]])   # B and C; D is alone on its day
        self.assertEqual(sum(o[1] == "Edge single" for o in r["out"]), 4)

    def test_the_plan_names_three_rungs_and_leaves_the_rest_out(self):
        js = STUBS + "const window = {};\nconst D = {days: []}, OG = {rules: {card: {book: 'William Hill'}}, record: {card: {settled: 35, won: 11, staked: 35, returned: 30.72}}, days: []};\n" \
            + page_functions() + "console.log(JSON.stringify({rungs: planRungs().map(r => [r.name, r.v]), html: signalsPanel()}));"
        r = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
        self.assertEqual(r["rungs"], [["Edge singles", "Tested"], ["Edge double", "Tested"], ["The Card", "On trial"]])
        self.assertIn("live 11 of 35, -12.2%", r["html"])
        self.assertIn("No bet", r["html"])
        self.assertIn("not in the plan", r["html"])


if __name__ == "__main__":
    unittest.main()
