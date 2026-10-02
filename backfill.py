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


# Season boundaries that differ from the default window, each backed by the
# 2025-26 data (audit, 2 Oct 2026). Real season end / next season start:
#   mx.1   2026-05-25 / 2026-07-17   ru.1   2026-05-17 / 2026-07-24
#   dnk.1  2026-05-21 / 2026-07-24   (and 2025-06-01 Randers v Silkeborg was
#                                     the 2024-25 European play-off)
# The default window (1 June to 31 July) ran into all three next seasons and,
# for Denmark, back into the previous one. 1 July to 30 June sits inside every
# gap. Other competitions keep the default: their data shows no overlap
# (nl.2, sa.1, sco.2 start in August) or cannot be checked yet (au.1, in.1).
# Add a competition here only with that kind of evidence.
SEASON_BOUNDS = {          # code: ((start month, day), (end month, day)), split-year seasons
    "mx.1": ((7, 1), (6, 30)),
    "ru.1": ((7, 1), (6, 30)),
    "dnk.1": ((7, 1), (6, 30)),
}


def season_window(code, season):
    """The calendar range a season string covers.

    A calendar-year league ("2026") runs January to December. A split-year one
    ("2026-27") runs, by default, 1 June to 31 July of the following year,
    drawn wide for play-offs and rearranged fixtures, unless SEASON_BOUNDS
    holds evidence for tighter dates.
    """
    if "-" in season:
        y = int(season.split("-")[0])
        (sm, sd), (em, ed) = SEASON_BOUNDS.get(code, ((6, 1), (7, 31)))
        return date(y, sm, sd), date(y + 1, em, ed)
    y = int(season)
    return date(y, 1, 1), date(y, 12, 31)


def next_season(season):
    if "-" in season:
        y = int(season.split("-")[0]) + 1
        return f"{y}-{str(y + 1)[-2:]}"
    return str(int(season) + 1)


def clip_to_next_season(code, season, end):
    """End the walk the day before the next season's first cached result, if
    there is one: whatever the window says, a backfill must not run into the
    season that follows it."""
    nxt, _ = S.load_current(code, next_season(season))
    if nxt:
        first = min(r["date"] for r in nxt.values())
        end = min(end, date.fromisoformat(first) - timedelta(days=1))
    return end


def walk(code, season, sleep=0.15, verbose=True):
    """Every completed match of one season, one date at a time."""
    start, end = season_window(code, season)
    end = clip_to_next_season(code, season, min(end, date.today() - timedelta(days=1)))
    if start > end:
        return []
    rows, seen, errors = [], set(), 0
    day, n_days = start, (end - start).days + 1
    while day <= end:
        got, ok = S.fetch_espn(code, day, day, log=None, clip=False)
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


def probe(codes, days=None):
    """Ask every slug for a recent busy weekend and report what came back."""
    # A Saturday and a Wednesday, so both weekend leagues and midweek rounds
    # get a fair chance. Recent, so a league in season should have something.
    # In an international window most club leagues are idle and answer empty,
    # so pass club dates with --on rather than trusting the default then.
    if not days:
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
    ap.add_argument("--on", help="probe these dates instead, e.g. 2026-09-19,2026-09-13")
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
        probe(codes, [date.fromisoformat(x.strip()) for x in args.on.split(",")]
              if args.on else None)
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
