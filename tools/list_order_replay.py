"""Replay of Daily List orderings on the pinned lists since the 80% bar (28 Oct 2026).

Advisory only. Usage: python3 tools/list_order_replay.py [START_DATE]

For each UK day, rebuild the pinned list exactly as daylist.py does (latest
archived price before start, list-flagged rows), attach results, then rank
under several orderings and score the top 10 / two groups of 5.
Nothing is fitted; orderings are compared on the record only.
"""
import json, os, sys, random
from datetime import datetime, timedelta, timezone
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
import daylist as D, build as B, engine as E

random.seed(7)
import sports as SP
_g = D._load(os.path.join(REPO, "record-graded.json"), {}).get("graded") or []
rec = {"days": [{"date": "all", "games": [dict(g, _d=g["date"]) for g in _g]}]}
# daylist keys football results by (date, league, home, away) from record.days; rebuild that from the full graded file
_bd = {}
for g in _g: _bd.setdefault(g["date"], []).append(g)
rec = {"days": [{"date": d, "games": gs} for d, gs in _bd.items()]}
_sg, _sv = SP.graded_games()
srec = {"days": [{"date": "all", "games": _sg}]}
trec = D._load(os.path.join(REPO, "tennis-record.json"), {})

START, END = "2026-10-08", "2026-10-27"       # uncapped list (8 Oct) to last graded day
if len(sys.argv) > 1: START = sys.argv[1]
days = []
d = datetime.fromisoformat(START).date()
while d.isoformat() <= END:
    days.append(d.isoformat()); d += timedelta(days=1)

def fill_football_accuracy(it):
    if it["sport"] != "football" or it.get("accuracy"): return
    lg = it.get("league"); meta = E.LEAGUES.get(lg) or {}
    it["accuracy"] = B.accuracy_for(it["confidence"] or 0, meta.get("international"), False, lg)
    it["acc_backfilled"] = True

rows = {}
for day in days:
    now = datetime.fromisoformat(day + "T23:59:59+00:00") + timedelta(days=1)
    arch = D.read_archives(day, REPO)
    items = D.pinned(day, arch, now)
    D.attach_results(items, rec, trec, srec)
    lst = [i for i in items if i["list"]]
    for it in lst:
        it["acc_shipped"] = it.get("accuracy")          # None for football: the daylist bug
        fill_football_accuracy(it)
    settled = [i for i in lst if i["status"] in ("won", "lost")]
    rows[day] = settled

def cum(it): a = it.get("accuracy") or {}; return a.get("cumHit") or a.get("hit") or 0
def own(it): a = it.get("accuracy") or {}; return a.get("hit") or a.get("cumHit") or 0
def shipped(it):
    a = it.get("acc_shipped") or {}
    return a.get("cumHit") or a.get("hit") or 0
conf = lambda it: it.get("confidence") or 0

ORDERS = {
    "A shipped (tested cum, football pinned=0)": lambda it: (-shipped(it), -conf(it)),
    "B intended (tested cum, then conf)":        lambda it: (-cum(it), -conf(it)),
    "C own band, then conf":                    lambda it: (-own(it), -conf(it)),
    "D confidence only":                        lambda it: (-conf(it),),
    "E min(conf, tested)":                      lambda it: (-min(conf(it), cum(it) or conf(it)), -conf(it)),
    "F mean(conf, tested)":                     lambda it: (-(conf(it) + (cum(it) or conf(it))) / 2, -conf(it)),
    "G conf, football first":                   lambda it: (it["sport"] != "football", -conf(it)),
    "H min(conf,tested), football first":       lambda it: (it["sport"] != "football", -min(conf(it), cum(it) or conf(it))),
}

def score(order, rows, n1=5, n2=10):
    out = {"days": 0, "top5": [0, 0], "six10": [0, 0], "top10": [0, 0], "all5a": 0, "all5b": 0, "both": 0, "any5": 0,
           "d5": []}
    for day, xs in rows.items():
        if len(xs) < n2: continue
        s = sorted(xs, key=order)
        a, b = s[:n1], s[n1:n2]
        wa, wb = sum(i["status"] == "won" for i in a), sum(i["status"] == "won" for i in b)
        out["days"] += 1
        out["top5"][0] += wa; out["top5"][1] += n1
        out["six10"][0] += wb; out["six10"][1] += n2 - n1
        out["top10"][0] += wa + wb; out["top10"][1] += n2
        out["all5a"] += wa == n1; out["all5b"] += wb == n2 - n1
        out["both"] += (wa == n1 and wb == n2 - n1); out["any5"] += (wa == n1 or wb == n2 - n1)
        out["d5"].append(wa)
    return out

