#!/usr/bin/env python3
"""
Build the dashboard payload.

    python3 build.py --days 4 --top 50

Reads openfootball, rates every team, prices every upcoming fixture, keeps the
top N by confidence per day, writes data.json next to index.html.
"""
import argparse, json, os, sys
from collections import defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

SEASON = "2026-27"
PREV = ["2025-26", "2024-25"]
CODES = list(E.LEAGUES.keys())

# Manual per-team adjustment on expected goals. 1.0 = no change.
# The model reads last season's results and nothing else, so it is blind to
# transfers, injuries and managerial change. This is the hook for that.
# Example: "Liverpool": {"att": 0.95, "def": 1.05, "why": "Slot sacked, squad unsettled"}
ADJUSTMENTS = {}
_ADJ_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adjustments.json")
if os.path.exists(_ADJ_FILE):
    ADJUSTMENTS = json.load(open(_ADJ_FILE))


def prev_of(code):
    return E.LEAGUES[code].get("prev", PREV)


def team_pool(history, fixtures):
    """Work out which competition each team played in last season, so promoted
    and relegated sides can have their ratings carried across divisions."""
    last_league = {}
    for code, seasons in history.items():
        p0 = prev_of(code)[0]
        for t in {m[1] for m in seasons.get(p0, [])} | {m[2] for m in seasons.get(p0, [])}:
            last_league[t] = code
    return last_league


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=4, help="days of fixtures to include")
    ap.add_argument("--top", type=int, default=50, help="fixtures kept per day")
    ap.add_argument("--from", dest="start", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cache", default=None, help="directory to cache raw downloads")
    args = ap.parse_args()

    start = date.fromisoformat(args.start) if args.start else date.today()
    end = start + timedelta(days=args.days - 1)

    print(f"fetching {len(CODES)} competitions ...", file=sys.stderr)
    # Not every league runs August-to-May. Brazil and the Nordics use a calendar
    # year, so the season strings are per-competition rather than global.
    history, fixtures, missing = S.fetch_all_seasons(
        {c: (E.LEAGUES[c].get("season", SEASON), E.LEAGUES[c].get("prev", PREV))
         for c in CODES}, cache_dir=args.cache)
    if missing:
        print(f"  no data for: {', '.join(sorted(missing))}", file=sys.stderr)

    last_league = team_pool(history, fixtures)

    # ---- ratings -----------------------------------------------------------
    prior_ratings, prior_tables, league_mu = {}, {}, {}
    for code, seasons in history.items():
        pv = prev_of(code)
        ms = seasons.get(pv[0]) or seasons.get(pv[1]) or []
        if not ms:
            continue
        tbl = E.build_table(ms)
        prior_tables[code] = tbl
        prior_ratings[code] = E.strength_from_table(tbl)
        league_mu[code] = E.league_goal_rate(tbl)

    # current-season tables, from whatever has been played so far
    cur_tables, cur_ratings = {}, {}
    for code, rows in fixtures.items():
        played = [(r["date"], r["home"], r["away"], r["hg"], r["ag"])
                  for r in rows if r["hg"] is not None]
        tbl = E.build_table(played)
        cur_tables[code] = tbl
        cur_ratings[code] = E.strength_from_table(tbl, k=0.0) if played else {}

    def rating_for(team, code):
        """Prior (carried across divisions if needed) blended with this season."""
        src = last_league.get(team)
        if src and src in prior_ratings and team in prior_ratings[src]:
            prior = E.transfer_rating(prior_ratings[src][team], src, code)
            carried = (src != code)
        else:
            prior = {"att": 1.0, "def": 1.0}
            carried = None
        row = cur_tables.get(code, {}).get(team)
        played = row["P"] if row else 0
        cur = cur_ratings.get(code, {}).get(team)
        return E.blend(prior, cur, played), carried, played, src

    def team_block(team, code):
        rating, carried, played, src = rating_for(team, code)
        prow = prior_tables.get(src, {}).get(team) if src else None
        crow = cur_tables.get(code, {}).get(team)
        fp = E.form_points(crow)
        adj = ADJUSTMENTS.get(team, {})
        return {
            "name": team,
            "att": round(rating["att"], 3),
            "def": round(rating["def"], 3),
            "played": played,
            # No prior season on file and nothing played yet: the 1.00/1.00
            # rating is a placeholder, not a judgement. Usually a side promoted
            # from a division this build does not cover.
            "unrated": (prow is None and played == 0),
            "carriedFrom": src if carried else None,
            "form": fp,
            "adj": {"att": adj.get("att", 1.0), "def": adj.get("def", 1.0),
                    "why": adj.get("why")} if adj else None,
            "last": ({"P": prow["P"], "W": prow["W"], "D": prow["D"], "L": prow["L"],
                      "GF": prow["GF"], "GA": prow["GA"], "GD": prow["GD"],
                      "Pts": prow["Pts"], "PPG": prow["PPG"]} if prow else None),
            "now": ({"P": crow["P"], "W": crow["W"], "D": crow["D"], "L": crow["L"],
                     "GF": crow["GF"], "GA": crow["GA"], "GD": crow["GD"],
                     "Pts": crow["Pts"], "PPG": crow["PPG"]} if crow and crow["P"] else None),
        }, rating

    # ---- price the fixtures ------------------------------------------------
    by_day = defaultdict(list)
    for code, rows in fixtures.items():
        meta = E.LEAGUES[code]
        mu = league_mu.get(code, 1.35)
        for r in rows:
            if r["hg"] is not None:
                continue
            d = date.fromisoformat(r["date"])
            if not (start <= d <= end):
                continue
            hb, hr = team_block(r["home"], code)
            ab, ar = team_block(r["away"], code)
            fh = E.form_factor(hb["form"])
            fa = E.form_factor(ab["form"])
            adj_h = hb["adj"] or {}
            adj_a = ab["adj"] or {}
            p = E.match_probabilities(
                hr["att"] * adj_h.get("att", 1.0), hr["def"] * adj_h.get("def", 1.0),
                ar["att"] * adj_a.get("att", 1.0), ar["def"] * adj_a.get("def", 1.0),
                mu, tier=meta["tier"], form_h=fh, form_a=fa)

            evidence = "current" if min(hb["played"], ab["played"]) >= 6 else (
                "mixed" if max(hb["played"], ab["played"]) > 0 else "carryover")

            by_day[r["date"]].append({
                "league": code, "leagueName": meta["name"], "short": meta["short"],
                "country": meta["country"], "iso": meta["iso"],
                "tier": meta["tier"], "order": meta["order"], "round": r["round"],
                "date": r["date"], "time": r["time"],
                "home": hb, "away": ab,
                "p": {"h": round(p["home"], 4), "d": round(p["draw"], 4),
                      "a": round(p["away"], 4)},
                "xg": [round(p["xg_home"], 2), round(p["xg_away"], 2)],
                "score": list(p["likely_score"]),
                "confidence": round(p["confidence"], 4),
                "evidence": evidence,
                "unrated": hb["unrated"] or ab["unrated"],
            })

    days = []
    for d in sorted(by_day):
        # A fixture with an unrated side can look confident purely because the
        # placeholder rating flatters the other team. Rank those last so they
        # never occupy the top of the slate.
        games = sorted(by_day[d], key=lambda g: (g["unrated"], -g["confidence"]))[:args.top]
        games.sort(key=lambda g: (g["order"], -g["confidence"]))
        for i, g in enumerate(sorted(games, key=lambda g: -g["confidence"]), 1):
            g["rank"] = i
        days.append({"date": d, "count": len(games), "games": games})

    payload = {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "season": SEASON,
        "window": {"from": start.isoformat(), "to": end.isoformat()},
        "topPerDay": args.top,
        "leagues": [{"code": c, **E.LEAGUES[c],
                     "haveFixtures": c in fixtures,
                     "haveHistory": c in prior_ratings} for c in CODES],
        "missing": sorted(missing),
        "days": days,
        "model": {
            "blendK": E.BLEND_K, "formCap": E.FORM_MAX, "rho": E.RHO, "temperature": E.TEMPERATURE,
            "homeMult": E.HOME_MULT, "awayMult": E.AWAY_MULT,
        },
    }

    here = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(here, "data.json")
    with open(out, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    # Emit a JS shim so index.html opens straight off the filesystem; a bare
    # fetch() of data.json is blocked by CORS on file:// URLs.
    blob = json.dumps(payload, separators=(",", ":"))
    with open(os.path.join(here, "data.js"), "w") as f:
        f.write("window.__FIXTURE_DATA__=" + blob + ";")

    # And emit a fully self-contained single file. Two files is one file too
    # many the moment anyone emails it, drops it in a preview pane, or opens it
    # somewhere the sibling script cannot be fetched.
    tpl_path = os.path.join(here, "index.html")
    if os.path.exists(tpl_path):
        tpl = open(tpl_path).read()
        inline = '<script>window.__FIXTURE_DATA__=' + blob.replace("</", "<\\/") + ';</script>'
        html = tpl.replace('<script src="data.js"></script>', inline)
        with open(os.path.join(here, "dashboard.html"), "w") as f:
            f.write(html)
    total = sum(d["count"] for d in days)
    print(f"wrote {out}: {total} fixtures across {len(days)} days", file=sys.stderr)


if __name__ == "__main__":
    main()
