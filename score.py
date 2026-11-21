#!/usr/bin/env python3
"""
Score past predictions against what actually happened.

Every build writes what it predicted to predictions/<date>.json. This reads all
of them, fetches the results that have landed since, and works out how the model
is actually doing: overall, by confidence band, and split by whether the fixture
was flagged under Celtic's Law.

    python3 score.py

Writes record.json for the dashboard to display.

This is the part that makes the project honest. A prediction site that never
checks itself is asking to be believed on nothing, and the numbers here are the
only ones that describe how the model performs in the wild rather than in a
backtest.
"""
import json, os, sys, glob
from collections import defaultdict
from datetime import date, timedelta
from math import log

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

HERE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(HERE, "predictions")
EPS = 1e-9

# How far back to chase results on the live source. openfootball backfills a
# result days after the whistle, which is fine for a season record and useless
# for a page that reviews yesterday. Anything played inside this window and
# still ungraded is worth one ESPN request per competition per date.
LIVE_LOOKBACK = 10

# Days a cached result may sit from a prediction's date and still grade it
# (20 Nov 2026, claude/nominal-date-grading-2026-11-20.md). openfootball dates
# some leagues by round (the Premier League a nominal Saturday, La Liga and
# Brazil's Serie A with no time), so a match played the day after was archived
# under the round's date and never met its result: Crystal Palace v Liverpool,
# archived 7 Nov, played 8 Nov.
NEAR_DAYS = 3

# Results the live source settled, kept between builds (6 Oct 2026). Without
# this a fixture openfootball never backfills (internationals, most ESPN-only
# competitions) was graded only while it sat inside LIVE_LOOKBACK, then fell
# out of the record: 29 Sep's 46 graded games, 14 of them Daily List picks,
# went to 6 on 6 Oct. Lives in current/, which the deploy already commits.
# Its key is "settled", not "rows", so replay.py's freeze of current/ skips it.
SETTLED = os.path.join(HERE, "current", "settled-results.json")
# Every graded fixture, not just the page's last REVIEW_DAYS (8 Oct 2026).
GRADED = os.path.join(HERE, "record-graded.json")


def load_settled(path=SETTLED):
    try:
        doc = json.load(open(path))
    except Exception:
        return {}
    return {(c, d, h, a): (hg, ag) for c, d, h, a, hg, ag in doc.get("settled", [])}


def save_settled(settled, path=SETTLED):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = sorted([list(k) + list(v) for k, v in settled.items()], key=lambda r: (r[1], r[0], r[2]))
    with open(path, "w") as f:
        json.dump({"note": "Live-source results kept by score.py once settled; openfootball wins where it has the game.",
                   "settled": rows}, f, separators=(",", ":"), ensure_ascii=False)

# Days of graded fixtures handed to the dashboard's results board.
REVIEW_DAYS = 14

# The confidence ladder, identical to the one index.html renders. It lives in
# both places because the dashboard has to label a fixture that has not been
# played, and this file has to grade one that has. Change one, change the other.
# Celtic's Law drops a fixture one rung: flagged rows measurably underperform
# their quoted number, so they are not allowed to claim the same tier.
TIERS = [(0.70, 3, "Strong"), (0.62, 2, "Firm"), (0.55, 1, "Lean"), (0.00, 0, "No read")]
# Recalibrated 2025/26 backtest hit rate per tier, shown beside the live rate.
# The page reads the ladder from record.json ("ladder"); its own copy of TIERS
# is only a fallback for a page built without a record, so this is the one
# definition to change (25 Oct 2026).
TIER_BACKTEST = {"Strong": "79%", "Firm": "66%", "Lean": "61%", "No read": "44%"}


def ladder():
    return [{"min": lo, "k": k, "name": name, "was": TIER_BACKTEST[name]} for lo, k, name in TIERS]



def tier_of(confidence, celtic, unrated=False):
    # A side with no rating is priced off a 1.00/1.00 placeholder, so the
    # number is not a read at all, however confident it looks.
    if unrated:
        return TIERS[-1]
    i = next(i for i, (m, _, _) in enumerate(TIERS) if confidence >= m)
    if celtic and i < len(TIERS) - 1:
        i += 1
    return TIERS[i]


def verification(g):
    """How sure we are that an archived price was published before kick-off.

      verified              published before a known kick-off (timezone-aware)
      verified-by-date      no usable kick-off; published before the earliest
                            instant the fixture's date exists anywhere
                            (sources.earliest_start: 10:00 UTC the day before)
      legacy-unverified     no publish time: archived before 2 Oct 2026, when
                            times started being recorded. Graded as before,
                            prices never rewritten, reported separately
      late                  a known kick-off proves the price was published at
                            or after it. Not graded
      timing-unverifiable   no usable kick-off (missing, or without a zone) and
                            published at or after the conservative earliest
                            start, so it cannot be shown to be early. Not
                            graded; not proof of lateness either

    A row with a publish time is never legacy: it is evidenced as early, as
    late, or as unverifiable.
    """
    pub = S.parse_utc(g.get("published"))
    if not pub:
        return "legacy-unverified"
    ko = S.parse_utc(g.get("kickoff"))
    if ko:
        return "verified" if pub < ko else "late"
    return "verified-by-date" if pub < S.earliest_start(g["date"]) else "timing-unverifiable"


EXCLUDED_FROM_GRADING = ("late", "timing-unverifiable")
SKIPPED = {v: [] for v in EXCLUDED_FROM_GRADING}   # (league, date, home, away) refused, last load


