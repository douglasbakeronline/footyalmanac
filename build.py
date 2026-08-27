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

SEASON = os.environ.get("ALMANAC_SEASON", "2026-27")
PREV = ["2025-26", "2024-25"]
CODES = list(E.LEAGUES.keys())

# Manual per-team adjustment on expected goals. 1.0 = no change.
# The model reads last season's results and nothing else, so it is blind to
# transfers, injuries and managerial change. This is the hook for that.
# Example: "Liverpool": {"att": 0.95, "def": 1.05, "why": "Slot sacked, squad unsettled"}
ADJUSTMENTS = {}
_HERE = os.path.dirname(os.path.abspath(__file__))
_ADJ_FILE = os.path.join(_HERE, "adjustments.json")
if os.path.exists(_ADJ_FILE):
    ADJUSTMENTS = json.load(open(_ADJ_FILE))

# Unavailable players, entered by hand. See absences.json and
# engine.absence_factors for how a squad list becomes a rating adjustment.
ABSENCES = {}
_ABS_FILE = os.path.join(_HERE, "absences.json")
if os.path.exists(_ABS_FILE):
    ABSENCES = {k: v for k, v in json.load(open(_ABS_FILE)).items()
                if not k.startswith("_")}


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
        {c: (None if E.LEAGUES[c].get("ratingsOnly") else E.LEAGUES[c].get("season", SEASON),
             [] if E.LEAGUES[c].get("cup") else E.LEAGUES[c].get("prev", PREV))
         for c in CODES}, cache_dir=args.cache)
    if missing:
        print(f"  no data for: {', '.join(sorted(missing))}", file=sys.stderr)

    # Where openfootball has nothing for a competition, try the live fallback.
    # European competitions are the reason this exists: the repo lags a season
    # behind, so UEFA ties would otherwise never appear.
    gaps = [c for c in CODES if c not in fixtures
            and not E.LEAGUES[c].get("ratingsOnly")]
    if gaps:
        got, tried = [], []
        for c in gaps:
            rows, ok = S.fetch_espn(c, start, end, log=tried)
            if ok:
                fixtures[c] = rows
                got.append(f"{c}({len(rows)})")
        # Log every attempt, not just the wins. A silent fallback that returns
        # nothing is indistinguishable from one that was never called, which
        # cost a day of debugging.
        for line in tried:
            print(f"    espn {line}", file=sys.stderr)
        print(f"  live fallback supplied: {', '.join(got) if got else 'nothing'}",
              file=sys.stderr)

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
        # Shrunk, not raw. A one-match sample must regress hard toward the
        # league average before it is allowed anywhere near a rating.
        cur_ratings[code] = E.strength_from_table(tbl) if played else {}

    rated_pool = set(last_league)

    def rating_for(team, code):
        """Prior (carried across divisions if needed) blended with this season."""
        src = last_league.get(team)
        if src is None:
            # A live-source club name may not match openfootball's spelling.
            alt = S.match_team(team, rated_pool)
            if alt:
                src = last_league.get(alt)
                team = alt
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
        out = (ABSENCES.get(team) or {}).get("out") or []
        abs_att, abs_def = E.absence_factors(out)
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
            "out": ([{"name": p.get("name", "unnamed"), "role": p.get("role", "midfield"),
                      "importance": p.get("importance", "key"), "why": p.get("why")}
                     for p in out] if out else None),
            "outFactors": ([round(abs_att, 3), round(abs_def, 3)] if out else None),
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
            # In a cup, a side keeps its own division's rating and the two are
            # converted into a shared frame. Rating it "in the cup" would be
            # meaningless: a cup has no table to be average in.
            # A side whose division cannot be resolved has no rating anyway, so
            # fall back to the cup's own code rather than inventing a division.
            # team_block will mark it unrated and the row will say so.
            h_src = last_league.get(r["home"]) if meta.get("cup") else None
            a_src = last_league.get(r["away"]) if meta.get("cup") else None
            h_league = h_src or code
            a_league = a_src or code
            hb, hr = team_block(r["home"], h_league)
            ab, ar = team_block(r["away"], a_league)
            fh = E.form_factor(hb["form"])
            fa = E.form_factor(ab["form"])
            adj_h = hb["adj"] or {}
            adj_a = ab["adj"] or {}
            oh = hb["outFactors"] or [1.0, 1.0]
            oa = ab["outFactors"] or [1.0, 1.0]
            rh = {"att": hr["att"] * adj_h.get("att", 1.0) * oh[0],
                  "def": hr["def"] * adj_h.get("def", 1.0) * oh[1]}
            ra = {"att": ar["att"] * adj_a.get("att", 1.0) * oa[0],
                  "def": ar["def"] * adj_a.get("def", 1.0) * oa[1]}
            if meta.get("cup"):
                s_h = E.LEAGUES[h_league]["strength"]
                s_a = E.LEAGUES[a_league]["strength"]
                cup_mu = (league_mu.get(h_league, 1.35) + league_mu.get(a_league, 1.35)) / 2
                p = E.cup_match(rh, s_h, ra, s_a, cup_mu,
                                tier=meta["tier"], form_h=fh, form_a=fa)
            else:
                p = E.match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                                          mu, tier=meta["tier"], form_h=fh, form_a=fa)

            evidence = "current" if min(hb["played"], ab["played"]) >= 6 else (
                "mixed" if max(hb["played"], ab["played"]) > 0 else "carryover")

            # Celtic's Law: declared before kick-off, never after.
            #
            # Some fixtures are ones the model is structurally blind to, and it
            # is possible to say which in advance. Backtesting 2025/26: fixtures
            # where a side had changed division hit 47.2% against 50.4% for
            # settled ones, and 43.8% against 48.8% inside the first ten games.
            # The probability is not wrong so much as less trustworthy, so the
            # row is marked rather than hidden.
            #
            # Applied afterwards to whatever the model got wrong, this would
            # explain everything and predict nothing. The flag only counts
            # because it is set before the result is known.
            reasons = []
            if meta.get("cup") and h_src and a_src and h_src != a_src:
                gap = abs(E.LEAGUES[h_src]["strength"] - E.LEAGUES[a_src]["strength"])
                if gap > 0.05:
                    reasons.append(
                        f"cup tie across divisions ({E.LEAGUES[h_src]['name']} v "
                        f"{E.LEAGUES[a_src]['name']}), priced entirely off league "
                        f"strength coefficients")
            for side, t in (("home", hb), ("away", ab)):
                if t["unrated"]:
                    reasons.append(f"{t['name']} has no rating on file")
                elif t["carriedFrom"]:
                    moved = E.LEAGUES[t["carriedFrom"]]
                    updown = "up from" if moved["tier"] > meta["tier"] else "down from"
                    reasons.append(f"{t['name']} came {updown} the {moved['name']}")
                if t["adj"]:
                    reasons.append(f"{t['name']} carries a manual override")
                if t["out"]:
                    n = len(t["out"])
                    big = [p["name"] for p in t["out"] if p["importance"] == "star"]
                    reasons.append(
                        f"{t['name']} {'is' if n == 1 else 'are'} missing {n} player{'' if n == 1 else 's'}"
                        + (f", including {', '.join(big)}" if big else ""))
            early = min(hb["played"], ab["played"]) < 10

            by_day[r["date"]].append({
                "league": code, "leagueName": meta["name"], "short": meta["short"],
                "country": meta["country"], "iso": meta["iso"],
                "tier": meta["tier"], "order": meta["order"], "round": r["round"],
                "date": r["date"], "time": r["time"],
                "home": hb, "away": ab,
                "p": {"h": round(p["home"], 4), "d": round(p["draw"], 4),
                      "a": round(p["away"], 4)},
                "xg": [round(p["xg_home"], 2), round(p["xg_away"], 2)],
                "btts": round(p["btts"], 4),
                "over25": round(p["over25"], 4),
                "score": list(p["likely_score"]),
                "confidence": round(p["confidence"], 4),
                "evidence": evidence,
                "unrated": hb["unrated"] or ab["unrated"],
                "celtic": ({"reasons": reasons, "early": early} if reasons else None),
            })

    # Backstop against the same fixture arriving from two competitions or two
    # sources. Keyed on the teams and the date, so a genuine two-legged tie on
    # different days still shows both legs.
    for d in by_day:
        seen, unique = set(), []
        for g in by_day[d]:
            key = (g["home"]["name"], g["away"]["name"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(g)
        by_day[d] = unique

    days = []
    for d in sorted(by_day):
        # A fixture with an unrated side can look confident purely because the
        # placeholder rating flatters the other team. Rank those last so they
        # never occupy the top of the slate.
        games = sorted(by_day[d], key=lambda g: (g["unrated"], -g["confidence"]))[:args.top]
        # Straight confidence order, most one-sided at the top of every day.
        games.sort(key=lambda g: -g["confidence"])
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

    # Archive what was predicted, so score.py can grade it once results land.
    # Without this the site can never say how it is actually doing.
    pred_dir = os.path.join(here, "predictions")
    os.makedirs(pred_dir, exist_ok=True)
    flat = [{"league": g["league"], "date": g["date"],
             "home": g["home"]["name"], "away": g["away"]["name"],
             "p": g["p"], "xg": g["xg"], "score": g["score"],
             "btts": g["btts"], "over25": g["over25"],
             "confidence": g["confidence"], "celtic": bool(g["celtic"]),
             "unrated": g["unrated"]}
            for d in days for g in d["games"]]
    with open(os.path.join(pred_dir, f"{start.isoformat()}.json"), "w") as f:
        json.dump(flat, f, separators=(",", ":"))

    out = args.out or os.path.join(here, "data.json")
    with open(out, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    # Emit a JS shim so index.html opens straight off the filesystem; a bare
    # fetch() of data.json is blocked by CORS on file:// URLs.
    # The live record, if score.py has run. Inlined the same way as the fixture
    # data so the dashboard stays a single self-contained file.
    rec_path = os.path.join(here, "record.json")
    record = None
    if os.path.exists(rec_path):
        try:
            record = json.load(open(rec_path))
        except Exception:
            record = None

    blob = json.dumps(payload, separators=(",", ":"))
    rec_blob = json.dumps(record, separators=(",", ":")) if record else "null"
    with open(os.path.join(here, "data.js"), "w") as f:
        f.write("window.__FIXTURE_DATA__=" + blob + ";window.__RECORD__=" + rec_blob + ";")

    # And emit a fully self-contained single file. Two files is one file too
    # many the moment anyone emails it, drops it in a preview pane, or opens it
    # somewhere the sibling script cannot be fetched.
    tpl_path = os.path.join(here, "index.html")
    if os.path.exists(tpl_path):
        tpl = open(tpl_path).read()
        inline = ('<script>window.__FIXTURE_DATA__=' + blob.replace("</", "<\\/")
                  + ';window.__RECORD__=' + rec_blob.replace("</", "<\\/") + ';</script>')
        html = tpl.replace('<script src="data.js"></script>', inline)
        with open(os.path.join(here, "dashboard.html"), "w") as f:
            f.write(html)
    total = sum(d["count"] for d in days)
    print(f"wrote {out}: {total} fixtures across {len(days)} days", file=sys.stderr)


if __name__ == "__main__":
    main()
