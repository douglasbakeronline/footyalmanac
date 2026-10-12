"""Goal-cap test of 12 Oct 2026 (claude/goal-cap-test-2026-10-12.md). Needs a pickle of tune.load() at /tmp/goal_cap_data.pkl. Advisory; writes nothing."""
import sys, pickle
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
import tune, engine as E
data = pickle.load(open('/tmp/goal_cap_data.pkl','rb'))
orig = E.build_table
def capped(cap):
    def bt(matches):
        if cap is None: return orig(matches)
        return orig([(d,h,a,min(hg,cap),min(ag,cap)) for d,h,a,hg,ag in matches])
    return bt
def fit(raw):
    best=(9,None)
    for a in [x/100 for x in range(90,136,5)]:
        for b in [x/4 for x in range(-8,9)]:
            ll=tune.mean(tune.score_raw(raw,cal={"a":a,"b":b})[0])
            if ll<best[0]: best=(ll,{"a":a,"b":b})
    return best[1]
live={"a":E.CALIBRATION["a"],"b":E.CALIBRATION["b"]}
res={}
for cap in [None,5,4,3]:
    E.build_table=capped(cap)
    fr=tune.raw_probs(tune.lambdas(data,"fit")); cr=tune.raw_probs(tune.lambdas(data,"check"))
    res[cap]=(fr,cr)
    print(cap,len(fr),len(cr),flush=True)
E.build_table=orig
bf,bc=res[None]
for cap in [5,4,3]:
    fr,cr=res[cap]
    for label,cf in (("live curve",live),("refit",fit(fr))):
        out=[]
        for (r0,r1,n) in ((bf,fr,"fit"),(bc,cr,"check")):
            a=tune.score_raw(r1,cal=cf)[0]; b=tune.score_raw(r0,cal=live)[0]
            m,sd,pw=tune.paired(a,b); out.append(f"{n} {m:+.4f} p(worse) {pw:.2f}")
        print(f"cap {cap} {label} {cf}: "+" | ".join(out),flush=True)
