#!/usr/bin/env python3
"""
Which free price sources can price which sports (25 Oct 2026). Advisory:
changes nothing in the site, writes one report.

    API_FOOTBALL_KEY=... python3 tools/odds_probe.py audit-out/odds-probe.json

Douglas: "scope a few different free sources, let's utilise what we can".
The cloud session cannot reach these hosts; CI can. For each source it
records whether it answers, how many games it lists for today and tomorrow,
how many of those carry a match-winner price, and the field names of one
priced record, so the integration can be written against what the source
really returns. It never records prices themselves, account details or keys
(the report is public).

Sources:
  api-sports   rugby, basketball, hockey, baseball, american-football,
               handball, volleyball, with the API-Football key: the same
               account; each product has its own free daily allowance
  pinnwire     Pinnacle prices, 13 sports, the public demo key (50 calls a
               day, 10 a minute); the docs are fetched so the endpoints can
               be read
  espn         rugby scoreboards (do they carry odds?) and NBA a few days out

Standard library only. About 40 calls in all.
"""
import json, os, sys, time, urllib.error, urllib.request
from datetime import date, timedelta

UA = {"User-Agent": "Mozilla/5.0 (footyalmanac odds probe)"}
TODAY = date.today()
DAYS = [TODAY, TODAY + timedelta(days=1)]
API_SPORTS = {
    "rugby": "v1.rugby.api-sports.io",
    "basketball": "v1.basketball.api-sports.io",
    "hockey": "v1.hockey.api-sports.io",
    "baseball": "v1.baseball.api-sports.io",
    "american-football": "v1.american-football.api-sports.io",
    "handball": "v1.handball.api-sports.io",
    "volleyball": "v1.volleyball.api-sports.io",
}


def get(url, headers=None, raw=False, timeout=30):
    req = urllib.request.Request(url, headers=dict(UA, **(headers or {})))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, (body.decode("utf-8", "replace") if raw else json.loads(body))
    except urllib.error.HTTPError as e:
        try: body = e.read().decode("utf-8", "replace")[:300]
        except Exception: body = ""
        return e.code, body
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"[:300]


def shape(x, depth=0):
    """Field names and types of a record, no values (prices stay out)."""
    if depth > 4: return "..."
    if isinstance(x, dict): return {k: shape(v, depth + 1) for k, v in list(x.items())[:25]}
    if isinstance(x, list): return [shape(x[0], depth + 1)] if x else []
    return type(x).__name__


def api_sports(key):
    out = {}
    for sport, host in API_SPORTS.items():
        rep = {"host": host}
        h = {"x-apisports-key": key}
        st, d = get(f"https://{host}/status", h)
        if isinstance(d, dict):
            r = d.get("response") or {}
            rep["status"] = st
            rep["errors"] = d.get("errors") or None
            rep["plan"] = (r.get("subscription") or {}).get("plan") if isinstance(r, dict) else None
            rep["requests"] = r.get("requests") if isinstance(r, dict) else None
        else:
            rep["status"], rep["error"] = st, d
            out[sport] = rep; continue
        games = []
        for dd in DAYS:
            st, d = get(f"https://{host}/games?date={dd.isoformat()}", h)
            n = len(d.get("response") or []) if isinstance(d, dict) else None
            rep[f"games_{dd.isoformat()}"] = n
            if isinstance(d, dict): games += d.get("response") or []
            if isinstance(d, dict) and d.get("errors"): rep[f"games_errors_{dd.isoformat()}"] = d.get("errors")
        # odds: by date first (one call), else by game for three games
        st, d = get(f"https://{host}/odds?date={DAYS[0].isoformat()}", h)
        if isinstance(d, dict):
            rep["odds_by_date"] = {"status": st, "results": d.get("results"), "errors": d.get("errors") or None,
                                   "paging": d.get("paging")}
            items = d.get("response") or []
            if items: rep["odds_shape"] = shape(items[0])
            rep["odds_bets_named"] = sorted({b.get("name") for it in items[:20] for bk in it.get("bookmakers") or []
                                             for b in bk.get("bets") or [] if b.get("name")})[:20]
            rep["odds_books"] = sorted({bk.get("name") for it in items[:50] for bk in it.get("bookmakers") or []})[:40]
        else:
            rep["odds_by_date"] = {"status": st, "error": d}
        if not rep.get("odds_shape"):
            priced = 0
            for g in games[:3]:
                gid = (g.get("id") or (g.get("game") or {}).get("id"))
                if not gid: continue
                st, d = get(f"https://{host}/odds?game={gid}", h)
                items = d.get("response") or [] if isinstance(d, dict) else []
                if items:
                    priced += 1
                    rep.setdefault("odds_shape", shape(items[0]))
            rep["odds_by_game_priced_of_3"] = priced
        if games: rep["game_shape"] = shape(games[0])
        out[sport] = rep
        time.sleep(1)
    return out


def pinnwire():
    rep = {}
    for path in ("/llms.txt", "/llms-full.txt"):
        st, txt = get("https://pinnwire.com" + path, raw=True)
        rep[path] = {"status": st, "text": txt[:12000] if isinstance(txt, str) else None}
    # Best guesses at the REST paths from the public docs page; recorded
    # either way so the next step is written against what answers.
    for path in ("/kit/v1/health", "/kit/v1/sports", "/kit/v1/markets?sport=tennis&key=demo",
                 "/kit/v1/prematch_fixtures?sport=tennis&key=demo", "/kit/v1/markets?sport=rugby&key=demo"):
        st, d = get("https://pinnwire.com" + path)
        rep[path] = {"status": st, "shape": shape(d) if isinstance(d, (dict, list)) else (d[:300] if isinstance(d, str) else None)}
        time.sleep(7)
    return rep


def espn():
    rep = {}
    base = "https://site.api.espn.com/apis/site/v2/sports"
    span = f"{TODAY.strftime('%Y%m%d')}-{(TODAY + timedelta(days=7)).strftime('%Y%m%d')}"
    for slug in ("rugby/267979", "rugby/270557", "rugby/270559", "rugby/289234"):   # Premiership, URC, Top 14, Tests
        st, d = get(f"{base}/{slug}/scoreboard?dates={span}")
        evs = d.get("events") or [] if isinstance(d, dict) else []
        rep[slug] = {"status": st, "events": len(evs),
                     "with_odds": sum(1 for e in evs if ((e.get("competitions") or [{}])[0].get("odds")))}
    for k in range(0, 4):
        dd = (TODAY + timedelta(days=k)).strftime("%Y%m%d")
        st, d = get(f"{base}/basketball/nba/scoreboard?dates={dd}")
        evs = d.get("events") or [] if isinstance(d, dict) else []
        rep[f"nba_{dd}"] = {"events": len(evs), "with_odds": sum(1 for e in evs if ((e.get("competitions") or [{}])[0].get("odds")))}
    return rep


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "audit-out/odds-probe.json"
    key = os.environ.get("API_FOOTBALL_KEY")
    rep = {"run": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "days": [d.isoformat() for d in DAYS]}
    rep["api_sports"] = api_sports(key) if key else "no key"
    rep["pinnwire"] = pinnwire()
    rep["espn"] = espn()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rep, f, indent=1)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
