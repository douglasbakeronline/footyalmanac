#!/usr/bin/env python3
"""
Pulls this week's ATP and WTA fixtures and prices them off tennis.json's Elo
ratings (see tune_tennis.py). Same shape of pipeline as build.py, run
separately because tennis isn't a competition among the football ones — it's
a different sport with a different unit of prediction (a player, not a club)
and no draw to price around.

    python3 build_tennis.py                 this week, today onward
    python3 build_tennis.py --from 2026-09-22 --days 7

What's tested and what isn't
-----------------------------
Player-name matching (match_player, below) is tested against the real
tennis.json ratings pool, including genuine ambiguous cases this project's
own data throws up — Z. Zhang could be Ze Zhang or Zhizhen Zhang; K.
Pliskova has actual twin sisters (Karolina and Kristyna) both active. It
refuses rather than guesses on any of those, the same contract as
sources.match_team for clubs.

The Elo pricing math (price_match) is the exact formula tune_tennis.py
validated — same blend, same win-probability curve, nothing new introduced
here that wasn't already checked against real 2026 results.

What is NOT tested: the shape of ESPN's tennis scoreboard response.
Every other ESPN integration in this project follows soccer's team-based
schema (home/away "competitors", each a "team"). Tennis is two individual
athletes, not two teams, and ESPN's schema for that has never been seen by
this build — the sandbox this was written in cannot reach espn.com. _row()
below is written defensively (try several plausible field paths, return
None rather than crash on anything unexpected) precisely because of that,
and the whole fetch is wrapped so a bad guess produces "no fixtures today",
never a broken build. Run with --probe first and read what actually comes
back before trusting any of it.

Standard library only, like the rest of the project.
"""
import argparse, json, math, os, re, sys, unicodedata, urllib.request
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))

ESPN_HOSTS = ["https://site.api.espn.com", "https://site.web.api.espn.com"]
# Soccer's path is /sports/soccer/{league-slug}/scoreboard. Tennis's sport
# slug is presumably "tennis", but where soccer has one continuous league
# feed per competition, tennis tournaments start and stop — there may be no
# single "atp"/"wta" feed that always has something behind it the way
# eng.1 always does. Tried here because it's the natural guess by analogy;
# unconfirmed.
ESPN_PATH = "/apis/site/v2/sports/tennis/{tour}/scoreboard?dates={d}&limit=400"
ESPN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (footyalmanac build)",
    "Referer": "https://www.espn.com/tennis/scoreboard",
    "Origin": "https://www.espn.com",
}
TOUR_SLUGS = {"atp": ["atp"], "wta": ["wta"]}   # unverified — see module docstring

SURFACE_MAP = {"hard": "Hard", "clay": "Clay", "grass": "Grass",
               "carpet": "Hard", "indoor hard": "Hard", "i. hard": "Hard"}


# ---------------------------------------------------------------------------
# player-name matching — tested, see module docstring
# ---------------------------------------------------------------------------

def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _normalize(s):
    s = _strip_accents(s).lower()
    s = re.sub(r"[.\-']", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def build_index(ratings_pool):
    by_full, by_initial_last = {}, {}
    for name in ratings_pool:
        norm = _normalize(name)
        by_full[norm] = name
        parts = norm.split()
        if len(parts) >= 2:
            by_initial_last.setdefault((parts[0][0], parts[-1]), set()).add(name)
    return by_full, by_initial_last


def match_player(raw_name, by_full, by_initial_last):
    """Exact normalized name first. Falls back to ESPN's common "F. Last"
    scoreboard abbreviation ONLY when exactly one rated player shares that
    first-initial + last-token pair. Any ambiguity, or no match at all,
    returns None — never a guess."""
    norm = _normalize(raw_name)
    if norm in by_full:
        return by_full[norm]
    parts = norm.split()
    if len(parts) >= 2:
        cands = by_initial_last.get((parts[0][0], parts[-1]))
        if cands and len(cands) == 1:
            return next(iter(cands))
    return None


# ---------------------------------------------------------------------------
# Elo pricing — the exact formula tune_tennis.py validated, unchanged
# ---------------------------------------------------------------------------

def price_match(rating_a, rating_b, surface, surface_weight):
    """rating_a/b: the {"overall":..., "surface_Hard":..., ...} dict from
    tennis.json. Returns P(a wins). Missing surface rating (a player with no
    matches on this surface yet) falls back to their overall rating for that
    term, rather than a fabricated 1500 — a new-to-surface player is not the
    same as an unrated one."""
    oa, ob = rating_a["overall"], rating_b["overall"]
    sa = rating_a.get(f"surface_{surface}", oa)
    sb = rating_b.get(f"surface_{surface}", ob)
    ba = (1 - surface_weight) * oa + surface_weight * sa
    bb = (1 - surface_weight) * ob + surface_weight * sb
    return 1.0 / (1.0 + 10 ** ((bb - ba) / 400.0))


TIERS = [(0.70, "Strong"), (0.62, "Firm"), (0.55, "Lean"), (0.0, "No read")]
def tier_of(p):
    # Borrowed straight from football's thresholds as a starting point, not
    # a tennis-specific calibration — tennis's probability distribution from
    # Elo may not land in these bands the same way goals-based probabilities
    # do. Worth its own tune_tennis.py-style calibration pass once there's a
    # season of graded tennis picks to check it against.
    for m, name in TIERS:
        if p >= m:
            return name


# ---------------------------------------------------------------------------
# fetch — UNVERIFIED, see module docstring
# ---------------------------------------------------------------------------

def _get_day(tour_slug, day, timeout, errs):
    d = day.strftime("%Y%m%d")
    for host in ESPN_HOSTS:
        url = host + ESPN_PATH.format(tour=tour_slug, d=d)
        try:
            req = urllib.request.Request(url, headers=ESPN_HEADERS)
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read()).get("events") or []
        except Exception as e:
            errs.append(f"{tour_slug} {d}: {type(e).__name__} {e}")
    return []


