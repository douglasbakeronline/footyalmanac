#!/usr/bin/env python3
"""
Build the dashboard payload.

    python3 build.py --days 4 --top 50

Reads openfootball, rates every team, prices every upcoming fixture, keeps the
top N by confidence per day, writes data.json next to index.html.
"""
import argparse, concurrent.futures as cf, json, os, sys
from collections import defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S
import rankings as RK

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


# The Daily List: the fixtures obvious enough to serve on their own. The model's
# number and nothing else, no bookmaker input, so it stays an independent read.
#
# Why 75%: on the walk-forward (predictability.py, re-run 27 Sep 2026 with the
# current calibration.json), league fixtures the model rated 75%+ landed 78.9%
# of the time in 2025/26 (242 games) and 76.2% in 2026/27 so far (21).
# Raising it further buys little: the model's most extreme numbers are its
# least well calibrated. So the bar is set where hit rate stops climbing, and
# the rest of the selection is about removing games the model cannot see.
# Internationals are rated by a separate fit (tune_international.py); on its
# 2026 holdout, calibrated calls at 75%+ landed 81.6% (49 games).
# The shared rule (sports.list_threshold): the lowest confidence at which
# calls landed 75%+ in every test window with 30+ such calls. League
# fixtures: 75% (2025/26 78.9% of 242; 2026/27 76.2% of 21, too few to count
# yet). Internationals: 55%, where the 2026 holdout landed 75.7% of 177, since
# the international fit under-quotes itself.
LIST_MIN = {"league": 0.75, "intl": 0.55,
            # an international adjusted by the FIFA ranking (rankings.py): the
            # ranking model's own test, 60%+ landed 77.8% of 536 in 2025 and
            # 75.3% of 190 in 2026
            "intlRanked": 0.60}
LIST_BACKTEST = {"fit": {"season": "2025-26", "n": 242, "hit": 0.789},
                 "check": {"season": "2026-27", "n": 21, "hit": 0.762},
                 "intl": {"season": "2026", "n": 49, "hit": 0.816}}

# How calls at each level landed on games the model was never tuned on, shown
# on every row so a reader can weigh the number: "calls at 70%+ landed 78%".
# League: 2026/27 where a band has 30+ games, else 2025/26. Internationals:
# the 2026 holdout. Same walk-forward as above.
ACCURACY_BANDS_RANKED = [{"from": 0.55, "hit": 0.7436, "n": 234, "quoted": 0.7148}, {"from": 0.6, "hit": 0.7526, "n": 190, "quoted": 0.7475}, {"from": 0.65, "hit": 0.7986, "n": 144, "quoted": 0.787}, {"from": 0.7, "hit": 0.8235, "n": 119, "quoted": 0.8099}, {"from": 0.75, "hit": 0.8427, "n": 89, "quoted": 0.8377}, {"from": 0.8, "hit": 0.8387, "n": 62, "quoted": 0.8652}, {"from": 0.85, "hit": 0.9394, "n": 33, "quoted": 0.9006}]
ACCURACY_BANDS = {"league": {"check": [{"from": 0.45, "hit": 0.5498, "n": 733, "quoted": 0.5504}, {"from": 0.5, "hit": 0.597, "n": 474, "quoted": 0.5921}, {"from": 0.55, "hit": 0.6714, "n": 280, "quoted": 0.639}, {"from": 0.6, "hit": 0.7459, "n": 181, "quoted": 0.6755}, {"from": 0.65, "hit": 0.7767, "n": 103, "quoted": 0.7145}, {"from": 0.7, "hit": 0.7347, "n": 49, "quoted": 0.7605}, {"from": 0.75, "hit": 0.7619, "n": 21, "quoted": 0.8041}, {"from": 0.8, "hit": 0.8, "n": 10, "quoted": 0.8354}], "fit": [{"from": 0.45, "hit": 0.5564, "n": 4371, "quoted": 0.5599}, {"from": 0.5, "hit": 0.6032, "n": 2916, "quoted": 0.6028}, {"from": 0.55, "hit": 0.6524, "n": 1910, "quoted": 0.6447}, {"from": 0.6, "hit": 0.6879, "n": 1163, "quoted": 0.6904}, {"from": 0.65, "hit": 0.7287, "n": 726, "quoted": 0.7315}, {"from": 0.7, "hit": 0.778, "n": 419, "quoted": 0.775}, {"from": 0.75, "hit": 0.7893, "n": 242, "quoted": 0.8127}, {"from": 0.8, "hit": 0.8397, "n": 131, "quoted": 0.8471}]}, "intl": [{"from": 0.45, "hit": 0.6756, "n": 299, "quoted": 0.6093}, {"from": 0.5, "hit": 0.7118, "n": 229, "quoted": 0.6508}, {"from": 0.55, "hit": 0.7571, "n": 177, "quoted": 0.6877}, {"from": 0.6, "hit": 0.7687, "n": 134, "quoted": 0.725}, {"from": 0.65, "hit": 0.7822, "n": 101, "quoted": 0.7581}, {"from": 0.7, "hit": 0.7971, "n": 69, "quoted": 0.7983}, {"from": 0.75, "hit": 0.8163, "n": 49, "quoted": 0.8255}, {"from": 0.8, "hit": 0.8667, "n": 30, "quoted": 0.8581}]}


