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
LIVE_LOOKBACK = 6

# Days of graded fixtures handed to the dashboard's results board.
REVIEW_DAYS = 14

# The confidence ladder, identical to the one index.html renders. It lives in
# both places because the dashboard has to label a fixture that has not been
# played, and this file has to grade one that has. Change one, change the other.
# Celtic's Law drops a fixture one rung: flagged rows measurably underperform
# their quoted number, so they are not allowed to claim the same tier.
TIERS = [(0.70, 3, "Strong"), (0.62, 2, "Firm"), (0.55, 1, "Lean"), (0.00, 0, "No read")]


def tier_of(confidence, celtic):
    i = next(i for i, (m, _, _) in enumerate(TIERS) if confidence >= m)
    if celtic and i < len(TIERS) - 1:
        i += 1
    return TIERS[i]


def load_predictions():
    """Every fixture ever predicted, keyed so it can be matched to a result.
    Later files win: if a fixture was predicted on several days, the most recent
    build is the one judged, which is the one a reader would have seen."""
    out = {}
    for path in sorted(glob.glob(os.path.join(PRED_DIR, "*.json"))):
        try:
            for g in json.load(open(path)):
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
        rows, ok = S.fetch_espn(code, day, day, log=log)
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


def summarise(rows):
    if not rows:
        return None
    n = len(rows)
    idx = {"h": 0, "d": 1, "a": 2}
    hit = sum(1 for r in rows if r["pick"] == r["actual"])
    ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in rows) / n
    home = sum(1 for r in rows if r["actual"] == "h") / n
    exact = sum(1 for r in rows if r["score"] == r["result"])
    # Where the misses actually come from. The model almost never picks a draw,
    # so a draw is a guaranteed loss on the top pick, and counting them is the
    # difference between "we got it wrong" and knowing why.
    drawn = sum(1 for r in rows if r["actual"] == "d" and r["pick"] != "d")
    picks = {k: sum(1 for r in rows if r["pick"] == k) for k in "hda"}
    actual = {k: sum(1 for r in rows if r["actual"] == k) for k in "hda"}
    return {"n": n, "correct": hit, "accuracy": round(hit / n, 4),
            "logLoss": round(ll, 4), "homeRate": round(home, 4),
            "exactScores": exact, "exactRate": round(exact / n, 4),
            "drawnOut": drawn, "picks": picks, "actuals": actual}


def tier_table(rows):
    """Live hit rate for each rung of the confidence ladder.

    This is the number that matters most on the review board. The tier labels
    were fitted on a backtest of last season; this says whether they have held
    up on fixtures the site published in advance, which is a much harder test.
    """
    out = []
    for lo, k, name in TIERS:
        g = [r for r in rows if tier_of(r["confidence"], r["celtic"])[2] == name]
        if not g:
            continue
        out.append({
            "name": name, "k": k, "min": lo, "n": len(g),
            "correct": sum(1 for r in g if r["pick"] == r["actual"]),
            "hit": round(sum(1 for r in g if r["pick"] == r["actual"]) / len(g), 4),
            "expected": round(sum(r["confidence"] for r in g) / len(g), 4),
            "drawnOut": sum(1 for r in g if r["actual"] == "d" and r["pick"] != "d"),
        })
    return out


def main():
    preds = load_predictions()
    if not preds:
        print("no predictions archived yet", file=sys.stderr)
        json.dump({"generated": None, "graded": 0, "overall": None},
                  open(os.path.join(HERE, "record.json"), "w"))
        return

    codes = sorted({k[0] for k in preds})
    results = load_results(codes)

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
            "score": tuple(g.get("score") or (-1, -1)), "result": (hg, ag),
        })

    if not rows:
        print(f"{len(preds)} predictions archived, none resolved yet", file=sys.stderr)

    # confidence bands: does a 70% call actually land 70% of the time?
    bands = []
    for lo, hi in [(0.0, 0.40), (0.40, 0.50), (0.50, 0.60), (0.60, 0.70), (0.70, 1.01)]:
        g = [r for r in rows if lo <= r["confidence"] < hi]
        if g:
            bands.append({
                "from": lo, "to": min(hi, 1.0), "n": len(g),
                "hit": round(sum(1 for r in g if r["pick"] == r["actual"]) / len(g), 4),
                "expected": round(sum(r["confidence"] for r in g) / len(g), 4),
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
    def game_row(r):
        _, k, name = tier_of(r["confidence"], r["celtic"])
        return {"league": r["league"], "home": r["home"], "away": r["away"],
                "p": [round(x, 4) for x in r["p"]], "pick": r["pick"],
                "actual": r["actual"], "confidence": r["confidence"],
                "celtic": r["celtic"], "tier": name, "k": k,
                "predScore": list(r["score"]), "result": list(r["result"]),
                "ok": r["pick"] == r["actual"]}

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
        "settled": summarise([r for r in rows if not r["celtic"]]),
        "celtic": summarise([r for r in rows if r["celtic"]]),
        "bands": bands,
        "tiers": tier_table(rows),
        "days": review,
        "byLeague": per_league,
        "recent": [{"date": r["date"], "league": r["league"], "home": r["home"],
                    "away": r["away"], "p": r["p"], "pick": r["pick"],
                    "actual": r["actual"], "confidence": r["confidence"],
                    "celtic": r["celtic"], "predScore": list(r["score"]),
                    "result": list(r["result"]),
                    "ok": r["pick"] == r["actual"]} for r in recent],
    }
    json.dump(payload, open(os.path.join(HERE, "record.json"), "w"),
              separators=(",", ":"))

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
