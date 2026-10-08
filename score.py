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
        season = E.LEAGUES[code].get("season", "2026-27")
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
    cutoff = (date.today() - timedelta(days=LIVE_LOOKBACK)).isoformat()
    today = date.today().isoformat()
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


def correct(r):
    """A reading is right when the top pick landed, or when the predicted
    scoreline was a draw and the game was drawn (Douglas, 6 Oct 2026: a 1-1
    call on a game that ends level is a correct reading)."""
    return r["pick"] == r["actual"] or (r["actual"] == "d" and score_draw(r))


def score_draw(r):
    sc = r.get("score") or (-1, -1)
    return sc[0] >= 0 and sc[0] == sc[1]


def expected(r):
    """The chance of `correct(r)` on the model's own numbers: the top pick,
    plus the draw when the predicted scoreline is a draw. Keeps the quoted
    side of every quoted-vs-landed comparison on the same footing as the
    landed side."""
    extra = r["p"][1] if score_draw(r) and r["pick"] != "d" else 0.0
    return r["confidence"] + extra


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
    hit = sum(1 for r in rows if correct(r))
    ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in rows) / n
    home = sum(1 for r in rows if r["actual"] == "h") / n
    exact = sum(1 for r in rows if r["score"] == r["result"])
    # Where the misses actually come from. The model almost never picks a draw,
    # so a draw is a guaranteed loss on the top pick, and counting them is the
    # difference between "we got it wrong" and knowing why.
    drawn = sum(1 for r in rows if r["actual"] == "d" and not correct(r))
    draw_reads = sum(1 for r in rows if r["actual"] == "d" and r["pick"] != "d" and score_draw(r))
    picks = {k: sum(1 for r in rows if r["pick"] == k) for k in "hda"}
    actual = {k: sum(1 for r in rows if r["actual"] == k) for k in "hda"}
    return {"n": n, "correct": hit, "accuracy": round(hit / n, 4),
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
        out.append({
            "name": name, "k": k, "min": lo, "n": len(g),
            "correct": sum(1 for r in g if correct(r)),
            "hit": round(sum(1 for r in g if correct(r)) / len(g), 4),
            "expected": round(sum(expected(r) for r in g) / len(g), 4),
            "drawnOut": sum(1 for r in g if r["actual"] == "d" and not correct(r)),
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
            "confidence": g["confidence"], "celtic": bool(g.get("celtic")),
            "unrated": bool(g.get("unrated")),
            "verified": verification(g),
            "list": bool(g.get("list")), "reserve": bool(g.get("reserve")),
            "score": tuple(g.get("score") or (-1, -1)), "result": (hg, ag),
            "published": g.get("published"), "kickoff": g.get("kickoff"),
        })
    return preds, rows, results



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
            bands.append({
                "from": lo, "to": min(hi, 1.0), "n": len(g),
                "hit": round(sum(1 for r in g if correct(r)) / len(g), 4),
                "expected": round(sum(expected(r) for r in g) / len(g), 4),
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
                "list": r["list"], "reserve": r["reserve"], "ok": correct(r),
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
        "tiers": tier_table(rows),
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
                    "ok": correct(r)} for r in recent],
    }
    json.dump(payload, open(os.path.join(HERE, "record.json"), "w"),
              separators=(",", ":"))
    # Every graded fixture in full (record.json keeps REVIEW_DAYS of them for
    # the page). Read by tools/julius_export.py; the page never loads it.
    with open(GRADED, "w") as f:
        json.dump({"generated": payload["generated"], "graded": [
            {**r, "p": list(r["p"]), "score": list(r["score"]), "result": list(r["result"]),
             "tier": tier_of(r["confidence"], r["celtic"], r["unrated"])[2],
             "ok": correct(r), "drawRead": r["actual"] == "d" and r["pick"] != "d" and score_draw(r),
             "expected": round(expected(r), 4)}
            for r in sorted(rows, key=lambda r: (r["date"], r["league"], r["home"]))]},
            f, separators=(",", ":"), ensure_ascii=False)

    o = payload["overall"]
    if o:
        print(f"graded {o['n']} fixtures: {o['accuracy']:.1%} correct "
              f"(home baseline {o['homeRate']:.1%}), log loss {o['logLoss']}, "
              f"{o['exactScores']} exact scorelines", file=sys.stderr)
        if payload["celtic"] and payload["settled"]:
            print(f"  settled {payload['settled']['accuracy']:.1%} vs "
                  f"flagged {payload['celtic']['accuracy']:.1%}", file=sys.stderr)


if __name__ == "__main__":
    main()