def accuracy_for(conf, intl, ranked=False):
    def pick(bands):
        best = None
        for b in bands:
            if conf >= b["from"]:
                best = b
        return best
    if intl and ranked:
        b = pick(ACCURACY_BANDS_RANKED)
        return {"from": b["from"], "hit": b["hit"], "n": b["n"], "season": "2026, with FIFA ranking"} if b else None
    if intl:
        b = pick(ACCURACY_BANDS["intl"])
        return {"from": b["from"], "hit": b["hit"], "n": b["n"], "season": "2026"} if b else None
    c = pick(ACCURACY_BANDS["league"]["check"])
    if c and c["n"] >= 30:
        return {"from": c["from"], "hit": c["hit"], "n": c["n"], "season": "2026-27"}
    f = pick(ACCURACY_BANDS["league"]["fit"])
    return {"from": f["from"], "hit": f["hit"], "n": f["n"], "season": "2025-26"} if f else None


def list_eligible(g):
    """Whether a fixture is obvious enough for the Daily List.

    A win pick, never a draw, at LIST_MIN or above, and nothing the model is
    blind to: no Celtic's Law flag, no unrated side, and every club rated from
    a prior season on file. That last condition is not on the board: a club in
    a league with no history gets a rating from its first few games and counts
    as rated there, which is exactly how a mislabelled feed (El Salvador as
    Slovenia, Sep 2026) produced confident-looking rows. National teams carry
    no domestic table, so their gate is simply having a rating at all.
    """
    p = g["p"]
    pick = max(("h", "d", "a"), key=lambda k: p[k])
    intl = bool(E.LEAGUES[g["league"]].get("international"))
    bar = LIST_MIN["intlRanked" if g.get("rankAdjusted") else ("intl" if intl else "league")]
    if pick == "d" or p[pick] < bar or g["celtic"] or g["unrated"]:
        return False
    for t in (g["home"], g["away"]):
        if t["played"] is not None and not t["last"]:
            return False
    return True


def prev_of(code):
    return E.LEAGUES[code].get("prev", PREV)


def pick_prior(code, seasons, log=None):
    """The prior season a competition is rated from, and how complete it is.

    Newest first, but only if it is actually a finished season. A partial file
    used to win simply for being non-empty: Norway 2025 has 44 of 240 matches
    and was chosen over a complete 2024, so every Norwegian club was rated off
    four spring fixtures. If nothing clears the bar, the most complete season
    is used and the shortfall is returned so the fixture can say so.

    Returns (season, matches, share, expected, newer_matches). newer_matches
    is the partial, more recent season's rows kept SEPARATE from matches (the
    complete older season) rather than pooled into it — see engine.blend_prior_seasons
    for why: pooling them let a match from fourteen months ago outweigh recent
    form just by there being more of them.

    Returns (None, [], 0.0, 0, []) if nothing usable is on file.
    """
    pv = prev_of(code)
    cands = []
    for i, s in enumerate(pv):
        rows = seasons.get(s) or []
        if not rows:
            continue
        older = seasons.get(pv[i + 1]) if i + 1 < len(pv) else None
        share, expected = S.completeness(rows, older, E.LEAGUES[code].get("games"))
        cands.append((s, rows, share, expected))
        if share >= S.PRIOR_MIN_SHARE:
            if cands[:-1]:
                # A newer season exists but stops short. Keep its matches
                # rather than throwing them away: a club promoted into it has
                # no other top-flight record, and dropping it would turn a
                # thin rating into no rating at all. Kept separate so it can
                # be weighted by recency instead of pooled flat.
                ns, nrows, nshare, nexp = cands[0]
                if log is not None:
                    log.append(f"{code}: {ns} incomplete ({len(nrows)} of ~{nexp}), "
                               f"rated from {s} weighted with those {len(nrows)}")
                return f"{s}+{ns}", rows, share, expected, nrows
            return s, rows, share, expected, []
    if not cands:
        return None, [], 0.0, 0, []
    best = max(cands, key=lambda c: c[2])
    if log is not None:
        log.append(f"{code}: no complete prior, using {best[0]} "
                   f"({len(best[1])} of ~{best[3]} matches)")
    return best + ([],)