keys = list(ORDERS)
res = {k: score(ORDERS[k], rows) for k in keys}
print(f"Pinned Daily List picks, settled, {START} to {END}: "
      f"{sum(len(v) for v in rows.values())} picks over {len([v for v in rows.values() if v])} days; "
      f"{res[keys[0]]['days']} days with 10+ picks\n")
print(f"{'ordering':44} top5    6-10    top10   all5 A  all5 B  both  either")
for k in keys:
    r = res[k]
    f = lambda p: f"{p[0]}/{p[1]} {100*p[0]/max(p[1],1):4.0f}%"
    print(f"{k:44} {f(r['top5']):10} {f(r['six10']):10} {f(r['top10']):11} "
          f"{r['all5a']:3}/{r['days']}  {r['all5b']:3}/{r['days']}  {r['both']:3}   {r['any5']:3}")

# paired bootstrap of top-5 hit rate: each candidate v B (intended) and v D (conf only)
def boot(ka, kb, reps=3000):
    da, db = [], []
    for day, xs in rows.items():
        if len(xs) < 10: continue
        sa = sorted(xs, key=ORDERS[ka])[:5]; sb = sorted(xs, key=ORDERS[kb])[:5]
        da.append(sum(i["status"] == "won" for i in sa)); db.append(sum(i["status"] == "won" for i in sb))
    n = len(da); diffs = []
    if n == 0: return 0, 0, 0, 1
    for _ in range(reps):
        idx = [random.randrange(n) for _ in range(n)]
        diffs.append(sum(da[i] - db[i] for i in idx) / (5 * n))
    diffs.sort()
    return (sum(da) - sum(db)) / (5 * n), diffs[int(0.05 * reps)], diffs[int(0.95 * reps)], sum(x <= 0 for x in diffs) / reps
print("\nTop-5 hit rate, paired bootstrap, 90% band, p(no better):")
for k in keys:
    if k.startswith("B"): continue
    m, lo, hi, p = boot(k, "B intended (tested cum, then conf)")
    print(f"  {k:44} v B: {100*m:+5.1f} pts [{100*lo:+5.1f}, {100*hi:+5.1f}]  p {p:.2f}")

# where do the misses in the top 10 come from, under B and D?
from collections import Counter
for k in ("B intended (tested cum, then conf)", "D confidence only"):
    c, n = Counter(), Counter()
    for day, xs in rows.items():
        if len(xs) < 10: continue
        for i in sorted(xs, key=ORDERS[k])[:10]:
            n[i["sport"]] += 1; c[i["sport"]] += i["status"] == "won"
    print(f"\n{k}: top-10 by sport " + ", ".join(f"{s} {c[s]}/{n[s]}" for s in n))

# cross-check: landed by confidence band and by tested-rate band across all settled list picks
allp = [i for v in rows.values() for i in v]
print(f"\nAll settled list picks {len(allp)}: landed {sum(i['status']=='won' for i in allp)}")
for lo, hi in ((0.80, 0.85), (0.85, 0.90), (0.90, 0.95), (0.95, 1.01)):
    xs = [i for i in allp if lo <= conf(i) < hi]
    if xs: print(f"  conf {lo:.2f}-{hi:.2f}: {sum(i['status']=='won' for i in xs)}/{len(xs)} = {100*sum(i['status']=='won' for i in xs)/len(xs):.0f}%")
for lo, hi in ((0.0, 0.82), (0.82, 0.85), (0.85, 0.88), (0.88, 0.92), (0.92, 1.01)):
    xs = [i for i in allp if lo <= cum(i) < hi]
    if xs: print(f"  tested {lo:.2f}-{hi:.2f}: {sum(i['status']=='won' for i in xs)}/{len(xs)} = {100*sum(i['status']=='won' for i in xs)/len(xs):.0f}%  (mean conf {100*sum(conf(i) for i in xs)/len(xs):.0f}%)")
bysp = Counter(); wsp = Counter(); csp = {}
for i in allp:
    bysp[i["sport"]] += 1; wsp[i["sport"]] += i["status"] == "won"; csp.setdefault(i["sport"], []).append(conf(i))
print("  by sport: " + ", ".join(f"{s} {wsp[s]}/{bysp[s]} ({100*wsp[s]/bysp[s]:.0f}%, quoted {100*sum(csp[s])/len(csp[s]):.0f}%)" for s in bysp))


