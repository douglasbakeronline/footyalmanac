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
import rankings as RK
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
# Every priced match, archived so score_tennis.py can grade it once played.
PRED_DIR = os.path.join(HERE, "predictions-tennis")

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


# How far each probability is pulled back toward a coin flip, per tour.
# Was a flat 0.8 judgement call. Tested 27 Sep 2026 on the tour-level archive
# (main draw, both players 10+ matches): shrink chosen on 2025, checked on 2026
# against 0.8, paired bootstrap, tune.py gates plus the honesty guard (the
# quoted-minus-landed gap at 65%+ may not widen). ATP 0.9: -0.0023 log loss,
# p(worse) 0.03, gap 5.0 -> 1.5 pts. WTA 0.95: -0.0034, p(worse) 0.04, gap
# 5.7 -> 1.5 pts. 0.8 was under-quoting: its 75% calls landed 85%.
CONFIDENCE_SHRINK = {"atp": 0.9, "wta": 0.95}

# The Daily List. Same archive and filter, the shrink above. The shared rule
# (sports.list_threshold): the lowest confidence at which calls landed 75%+
# in every test window with 30+ such calls. Both tours: 70%, where ATP landed
# 79.1% (673) in 2025 and 78.1% (320) in 2026, WTA 78.1% (661) and 80.2%
# (384). The archive is main draw only, so qualifying rounds (thin ratings,
# and not what was tested) never make the list.
#
# Raised 29 Sep 2026 with every sport to the 80% target (sports.LIST_MIN_HIT):
# 80% on both tours, where 2026 landed ATP 89.1% (92), WTA 87.0% (138), ATP
# with ranking 85.6% (118). 75% passes on 2026 too (81.0%, 81.0%, 83.2%) but
# the 2025 bands at that level are not on file, so the list takes the level
# both windows are well clear of rather than one only 2026 can vouch for.
LIST_MIN = {"ATP": 0.80, "WTA": 0.80,
            # an ATP match re-scored by the world ranking (rankings.py): that
            # model's own test, 65%+ landed 76.9%/77% in 2025/2026
            "ATP_RANKED": 0.80}
LIST_MIN_MATCHES = 10
LIST_BACKTEST = {"ATP": {"2025": [0.791, 673], "2026": [0.781, 320]},
                 "WTA": {"2025": [0.781, 661], "2026": [0.802, 384]}}
# ATP with the world ranking applied: how calls at each level landed in 2026.
ACCURACY_BANDS_ATP_RANKED = [{"from": 0.55, "hit": 0.6938, "n": 921, "quoted": 0.6796}, {"from": 0.6, "hit": 0.7328, "n": 670, "quoted": 0.7183}, {"from": 0.65, "hit": 0.7688, "n": 519, "quoted": 0.746}, {"from": 0.7, "hit": 0.7867, "n": 347, "quoted": 0.7811}, {"from": 0.75, "hit": 0.8316, "n": 196, "quoted": 0.8256}, {"from": 0.8, "hit": 0.8559, "n": 118, "quoted": 0.8607}, {"from": 0.85, "hit": 0.9194, "n": 62, "quoted": 0.8938}]
# How calls at each level landed in 2026 (never fitted on), for every row.
ACCURACY_BANDS = {"ATP": [{"from": 0.55, "hit": 0.6824, "n": 973, "quoted": 0.6734}, {"from": 0.6, "hit": 0.7188, "n": 754, "quoted": 0.7019}, {"from": 0.65, "hit": 0.7514, "n": 523, "quoted": 0.7363}, {"from": 0.7, "hit": 0.7812, "n": 320, "quoted": 0.775}, {"from": 0.75, "hit": 0.8098, "n": 184, "quoted": 0.8137}, {"from": 0.8, "hit": 0.8913, "n": 92, "quoted": 0.852}, {"from": 0.85, "hit": 0.9048, "n": 42, "quoted": 0.8855}], "WTA": [{"from": 0.55, "hit": 0.6829, "n": 965, "quoted": 0.6843}, {"from": 0.6, "hit": 0.7151, "n": 737, "quoted": 0.7187}, {"from": 0.65, "hit": 0.7681, "n": 539, "quoted": 0.7534}, {"from": 0.7, "hit": 0.8021, "n": 384, "quoted": 0.7854}, {"from": 0.75, "hit": 0.8103, "n": 253, "quoted": 0.8161}, {"from": 0.8, "hit": 0.8696, "n": 138, "quoted": 0.8499}, {"from": 0.85, "hit": 0.9032, "n": 62, "quoted": 0.8795}]}


