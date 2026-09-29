#!/usr/bin/env python3
"""
Out-of-time check of the FIFA ranking adjustment (rankings.adjust_fifa), with
FIFA_W frozen exactly as shipped. Advisory only, changes nothing.

    python3 ranktest.py

Window: Oct 2022 - Oct 2024, the years FIFA's public ranking history covers
(Dato-Futbol's archive ends Sep 2024). The weights were fit on 2025 and the
international ratings are refitted each quarter from the ten years before it
(international.json's half-life and tournament weights), so neither saw these
games. Every win pick where both sides hold a FIFA ranking is re-scored with
the release current before kick-off.

Written 29 Sep 2026 after Burundi 2-2 Algeria, a Daily List pick the ranking
had lifted from the model's 57% to 79%. Findings (claude/ranking-review.md):
the adjustment still helps (-0.0099 pick log loss, p(worse) 0.012) but quotes
3-5 points high in this window, 60%+ landed 73.7% (so the list bar is 65%),
and picks it lifted by 20+ points landed 65% of 40.

Data: martj42/international_results and Dato-Futbol/fifa-ranking on GitHub,
cached in .tunecache/. Standard library only.
"""
import bisect, csv, math, os, random, sys, urllib.request
from datetime import datetime, timedelta
import engine as E, rankings as RK, tune_international as TI

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tunecache")
SOURCES = {
    "results.csv": TI.DATA_URL,
    "fifa_hist.csv": "https://raw.githubusercontent.com/Dato-Futbol/fifa-ranking/master/ranking_fifa_historical.csv",
}
os.makedirs(HERE, exist_ok=True)
for fn, url in SOURCES.items():
    path = os.path.join(HERE, fn)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "footyalmanac-ranktest"})
        open(path, "wb").write(urllib.request.urlopen(req, timeout=60).read())

rows = list(csv.DictReader(open(os.path.join(HERE, "results.csv"), encoding="utf-8")))
allm = TI.build_matches(rows, "2012-01-01")

# FIFA history: release date -> {team: points}
rel = {}
for r in csv.DictReader(open(os.path.join(HERE, "fifa_hist.csv"), encoding="utf-8")):
    try:
        rel.setdefault(r["date"], {})[r["team"]] = float(r["total_points"])
    except ValueError:
        pass
rdates = sorted(rel)
# FIFA's spelling first, then with a curly apostrophe, then as given
def fifa_pts(date, name):
    i = bisect.bisect_left(rdates, date) - 1
    if i < 0:
        return None
    t = rel[rdates[i]]
    n = RK.FIFA_NAMES.get(name, name)
    for k in (n, n.replace("'", "’"), name):
        if k in t:
            return t[k]
    return None

START, END = "2022-10-01", "2024-10-15"
quarters = []
d = datetime.strptime(START, "%Y-%m-%d")
while d.strftime("%Y-%m-%d") < END:
    quarters.append(d)
    d = (d.replace(day=1) + timedelta(days=95)).replace(day=1)

