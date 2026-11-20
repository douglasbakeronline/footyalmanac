"""The model against the bookmakers on the results ledger (20 Nov 2026).

Douglas, 20 Nov 2026, after reviewing a slip by hand: "Can we learn from this
method to apply to anything in the almanac for automation", then "build now".
Of the checks the hand review made, the one with evidence on the site's own
record is the market check: a pick the model rates well above the
bookmakers' fair chance lands at the bookmakers' rate, not the model's.
Stephen F. Austin (model 83%, ESPN's moneyline about 63%) and South Dakota
State (81% v about 68%) on 20 Nov were the examples.

This tool tallies every settled, priced pick on `results-ledger.json.gz` by
how far the model sat above the bookmakers (the first real price, its fair
chance taken as 1 / price / LEDGER_MARGIN since the ledger keeps the pick's
price only) and prints landed against the model and the bookmakers, with the
return at the recorded price, by band and by sport. A tally, never a fit:
nothing here moves a number on the page.

The page shows the result as the Bookies mark (`bookGapChip` in index.html):
a row whose model sits GAP_WARN (10 points) or more above the bookmakers'
fair chance says what the bookmakers give. The fair chance comes from the
build's own price (`groupings.board_prices` `f`), the football market line,
or, for a US game no UK book prices, ESPN's free moneyline (`ml_fair`, the
same rule as `mlFair` in index.html).

    python3 tools/market_gap.py            # all sports, model 60%+
    python3 tools/market_gap.py --min 0.7  # another floor
"""
import argparse, gzip, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(HERE, "results-ledger.json.gz")
GAP_WARN = 0.10          # mirrored as BOOK_GAP in index.html
LEDGER_MARGIN = 1.05     # the ledger keeps the pick's price, not the market's margin
BANDS = ((None, 0.0, "under"), (0.0, 0.05, "0-5"), (0.05, 0.10, "5-10"), (0.10, 0.15, "10-15"), (0.15, None, "15+"))


def american_implied(ml):
    """American odds to the implied chance (with margin): -192 -> 0.658, +160 -> 0.385."""
    if ml is None: return None
    ml = float(ml)
    if ml == 0: return None
    return -ml / (-ml + 100) if ml < 0 else 100 / (ml + 100)


def ml_fair(line, side):
    """The fair chance of side "h" or "a" from an ESPN line's two moneylines,
    the margin removed in proportion; None without both."""
    if not isinstance(line, dict): return None
    h, a = american_implied(line.get("mlH")), american_implied(line.get("mlA"))
    if h is None or a is None or h + a <= 0: return None
    return round((h if side == "h" else a) / (h + a), 4)


def band_of(gap):
    for lo, hi, name in BANDS:
        if (lo is None or gap >= lo) and (hi is None or gap < hi): return name
    return BANDS[-1][2]


def settled(rows, floor=0.60):
    for r in rows:
        o = (r.get("first") or {}).get("o")
        if not o or o <= 1 or r.get("result") not in ("won", "lost") or (r.get("conf") or 0) < floor: continue
        yield r, o, (1 / o) / LEDGER_MARGIN


def tally(rows, floor=0.60):
    """{sport: {band: {n, landed, model, bookies, ret}}} plus "all"."""
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0, 0.0, 0.0]))
    for r, o, fair in settled(rows, floor):
        b = band_of(r["conf"] - fair)
        won = r["result"] == "won"
        for s in ("all", r.get("sport") or "?"):
            t = acc[s][b]
            t[0] += 1; t[1] += won; t[2] += r["conf"]; t[3] += fair; t[4] += (o - 1) if won else -1
    out = {}
    for s, bands in acc.items():
        out[s] = {b: {"n": n, "landed": round(w / n, 4), "model": round(c / n, 4), "bookies": round(f / n, 4),
                      "ret": round(ret / n, 4)} for b, (n, w, c, f, ret) in bands.items()}
    return out


def warned(rows, floor=0.60):
    """The picks the Bookies mark would have carried (GAP_WARN+) v the rest."""
    a = {"warn": [0, 0, 0.0, 0.0], "rest": [0, 0, 0.0, 0.0]}
    for r, o, fair in settled(rows, floor):
        t = a["warn" if r["conf"] - fair >= GAP_WARN else "rest"]
        t[0] += 1; t[1] += r["result"] == "won"; t[2] += r["conf"]; t[3] += fair
    return {k: {"n": n, "landed": round(w / n, 4) if n else None, "model": round(c / n, 4) if n else None,
                "bookies": round(f / n, 4) if n else None} for k, (n, w, c, f) in a.items()}


def load(path=LEDGER):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f).get("rows") or []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=0.60)
    ap.add_argument("--ledger", default=LEDGER)
    a = ap.parse_args(argv)
    rows = load(a.ledger)
    T = tally(rows, a.min)
    print(f"Model against the bookmakers, settled priced picks at {round(a.min * 100)}%+ (ledger first price)")
    for s in ["all"] + sorted(k for k in T if k != "all"):
        print(f"\n{s}")
        for _, _, b in BANDS:
            t = T[s].get(b)
            if t: print(f"  {b:6} n={t['n']:5}  landed {t['landed']:.1%}  model {t['model']:.1%}  "
                        f"bookies {t['bookies']:.1%}  return {t['ret']:+.1%}")
    w = warned(rows, a.min)
    print(f"\nBookies mark ({round(GAP_WARN * 100)}+ points above): {w['warn']}\nThe rest: {w['rest']}")


if __name__ == "__main__":
    sys.exit(main())