def load_predictions():
    """Every fixture ever predicted, keyed so it can be matched to a result.
    Later files win: if a fixture was predicted on several days, the most recent
    build is the one judged, which is the one a reader would have seen."""
    out = {}
    for v in SKIPPED.values():
        del v[:]
    for path in sorted(glob.glob(os.path.join(PRED_DIR, "*.json"))):
        try:
            with open(path) as f:
                archived = json.load(f)
            for g in archived:
                # A price shown to be late, or that cannot be shown to be
                # early, proves nothing: neither is graded.
                v = verification(g)
                if v in EXCLUDED_FROM_GRADING:
                    SKIPPED[v].append((g["league"], g["date"], g["home"], g["away"]))
                    continue
                out[(g["league"], g["date"], g["home"], g["away"])] = g
        except Exception as e:
            print(f"  skipping {os.path.basename(path)}: {e}", file=sys.stderr)
    return out


def load_results(codes, cache=None):
    """Actual scores, from the same fixture lists the predictions came from.
    openfootball backfills results into those files, so no second source is
    needed and nothing has to be scraped."""
    res = {}
    for code in codes:
        season = E.LEAGUES[code].get("season") or E.current_season(code)
        rows, ok = S.fetch_fixtures(code, season, cache)
        if not ok:
            continue
        for r in rows:
            if r["hg"] is None:
                continue
            res[(code, r["date"], r["home"], r["away"])] = (r["hg"], r["ag"])
    return res


def live_results(pending, log=None):
    """Results for fixtures openfootball has not backfilled yet.

    openfootball is the primary source and stays that way: this only runs on
    what it has left ungraded, and only for the last few days, which is exactly
    the window where the backfill lag bites and the review board is empty.

    Returns the same {(code, date, home, away): (hg, ag)} shape as load_results,
    so the caller cannot tell which source settled a fixture.
    """
    cutoff = (E.uk_today() - timedelta(days=LIVE_LOOKBACK)).isoformat()
    today = E.uk_today().isoformat()      # UK day, not UTC (bug 22)
    wanted = defaultdict(list)
    for code, d, home, away in pending:
        if cutoff <= d < today:
            wanted[(code, d)].append((code, d, home, away))

    out = {}
    for (code, d), keys in sorted(wanted.items()):
        day = date.fromisoformat(d)
        # d is a UTC date; ESPN's days are US Eastern. A late kick-off in the
        # Americas dated d is only returned by the previous day's query.
        rows, ok = S.fetch_espn(code, day - timedelta(days=1), day, log=log)
        if not ok:
            continue
        played = [r for r in rows if r["date"] == d and r["hg"] is not None]
        if not played:
            continue
        hpool = {r["home"] for r in played}
        apool = {r["away"] for r in played}
        for key in keys:
            _, _, home, away = key
            h = home if home in hpool else S.match_team(home, hpool)
            a = away if away in apool else S.match_team(away, apool)
            if not h or not a:
                continue
            # Both ends must match the same fixture. A half-match is a wrong
            # match, and a wrong result is worse than no result.
            hit = next((r for r in played if r["home"] == h and r["away"] == a), None)
            if hit:
                out[key] = (hit["hg"], hit["ag"])
    return out


def lag_results(preds, results, today=None, fetch=None, log=None, earlier=None):
    """Results for the AF_LAG leagues (20 Nov 2026): leagues whose openfootball
    file stopped scoring and ESPN cannot score, today the Czech First League.

    The build has scored their table from the API-Football day pool since
    18 Nov (`sources.af_lag_results`, `build.fill_lagging(source=
    "apifootball")`), but wrote nothing to current/, so this grader never saw a
    Czech result after 20 Sep: 41 fixtures from 9 Oct to 8 Nov sat ungraded.
    Same pool, same rules: clubs mapped to the archive's spelling all
    or nothing (Rule 6, `build._map_names`), a prediction graded only from the
    one result of the same home and away clubs on its own date; a result a day
    or two off the archived date goes through `nearby_results` with this pool
    as its source, under that function's guards. Returns {key: (hg, ag)}.
    No key (a local run) or no pool: {}."""
    today = (today or E.uk_today()).isoformat()
    fetch = fetch or S.af_lag_results
    codes = sorted({k[0] for k in preds if k[0] in S.AF_LAG and k not in results and k[1] < today})
    out, pools = {}, {}
    for code in codes:
        season = E.LEAGUES[code].get("season") or E.current_season(code)
        rows, why = fetch(code, season)
        if why:
            if log is not None:
                log.append(f"{code}: API-Football results not used: {why}")
            continue
        played = [x for x in rows if x.get("hg") is not None and x["date"] < today]
        if not played:
            continue
        import build as B
        mapping, bad = B._map_names([{"home": k[2], "away": k[3]} for k in preds if k[0] == code], played)
        if bad:
            if log is not None:
                log.append(f"{code}: API-Football results not used, unmatched: {'; '.join(bad[:5])}")
            continue
        mapped = [dict(x, home=mapping[x["home"]], away=mapping[x["away"]]) for x in played]
        seen = defaultdict(int)
        for x in mapped:
            seen[(x["date"], x["home"], x["away"])] += 1
        for x in mapped:
            key = (code, x["date"], x["home"], x["away"])
            if key in preds and key not in results and seen[key[1:]] == 1:
                out[key] = (x["hg"], x["ag"])
        pools[code] = mapped
    if pools:
        def load(code, season):
            return {i: x for i, x in enumerate(pools.get(code, []))}, None
        merged = dict(results)
        merged.update(out)
        sub = {k: v for k, v in preds.items() if k[0] in pools}
        near = nearby_results(sub, merged, today=date.fromisoformat(today), load=load, earlier=earlier)
        for k in near:
            preds[k] = sub[k]   # an earlier copy nearby_results chose, if any
        out.update(near)
    if log is not None and out:
        log.append(f"{len(out)} graded from API-Football results ({', '.join(sorted(pools))})")
    return out


_COPIES = {}   # archive file path -> {key: row}, read once a process by earlier_copy