out = []
miss = set()
for qi, q in enumerate(quarters):
    qs = q.strftime("%Y-%m-%d")
    qe = quarters[qi + 1].strftime("%Y-%m-%d") if qi + 1 < len(quarters) else END
    train = [m for m in allm if (q - timedelta(days=3650)).strftime("%Y-%m-%d") <= m["date"] < qs]
    ratings, mu, ha = TI.fit_ratings(train, q, 1460, TI.TIER_WEIGHTS)
    for m in allm:
        if not (qs <= m["date"] < qe):
            continue
        rh, ra = ratings.get(m["home"]), ratings.get(m["away"])
        if not rh or not ra:
            continue
        hm = 1.0 if m["neutral"] else ha
        E.HOME_MULT[1], E.AWAY_MULT[1] = hm, 1.0 / hm
        p = E.match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"], mu, tier=1)
        trip = {"h": p["home"], "d": p["draw"], "a": p["away"]}
        pk = max(trip, key=trip.get)
        if pk == "d":
            continue
        fh, fa = fifa_pts(m["date"], m["home"]), fifa_pts(m["date"], m["away"])
        if fh is None or fa is None:
            for t, f in ((m["home"], fh), (m["away"], fa)):
                if f is None:
                    miss.add(t)
            continue
        fav, opp = ((0, fh), (0, fa)) if pk == "h" else ((0, fa), (0, fh))
        raw = trip[pk]
        adj = RK.adjust_fifa(raw, fav, opp)
        y = (m["hg"] > m["ag"]) if pk == "h" else (m["ag"] > m["hg"])
        out.append(dict(date=m["date"], raw=raw, adj=adj, y=int(y), gap=fav[1] - opp[1],
                        m=f'{m["home"]} {m["hg"]}-{m["ag"]} {m["away"]}', tier=m["tier"]))
    print(f"quarter {qs}: {sum(1 for o in out if qs <= o['date'] < qe)} ranked win picks", file=sys.stderr)

def ll(p, y):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))

def boot(a, b, reps=2000, seed=17):
    rnd = random.Random(seed); n = len(a); d = [x - y for x, y in zip(a, b)]
    worse = 0
    for _ in range(reps):
        s = sum(d[rnd.randrange(n)] for _ in range(n)) / n
        worse += s > 0
    return sum(d) / n, worse / reps

def table(label, sel):
    n = len(sel)
    if not n:
        print(f"{label:34s} n=0"); return
    print(f"{label:34s} n={n:4d}  raw {sum(o['raw'] for o in sel)/n:.3f}  "
          f"adjusted {sum(o['adj'] for o in sel)/n:.3f}  landed {sum(o['y'] for o in sel)/n:.3f}")

print(f"\n{len(out)} ranked win picks, {START} to {END}; unmatched names: {len(miss)}")
print(sorted(miss)[:40])
a = [ll(o["adj"], o["y"]) for o in out]; r = [ll(o["raw"], o["y"]) for o in out]
m, pw = boot(a, r)
print(f"\npick log loss raw {sum(r)/len(r):.4f} -> adjusted {sum(a)/len(a):.4f}  ({m:+.4f}, p(worse) {pw:.3f})")

print("\nby adjusted band")
for lo, hi in ((0.55, .6), (.6, .65), (.65, .7), (.7, .75), (.75, .8), (.8, .85), (.85, .9), (.9, 1.01)):
    table(f"  adjusted {lo:.2f}-{hi:.2f}", [o for o in out if lo <= o["adj"] < hi])
print("\nby uplift (adjusted - raw)")
for lo, hi in ((-1, 0), (0, .05), (.05, .10), (.10, .15), (.15, .20), (.20, 1)):
    table(f"  uplift {lo:+.2f} to {hi:+.2f}", [o for o in out if lo <= o["adj"] - o["raw"] < hi])
print("\nDaily List zone (adjusted >= 0.60), by raw confidence")
for lo, hi in ((0, .5), (.5, .55), (.55, .6), (.6, .65), (.65, .7), (.7, .8), (.8, 1.01)):
    table(f"  raw {lo:.2f}-{hi:.2f}", [o for o in out if o["adj"] >= .6 and lo <= o["raw"] < hi])
print("\nAlgeria-like: raw < 0.62, adjusted >= 0.75")
al = [o for o in out if o["raw"] < .62 and o["adj"] >= .75]
table("  all", al)
for o in al[:25]:
    print(f"   {o['date']} {o['m']:45s} raw {o['raw']:.2f} adj {o['adj']:.2f} gap {o['gap']:.0f} {'hit' if o['y'] else 'MISS'}")
print("\ncumulative (the list rule's form)")
for t in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85):
    table(f"  adjusted {t:.2f}+", [o for o in out if o["adj"] >= t])
