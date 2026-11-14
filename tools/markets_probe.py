#!/usr/bin/env python3
"""Which leagues William Hill prices for win and both teams to score over the
coming week, and which bets API-Sports lists for the other sports (14 Nov 2026).
Advisory: league and bet names and counts only, never a price or a key."""
import json, os, sys, time, urllib.request
from datetime import date, timedelta

def get(host, path, key):
    req = urllib.request.Request(f"https://{host}{path}", headers={"x-apisports-key": key, "User-Agent": "footyalmanac markets probe"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"[:200]}

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "probe/markets-probe.json"
    key = os.environ.get("API_FOOTBALL_KEY")
    rep = {"run": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if not key:
        rep["error"] = "no key"
    else:
        F = "v3.football.api-sports.io"
        rep["hill"] = {}
        for off in range(0, 9):
            day = (date.today() + timedelta(days=off)).isoformat()
            dd = {}
            for bet, lab in ((24, "wbtts"), (8, "btts")):
                leagues, page, total, fixtures = {}, 1, 1, 0
                while page <= min(total, 12 if bet == 24 else 3):
                    d = get(F, f"/odds?date={day}&bookmaker=7&bet={bet}&page={page}", key)
                    total = int((d.get("paging") or {}).get("total") or 1)
                    for it in d.get("response") or []:
                        has = any(b2.get("id") == bet for bk in it.get("bookmakers") or [] for b2 in bk.get("bets") or [])
                        if not has: continue
                        lg = it.get("league") or {}
                        k = f"{lg.get('id')}|{lg.get('country')}|{lg.get('name')}"
                        leagues[k] = leagues.get(k, 0) + 1; fixtures += 1
                    if d.get("error") or d.get("errors"):
                        dd[lab + "Error"] = d.get("error") or d.get("errors"); break
                    page += 1
                dd[lab] = {"pages": total, "fixtures": fixtures, "leagues": dict(sorted(leagues.items(), key=lambda kv: -kv[1]))}
            rep["hill"][day] = dd
        rep["sports"] = {}
        for sp, host in (("basketball", "v1.basketball.api-sports.io"), ("american-football", "v1.american-football.api-sports.io"),
                         ("rugby", "v1.rugby.api-sports.io"), ("hockey", "v1.hockey.api-sports.io")):
            b = get(host, "/odds/bets", key); k = get(host, "/odds/bookmakers", key)
            rep["sports"][sp] = {"bets": [x.get("name") for x in b.get("response") or []][:80] or b.get("error") or b.get("errors"),
                                 "bookmakers": [x.get("name") for x in k.get("response") or []][:60] or k.get("error") or k.get("errors")}
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rep, f, indent=1)
    print("wrote", out_path)

if __name__ == "__main__":
    main()