def earlier_copy(key, before, pred_dir=None, back=10):
    """The latest archived copy of a prediction published before `before` (an
    ISO date, UTC day start), or None (21 Nov 2026).

    `load_predictions` keeps the last build's copy of every fixture. A match
    played the day before its archived round date (La Liga and the Süper Lig
    archived under 8 Nov, played 6 and 7 Nov) was refused by `nearby_results`
    when that last copy was written on the match day itself, as its real
    kick-off is unknown, even though the build the evening before had
    published the same fixture. This finds that earlier copy, read from the
    archive files dated before `before`, newest first, at most `back` days
    back; only a copy `verification` grades, published before `before`."""
    pred_dir = pred_dir or PRED_DIR
    end = date.fromisoformat(before)
    for i in range(1, back + 1):
        path = os.path.join(pred_dir, f"{(end - timedelta(days=i)).isoformat()}.json")
        if path not in _COPIES:
            try:
                with open(path) as f:
                    _COPIES[path] = {(g["league"], g["date"], g["home"], g["away"]): g for g in json.load(f)}
            except Exception:
                _COPIES[path] = {}
        g = _COPIES[path].get(tuple(key))
        if g and verification(g) not in EXCLUDED_FROM_GRADING and (g.get("published") or "~") < before:
            return g
    return None


def _runs(keys, gap):
    """Keys sorted by date and split where consecutive dates sit more than
    `gap` days apart."""
    runs, last = [], None
    for k in sorted(keys, key=lambda k: k[1]):
        d = date.fromisoformat(k[1])
        if last is None or (d - last).days > gap:
            runs.append([])
        runs[-1].append(k)
        last = d
    return runs


def _owned(code, x, k, preds):
    """True when a prediction other than `k` sits on the result's own date for
    the same clubs, under any spelling (21 Nov 2026): the Süper Lig's October
    rounds were archived twice, once under ESPN's spelling on the real date
    (Caykur Rizespor v Fenerbahce, 10 Oct) and once under openfootball's on
    the round date (Çaykur Rizespor v Fenerbahçe, 11 Oct), so the exact-name
    check alone would have graded the round-date copy as well."""
    if (code, x["date"], k[2], k[3]) in preds and (code, x["date"], k[2], k[3]) != k:
        return True
    for o in preds:
        if o[0] == code and o[1] == x["date"] and o != k and (
                S.match_team(x["home"], {o[2]}) and S.match_team(x["away"], {o[3]})):
            return True
    return False


def _claim_run(code, keys, preds, cached, today, window, earlier, claims, log):
    """`nearby_results` for one run of pending keys: adds (key, result, copy)
    to `claims` by result, returns how many were left out as late."""
    # Only results a pending prediction could claim take part (21 Nov 2026):
    # the 2026-27 Segunda cache still held June's promotion play-offs
    # (Málaga, since promoted), so every es.2 result was refused on a club
    # the league's archive no longer has. All or nothing on names still
    # holds over the results that matter.
    days = [date.fromisoformat(k[1]) for k in keys]
    played = [x for x in (cached or {}).values() if x.get("hg") is not None and x["date"] < today
              and any(abs((date.fromisoformat(x["date"]) - d).days) <= window for d in days)]
    if not played:
        return 0
    import build as B
    lo = min(date.fromisoformat(x["date"]) for x in played) - timedelta(days=window)
    hi = max(date.fromisoformat(x["date"]) for x in played) + timedelta(days=window)
    rows = [k for k in preds if k[0] == code]
    near_rows = [{"home": k[2], "away": k[3]} for k in rows if lo <= date.fromisoformat(k[1]) <= hi]
    mapping, bad = B._map_names(near_rows, played)
    if bad:
        # A club the archive has no row for near these dates (a fixture the
        # build never published) takes the whole season's spelling, as before
        # 21 Nov; a near spelling, once found, always wins.
        whole, _ = B._map_names([{"home": k[2], "away": k[3]} for k in rows], played)
        mapping = {n: mapping.get(n) or whole.get(n) for n in whole}
        seen = defaultdict(list)
        for n, v in mapping.items():
            if v is not None:
                seen[v].append(n)
        bad = sorted([n for n, v in mapping.items() if v is None]
                     + [f"{'/'.join(v)} -> {t}" for t, v in seen.items() if len(v) > 1])
    if bad:
        if log is not None:
            log.append(f"{code}: cached results not used, unmatched: {'; '.join(bad[:5])}")
        return 0
    by_pair = defaultdict(list)
    for x in played:
        by_pair[(mapping[x["home"]], mapping[x["away"]])].append(x)
    late = 0
    for k in keys:
        d = date.fromisoformat(k[1])
        near = [x for x in by_pair.get((k[2], k[3]), [])
                if abs((date.fromisoformat(x["date"]) - d).days) <= window]
        if len(near) != 1:
            continue
        x = near[0]
        if _owned(code, x, k, preds):
            continue
        copy = None
        if x["date"] < k[1] and not (preds[k].get("published") or "~") < x["date"]:
            copy = earlier(k, x["date"]) if earlier else None
            if copy is None:
                late += 1
                continue
        claims[(x["date"], k[2], k[3])].append((k, x, copy))
    return late


