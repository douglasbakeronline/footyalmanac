#!/usr/bin/env python3
"""
Calibration by confidence band, from history. Advisory only: changes nothing.

    python3 calibration_bands.py                    football and the other sports
    python3 calibration_bands.py --football         football only
    python3 calibration_bands.py --sports           NFL, MLB, NBA, rugby only
    python3 calibration_bands.py --snapshot FILE    football from a frozen snapshot (replay.py --freeze)
    python3 calibration_bands.py --json FILE        also write the numbers

Never reads record.json (Rule 1). Football is the walk-forward replay that
tune.py fits on (replay.replay_league, the live build's engine functions) with
the calibration the site prices with now (engine.CALIBRATION). The other sports
are sports.py's own replay with the parameters in sports.json.

For each band it reports how many calls, how often the pick landed, what the
model quoted, and a bootstrap 90% interval on landed minus quoted, so a gap
that is inside the noise is not read as a miscalibration. Football's
fit season is IN-SAMPLE for the calibration curve (it was fitted there); only
the check season is a fair test. Sports are shown the same way: the model's
parameters were fitted on the FIT window, the CHECK window is out of sample.
Thin bands (below MIN_BAND calls) are marked "thin": the interval is too wide
to say anything, and the table says so rather than hiding the band.

Standard library only.
"""
import argparse, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MIN_BAND = 30
REPS = 2000
EDGES = (0.0, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 1.01)
CUMULATIVE = (0.55, 0.62, 0.70, 0.75, 0.80, 0.85)   # the tier ladder and the list bars


def boot_gap(rows, reps=REPS, seed=29):
    """rows: [(quoted, hit)]. Bootstrap (landed - quoted): 5th and 95th
    percentile. Resamples calls, so it is the sampling noise of this set."""
    n = len(rows)
    rng = random.Random(seed)
    gaps = []
    for _ in range(reps):
        s = [rows[rng.randrange(n)] for _ in range(n)]
        gaps.append(sum(h for _, h in s) / n - sum(q for q, _ in s) / n)
    gaps.sort()
    return gaps[int(0.05 * reps)], gaps[int(0.95 * reps)]


def verdict(n, lo, hi):
    if n < MIN_BAND:
        return "thin"
    if lo > 0:
        return "under-confident"      # landed more often than quoted
    if hi < 0:
        return "OVER-confident"       # landed less often than quoted
    return "ok"