def accuracy_for(conf, tour, ranked=False):
    best = None
    for b in (ACCURACY_BANDS_ATP_RANKED if ranked else ACCURACY_BANDS.get(tour.upper(), [])):
        if conf >= b["from"]:
            best = b
    return {"from": best["from"], "hit": best["hit"], "n": best["n"]} if best else None


# The list's reserve, as football (build.RESERVE_MIN): below the bar, Firm
# or better, main draw, both players rated. Graded as its own group.
RESERVE_MIN = 0.62


def list_reserve(conf, tour, round_name, matches_a, matches_b, ranked=False):
    return (not list_eligible(conf, tour, round_name, matches_a, matches_b, ranked)
            and conf >= RESERVE_MIN and "qualif" not in (round_name or "").lower()
            and matches_a >= LIST_MIN_MATCHES and matches_b >= LIST_MIN_MATCHES)


def list_eligible(conf, tour, round_name, matches_a, matches_b, ranked=False):
    return (conf >= LIST_MIN["ATP_RANKED" if ranked else tour.upper()] and "qualif" not in (round_name or "").lower()
            and matches_a >= LIST_MIN_MATCHES and matches_b >= LIST_MIN_MATCHES)


def dampen(p, shrink):
    return 0.5 + (p - 0.5) * shrink


def dynamic_k(matches_played, k_base):
    return k_base / ((matches_played + 5) ** 0.4)