def nearby_results(preds, results, today=None, window=NEAR_DAYS, load=None, log=None, earlier=None):
    """Results for predictions archived under a round's nominal date.

    Reads the season-so-far cache the build commits in current/ (ESPN results,
    ESPN spelling) for each league with an ungraded, past prediction, maps the
    clubs to the archive's spelling all or nothing (Rule 6, `build._map_names`)
    and grades a prediction from the one result of the same home and away
    clubs within `window` days. Refused, so nothing is graded twice and no
    late price is graded:
    - a result whose own date has a prediction of the same pair (that row owns
      it: the copy retimed from API-Football, or the build that had the date);
    - a result two predictions could claim, or a prediction two results could;
    - a match played before the archived date when the prediction was not
      published before that day began (UTC): its real kick-off is unknown, so
      the price cannot be shown to be early. With `earlier` (`earlier_copy`;
      21 Nov 2026) the last copy published before that day is graded instead
      and put in `preds` in place of the later copy, so the row judged is the
      price shown in advance.
    Returns {prediction key: (hg, ag)}."""
    today = (today or E.uk_today()).isoformat()
    load = load or S.load_current
    pending = defaultdict(list)
    for k in preds:
        if k not in results and k[1] < today:
            pending[k[0]].append(k)
    out, late, earlier_n = {}, 0, 0
    for code, keys in sorted(pending.items()):
        meta = E.LEAGUES.get(code) or {}
        if meta.get("cup") or meta.get("international"):
            continue
        cached, _ = load(code, meta.get("season") or E.current_season(code))
        # Pending predictions in runs of nearby dates, each read on its own
        # (21 Nov 2026): the Süper Lig was archived under ESPN's spelling
        # until October (Eyupspor, Amed SFK) and openfootball's since
        # (Eyüpspor, Amed), so names mapped over the whole season sent each
        # club to its old spelling and November's rows never met their
        # results. Each run maps names over the predictions archived near its
        # own results only.
        claims = defaultdict(list)
        for run in _runs(keys, window):
            late += _claim_run(code, run, preds, cached, today, window, earlier, claims, log)
        for got in claims.values():
            if len(got) == 1:
                k, x, copy = got[0]
                out[k] = (x["hg"], x["ag"])
                if copy is not None:
                    preds[k] = copy
                    earlier_n += 1
    if log is not None and (out or late):
        log.append(f"{len(out)} graded from a result dated off the archive's round date"
                   + (f" ({earlier_n} from an earlier copy published before the match day)" if earlier_n else "")
                   + f"; {late} left out (played earlier than archived, price not shown to be early)")
    return out


def won(r):
    """The strict test: the top pick landed. This is what the headline
    accuracy, the tier hit rates and the band tables use (25 Oct 2026, bug 3
    of claude/full-review-2026-10-25.md: 4,658 rows carried a level likely
    score, and their "ok" rate was 71.6% while their pick won 44.8%)."""
    return r["pick"] == r["actual"]


def correct(r):
    """A reading is right when the top pick landed, or when the predicted
    scoreline was a draw and the game was drawn (Douglas, 6 Oct 2026: a 1-1
    call on a game that ends level is a correct reading). Reported as the
    separately labelled "reads" figure; never the headline."""
    return won(r) or (r["actual"] == "d" and score_draw(r))


def score_draw(r):
    sc = r.get("score") or (-1, -1)
    return sc[0] >= 0 and sc[0] == sc[1]


def expected(r):
    """The chance of `correct(r)` on the model's own numbers: the top pick,
    plus the draw when the predicted scoreline is a draw. Keeps the quoted
    side of the reads comparison on the same footing as its landed side.
    The strict comparison quotes `confidence` itself."""
    extra = r["p"][1] if score_draw(r) and r["pick"] != "d" else 0.0
    return r["confidence"] + extra


def rate(k, n):
    return round(k / n, 4) if n else None


def bands5(rows, lo=0.50, step=0.05):
    """Quoted v landed in 5-point bands from `lo` to 100%, for the Analysis
    page (6 Oct 2026). "won" is the top pick landing, strictly; "read" adds the
    draw readings (correct()), and each has its own quoted figure so neither
    comparison is flattered. The top band includes 100%."""
    out = []
    edges = [round(lo + i * step, 2) for i in range(int(round((1 - lo) / step)))]
    for a in edges:
        b = round(a + step, 2)
        g = [r for r in rows if a <= r["confidence"] < b or (b >= 1.0 and r["confidence"] >= 1.0)]
        L = [r for r in g if r.get("list")]
        n = len(g)
        out.append({
            "from": a, "to": b, "n": n,
            "won": sum(1 for r in g if r["pick"] == r["actual"]),
            "read": sum(1 for r in g if correct(r)),
            "quoted": round(sum(r["confidence"] for r in g) / n, 4) if n else None,
            "quotedRead": round(sum(expected(r) for r in g) / n, 4) if n else None,
            "draws": sum(1 for r in g if r["actual"] == "d"),
            "listN": len(L), "listWon": sum(1 for r in L if r["pick"] == r["actual"]),
        })
    return out


def by_day(rows):
    """One line per graded day, oldest first: games, top picks won, readings
    right, the average quoted chance, the same for 60%+ calls, and the
    counts per 5-point band (b5) for the page's bracket picker."""
    d = defaultdict(list)
    for r in rows:
        d[r["date"]].append(r)
    out = []
    for k in sorted(d):
        g = d[k]
        h = [r for r in g if r["confidence"] >= 0.60]
        out.append({"date": k, "n": len(g),
                    "won": sum(1 for r in g if r["pick"] == r["actual"]),
                    "read": sum(1 for r in g if correct(r)),
                    "draws": sum(1 for r in g if r["actual"] == "d"),
                    "quoted": round(sum(r["confidence"] for r in g) / len(g), 4),
                    "n60": len(h), "won60": sum(1 for r in h if r["pick"] == r["actual"]),
                    # per 5-point band from 0%: [games, won, read right, quoted sum, draws],
                    # so the page can show any bracket the reader picks
                    "b5": day_bands(g)})
    return out


def day_bands(g):
    out = [[0, 0, 0, 0.0, 0] for _ in range(20)]
    for r in g:
        i = min(19, max(0, int(r["confidence"] * 20 + 1e-9)))
        c = out[i]
        c[0] += 1
        c[1] += r["pick"] == r["actual"]
        c[2] += bool(correct(r))
        c[3] += r["confidence"]
        c[4] += r["actual"] == "d"
    return [[a, b, c, round(q, 4), d] for a, b, c, q, d in out]


