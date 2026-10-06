"""The tested rate quoted beside a pick: its own band, not everything above it.

Backtest bands are kept cumulative ("calls at 60% or more"), which is right
for setting the Daily List bar but flatters a pick near the bottom of a band:
a 62% pick quoted with the 60%+ rate borrows the record of every 80% and 90%
call above it. On 6 Oct 2026 Sasnovich (WTA, 62%) showed "72% tested" while
calls at 60-65% had landed 57%.

The cumulative bands hold everything needed: the calls between two
thresholds are the difference of the two counts and hit totals. A band with
fewer than MIN_N calls is widened upward until it holds enough. Standard
library only, shared by build.py, build_tennis.py and sports.py.
"""

MIN_N = 30


def band_rate(conf, bands, min_n=MIN_N):
    """{"from", "to" (None = and up), "hit", "n", "cumHit", "cumN"} for the
    band that holds conf, or None when conf is below every band."""
    bs = sorted(bands or [], key=lambda b: b["from"])
    i = None
    for k, b in enumerate(bs):
        if conf >= b["from"]:
            i = k
    if i is None:
        return None
    lo = bs[i]
    j = i + 1
    while j < len(bs) and lo["n"] - bs[j]["n"] < min_n:
        j += 1
    if j < len(bs):
        hi = bs[j]
        n = lo["n"] - hi["n"]
        hit = (lo["hit"] * lo["n"] - hi["hit"] * hi["n"]) / n
        to = hi["from"]
    else:
        n, hit, to = lo["n"], lo["hit"], None
    return {"from": lo["from"], "to": to, "hit": round(hit, 4), "n": int(round(n)),
            "cumHit": lo["hit"], "cumN": lo["n"]}
