#!/usr/bin/env python3
"""Team news from API-Football for a backtest (19 Oct 2026). Changes nothing.

    python3 tools/af_team_news.py --fetch [--out audit-out/team-news]

Needs API_FOOTBALL_KEY (a GitHub secret: run it from a workflow; the 19 Oct
2026 run used a push-triggered workflow on a probe branch, since deleted).
API-Football's data is not for redistribution: keep the output out of the
public repo (audit-out/ is gitignored). For each
league and season below it saves, trimmed:

  coverage.json                      what the plan says it covers (injuries, line-ups, players)
  injuries-<code>-<season>.json      every player listed missing or doubtful for a fixture
  players-<code>-<season>.json       each player's league minutes and appearances that season

API-Football seasons are the starting year: 2025 is 2025-26. 2024 gives player
importance for 2025-26 without using anything from the season being predicted.
Paced under the plan's 5 calls a second; stops at the daily allowance. Never
prints the key or the account block. Standard library only.
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

BASE = "https://v3.football.api-sports.io"
LEAGUES = {"en.1": 39, "en.2": 40, "es.1": 140, "de.1": 78, "it.1": 135, "fr.1": 61, "nl.1": 88, "pt.1": 94}
SEASONS = (2024, 2025, 2026)
PACE = 0.25
CALLS = {"n": 0, "left": None}


def get(path, params):
    key = os.environ.get("API_FOOTBALL_KEY")
    if not key:
        sys.exit("API_FOOTBALL_KEY is not set")
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"x-apisports-key": key, "User-Agent": "footyalmanac-teamnews"})
    for attempt in range(5):
        time.sleep(PACE)
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            doc = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  retry {path} {params}: {type(e).__name__}", file=sys.stderr)
            time.sleep(2 + 2 * attempt)
            continue
        CALLS["n"] += 1
        left = resp.headers.get("x-ratelimit-requests-remaining")
        if left and left.isdigit():
            CALLS["left"] = int(left)
        errs = doc.get("errors")
        if errs:
            if "requests" in str(errs) and "rateLimit" not in str(errs):
                sys.exit(f"daily allowance used up after {CALLS['n']} calls")
            if "rateLimit" in str(errs):
                time.sleep(3 + 2 * attempt)
                continue
            print(f"  refused {path} {params}: {errs}", file=sys.stderr)
            return None
        return doc
    print(f"  gave up on {path} {params}", file=sys.stderr)
    return None


def save(out, name, obj):
    with open(os.path.join(out, name), "w") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)


def coverage(out):
    cov = {}
    for code, lid in LEAGUES.items():
        doc = get("/leagues", {"id": lid}) or {}
        for item in doc.get("response") or []:
            for s in item.get("seasons") or []:
                if s.get("year") in SEASONS:
                    c = s.get("coverage") or {}
                    cov[f"{code}-{s['year']}"] = {
                        "league": (item.get("league") or {}).get("name"),
                        "start": s.get("start"), "end": s.get("end"),
                        "injuries": c.get("injuries"), "players": c.get("players"),
                        "lineups": (c.get("fixtures") or {}).get("lineups"),
                        "statistics_players": (c.get("fixtures") or {}).get("statistics_players")}
    save(out, "coverage.json", cov)
    return cov


def injuries(out, code, lid, season):
    doc = get("/injuries", {"league": lid, "season": season}) or {}
    rows = []
    for r in doc.get("response") or []:
        p, t, fx = r.get("player") or {}, r.get("team") or {}, r.get("fixture") or {}
        rows.append({"fixture": fx.get("id"), "date": (fx.get("date") or "")[:10], "team": t.get("name"),
                     "teamId": t.get("id"), "player": p.get("name"), "playerId": p.get("id"),
                     "type": p.get("type"), "reason": p.get("reason")})
    save(out, f"injuries-{code}-{season}.json", rows)
    return len(rows)


def players(out, code, lid, season):
    rows, page, pages = [], 1, 1
    while page <= pages:
        doc = get("/players", {"league": lid, "season": season, "page": page})
        if not doc:
            break
        pages = (doc.get("paging") or {}).get("total") or 1
        for r in doc.get("response") or []:
            p = r.get("player") or {}
            for st in r.get("statistics") or []:
                if (st.get("league") or {}).get("id") != lid:
                    continue
                g, t = st.get("games") or {}, st.get("team") or {}
                rows.append({"playerId": p.get("id"), "player": p.get("name"), "team": t.get("name"),
                             "teamId": t.get("id"), "minutes": g.get("minutes") or 0,
                             "apps": g.get("appearences") or 0, "lineups": g.get("lineups") or 0,
                             "position": g.get("position")})
        page += 1
    save(out, f"players-{code}-{season}.json", rows)
    return len(rows), pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--out", default=os.path.join("audit-out", "team-news"))
    args = ap.parse_args()
    if not args.fetch:
        ap.error("pass --fetch")
    os.makedirs(args.out, exist_ok=True)
    cov = coverage(args.out)
    for k, v in sorted(cov.items()):
        print(f"coverage {k}: injuries {v['injuries']}, players {v['players']}, lineups {v['lineups']}")
    summary = {}
    for code, lid in LEAGUES.items():
        for season in SEASONS:
            n_inj = injuries(args.out, code, lid, season) if season >= 2025 else 0
            n_pl, pages = players(args.out, code, lid, season) if season <= 2025 else (0, 0)
            summary[f"{code}-{season}"] = {"injuries": n_inj, "players": n_pl, "playerPages": pages}
            print(f"{code} {season}: {n_inj} injury rows, {n_pl} player rows ({pages} pages); calls {CALLS['n']}, left {CALLS['left']}")
    save(args.out, "summary.json", {"calls": CALLS["n"], "left": CALLS["left"], "rows": summary})


if __name__ == "__main__":
    main()