def model_card(rows=()):
    """The live model's settings, read from engine.py, calibration.json and
    the build's data.json, so the Analysis page can never describe a model
    the site is not running."""
    card = {"shrink": E.SHRINK_FULL_SEASON, "blendK": E.BLEND_K, "formMax": E.FORM_MAX,
            "rho": E.RHO, "temperature": E.TEMPERATURE,
            "homeMult": E.HOME_MULT.get(1), "awayMult": E.AWAY_MULT.get(1),
            "attBounds": list(E.ATT_BOUNDS), "defBounds": list(E.DEF_BOUNDS),
            # competitions with at least one graded game, not the size of the
            # league table (which carries cups and leagues with no fixtures yet)
            "competitions": len({r["league"] for r in rows})}
    try:
        cal = json.load(open(os.path.join(HERE, "calibration.json")))
        card["calibration"] = {"a": cal["a"], "b": cal["b"], "fitted": cal.get("fitted")}
    except Exception:
        card["calibration"] = None
    try:
        card["list"] = json.load(open(os.path.join(HERE, "data.json"))).get("list")
    except Exception:
        card["list"] = None
    return card


def form_index(results):
    """{(code, team): [(date, opp, gf, ga, home)]} from the graded results, for
    the form lines on "How it went" (6 Oct 2026). Same-competition games only:
    that is all the results dict holds, and the page says so."""
    idx = defaultdict(list)
    for (code, d, home, away), (hg, ag) in results.items():
        idx[(code, home)].append((d, away, hg, ag, True))
        idx[(code, away)].append((d, home, ag, hg, False))
    for v in idx.values():
        v.sort()
    return idx


def team_form(idx, code, team, before, n=5):
    """The last n results before `before`, newest first, as the page's form rows."""
    out = []
    for d, opp, gf, ga, home in reversed(idx.get((code, team), [])):
        if d >= before:
            continue
        out.append({"r": "W" if gf > ga else "L" if gf < ga else "D", "score": f"{gf}-{ga}",
                    "opp": opp, "home": home, "date": d})
        if len(out) == n:
            break
    return out


def summarise(rows):
    if not rows:
        return None
    n = len(rows)
    idx = {"h": 0, "d": 1, "a": 2}
    # "correct" / "accuracy" are strict since 25 Oct 2026: the top pick landed.
    # The draw-read figure, which until then was the headline, is "reads" /
    # "readRate" (with "quotedRead" as its own quoted side).
    hit = sum(1 for r in rows if won(r))
    reads = sum(1 for r in rows if correct(r))
    ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in rows) / n
    home = sum(1 for r in rows if r["actual"] == "h") / n
    exact = sum(1 for r in rows if r["score"] == r["result"])
    # Where the misses actually come from. The model almost never picks a draw,
    # so a draw is a guaranteed loss on the top pick, and counting them is the
    # difference between "we got it wrong" and knowing why.
    drawn = sum(1 for r in rows if r["actual"] == "d" and not won(r))
    draw_reads = sum(1 for r in rows if r["actual"] == "d" and r["pick"] != "d" and score_draw(r))
    picks = {k: sum(1 for r in rows if r["pick"] == k) for k in "hda"}
    actual = {k: sum(1 for r in rows if r["actual"] == k) for k in "hda"}
    return {"n": n, "correct": hit, "accuracy": rate(hit, n), "won": hit,
            "reads": reads, "readRate": rate(reads, n),
            "quoted": round(sum(r["confidence"] for r in rows) / n, 4),
            "quotedRead": round(sum(expected(r) for r in rows) / n, 4),
            "logLoss": round(ll, 4), "homeRate": round(home, 4),
            "exactScores": exact, "exactRate": round(exact / n, 4),
            "drawnOut": drawn, "drawReads": draw_reads, "picks": picks, "actuals": actual}


def tier_table(rows):
    """Live hit rate for each rung of the confidence ladder.

    This is the number that matters most on the review board. The tier labels
    were fitted on a backtest of last season; this says whether they have held
    up on fixtures the site published in advance, which is a much harder test.
    """
    out = []
    for lo, k, name in TIERS:
        g = [r for r in rows if tier_of(r["confidence"], r["celtic"], r["unrated"])[2] == name]
        if not g:
            continue
        w, rd = sum(1 for r in g if won(r)), sum(1 for r in g if correct(r))
        out.append({
            "name": name, "k": k, "min": lo, "n": len(g),
            # strict (the top pick landed) since 25 Oct 2026; the draw reads
            # are the separate "reads" / "readHit" / "expectedRead"
            "correct": w, "hit": rate(w, len(g)),
            "expected": round(sum(r["confidence"] for r in g) / len(g), 4),
            "reads": rd, "readHit": rate(rd, len(g)),
            "expectedRead": round(sum(expected(r) for r in g) / len(g), 4),
            "drawnOut": sum(1 for r in g if r["actual"] == "d" and not won(r)),
        })
    return out


