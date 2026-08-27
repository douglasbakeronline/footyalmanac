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
from datetime import date
from math import log

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

HERE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(HERE, "predictions")
EPS = 1e-9


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


def summarise(rows):
    if not rows:
        return None
    n = len(rows)
    idx = {"h": 0, "d": 1, "a": 2}
    hit = sum(1 for r in rows if r["pick"] == r["actual"])
    ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in rows) / n
    home = sum(1 for r in rows if r["actual"] == "h") / n
    exact = sum(1 for r in rows if r["score"] == r["result"])
    return {"n": n, "correct": hit, "accuracy": round(hit / n, 4),
            "logLoss": round(ll, 4), "homeRate": round(home, 4),
            "exactScores": exact, "exactRate": round(exact / n, 4)}


def main():
    preds = load_predictions()
    if not preds:
        print("no predictions archived yet", file=sys.stderr)
        json.dump({"generated": None, "graded": 0, "overall": None},
                  open(os.path.join(HERE, "record.json"), "w"))
        return

    codes = sorted({k[0] for k in preds})
    results = load_results(codes)

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

    payload = {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "archived": len(preds),
        "graded": len(rows),
        "overall": summarise(rows),
        "settled": summarise([r for r in rows if not r["celtic"]]),
        "celtic": summarise([r for r in rows if r["celtic"]]),
        "bands": bands,
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
