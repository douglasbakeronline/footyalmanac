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
import argparse, json, os, re, sys, unicodedata, urllib.request
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
    # Copied verbatim from sources.py's ESPN_HEADERS, which is the one
    # actually proven to work against ESPN — a genuine Chrome UA plus the
    # Accept/Accept-Language headers, not just a UA string on its own. The
    # earlier version of this file used a placeholder UA and nothing else,
    # which is almost certainly why ESPN returned 403 rather than data: it
    # read as a bot, correctly.
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.espn.com/tennis/scoreboard",
    "Origin": "https://www.espn.com",
}
TOUR_SLUGS = {"atp": ["atp"], "wta": ["wta"]}   # unverified — see module docstring

# SURFACE_MAP removed: ESPN's tennis feed carries no surface field at all
# (confirmed against a real response), so there was never anything to map —
# see the "Hard" fallback and its comment in _matches_from_event below.


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


# Deliberately separate from price_match rather than folded into it: this is
# a direct response to a few live results looking wrong by eye, not a
# re-validated calibration. The walk-forward holdout (tune_tennis.py, 1437
# ATP + 1286 WTA matches from 2026) showed the tiers landing close to or
# above what their labels claim — WTA Strong at 80.8% against a label of
# 70%+, for instance — so the backtested model itself isn't the obvious
# problem. But a handful of live matches is a genuinely different, much
# smaller sample than a season-long backtest, and there's no tennis
# equivalent of score.py yet to actually track whether this shrink helps or
# overcorrects. Until that exists, treat this constant as a judgement call
# to revisit, not a fitted value: 0.8 pulls every probability 20% of the way
# back toward a coin flip, softening the number shown without changing which
# side is favoured.
CONFIDENCE_SHRINK = 0.8


def dampen(p, shrink=CONFIDENCE_SHRINK):
    return 0.5 + (p - 0.5) * shrink


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


# Confirmed against a real response fetched by hand on 22 Sep 2026 — not a
# guess. Only two draw types get rated: tennis.json is singles-only, so
# doubles/mixed groupings are skipped outright rather than half-parsed.
SINGLES_SLUGS = {"mens-singles", "womens-singles"}


def _matches_from_event(ev, tour):
    """One ESPN tennis "event" is a whole TOURNAMENT (e.g. "Chengdu Open"),
    not a match — soccer's schema has one event per game, but tennis nests
    every match for every draw of that tournament inside
    event["groupings"][i]["competitions"][j]. Getting this wrong was the
    actual reason nothing was ever extracted, even once the 403 was fixed:
    the earlier version of this file read event["competitions"] directly,
    which doesn't exist, and silently found nothing every time."""
    tourney = ev.get("name") or ev.get("shortName") or ""
    out = []
    for g in ev.get("groupings") or []:
        if ((g.get("grouping") or {}).get("slug")) not in SINGLES_SLUGS:
            continue
        for comp in g.get("competitions") or []:
            sides = comp.get("competitors") or []
            if len(sides) != 2:
                continue

            def name(c):
                return (c.get("athlete") or {}).get("displayName")

            p0, p1 = name(sides[0]), name(sides[1])
            if not p0 or not p1:
                continue

            status = ((comp.get("status") or {}).get("type") or {}).get("state")
            completed = status == "post"
            winner = None
            if completed:
                winner = p0 if sides[0].get("winner") else (p1 if sides[1].get("winner") else None)

            iso = comp.get("date") or ""
            round_name = (comp.get("round") or {}).get("displayName")
            out.append({
                "tour": tour, "date": iso[:10], "time": iso[11:16] if len(iso) >= 16 else None,
                "p0": p0, "p1": p1, "completed": completed, "winner": winner,
                # ESPN's tennis feed carries no surface field at all — an
                # earlier version of this read one that doesn't exist and
                # always fell back to Hard anyway. Hard-coding it here
                # instead is the same fallback made honest: correct for the
                # current hard-court swing (Sep-Mar is nearly all hard
                # court), a real gap once clay/grass season starts. Needs a
                # tournament-name lookup to fix properly — not attempted
                # here, flagged instead of silently guessed at.
                "surface": "Hard",
                "round": round_name, "tournament": tourney,
            })
    return out


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
                for r in _matches_from_event(ev, tour):
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
    ap.add_argument("--out", default=os.path.join(HERE, "tennis-data.js"))
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
            p = dampen(price_match(pool[a], pool[b], r["surface"], sw))
            surf_key = f"surface_{r['surface']}"
            matches.append({
                "tour": tour.upper(), "date": r["date"], "time": r["time"],
                "tournament": r["tournament"], "round": r["round"], "surface": r["surface"],
                "playerA": a, "playerB": b,
                # The evidence behind the number, same principle as football's
                # ppg/W-D-L/GD line under each club: elo is career-overall,
                # surfaceElo is specific to the surface this match is actually
                # on (the one price_match used) and falls back to the same
                # value as elo if the player hasn't got surface-specific
                # matches yet — a genuinely new-to-surface player, not a
                # missing stat.
                "ratingA": {"elo": round(pool[a]["overall"]), "matches": pool[a]["matches"],
                            "surfaceElo": round(pool[a].get(surf_key, pool[a]["overall"]))},
                "ratingB": {"elo": round(pool[b]["overall"]), "matches": pool[b]["matches"],
                            "surfaceElo": round(pool[b].get(surf_key, pool[b]["overall"]))},
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
    blob = json.dumps(payload, separators=(",", ":"))
    with open(args.out, "w") as f:
        f.write("window.__TENNIS_DATA__=" + blob + ";")
    print(f"wrote {args.out}: {len(matches)} priced matches", file=sys.stderr)


if __name__ == "__main__":
    main()