def graded_rows(save=True):
    """Every archived prediction that has a result, graded: (preds, rows,
    results). The record below is built from these. save=False leaves the
    settled-results cache untouched."""
    preds = load_predictions()
    if not preds:
        return preds, [], {}

    codes = sorted({k[0] for k in preds})
    results = load_results(codes)

    # Results settled by an earlier build fill what openfootball lacks.
    settled = load_settled()
    kept = {k: v for k, v in settled.items() if k in preds and k not in results}
    results.update(kept)
    # API-Football cup results come from a rolling date pool (sources.
    # af_cup_pool), so they are kept the moment they land, as the live
    # source's are, or they would drop out of the record after 12 days.
    cup_new = {k: v for k, v in results.items()
               if E.LEAGUES.get(k[0], {}).get("afCup") and settled.get(k) != v}
    if cup_new:
        settled.update(cup_new)
        if save:
            save_settled(settled)

    # Anything played but not yet backfilled gets one pass at the live source.
    pending = [k for k in preds if k not in results]
    tried = []
    live = live_results(pending, log=tried)
    for line in tried:
        print(f"    espn {line}", file=sys.stderr)
    if live:
        print(f"  live source settled {len(live)} fixture(s) openfootball has "
              f"not backfilled yet", file=sys.stderr)
    results.update(live)
    if live:
        settled.update(live)
        if save:
            save_settled(settled)

    # Leagues the build scores from API-Football (sources.AF_LAG, 20 Nov 2026).
    # Kept in the settled cache like a live result, as the cup results are,
    # so a match stays graded once the day pool has rolled past it.
    note = []
    lag = lag_results(preds, results, log=note, earlier=earlier_copy)
    for line in note:
        print(f"  {line}", file=sys.stderr)
    if lag:
        results.update(lag)
        settled.update(lag)
        if save:
            save_settled(settled)

    # A match played a day or two off its archived round date (20 Nov 2026).
    note = []
    near = nearby_results(preds, results, log=note, earlier=earlier_copy)
    for line in note:
        print(f"  {line}", file=sys.stderr)
    if near:
        results.update(near)
        settled.update(near)
        if save:
            save_settled(settled)

    # 10 Nov 2026: the green Edge flag (groupings.edge_flag). A row archived
    # with an "edge" key carried the flag as published ("live", from 10 Nov);
    # earlier rows are flagged from the prices archived with them before
    # kick-off ("replayed": the rule applied to what the page showed).
    try:
        import groupings as GR
        flag_of = GR.edge_flag
    except Exception:
        flag_of = lambda g: None
    rows = []
    for key, g in preds.items():
        if key not in results:
            continue
        hg, ag = results[key]
        actual = "h" if hg > ag else ("a" if ag > hg else "d")
        p = (g["p"]["h"], g["p"]["d"], g["p"]["a"])
        pick = max((p[0], "h"), (p[1], "d"), (p[2], "a"))[1]
        rows.append({
            "league": g["league"], "date": g["date"],
            "home": g["home"], "away": g["away"],
            "p": p, "pick": pick, "actual": actual,
            # 25 Oct 2026: the published top probability, not the stored
            # "confidence". Until 24 Oct domestic cup rows (afc.*) stored the
            # untempered number beside tempered probabilities (Berkhamsted:
            # 80% beside 61%), which put them in the wrong bands and tiers
            # on the record and the Analysis page. max(p) is what the row
            # showed as its pick's chance; for every other row the two agree.
            "confidence": max(p), "celtic": bool(g.get("celtic")),
            "unrated": bool(g.get("unrated")),
            "verified": verification(g),
            "list": bool(g.get("list")), "reserve": bool(g.get("reserve")),
            "score": tuple(g.get("score") or (-1, -1)), "result": (hg, ag),
            "published": g.get("published"), "kickoff": g.get("kickoff"),
            "edge": edge_of(g, flag_of),
        })
    # One row per match (21 Nov 2026, #464): a match archived under two
    # spellings is graded once.
    rows, pairs = drop_duplicates(rows)
    DUPLICATES[:] = pairs
    if pairs:
        print(f"  {len(pairs)} graded twice under two spellings, counted once", file=sys.stderr)
    return preds, rows, results


DUPLICATES = []   # (kept, dropped) row pairs, last graded_rows


def _same_club(a, b):
    """Two spellings of one club, both ways (Southend United / Southend)."""
    return a == b or bool(S.match_team(a, {b}) and S.match_team(b, {a}))


def distinct_names(rows, window=NEAR_DAYS):
    """{league: {frozenset((a, b))}} of names the archive shows are two clubs:
    they met each other, or one build published both, within `window` days,
    against opponents that are not one club (Managua and UNAN Managua, which
    `match_team` would join: Managua v UNAN Managua, 2 Nov 2026)."""
    out = defaultdict(set)
    builds = defaultdict(list)
    for r in rows:
        out[r["league"]].add(frozenset((r["home"], r["away"])))
        if r.get("published"):
            builds[(r["league"], r["published"])].append(r)
    for (lg, _), rs in builds.items():
        for i, a in enumerate(rs):
            da = date.fromisoformat(a["date"])
            for b in rs[i + 1:]:
                if abs((date.fromisoformat(b["date"]) - da).days) > window:
                    continue
                for x, xo in ((a["home"], a["away"]), (a["away"], a["home"])):
                    for y, yo in ((b["home"], b["away"]), (b["away"], b["home"])):
                        if x != y and xo != yo and not _same_club(xo, yo):
                            out[lg].add(frozenset((x, y)))
    return out


def drop_duplicates(rows, window=NEAR_DAYS):
    """One graded row per match (21 Nov 2026, #464).

    `load_predictions` keys on names, so a match archived under two spellings
    (ESPN's and openfootball's, or an API-Football short form) on the same day
    or a round date apart was graded twice: 24 copies on the record at 21 Nov
    (National League, India, the Süper Lig, J1...). Two rows are one match when
    they share a league, sit within `window` days, carry the same final score
    and both clubs match under `match_team` both ways, home and away in the
    same order. The copy kept is a Daily List copy, else a reserve copy, so
    no list pick leaves the list's record, then the one published earliest
    (the price shown first in advance), then the earlier date. Flags are never
    moved between copies. Returns (kept rows, [(kept, dropped)])."""
    by = defaultdict(list)
    for i, r in enumerate(rows):
        by[(r["league"], tuple(r["result"]))].append(i)
    apart = distinct_names(rows, window)
    drop, pairs = set(), []

    def order(i):
        r = rows[i]
        return (not r.get("list"), not r.get("reserve"), r.get("published") or "~",
                r["date"], r["home"], r["away"])

    for idx in by.values():
        if len(idx) < 2:
            continue
        idx = sorted(idx, key=order)
        for a_pos, a in enumerate(idx):
            if a in drop:
                continue
            ra = rows[a]
            da = date.fromisoformat(ra["date"])
            for b in idx[a_pos + 1:]:
                if b in drop:
                    continue
                rb = rows[b]
                if (ra["home"], ra["away"]) == (rb["home"], rb["away"]) and ra["date"] == rb["date"]:
                    continue
                if abs((date.fromisoformat(rb["date"]) - da).days) > window:
                    continue
                lg = ra["league"]
                if any(frozenset((x, y)) in apart.get(lg, ()) for x, y in
                       ((ra["home"], rb["home"]), (ra["away"], rb["away"])) if x != y):
                    continue
                if _same_club(ra["home"], rb["home"]) and _same_club(ra["away"], rb["away"]):
                    drop.add(b)
                    pairs.append((ra, rb))
    return [r for i, r in enumerate(rows) if i not in drop], pairs