def season_label(season, share=1.0):
    """How the prior season reads on a team sheet. "2025-26" -> "2025/26";
    a complete season blended with a partial newer one -> "2024/25 + 2025/26
    so far" (not "Since 2024/25" — that read as one continuous span rather
    than two seasons weighted toward the more recent); a season that is the
    best available but still partial gets "(part)"."""
    if not season:
        return None
    first = season.split("+")[0].replace("-", "/")
    if "+" in season:
        second = season.split("+")[1].replace("-", "/")
        return f"{first} + {second} so far"
    return first if share >= S.PRIOR_MIN_SHARE else f"{first} (part)"


def team_pool(history, fixtures):
    """Work out which competition each team played in last season, so promoted
    and relegated sides can have their ratings carried across divisions.

    Takes whichever prior season actually resolved, not just the most recent
    one. The ratings below already fall back to the older season when the
    newer one is missing, and this did not, so twenty-five competitions ended
    up with ratings computed and no club findable in them: Mexico, Ukraine,
    Czechia, Azerbaijan and the rest all rated every fixture as unrated.
    """
    last_league = {}
    for code, seasons in history.items():
        _, ms, _, _, newer_ms = pick_prior(code, seasons)
        all_ms = ms + newer_ms
        for t in {m[1] for m in all_ms} | {m[2] for m in all_ms}:
            last_league[t] = code
    return last_league


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=4, help="days of fixtures to include")
    # Every fixture is published and archived. --top used to cut each day to
    # the N most confident, which left a league filter showing three of a
    # weekend's ten matches. It now only tells the page how many rows the "All
    # competitions" view shows before its "Show all" button.
    ap.add_argument("--top", type=int, default=50,
                    help="rows the All view shows per day before 'Show all'")
    ap.add_argument("--from", dest="start", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cache", default=None, help="directory to cache raw downloads")
    ap.add_argument("--no-odds", action="store_true",
                    help="skip bookmaker prices and the weekly value backtest")
    ap.add_argument("--no-topup", action="store_true",
                    help="skip walking this season for live-sourced competitions")
    args = ap.parse_args()

    start = date.fromisoformat(args.start) if args.start else date.today()
    end = start + timedelta(days=args.days - 1)

    print(f"fetching {len(CODES)} competitions ...", file=sys.stderr)
    # Not every league runs August-to-May. Brazil and the Nordics use a calendar
    # year, so the season strings are per-competition rather than global.
    # The FIFA world ranking, refreshed when a new release is out (rankings.py).
    rk_log = []
    FIFA = RK.refresh_fifa(log=rk_log)
    for line in rk_log:
        print(f"  {line}", file=sys.stderr)

    history, fixtures, missing = S.fetch_all_seasons(
        {c: (None if E.LEAGUES[c].get("ratingsOnly") else E.LEAGUES[c].get("season", SEASON),
             [] if E.LEAGUES[c].get("cup") or E.LEAGUES[c].get("international")
                else E.LEAGUES[c].get("prev", PREV))
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

    # The fallback above asks only for the fixture window, so every row it
    # returns is a match not yet played and the current-season table for those
    # competitions was built from nothing. Walk the season so far separately
    # and cache it: sixty-one leagues had no idea this season had started.
    season_so_far = {}
    if not args.no_topup:
        live = [c for c in gaps if c in fixtures and not E.LEAGUES[c].get("cup")
                and not E.LEAGUES[c].get("international")]
        if live:
            print(f"  topping up the season so far for {len(live)} "
                  f"competitions ...", file=sys.stderr)
            issues, fetched = [], 0

            def top(c):
                s = E.LEAGUES[c].get("season", SEASON)
                return c, S.topup_current(c, s, until=start - timedelta(days=1),
                                          log=issues)

            # Six at a time. The scoreboard is a public endpoint being asked
            # for a lot of days at once, and politeness costs a minute.
            with cf.ThreadPoolExecutor(max_workers=6) as pool:
                for c, (rows, n) in pool.map(top, live):
                    fetched += n
                    if rows:
                        season_so_far[c] = list(rows.values())
            print(f"  {fetched} day(s) fetched, {len(season_so_far)} "
                  f"competitions with results on file", file=sys.stderr)
            for line in issues[:5]:
                print(f"    topup {line}", file=sys.stderr)

    last_league = team_pool(history, fixtures)

    # ---- ratings -----------------------------------------------------------
    prior_ratings, prior_tables, league_mu = {}, {}, {}
    partial_prior, prior_log, prior_label = {}, [], {}
    for code, seasons in history.items():
        season_used, ms, share, expected, newer_ms = pick_prior(code, seasons, log=prior_log)
        if not ms:
            continue
        prior_label[code] = season_label(season_used, share)
        if share < S.PRIOR_MIN_SHARE:
            partial_prior[code] = (len(ms), expected, season_used)
        tbl = E.build_table(ms)
        if newer_ms:
            # Two seasons, weighted by recency rather than pooled flat —
            # see engine.blend_prior_seasons.
            newer_tbl = E.build_table(newer_ms)
            prior_ratings[code] = E.blend_prior_seasons(tbl, newer_tbl)
            # The table shown on a team sheet stays the full combined record
            # (a reader wants to see the whole P/W/D/L window), with any
            # newer-only row added for a club promoted since the older season.
            merged = dict(tbl)
            for team, row in newer_tbl.items():
                if team not in merged:
                    merged[team] = row
            prior_tables[code] = merged
            league_mu[code] = E.league_goal_rate(merged)
        else:
            prior_tables[code] = tbl
            prior_ratings[code] = E.strength_from_table(tbl)
            league_mu[code] = E.league_goal_rate(tbl)
    # Loud, because the whole cost of this fault was that it was silent.
    for line in prior_log:
        print(f"  PRIOR {line}", file=sys.stderr)

    # current-season tables, from whatever has been played so far
    cur_tables, cur_ratings = {}, {}
    for code, rows in fixtures.items():
        # The fixture list carries results for the competitions openfootball
        # supplies as a whole season; for the rest the cache above is the only
        # place this season exists. Merged rather than either/or, so a result
        # that has landed since the last top-up still counts.
        seen, played = set(), []
        for r in list(rows) + season_so_far.get(code, []):
            if r["hg"] is None:
                continue
            key = (r["date"], r["home"], r["away"])
            if key in seen:
                continue
            seen.add(key)
            played.append((r["date"], r["home"], r["away"], r["hg"], r["ag"]))
        played.sort()
        tbl = E.build_table(played)
        cur_tables[code] = tbl
        # Shrunk, not raw. A one-match sample must regress hard toward the
        # league average before it is allowed anywhere near a rating.
        cur_ratings[code] = E.strength_from_table(tbl) if played else {}

    # A club stuck on zero games while the rest of its division has moved on
    # is the exact symptom a stale cached fixture file produces: openfootball
    # updates the whole file at once, but this build's own cache of it can
    # predate that update. Every other club in the file shows fine, so this
    # is invisible unless something is actually looking for the gap — this
    # is that something, run every build rather than found by eye per fixture.
    for code, tbl in cur_tables.items():
        if len(tbl) < 4:
            continue
        played_counts = sorted(row["P"] for row in tbl.values())
        median_p = played_counts[len(played_counts) // 2]
        if median_p < 3:
            continue  # too early in the season for a gap to mean anything
        stuck = [name for name, row in tbl.items() if row["P"] == 0]
        if stuck:
            print(f"  STALE? {code}: {', '.join(stuck)} show 0 games played "
                  f"this season while the division median is {median_p} — "
                  f"likely a cached fixture file that predates their results, "
                  f"not a rating problem", file=sys.stderr)

    rated_pool = set(last_league)
    _dom_cache = {}

    def domestic_of(team):
        """The division a club plays in, under either source's spelling.

        A cup tie has no table of its own, so each side is rated in its own
        division and the two are converted into a shared frame. Resolving that
        division on the raw name alone failed for every club the live source
        spells differently, which is most of them: the tie fell back to the
        cup's own code, both sides came out unrated, and the fixture was priced
        off two placeholder ratings.

        Returns (division code or None, the club under the prior season's
        spelling), so callers that need the resolved name do not have to run
        the match a second time.
        """
        if team not in _dom_cache:
            src, name = last_league.get(team), team
            if src is None:
                alt = S.match_team(team, rated_pool)
                if alt:
                    src, name = last_league.get(alt), alt
            _dom_cache[team] = (src, name)
        return _dom_cache[team]

    def rating_for(team, code):
        """Prior (carried across divisions if needed) blended with this season.

        There are two namespaces in play and they are not interchangeable. The
        prior season comes from openfootball and is keyed by its spellings; the
        current season is keyed by whatever supplied the fixture list, which
        for most competitions is now the live source and its own spellings.
        Looking either up with the other's name returns nothing and says so
        silently, so the resolved name travels back out with the rating.
        """
        src, prior_name = domestic_of(team)
        if src and src in prior_ratings and prior_name in prior_ratings[src]:
            prior = E.transfer_rating(prior_ratings[src][prior_name], src, code)
            carried = (src != code)
        else:
            prior = {"att": 1.0, "def": 1.0}
            carried = None
        # Under either name. A cup tie is rated against the club's DOMESTIC
        # league, but the fixture carried the live source's spelling, and that
        # league's current table is keyed by whatever built it. Asking for
        # "Bayern Munich" in a table keyed "FC Bayern München" returns nothing,
        # played comes back 0, and the blend falls all the way back to last
        # season: every European tie was being priced as though this season had
        # not started.
        ct = cur_tables.get(code, {})
        cur_name = team if team in ct else (prior_name if prior_name in ct else None)
        if cur_name is None and ct:
            # Neither spelling is in the table. A promoted club has no prior
            # season to resolve through, so this is its only chance to be found.
            cur_name = S.match_team(team, set(ct))
        row = ct.get(cur_name) if cur_name else None
        played = row["P"] if row else 0
        cur = cur_ratings.get(code, {}).get(cur_name) if cur_name else None
        return E.blend(prior, cur, played), carried, played, src, prior_name, cur_name

    def team_block(team, code):
        # prior_name is the club under openfootball's spelling, team is the
        # name the fixture list gave. Using the latter here was marking clubs
        # whose rating had just been resolved successfully as having no season
        # on file, which flagged the fixture, cost it a confidence tier and
        # threw away its form.
        rating, carried, played, src, prior_name, cur_name = rating_for(team, code)
        prow = prior_tables.get(src, {}).get(prior_name) if src else None
        crow = cur_tables.get(code, {}).get(cur_name) if cur_name else None
        fp = E.form_points(crow)
        adj = ADJUSTMENTS.get(team) or ADJUSTMENTS.get(prior_name) or {}
        out = ((ABSENCES.get(team) or ABSENCES.get(prior_name) or {}).get("out")) or []
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
            # The division these ratings actually come from — distinct from
            # carriedFrom, which is only set when a promoted side's rating
            # crossed divisions. In a cup, every side's rating comes from its
            # own domestic league (there's no table for the cup itself), so
            # this is the one place a reader can see which league a club's
            # stats below actually belong to without already knowing it.
            "league": E.LEAGUES[src]["name"] if src in E.LEAGUES else None,
            "form": fp,
            "adj": {"att": adj.get("att", 1.0), "def": adj.get("def", 1.0),
                    "why": adj.get("why")} if adj else None,
            "out": ([{"name": p.get("name", "unnamed"), "role": p.get("role", "midfield"),
                      "importance": p.get("importance", "key"), "why": p.get("why")}
                     for p in out] if out else None),
            "outFactors": ([round(abs_att, 3), round(abs_def, 3)] if out else None),
            "lastSeason": prior_label.get(src) if prow else None,
            "last": ({"P": prow["P"], "W": prow["W"], "D": prow["D"], "L": prow["L"],
                      "GF": prow["GF"], "GA": prow["GA"], "GD": prow["GD"],
                      "Pts": prow["Pts"], "PPG": prow["PPG"]} if prow else None),
            "now": ({"P": crow["P"], "W": crow["W"], "D": crow["D"], "L": crow["L"],
                     "GF": crow["GF"], "GA": crow["GA"], "GD": crow["GD"],
                     "Pts": crow["Pts"], "PPG": crow["PPG"]} if crow and crow["P"] else None),
        }, rating

    def international_block(team, display_name=None, women=False):
        # Same return shape as team_block, so every downstream line — Celtic's
        # Law reasons, the row dict, the team-sheet card — reads it without
        # caring which path built it. No domestic table exists here, so
        # "last"/"now"/"carriedFrom"/absences are simply always empty rather
        # than faked from something that doesn't apply. display_name lets a
        # youth fixture look "Germany" up in international.json while still
        # showing "Germany U21" on the row.
        r = E.international_rating(team, women=women)
        return {
            "name": display_name or team,
            "att": round(r[0], 3) if r else 1.0,
            "def": round(r[1], 3) if r else 1.0,
            "played": None,
            "unrated": r is None, "worldRank": None,
            "carriedFrom": None, "league": None, "form": None, "adj": None,
            "out": None, "outFactors": None,
            "lastSeason": None, "last": None, "now": None,
        }, {"att": r[0], "def": r[1]} if r else {"att": 1.0, "def": 1.0}

    def unrated_international(name):
        # A youth fixture that didn't clear AGE_POWER_RATIO, or one where a
        # senior rating for either side doesn't exist at all: same shape as
        # every other unrated side, so it's filtered the same way downstream
        # rather than needing its own special case there.
        return {
            "name": name, "att": 1.0, "def": 1.0, "played": None, "unrated": True,
            "carriedFrom": None, "league": None, "form": None, "adj": None,
            "out": None, "outFactors": None, "lastSeason": None, "last": None, "now": None,
        }, {"att": 1.0, "def": 1.0}

    # ---- price the fixtures ------------------------------------------------
    by_day = defaultdict(list)
    dropped_unrated = 0
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
            is_intl = meta.get("international")
            is_youth = meta.get("ageProxy")
            is_women = meta.get("women")
            h_src = domestic_of(r["home"])[0] if meta.get("cup") else None
            a_src = domestic_of(r["away"])[0] if meta.get("cup") else None
            h_league = h_src or code
            a_league = a_src or code
            if is_youth:
                # Only ever priced off the senior gap when that gap is wide
                # enough to trust despite being the wrong players — see
                # engine.age_power_gap. Anything closer, or either side
                # missing a senior rating altogether, comes back unrated and
                # is dropped by the no-data filter below rather than shown
                # on a guess.
                ratio, hsr, asr = E.age_power_gap(r["home"], r["away"], women=is_women)
                if ratio is not None and ratio >= E.AGE_POWER_RATIO:
                    hb, hr = international_block(E.senior_of(r["home"]), display_name=r["home"], women=is_women)
                    ab, ar = international_block(E.senior_of(r["away"]), display_name=r["away"], women=is_women)
                else:
                    hb, hr = unrated_international(r["home"])
                    ab, ar = unrated_international(r["away"])
            elif is_intl:
                hb, hr = international_block(r["home"], women=is_women)
                ab, ar = international_block(r["away"], women=is_women)
            else:
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
            if is_intl:
                # No cross-competition transfer here — both sides are already
                # in international.json's own shared frame — and international
                # goes to a *lower* average than club football's ~1.35, which
                # is exactly why this needs its own mu rather than borrowing
                # a club one: fewer settled defences, more cagey qualifiers.
                intl_mu = E.INTERNATIONAL["mu"] if E.INTERNATIONAL else 1.2
                intl_ha = E.INTERNATIONAL["homeAdvantage"] if E.INTERNATIONAL else 1.2
                neutral = bool(r.get("neutral"))
                saved_h, saved_a = E.HOME_MULT.get(meta["tier"]), E.AWAY_MULT.get(meta["tier"])
                E.HOME_MULT[meta["tier"]] = 1.0 if neutral else intl_ha
                E.AWAY_MULT[meta["tier"]] = 1.0 if neutral else 1.0 / intl_ha
                try:
                    p = E.match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                                              intl_mu, tier=meta["tier"], form_h=fh, form_a=fa)
                finally:
                    E.HOME_MULT[meta["tier"]], E.AWAY_MULT[meta["tier"]] = saved_h, saved_a
                # FIFA world ranking (rankings.py): the points gap re-scores the
                # win pick, tested on 2026 internationals (-0.036 log loss,
                # p(worse) 0.00). Senior men's only: the women's and youth
                # sides are rated differently and were not tested.
                if not is_youth and not is_women:
                    fr_h, fr_a = RK.fifa_team(FIFA, r["home"]), RK.fifa_team(FIFA, r["away"])
                    hb["worldRank"] = fr_h[0] if fr_h else None
                    ab["worldRank"] = fr_a[0] if fr_a else None
                    trip = {"home": p["home"], "draw": p["draw"], "away": p["away"]}
                    pk = max(trip, key=trip.get)
                    if pk != "draw" and fr_h and fr_a:
                        fav, opp = (fr_h, fr_a) if pk == "home" else (fr_a, fr_h)
                        new = RK.adjust_fifa(trip[pk], fav, opp)
                        rest = 1 - trip[pk]
                        for k in trip:
                            p[k] = new if k == pk else (trip[k] * (1 - new) / rest if rest > 0 else 0.0)
                        p["confidence"] = max(p["home"], p["draw"], p["away"])
                        p["rankAdjusted"] = True
            elif meta.get("cup"):
                s_h = E.tie_strength(h_league, code)
                s_a = E.tie_strength(a_league, code)
                cup_mu = (league_mu.get(h_league, 1.35) + league_mu.get(a_league, 1.35)) / 2
                p = E.cup_match(rh, s_h, ra, s_a, cup_mu,
                                tier=meta["tier"], form_h=fh, form_a=fa,
                                frame_k=(E.CONTINENTAL_FRAME_K if E.continental(code) else None))
            else:
                p = E.match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                                          mu, tier=meta["tier"], form_h=fh, form_a=fa)

            if is_intl:
                # "Evidence" and Celtic's Law both describe things specific to
                # a domestic table (games played this season, a division
                # change) that a national team doesn't have. An unrated side
                # here means no history at all, not a thin one — closer to
                # the domestic "carryover" case than "current" or "mixed".
                evidence = "carryover"
                reasons = []
                for t in (hb, ab):
                    if t["unrated"]:
                        reasons.append(f"{t['name']} has no rating on file")
                if is_youth and not reasons:
                    reasons.append(
                        "priced off senior national team ratings, not actual U21 form — "
                        "shown only because the senior gap is wide enough to trust despite that")
                early = False
            else:
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
                # A continental tie between two leagues europe.json has fitted is
                # no longer priced off a guess. On the 2025-26 check season those
                # ties landed at or above the league tiers' own backtest rates
                # (70%+ quoted 77.6%, landed 77.1%), so demoting them a tier would
                # now understate them. Domestic cups, and any tie with a league
                # the fit never saw, still carry the flag.
                fitted_pair = (E.continental(code) and h_src in E.CONTINENTAL_FITTED
                               and a_src in E.CONTINENTAL_FITTED)
                if meta.get("cup") and h_src and a_src and h_src != a_src and not fitted_pair:
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
                    src_code = t["carriedFrom"] or (h_src if side == "home" else a_src) or code
                    if src_code in partial_prior and not t["unrated"]:
                        n, exp, s_used = partial_prior[src_code]
                        reasons.append(f"{t['name']} is rated from a partial season "
                                       f"({n} of ~{exp} matches, {s_used})")
                    if t["adj"]:
                        reasons.append(f"{t['name']} carries a manual override")
                    if t["out"]:
                        n = len(t["out"])
                        big = [p["name"] for p in t["out"] if p["importance"] == "star"]
                        reasons.append(
                            f"{t['name']} {'is' if n == 1 else 'are'} missing {n} player{'' if n == 1 else 's'}"
                            + (f", including {', '.join(big)}" if big else ""))
                early = min(hb["played"], ab["played"]) < 10

            # "Unrated" was a display flag; it's a publish gate now. A
            # fixture where a side has genuinely nothing behind it — no
            # domestic table, no international rating, no senior-proxy gap
            # wide enough to trust — isn't a prediction, it's a coin flip
            # wearing a percentage sign. Better absent from the board than
            # shown and ignored, or worse, mistaken for a real read.
            unrated = hb["unrated"] or ab["unrated"]
            if unrated:
                dropped_unrated += 1
                continue

            by_day[r["date"]].append({
                "league": code, "leagueName": meta["name"], "short": meta["short"],
                "country": meta["country"], "iso": meta["iso"],
                "tier": meta["tier"], "order": meta["order"], "round": r["round"],
                "cup": bool(meta.get("cup")),
                "date": r["date"], "time": r["time"],
                "kickoff": S.kickoff_utc(r, meta["iso"]),
                "home": hb, "away": ab,
                "p": {"h": round(p["home"], 4), "d": round(p["draw"], 4),
                      "a": round(p["away"], 4)},
                "xg": [round(p["xg_home"], 2), round(p["xg_away"], 2)],
                "btts": round(p["btts"], 4),
                "over25": round(p["over25"], 4),
                "score": list(p["likely_score"]),
                "confidence": round(p["confidence"], 4),
                "evidence": evidence,
                "unrated": unrated,
                "rankAdjusted": bool(p.get("rankAdjusted")),
                "celtic": ({"reasons": reasons, "early": early} if reasons else None),
            })

    if dropped_unrated:
        print(f"  {dropped_unrated} fixture(s) dropped: no rating on file for a side "
              f"(unrated is now a publish gate, not just a display flag)", file=sys.stderr)

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

    # Bookmaker prices, beside the model's number. Value is only flagged if
    # odds.py's weekly backtest says the model beats the closing price; see
    # the docstring there for why it is gated rather than trusted.
    odds_meta = {"gate": False, "verdict": None, "source": "football-data.co.uk"}
    if not args.no_odds:
        import odds as O
        olog = []
        try:
            rep = O.refresh_report(log=olog)
            if rep:
                odds_meta.update(gate=bool(rep.get("valueGate")), verdict=rep.get("verdict"),
                                 seasons=rep.get("seasons"))
            live = O.fetch_live(log=olog)
            everything = [g for d in by_day for g in by_day[d]]
            keyed = {(g["league"], g["date"], g["home"]["name"], g["away"]["name"]): g
                     for g in everything}
            joined = O.match(live, [(k, *k) for k in keyed])
            for k, r in joined.items():
                g = keyed[k]
                mp = [g["p"]["h"], g["p"]["d"], g["p"]["a"]]
                g["market"] = O.market_block(r, mp)
                pick = max(range(3), key=lambda i: mp[i])
                if (odds_meta["gate"] and mp[pick] >= O.PICK_MIN and not g["celtic"]
                        and not g["unrated"] and g["market"]["ev"][pick] >= O.EDGE):
                    g["value"] = {"side": "hda"[pick], "ev": g["market"]["ev"][pick],
                                  "price": g["market"]["best"][pick]}
            print(f"odds: {len(live)} priced, {len(joined)} matched to fixtures, "
                  f"value gate {'open' if odds_meta['gate'] else 'closed'}", file=sys.stderr)
        except Exception as e:
            olog.append(f"odds failed: {e}")
        for line in olog[:8]:
            print(f"  ODDS {line}", file=sys.stderr)

    days = []
    for d in sorted(by_day):
        # Every fixture of the day, most one-sided first. A fixture with an
        # unrated side can look confident purely because the placeholder rating
        # flatters the other team, so those rank after every rated one.
        games = sorted(by_day[d], key=lambda g: (g["unrated"], -g["confidence"]))
        for i, g in enumerate(games, 1):
            g["rank"] = i
            g["list"] = list_eligible(g)
            g["accuracy"] = accuracy_for(g["confidence"], E.LEAGUES[g["league"]].get("international"),
                                         g.get("rankAdjusted"))
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
        "odds": odds_meta,
        "list": {"min": LIST_MIN["league"], "minIntl": LIST_MIN["intl"], "backtest": LIST_BACKTEST},
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
             "unrated": g["unrated"],
             # fixed at publication, so the list is graded on what it said
             "list": g["list"],
             # archived so the prices a reader saw can be graded later
             "market": g.get("market"), "value": g.get("value")}
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