def _row(ev, tour):
    """One ESPN tennis event -> a plain match dict, or None if the shape
    doesn't match what was guessed. Tries a couple of plausible layouts for
    where the two players' names live, since individual-athlete events don't
    follow soccer's team-competitor schema and the real shape is unseen."""
    comp = (ev.get("competitions") or [{}])[0]
    sides = comp.get("competitors") or []
    if len(sides) != 2:
        return None

    def side_name(c):
        for path in (("athlete", "displayName"), ("athlete", "shortName"), ("team", "displayName")):
            obj = c
            for key in path:
                obj = (obj or {}).get(key) if isinstance(obj, dict) else None
            if obj:
                return obj
        return None

    p0, p1 = side_name(sides[0]), side_name(sides[1])
    if not p0 or not p1:
        return None

    status = ((ev.get("status") or {}).get("type") or {}).get("state")
    completed = status == "post"
    winner = None
    if completed:
        w0 = sides[0].get("winner")
        winner = p0 if w0 else (p1 if sides[1].get("winner") else None)

    iso = comp.get("date") or ev.get("date") or ""
    surface_raw = ((ev.get("groupings") or [{}])[0].get("grouping") or {}).get("surface") \
        or ev.get("surface") or ""
    round_name = ((ev.get("competitions") or [{}])[0].get("notes") or [{}])
    round_name = round_name[0].get("headline") if round_name else None
    tourney = ((ev.get("league") or {}).get("name")) or ev.get("shortName") or ""

    return {
        "tour": tour, "date": iso[:10], "time": iso[11:16] if len(iso) >= 16 else None,
        "p0": p0, "p1": p1, "completed": completed, "winner": winner,
        "surface": SURFACE_MAP.get(surface_raw.strip().lower(), "Hard"),
        "round": round_name, "tournament": tourney,
    }


def fetch_week(tour, start, end, timeout=25, log=None):
    days = []
    d = start
    while d <= end:
        days.append(d)
        d += timedelta(days=1)
    for slug in TOUR_SLUGS.get(tour, []):
        errs, rows, seen = [], [], set()
        for day in days:
            for ev in _get_day(slug, day, timeout, errs):
                r = _row(ev, tour)
                if not r:
                    continue
                key = (r["date"], r["p0"], r["p1"])
                if key not in seen:
                    seen.add(key)
                    rows.append(r)
        if log is not None:
            note = f"  ERROR {errs[0]}" if errs else ""
            log.append(f"{tour}/{slug}: {len(rows)} matches{note}")
        if rows or not errs:
            return rows
    return []


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--ratings", default=os.path.join(HERE, "tennis.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "tennis-data.json"))
    args = ap.parse_args()

    if not os.path.exists(args.ratings):
        print(f"no {args.ratings} — run tune_tennis.py --fit first", file=sys.stderr)
        sys.exit(1)
    ratings = json.load(open(args.ratings))

    start = date.fromisoformat(args.start) if args.start else date.today()
    end = start + timedelta(days=args.days - 1)

    log = []
    matches = []
    for tour in ("atp", "wta"):
        pool = ratings[tour]["ratings"]
        sw = ratings[tour]["constants"]["surfaceWeight"]
        by_full, by_initial = build_index(pool)
        rows = fetch_week(tour, start, end, log=log)
        dropped = 0
        for r in rows:
            if r["completed"]:
                continue   # only price what hasn't been played yet
            a = match_player(r["p0"], by_full, by_initial)
            b = match_player(r["p1"], by_full, by_initial)
            if not a or not b:
                dropped += 1
                continue   # no rating on at least one side — not published, same rule as football
            p = price_match(pool[a], pool[b], r["surface"], sw)
            matches.append({
                "tour": tour.upper(), "date": r["date"], "time": r["time"],
                "tournament": r["tournament"], "round": r["round"], "surface": r["surface"],
                "playerA": a, "playerB": b,
                "p": {"a": round(p, 4), "b": round(1 - p, 4)},
                "pick": a if p >= 0.5 else b,
                "confidence": round(max(p, 1 - p), 4),
                "tier": tier_of(max(p, 1 - p)),
            })
        log.append(f"{tour}: {len(rows)} fetched, {dropped} dropped (no rating on file for a side)")

    for line in log:
        print(f"  {line}", file=sys.stderr)

    payload = {"generated": datetime.now().isoformat(timespec="seconds"),
               "from": start.isoformat(), "to": end.isoformat(),
               "count": len(matches), "matches": matches}
    json.dump(payload, open(args.out, "w"), separators=(",", ":"))
    print(f"wrote {args.out}: {len(matches)} priced matches", file=sys.stderr)


if __name__ == "__main__":
    main()
