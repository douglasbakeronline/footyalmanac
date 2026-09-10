#!/usr/bin/env python3
"""
Give the competitions openfootball does not carry a past season to be rated on.

    python3 backfill.py --probe                which slugs actually answer
    python3 backfill.py --season 2025          walk a season into history/
    python3 backfill.py --season 2025 --only us.1,mx.1,ar.1

The problem
-----------
openfootball's current-season coverage stops at ten European leagues plus
Brazil. Everything else on the board — MLS, Liga MX, the Nordics, the J-League —
comes from the live scoreboard, which serves one date at a time and has no
"give me the season" call.

Fixtures are fine that way, because the board only ever looks a few days ahead.
Ratings are not: a side with no prior season gets a placeholder 1.00/1.00, is
flagged unrated, and its fixture is priced off nothing. So a season has to be
walked date by date, once, and the result committed. Roughly 300 requests per
competition, which is a lot to do once and out of the question every morning.

sources.fetch_season reads history/<code>-<season>.json before it goes near the
network, so a backfilled competition costs the daily build nothing.

On the slugs
------------
They were written somewhere that could not reach the live source, so some of
them are wrong. --probe is how you find out which: it asks each one for a date
that should be busy and reports what came back. A slug that answers nothing is
either wrong or out of season, and the two look identical from here, so it
prints enough for you to tell them apart.

A wrong slug is not dangerous. It returns nothing, the competition does not
appear, and the board is exactly as it was before.
"""
import argparse, json, os, sys, time
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(HERE, "history")

# Competitions that have no openfootball path at all. Everything else already
# has a history and does not need walking.
def live_codes():
    return [c for c, m in E.LEAGUES.items() if m.get("live")]


def season_window(code, season):
    """The calendar range a season string covers.

    A calendar-year league ("2026") runs January to December. A split-year one
    ("2026-27") runs July to June. Both are drawn wide by a month at each end,
    because play-offs and rearranged fixtures do not respect the boundary.
    """
    if "-" in season:
        y = int(season.split("-")[0])
        return date(y, 6, 1), date(y + 1, 7, 31)
    y = int(season)
    return date(y, 1, 1), date(y, 12, 31)


def walk(code, season, sleep=0.15, verbose=True):
    """Every completed match of one season, one date at a time."""
    start, end = season_window(code, season)
    end = min(end, date.today() - timedelta(days=1))
    if start > end:
        return []
    rows, seen, errors = [], set(), 0
    day, n_days = start, (end - start).days + 1
    while day <= end:
        got, ok = S.fetch_espn(code, day, day, log=None)
        if not ok:
            errors += 1
        for r in got:
            if r["hg"] is None:
                continue
            key = (r["date"], r["home"], r["away"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({"date": r["date"], "home": r["home"], "away": r["away"],
                         "hg": r["hg"], "ag": r["ag"]})
        if verbose and day.day == 1:
            print(f"    {day.isoformat()}  {len(rows)} matches so far", file=sys.stderr)
        day += timedelta(days=1)
        # The scoreboard is a public endpoint with no published rate limit.
        # A short pause is the polite way to ask for three hundred days of it.
        time.sleep(sleep)
    if verbose:
        print(f"  {code} {season}: {len(rows)} matches across {n_days} days"
              f"{f', {errors} days returned nothing' if errors else ''}", file=sys.stderr)
    return rows


def probe(codes):
    """Ask every slug for a recent busy weekend and report what came back."""
    # A Saturday and a Wednesday, so both weekend leagues and midweek rounds
    # get a fair chance. Recent, so a league in season should have something.
    days = []
    d = date.today() - timedelta(days=1)
    while len(days) < 2:
        if d.weekday() in (2, 5):
            days.append(d)
        d -= timedelta(days=1)

    print(f"probing {len(codes)} competitions on {', '.join(x.isoformat() for x in days)}\n")
    print(f"  {'code':8} {'slug':26} {'fixtures':>9}  status")
    dead, alive = [], []
    for code in codes:
        slugs = S.ESPN_SLUGS.get(code) or []
        if not slugs:
            print(f"  {code:8} {'(none configured)':26} {'-':>9}  no slug")
            dead.append(code)
            continue
        best = (0, slugs[0], "no answer")
        for slug in slugs:
            total, err = 0, None
            for day in days:
                errs = []
                evs = S._espn_day(slug, day, 20, errs)
                total += len(evs)
                if errs and err is None:
                    err = errs[0].split(": ", 1)[-1][:38]
            status = "ok" if total else (err or "empty")
            if total > best[0]:
                best = (total, slug, status)
            elif best[0] == 0:
                best = (0, slug, status)
        n, slug, status = best
        print(f"  {code:8} {slug:26} {n:>9}  {status}")
        (alive if n else dead).append(code)

    print(f"\n{len(alive)} answered, {len(dead)} did not")
    if dead:
        print("\nnot answering — either the slug is wrong or the league is out of")
        print("season. Check a couple by hand before deleting them from ESPN_SLUGS:")
        print("  " + ", ".join(dead))
    return alive, dead


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="report which slugs answer")
    ap.add_argument("--season", help="season string to walk, e.g. 2025 or 2025-26")
    ap.add_argument("--only", help="comma-separated competition codes")
    ap.add_argument("--sleep", type=float, default=0.15)
    args = ap.parse_args()

    codes = live_codes()
    if args.only:
        wanted = {c.strip() for c in args.only.split(",")}
        unknown = wanted - set(E.LEAGUES)
        if unknown:
            ap.error(f"unknown competition code(s): {', '.join(sorted(unknown))}")
        codes = [c for c in codes if c in wanted] or sorted(wanted)

    if args.probe:
        probe(codes)
        return
    if not args.season:
        ap.error("nothing to do: pass --probe or --season")

    os.makedirs(HIST, exist_ok=True)
    written = 0
    for code in codes:
        out = os.path.join(HIST, f"{code}-{args.season}.json")
        if os.path.exists(out):
            print(f"  {code} {args.season}: already cached, skipping", file=sys.stderr)
            continue
        rows = walk(code, args.season, sleep=args.sleep)
        # A season with almost nothing in it is a wrong slug or a wrong season
        # string, not a real season. Writing it would give the league a
        # confidently wrong set of ratings, which is worse than none.
        if len(rows) < 30:
            print(f"  {code} {args.season}: only {len(rows)} matches, not writing",
                  file=sys.stderr)
            continue
        json.dump(rows, open(out, "w"), separators=(",", ":"))
        written += 1
        print(f"  wrote history/{os.path.basename(out)}", file=sys.stderr)
    print(f"\n{written} season(s) cached. The next build will rate those "
          f"competitions instead of flagging them unrated.", file=sys.stderr)


if __name__ == "__main__":
    main()
