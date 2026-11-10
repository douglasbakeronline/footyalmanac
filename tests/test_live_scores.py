"""Live scores on started Daily List picks (10 Nov 2026): the page reads
ESPN's public scoreboard for each started pick. These tests check the
pinned item carries its ESPN feed and, where node is available, that the
page's parser and the ahead / behind read work on an ESPN-shaped payload."""
import json, os, re, shutil, subprocess, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import daylist


class PinnedFeed(unittest.TestCase):
    def test_sport_item_keeps_the_feed(self):
        g = {"id": "401", "when": "2026-11-10T00:30Z", "home": "A", "away": "B", "pick": "A",
             "confidence": 0.9, "feed": "basketball/mens-college-basketball", "sport": "ncaab"}
        self.assertEqual(daylist.sport_item(g)["feed"], "basketball/mens-college-basketball")


def page_functions():
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    start = src.index("function parseScoreboard(d){")
    end = src.index("function livePaint(el, g){")
    return src[start:end]


@unittest.skipUnless(shutil.which("node"), "node not installed")
class PageParser(unittest.TestCase):
    def run_js(self, payload, picks):
        js = page_functions() + f"""
const s = parseScoreboard({json.dumps(payload)});
const picks = {json.dumps(picks)};
console.log(JSON.stringify({{s, reads: picks.map(g => liveRead(g, s[String(g.id)]))}}));
"""
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
        return json.loads(out)

    def event(self, eid, state, hs, as_, done=False, detail="2nd 10:00"):
        return {"id": eid, "competitions": [{"status": {"type": {"state": state, "completed": done, "shortDetail": detail}},
                "competitors": [{"homeAway": "home", "score": str(hs), "team": {"displayName": "Home U"}},
                                {"homeAway": "away", "score": str(as_), "team": {"displayName": "Away U"}}]}]}

    def test_reads_ahead_behind_final_and_pre(self):
        payload = {"events": [self.event(1, "in", 40, 30), self.event(2, "in", 40, 30),
                              self.event(3, "post", 60, 70, done=True, detail="Final"), self.event(4, "pre", 0, 0)]}
        r = self.run_js(payload, [{"id": 1, "side": "h"}, {"id": 2, "side": "a"}, {"id": 3, "side": "a"},
                                  {"id": 4, "side": "h"}, {"id": 5, "side": "h"}])
        self.assertEqual(r["s"]["1"]["home"], {"name": "Home U", "score": 40})
        lead = [x and [x["lead"], x["final"], x["score"]] for x in r["reads"]]
        self.assertEqual(lead, [["ahead", False, "40–30"], ["behind", False, "40–30"], ["ahead", True, "60–70"], None, None])

    def test_ignores_malformed_events(self):
        r = self.run_js({"events": [{"id": 9, "competitions": [{"competitors": []}]}]}, [{"id": 9, "side": "h"}])
        self.assertEqual(r["s"], {}); self.assertEqual(r["reads"], [None])


if __name__ == "__main__":
    unittest.main()
