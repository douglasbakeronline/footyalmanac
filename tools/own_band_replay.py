"""Own-band Daily List admission, replayed for every sport (20 Oct 2026, Nina).

Advisory, writes nothing but audit-out/own-band.json. History only (never the
live record, Rule 1). For each sport: replay the Elo walk with sports.json's
shipped parameters and calibration, then compare two admission rules.

  cumulative (live): confidence >= the sport's list bar, found by
      sports.list_threshold on cumulative "calls at X% or more" bands.
  own band: the same, and the pick's own 5-point band (bands.band_rate,
      widened upward to 30 calls) must also have landed >= the bar.

The own-band table is built from the FIT season only and applied to the CHECK
season's games, so the check hit rates are out of sample. Reverse
direction (build on check, apply to fit) is shown as a second look.
"""
import json, os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports as S
from bands import band_rate

BAR = S.LIST_MIN_HIT


def rows_for(sport, prm):
    games = [g for g in S.history_for(sport) if g["final"]]
    preds = S.replay(games, prm["params"])[1]
    cal = prm.get("cal")
    fit = S.losses(preds, S.FIT, cal)[1]
    chk = S.losses(preds, S.CHECK, cal)[1]
    return fit, chk


def boot(adm, base, reps=2000, seed=11):
    """Hit rate of admitted minus hit rate of baseline, bootstrapped over the
    baseline games (admitted is a subset). Returns (diff, p(admitted worse))."""
    rng = random.Random(seed)
    n = len(base)
    if not n or not adm:
        return 0.0, 1.0
    d0 = sum(h for _, h in adm) / len(adm) - sum(h for _, h in base) / n
    worse = 0
    for _ in range(reps):
        s = [base[rng.randrange(n)] for _ in range(n)]
        a = [h for k, h in s if k]
        if not a:
            continue
        if sum(a) / len(a) - sum(h for _, h in s) / n < 0:
            worse += 1
    return d0, worse / reps


def old_threshold(windows):
    """sports.list_threshold as it stood before own-band admission."""
    for t in S.LIST_THRESHOLDS:
        ok, big = True, 0
        for w in windows:
            b = next((x for x in w if abs(x["from"] - t) < 1e-9), None)
            if b is None:
                ok = False
                break
            if b["n"] >= S.LIST_MIN_N:
                big += 1
                ok = ok and b["hit"] >= S.LIST_MIN_HIT
        if ok and big:
            return t
    return None


def pick(rows, thr):
    return [r for r in rows if thr is not None and r[0] >= thr]


def f(rs):
    return [len(rs), round(sum(r[1] for r in rs) / len(rs), 4) if rs else None]


def boot(adm, base, reps=2000, seed=11):
    """P(admitted hit rate < all-base hit rate) over resamples of base games."""
    rng = random.Random(seed)
    ids = {id(r) for r in adm}
    tagged = [(id(r) in ids, r[1]) for r in base]
    n = len(tagged)
    if not adm:
        return 1.0
    worse = 0
    for _ in range(reps):
        s = [tagged[rng.randrange(n)] for _ in range(n)]
        a = [h for k, h in s if k]
        if not a or sum(a) / len(a) < sum(h for _, h in s) / n:
            worse += 1
    return worse / reps


def main():
    prm = json.load(open(S.PARAMS))
    res = {}
    for sport in S.SPORTS:
        p = prm.get(sport)
        if not p:
            continue
        fit, chk = rows_for(sport, p)
        bf, bc = S.bands(fit), S.bands(chk)
        r = {}
        # held out: bar chosen on the fit season only, applied to the check season
        t_old, t_new = old_threshold([bf]), S.list_threshold([bf])
        floor = S.LIST_FLOOR.get(sport, 0.0)
        t_old = None if t_old is None else max(t_old, floor)
        t_new = None if t_new is None else max(t_new, floor)
        a, b = pick(chk, t_old), pick(chk, t_new)
        r["heldout"] = {"oldBar": t_old, "newBar": t_new, "old": f(a), "new": f(b),
                        "dropped": f([x for x in a if x not in b]),
                        "pWorse": boot(b, a) if b and a else None}
        # the live shape: both windows, no hold-out (descriptive)
        t_old, t_new = old_threshold([bf, bc]), S.list_threshold([bf, bc])
        t_old = None if t_old is None else max(t_old, floor)
        t_new = None if t_new is None else max(t_new, floor)
        allr = fit + chk
        r["bothWindows"] = {"oldBar": t_old, "newBar": t_new,
                            "check": [f(pick(chk, t_old)), f(pick(chk, t_new))],
                            "fit": [f(pick(fit, t_old)), f(pick(fit, t_new))]}
        res[sport] = r
        print(sport, json.dumps(r))
    os.makedirs("audit-out", exist_ok=True)
    json.dump(res, open("audit-out/own-band.json", "w"), indent=1)


if __name__ == "__main__":
    main()