def apply_result(pool, winner, loser, surface, k_base):
    """Nudges both players' overall and surface ratings by one result, the
    exact update tune_tennis.py's run_elo() applies during a full fit.
    This is what keeps tennis.json from just being a snapshot frozen at
    whatever date it was last fitted on: every real ESPN result this script
    can see gets folded in, in order, before anything is priced."""
    surf_key = f"surface_{surface}"
    ow = pool[winner]["overall"]
    ol = pool[loser]["overall"]
    sw = pool[winner].get(surf_key, ow)
    sl = pool[loser].get(surf_key, ol)
    nw = pool[winner].get("matches", 0)
    nl = pool[loser].get("matches", 0)
    kw, kl = dynamic_k(nw, k_base), dynamic_k(nl, k_base)

    e_ow = 1.0 / (1.0 + 10 ** ((ol - ow) / 400.0))
    pool[winner]["overall"] = ow + kw * (1 - e_ow)
    pool[loser]["overall"] = ol + kl * (0 - (1 - e_ow))
    e_sw = 1.0 / (1.0 + 10 ** ((sl - sw) / 400.0))
    pool[winner][surf_key] = sw + kw * (1 - e_sw)
    pool[loser][surf_key] = sl + kl * (0 - (1 - e_sw))
    pool[winner]["matches"] = nw + 1
    pool[loser]["matches"] = nl + 1


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
            # the ESPN athlete id, which is how the world ranking is keyed
            ids = [s.get("id") for s in sides]

            p0, p1 = name(sides[0]), name(sides[1])
            if not p0 or not p1:
                continue

            stype = (comp.get("status") or {}).get("type") or {}
            status = stype.get("state")
            completed = status == "post"
            winner = None
            if completed:
                winner = p0 if sides[0].get("winner") else (p1 if sides[1].get("winner") else None)
            # "Muller (FRA) bt Pavlovic (FRA) 6-4 6-7 (6-8) 6-3": the score, and
            # the only place a walkover or retirement is spelled out.
            note = " ".join(n.get("text", "") for n in comp.get("notes") or []).strip()

            iso = comp.get("date") or ""
            round_name = (comp.get("round") or {}).get("displayName")
            out.append({
                "id": comp.get("id"), "state": status, "statusName": stype.get("name"),
                "note": note or None,
                "tour": tour, "date": iso[:10], "time": iso[11:16] if len(iso) >= 16 else None,
                "p0": p0, "p1": p1, "id0": ids[0], "id1": ids[1],
                "completed": completed, "winner": winner,
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
# archive
# ---------------------------------------------------------------------------

def pred_key(m):
    """One match, however many builds priced it."""
    return m.get("id") or f"{m['tour']}|{m['date']}|{m['playerA']}|{m['playerB']}"


def archive(matches, published, day=None):
    """Add this build's prices to predictions-tennis/<day>.json.

    Merged into the day's file, not written over it: a second build the same
    day no longer prices a match that has since started, and replacing the
    file would throw away the earlier, pre-match price that was published.
    Each entry carries the time it was published, so score_tennis.py can
    refuse anything published after the match began.
    """
    os.makedirs(PRED_DIR, exist_ok=True)
    day = day or published[:10]
    path = os.path.join(PRED_DIR, f"{day}.json")
    try:
        old = json.load(open(path))
    except Exception:
        old = []
    merged = {pred_key(m): m for m in old}
    for m in matches:
        merged[pred_key(m)] = {**m, "published": published}
    with open(path, "w") as f:
        json.dump(list(merged.values()), f, separators=(",", ":"))


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--catchup-days", type=int, default=6,
                     help="how many days back to pull completed results from, to update "
                          "ratings before pricing. tennis.json is a snapshot from whenever "
                          "it was last fitted on bulk historical data; this is what keeps it "
                          "from just getting staler forever between full refits.")
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
        k_base = ratings[tour]["constants"]["kBase"]
        sw = ratings[tour]["constants"]["surfaceWeight"]
        by_full, by_initial = build_index(pool)
        world = RK.tennis_ranks(tour)   # {ESPN athlete id: rank}, top 150; {} if unavailable
        log.append(f"{tour}: {len(world)} players with a world ranking")

        # Catch-up pass: fold in whatever real results ESPN has for the last
        # few days before pricing anything, so the ratings used below aren't
        # just whatever tennis.json was fitted on — they're that plus every
        # result since that this script could actually see. Unmatched
        # players are skipped rather than guessed at, same rule as pricing.
        catchup_start = start - timedelta(days=args.catchup_days)
        catchup_rows = fetch_week(tour, catchup_start, end, log=log)
        completed = [r for r in catchup_rows if r["completed"] and r["winner"]]
        completed.sort(key=lambda r: (r["date"], r["time"] or ""))
        applied, skipped = 0, 0
        for r in completed:
            a = match_player(r["p0"], by_full, by_initial)
            b = match_player(r["p1"], by_full, by_initial)
            if not a or not b:
                skipped += 1
                continue
            winner = a if r["winner"] == r["p0"] else b
            loser = b if winner == a else a
            apply_result(pool, winner, loser, r["surface"], k_base)
            applied += 1
        log.append(f"{tour}: {applied} completed results applied to ratings, "
                    f"{skipped} skipped (no rating on file for a side)")

        rows = [r for r in catchup_rows if r["date"] >= start.isoformat()]
        dropped = 0
        for r in rows:
            if r["state"] != "pre":
                # Only what hasn't started. A match already in play at build
                # time was priced before, and published after, it began, which
                # score_tennis.py would rightly refuse to grade.
                continue
            a = match_player(r["p0"], by_full, by_initial)
            b = match_player(r["p1"], by_full, by_initial)
            if not a or not b:
                dropped += 1
                continue   # no rating on at least one side — not published, same rule as football
            p = dampen(price_match(pool[a], pool[b], r["surface"], sw), CONFIDENCE_SHRINK[tour])
            rank_a, rank_b = world.get(r["id0"]), world.get(r["id1"])
            ranked = False
            if tour == "atp" and (rank_a or rank_b):
                # ATP ranking gap on top of Elo (rankings.py): tested on 2026
                # main-draw matches, -0.0037 log loss, p(worse) 0.03. WTA did
                # not pass, so WTA ranks are shown but never move the number.
                fav_a = p >= 0.5
                conf = RK.adjust_atp(max(p, 1 - p), rank_a if fav_a else rank_b, rank_b if fav_a else rank_a)
                p = conf if fav_a else 1 - conf
                ranked = True
            surf_key = f"surface_{r['surface']}"
            matches.append({
                "id": r["id"], "espn": [r["p0"], r["p1"]],
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
                "rankA": rank_a, "rankB": rank_b, "rankAdjusted": ranked,
                "accuracy": accuracy_for(max(p, 1 - p), tour, ranked),
                "list": list_eligible(max(p, 1 - p), tour, r["round"],
                                      pool[a]["matches"], pool[b]["matches"], ranked),
                "reserve": list_reserve(max(p, 1 - p), tour, r["round"],
                                        pool[a]["matches"], pool[b]["matches"], ranked),
            })
        log.append(f"{tour}: {len(rows)} fetched, {dropped} dropped (no rating on file for a side)")

    for line in log:
        print(f"  {line}", file=sys.stderr)

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {"generated": generated,
               "list": {"min": LIST_MIN, "backtest": LIST_BACKTEST},
               "from": start.isoformat(), "to": end.isoformat(),
               "count": len(matches), "matches": matches}
    archive(matches, generated)
    blob = json.dumps(payload, separators=(",", ":"))
    with open(args.out, "w") as f:
        f.write("window.__TENNIS_DATA__=" + blob + ";")
    print(f"wrote {args.out}: {len(matches)} priced matches", file=sys.stderr)


if __name__ == "__main__":
    main()