def edge_of(g, flag_of):
    """The Edge flag a row carried (live) or would have carried on its
    archived prices (replayed), compact, or None."""
    live = "edge" in g
    e = g.get("edge") if live else flag_of(g)
    if not e: return None
    # rule: 1 = opposition 9+ (to 10 Nov), 2 = opposition 5.0+ / 4/1 (11 Nov 2026);
    # a live row before rule 2 carries no rule key and was published under 1
    return {"side": e["side"], "odds": e["odds"], "best": e["best"], "fair": e["fair"], "live": live,
            "rule": e.get("rule") or 1, "opp": e.get("opp")}


def edge_record(rows):
    """The Edge flag's record: landed against the bookmakers' chance, return
    per unit at the average and the best archived price, all flagged rows
    and the live ones alone (10 Nov 2026)."""
    def tally(rs):
        if not rs: return {"n": 0}
        n = len(rs); w = sum(r["actual"] == r["edge"]["side"] for r in rs)
        q = sum(r["edge"]["fair"] for r in rs)
        ret = sum(r["edge"]["odds"] for r in rs if r["actual"] == r["edge"]["side"])
        best = sum(r["edge"]["best"] for r in rs if r["actual"] == r["edge"]["side"])
        return {"n": n, "won": w, "expected": round(q, 2), "landed": rate(w, n), "quoted": round(q / n, 4),
                "return": round(ret / n - 1, 4), "returnBest": round(best / n - 1, 4),
                "from": min(r["date"] for r in rs), "to": max(r["date"] for r in rs)}
    fl = [r for r in rows if r.get("edge")]
    rules = sorted({r["edge"].get("rule") or 1 for r in fl})
    # 21 Nov 2026 (Douglas: "a visual tracker performance graph" under the
    # Bets tab's Edge picks): every graded flagged pick by day, oldest first,
    # compact: [side backed, opponent, average, best, won 1/0, live 1/0, opposition price].
    days = {}
    for r in sorted(fl, key=lambda r: (r["date"], r.get("kickoff") or "", r.get("home") or "")):
        e = r["edge"]; h = e["side"] == "h"; hn, an = r.get("home") or "", r.get("away") or ""
        days.setdefault(r["date"], []).append([hn if h else an, an if h else hn,
                                              e["odds"], e["best"], int(r["actual"] == e["side"]), int(bool(e["live"])), e.get("opp")])
    return {"all": tally(fl), "live": tally([r for r in fl if r["edge"]["live"]]),
            "days": [{"d": d, "p": p} for d, p in sorted(days.items())],
            "byRule": {str(k): tally([r for r in fl if (r["edge"].get("rule") or 1) == k]) for k in rules},
            "rule": __import__("groupings").EDGE_RULE if fl else None}



