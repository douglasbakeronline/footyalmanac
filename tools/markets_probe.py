#!/usr/bin/env python3
"""Which football markets API-Football prices, and under what names
(14 Nov 2026). Advisory: changes nothing in the site, writes one report.

The cloud session cannot reach API-Football; CI can. Records bet ids and
names, each bet's value labels, how many fixtures and bookmakers carry it and
which UK books do, and the paging totals with and without a bet filter (the
cost in calls). Never a price, a key or an account detail (the report is
public). About 14 calls. Standard library only.
"""
import json, os, sys, time, urllib.request
from datetime import date, timedelta

HOST = "https://v3.football.api-sports.io"
UK = {"bet365", "williamhill", "betfair", "paddypower", "betway", "unibet", "ladbrokes", "coral", "betfred", "skybet", "betvictor", "888sport"}


def get(path, key):
    req = urllib.request.Request(HOST + path, headers={"x-apisports-key": key, "User-Agent": "footyalmanac markets probe"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"[:200]}


def norm(n): return str(n or "").replace(" ", "").replace("-", "").replace(".", "").lower()


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "probe/markets-probe.json"
    key = os.environ.get("API_FOOTBALL_KEY")
    rep = {"run": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if not key:
        rep["error"] = "no key"
    else:
        d = get("/odds/bets", key)
        rep["bets"] = [{"id": b.get("id"), "name": b.get("name")} for b in d.get("response") or []] or d.get("error") or d.get("errors")
        d = get("/odds/bookmakers", key)
        rep["bookmakers"] = [{"id": b.get("id"), "name": b.get("name")} for b in d.get("response") or []] or d.get("error") or d.get("errors")
        rep["days"] = {}
        for off in (0, 1):
            day = (date.today() + timedelta(days=off)).isoformat()
            dd = {"paging": {}}
            agg = {}
            for page in (1, 2):
                d = get(f"/odds?date={day}&page={page}", key)
                dd["paging"]["all"] = d.get("paging") or d.get("error") or d.get("errors")
                for item in d.get("response") or []:
                    seen = {}
                    for bk in item.get("bookmakers") or []:
                        for bet in bk.get("bets") or []:
                            k = f"{bet.get('id')}|{bet.get('name')}"
                            a = agg.setdefault(k, {"fixtures": 0, "maxBooks": 0, "ukBooks": set(), "labels": set()})
                            s = seen.setdefault(k, set()); s.add(bk.get("name"))
                            if norm(bk.get("name")) in UK: a["ukBooks"].add(bk.get("name"))
                            for v in bet.get("values") or []:
                                if len(a["labels"]) < 60: a["labels"].add(str(v.get("value")))
                    for k, s in seen.items():
                        agg[k]["fixtures"] += 1; agg[k]["maxBooks"] = max(agg[k]["maxBooks"], len(s))
                dd["fixturesRead"] = dd.get("fixturesRead", 0) + len(d.get("response") or [])
            for bet in (1, 5, 8, 12, 24, 25):
                d = get(f"/odds?date={day}&bet={bet}&page=1", key)
                dd["paging"][f"bet{bet}"] = d.get("paging") or d.get("error") or d.get("errors")
                r = d.get("response") or []
                names = {b2.get("name") for it in r for bk in it.get("bookmakers") or [] for b2 in bk.get("bets") or []}
                dd.setdefault("betNameById", {})[str(bet)] = sorted(n for n in names if n)
            dd["bets"] = {k: {"fixtures": a["fixtures"], "maxBooks": a["maxBooks"], "ukBooks": sorted(a["ukBooks"]),
                              "labels": sorted(a["labels"])} for k, a in sorted(agg.items(), key=lambda kv: -kv[1]["fixtures"])}
            rep["days"][day] = dd
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rep, f, indent=1)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