def summarise(rows):
    n = len(rows)
    quoted = sum(q for q, _ in rows) / n
    landed = sum(h for _, h in rows) / n
    lo, hi = boot_gap(rows)
    return {"n": n, "quoted": round(quoted, 4), "landed": round(landed, 4),
            "gap": round(landed - quoted, 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "verdict": verdict(n, lo, hi)}


def band_table(rows):
    """Own (non-cumulative) bands, then the cumulative ones the site quotes."""
    own, cum = [], []
    for lo, hi in zip(EDGES, EDGES[1:]):
        r = [x for x in rows if lo <= x[0] < hi]
        if r:
            own.append({"band": f"{lo:.0%}-{min(hi, 1):.0%}", **summarise(r)})
    for t in CUMULATIVE:
        r = [x for x in rows if x[0] >= t]
        if r:
            cum.append({"band": f"{t:.0%}+", **summarise(r)})
    return own, cum


SPANS = ((0.60, 0.70),)   # wider than one band: the span the Daily List reserve sits in


def boot_p_nonpositive(rows, reps=REPS, seed=31):
    """Bootstrap chance that landed minus quoted is zero or below, i.e. how
    often resampling the same calls shows no under-confidence. One-sided, and
    one of several bands looked at, so read it with that in mind."""
    n = len(rows)
    rng = random.Random(seed)
    k = 0
    for _ in range(reps):
        s = [rows[rng.randrange(n)] for _ in range(n)]
        if sum(h for _, h in s) / n - sum(q for q, _ in s) / n <= 0:
            k += 1
    return k / reps


def show_spans(rows):
    for lo, hi in SPANS:
        r = [x for x in rows if lo <= x[0] < hi]
        if not r:
            continue
        b = summarise(r)
        b["pNoGap"] = round(boot_p_nonpositive(r), 3)
        print(f"  span {lo:.0%}-{hi:.0%}: n {b['n']}, quoted {b['quoted']:.1%}, landed "
              f"{b['landed']:.1%}, gap {b['gap']:+.1%} [{b['lo']:+.1%},{b['hi']:+.1%}], "
              f"P(gap <= 0) {b['pNoGap']:.3f}  {b['verdict']}")


def show(title, rows):
    print(f"\n{title}  ({len(rows)} calls)")
    if not rows:
        print("  none")
        return None
    own, cum = band_table(rows)
    for name, tbl in (("own band", own), ("cumulative", cum)):
        print(f"  {name:10} {'n':>6} {'quoted':>7} {'landed':>7} {'gap':>7}  {'90% interval':>16}  read")
        for b in tbl:
            print(f"  {b['band']:10} {b['n']:6} {b['quoted']:7.1%} {b['landed']:7.1%} "
                  f"{b['gap']:+7.1%}  [{b['lo']:+6.1%},{b['hi']:+6.1%}]  {b['verdict']}")
    show_spans(rows)
    return {"calls": len(rows), "own": own, "cumulative": cum}


# ---------------------------------------------------------------------------
# football
# ---------------------------------------------------------------------------

def football_rows(raws, cal):
    """(quoted confidence, pick landed) after the live calibration."""
    import engine as E, tune
    out = []
    for h, d, a, y in raws:
        p = (h, d, a)
        t = tune.curve_T(max(p), cal) if cal else E.TEMPERATURE
        q = [max(x, tune.EPS) ** (1.0 / t) for x in p]
        s = sum(q)
        p = [x / s for x in q]
        out.append((max(p), 1 if p.index(max(p)) == y else 0))
    return out


def football(snapshot=None, cache=None):
    import engine as E, replay as R, tune
    if snapshot:
        data, _, sha = R.load_snapshot(snapshot)
        print(f"snapshot {snapshot} sha256 {sha[:12]}")
    else:
        cache = cache or os.path.join(HERE, ".tunecache")
        os.makedirs(cache, exist_ok=True)
        data = tune.load(cache)
    cal = E.CALIBRATION
    print(f"football: live calibration {cal if cal else 'none, flat ' + str(E.TEMPERATURE)}")
    out, pooled = {}, []
    for split, label in (("fit", "fit season (IN-SAMPLE for the curve)"),
                         ("check", "check season (out of sample)")):
        usable, _ = R.coverage(data, tune.codes(), tune.splits, split)
        rows = football_rows(tune.raw_probs(tune.lambdas(data, split)), cal)
        pooled += rows
        print(f"\n{split}: {len(usable)} competitions")
        out[split] = show(f"football {label}", rows)
    out["pooled"] = show("football, both seasons pooled (fit part is in-sample)", pooled)
    return out


# ---------------------------------------------------------------------------
# other sports
# ---------------------------------------------------------------------------

def other_sports(only=None):
    import sports as SP
    params = SP.load_params()
    out = {}
    for sport in SP.SPORTS:
        if only and sport not in only:
            continue
        p = params.get(sport)
        if not p:
            print(f"\n{sport}: no entry in sports.json")
            continue
        games = [g for g in SP.history_for(sport) if g["final"]]
        preds = SP.replay(games, p["params"])[1]
        cal = p.get("cal")
        print(f"\n{SP.SPORTS[sport]['name']}: {len(games)} games, params {p['params']}, "
              f"calibration {cal if cal else 'none'}")
        out[sport] = {}
        for key, win, label in (("fit", SP.FIT, "fit window (fitted on)"),
                                ("check", SP.CHECK, "check window (out of sample)")):
            _, rows = SP.losses(preds, win, cal)
            out[sport][key] = show(f"{SP.SPORTS[sport]['name']} {label}",
                                   [(c, 1 if hit else 0) for c, hit, g in rows])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--football", action="store_true")
    ap.add_argument("--sports", action="store_true")
    ap.add_argument("--only", help="comma-separated sports for --sports")
    ap.add_argument("--snapshot", metavar="FILE")
    ap.add_argument("--cache")
    ap.add_argument("--json", metavar="FILE")
    args = ap.parse_args()
    both = not (args.football or args.sports)
    res = {}
    if args.football or both:
        res["football"] = football(args.snapshot, args.cache)
    if args.sports or both:
        res["sports"] = other_sports(args.only.split(",") if args.only else None)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