def main():
    preds, rows, results = graded_rows()
    if not preds:
        print("no predictions archived yet", file=sys.stderr)
        json.dump({"generated": None, "graded": 0, "overall": None},
                  open(os.path.join(HERE, "record.json"), "w"))
        return

    if not rows:
        print(f"{len(preds)} predictions archived, none resolved yet", file=sys.stderr)

    # confidence bands: does a 70% call actually land 70% of the time?
    bands = []
    for lo, hi in [(0.0, 0.40), (0.40, 0.50), (0.50, 0.60), (0.60, 0.70), (0.70, 1.01)]:
        g = [r for r in rows if lo <= r["confidence"] < hi]
        if g:
            w, rd = sum(1 for r in g if won(r)), sum(1 for r in g if correct(r))
            bands.append({
                "from": lo, "to": min(hi, 1.0), "n": len(g),
                # strict since 25 Oct 2026; reads kept apart
                "hit": rate(w, len(g)), "won": w,
                "expected": round(sum(r["confidence"] for r in g) / len(g), 4),
                "reads": rd, "readHit": rate(rd, len(g)),
                "expectedRead": round(sum(expected(r) for r in g) / len(g), 4),
            })

    per_league = {}
    byl = defaultdict(list)
    for r in rows:
        byl[r["league"]].append(r)
    for c, g in byl.items():
        per_league[c] = {"name": f"{E.LEAGUES[c]['country']} {E.LEAGUES[c]['name']}",
                         **summarise(g)}

    recent = sorted(rows, key=lambda r: r["date"], reverse=True)[:40]

    # ---- the review board --------------------------------------------------
    # One entry per day, most recent first, carrying every graded fixture on it
    # rather than a sample. The point of the board is to be able to read a whole
    # day back and see which tier the misses came from, so a truncated list
    # would defeat it.
    # Form lines also read the season-so-far cache (current/), which holds the
    # ESPN-sourced leagues openfootball does not.
    form_res = {}
    for path in glob.glob(os.path.join(HERE, "current", "*.json")):
        code = os.path.basename(path).split("-")[0]
        try:
            for x in json.load(open(path)).get("rows", []):
                if x.get("hg") is not None:
                    form_res[(code, x["date"], x["home"], x["away"])] = (x["hg"], x["ag"])
        except Exception:
            continue
    form_res.update(results)
    fidx = form_index(form_res)

    def game_row(r):
        _, k, name = tier_of(r["confidence"], r["celtic"], r["unrated"])
        return {"league": r["league"], "home": r["home"], "away": r["away"],
                "p": [round(x, 4) for x in r["p"]], "pick": r["pick"],
                "actual": r["actual"], "confidence": r["confidence"],
                "celtic": r["celtic"], "tier": name, "k": k,
                "predScore": list(r["score"]), "result": list(r["result"]),
                "list": r["list"], "reserve": r["reserve"], "ok": correct(r), "won": won(r),
                # 10 Nov 2026: the kick-off, for "Days at a glance" on How it went
                "kickoff": r.get("kickoff"),
                "drawRead": r["actual"] == "d" and r["pick"] != "d" and score_draw(r),
                "formH": team_form(fidx, r["league"], r["home"], r["date"]),
                "formA": team_form(fidx, r["league"], r["away"], r["date"])}

    by_date = defaultdict(list)
    for r in rows:
        by_date[r["date"]].append(r)
    review = []
    for d in sorted(by_date, reverse=True)[:REVIEW_DAYS]:
        g = sorted(by_date[d], key=lambda r: -r["confidence"])
        review.append({"date": d, **summarise(g), "tiers": tier_table(g),
                       "games": [game_row(r) for r in g]})

    payload = {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "archived": len(preds),
        "graded": len(rows),
        "overall": summarise(rows),
        # Publication-time evidence for every graded prediction, overall and
        # for the Daily List. "legacy-unverified" is the archive from before
        # publish/kick-off times were recorded (2 Oct 2026).
        "verification": {
            "all": {v: sum(1 for r in rows if r["verified"] == v)
                    for v in ("verified", "verified-by-date", "legacy-unverified")},
            "list": {v: sum(1 for r in rows if r["verified"] == v and r.get("list"))
                     for v in ("verified", "verified-by-date", "legacy-unverified")},
            # archived prices not graded: proven late, or timing unverifiable
            "late": len(set(SKIPPED["late"])),
            "timingUnverifiable": len(set(SKIPPED["timing-unverifiable"])),
            # one match archived under two spellings, graded once (#464)
            "duplicates": len(DUPLICATES),
        },
        "settled": summarise([r for r in rows if not r["celtic"]]),
        "celtic": summarise([r for r in rows if r["celtic"]]),
        "bands": bands,
        # Analysis page (6 Oct 2026): 5-point bands from 50%, per-day results,
        # the graded date range and the live model's settings.
        "bands5": bands5(rows),
        "byDay": by_day(rows),
        "range": {"from": min((r["date"] for r in rows), default=None),
                  "to": max((r["date"] for r in rows), default=None)},
        "model": model_card(rows),
        "ladder": ladder(),
        "tiers": tier_table(rows),
        # 10 Nov 2026: the green Edge flag's own record (edge_record)
        "edge": edge_record(rows),
        # The Daily List on its own. Only fixtures archived with the flag set,
        # which means from the day the list was first published: membership is
        # never worked out afterwards from the numbers, because the list is
        # judged on what it actually said before kick-off.
        "list": summarise([r for r in rows if r["list"]]),
        "listDays": [{"date": d, "games": [game_row(r) for r in by_date[d] if r["list"]]}
                     for d in sorted(by_date, reverse=True)[:REVIEW_DAYS]
                     if any(r["list"] for r in by_date[d])],
        # The list's reserve (below the bar, Firm or better), from 30 Sep 2026:
        # graded as its own group and by strength tag, never mixed into the
        # list's record above.
        "reserve": summarise([r for r in rows if r["reserve"]]),
        "reserveTiers": tier_table([r for r in rows if r["reserve"]]),
        "days": review,
        "byLeague": per_league,
        "recent": [{"date": r["date"], "league": r["league"], "home": r["home"],
                    "away": r["away"], "p": r["p"], "pick": r["pick"],
                    "actual": r["actual"], "confidence": r["confidence"],
                    "celtic": r["celtic"], "predScore": list(r["score"]),
                    "result": list(r["result"]),
                    "ok": correct(r), "won": won(r)} for r in recent],
    }
    json.dump(payload, open(os.path.join(HERE, "record.json"), "w"),
              separators=(",", ":"))
    # Every graded fixture in full (record.json keeps REVIEW_DAYS of them for
    # the page). Read by tools/julius_export.py; the page never loads it.
    with open(GRADED, "w") as f:
        json.dump({"generated": payload["generated"], "graded": [
            {**r, "p": list(r["p"]), "score": list(r["score"]), "result": list(r["result"]),
             "tier": tier_of(r["confidence"], r["celtic"], r["unrated"])[2],
             "ok": correct(r), "won": won(r),
             "drawRead": r["actual"] == "d" and r["pick"] != "d" and score_draw(r),
             "expected": round(expected(r), 4)}
            for r in sorted(rows, key=lambda r: (r["date"], r["league"], r["home"]))],
            # the second copy of a match archived under two spellings, with the
            # copy graded in its place (#464); the ledger reads these
            "duplicates": [{"league": b["league"], "date": b["date"], "home": b["home"], "away": b["away"],
                            "kept": [a["date"], a["home"], a["away"]]}
                           for a, b in sorted(DUPLICATES, key=lambda p: (p[1]["date"], p[1]["league"], p[1]["home"]))]},
            f, separators=(",", ":"), ensure_ascii=False)

    o = payload["overall"]
    if o:
        print(f"graded {o['n']} fixtures: {o['accuracy']:.1%} picked the winner "
              f"(home baseline {o['homeRate']:.1%}; {o['readRate']:.1%} counting draw reads), "
              f"log loss {o['logLoss']}, {o['exactScores']} exact scorelines", file=sys.stderr)
        if payload["celtic"] and payload["settled"]:
            print(f"  settled {payload['settled']['accuracy']:.1%} vs "
                  f"flagged {payload['celtic']['accuracy']:.1%}", file=sys.stderr)


if __name__ == "__main__":
    main()
