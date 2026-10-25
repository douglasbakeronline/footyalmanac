#!/usr/bin/env python3
"""Why API-Sports matched no NBA legs (25 Oct 2026). Loads the build's legs,
fetches API-Basketball games for their dates, and reports for each leg the
closest game names and kick-off gap. Team names and times only (public)."""
import json, os, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G
from difflib import SequenceMatcher

key = os.environ["API_FOOTBALL_KEY"]
today = datetime.now(timezone.utc).date()
dates = {(today + timedelta(days=i)).isoformat() for i in range(4)}
L = [l for l in G.legs(dates) if l["sport"] in ("nba", "rugby", "nfl")]
out = {"legs": len(L), "rows": []}
games = {}
for l in L[:20]:
    host = G.AS_HOST[l["sport"]]
    t = G.parse(l.get("when"))
    dd = (t.date().isoformat() if t else l["date"])
    k = (host, dd)
    if k not in games:
        d = G.get(f"https://{host}/games?date={dd}", {"x-apisports-key": key})
        games[k] = d.get("response") or []
        out.setdefault("calls", []).append({"host": host, "date": dd, "games": len(games[k]), "errors": d.get("errors") or None,
                                            "sample": [{"date": g.get("date"), "ts": g.get("timestamp"), "league": (g.get("league") or {}).get("name"),
                                                        "home": ((g.get("teams") or {}).get("home") or {}).get("name"),
                                                        "away": ((g.get("teams") or {}).get("away") or {}).get("name")} for g in games[k][:3]]})
    best = []
    for g in games[k]:
        tm = g.get("teams") or {}
        h, a = (tm.get("home") or {}).get("name", ""), (tm.get("away") or {}).get("name", "")
        sc = SequenceMatcher(None, G.norm(h), G.norm(l["home"])).ratio() + SequenceMatcher(None, G.norm(a), G.norm(l["away"])).ratio()
        best.append((sc, h, a, g.get("date"), g.get("timestamp"), (g.get("league") or {}).get("name")))
    best.sort(reverse=True)
    out["rows"].append({"sport": l["sport"], "leg": [l["home"], l["away"], l.get("when"), l["date"]], "top": best[:2]})
os.makedirs("probe", exist_ok=True)
json.dump(out, open("probe/match-probe.json", "w"), indent=1, default=str)
print("ok")
