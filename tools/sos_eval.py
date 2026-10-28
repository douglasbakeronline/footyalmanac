"""Opponent-adjusted (strength-of-schedule) ratings, 28 Oct 2026. Advisory.
Fetches via tune.load into /tmp/sos-cache on first run (about a minute). Writes nothing else.
See claude/sos-ratings-2026-10-28.md."""
import sys, pickle, random
import os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune, engine as E
data=pickle.load(open('/tmp/sos-data.pkl','rb')) if os.path.exists('/tmp/sos-data.pkl') else pickle.dump(tune.load('/tmp/sos-cache'),open('/tmp/sos-data.pkl','wb')) or pickle.load(open('/tmp/sos-data.pkl','rb'))
ob=E.build_table; os_=E.strength_from_table
def bt(matches):
    t=ob(matches)
    for r in t.values(): r['opps']=[]
    for d,h,a,hg,ag in matches:
        t[h]['opps'].append((a,hg,ag)); t[a]['opps'].append((h,ag,hg))
    return t
def make_sos(lam,iters):
    def f(table,k=None):
        k=E.SHRINK_FULL_SEASON if k is None else k
        base=os_(table,k=k)
        if not table or 'opps' not in next(iter(table.values())): return base
        mu=E.league_goal_rate(table); cur=base
        for _ in range(iters):
            new={}
            for t,r in table.items():
                p=r['P']
                if p==0: new[t]={'att':1.0,'def':1.0}; continue
                # expected GF given opp def; expected GA given opp att
                den_a=sum(cur[o]['def']**lam for o,_,_ in r['opps'])
                den_d=sum(cur[o]['att']**lam for o,_,_ in r['opps'])
                att_raw=r['GF']/(mu*den_a) if den_a else 1.0
                def_raw=r['GA']/(mu*den_d) if den_d else 1.0
                w=p/(p+k)
                new[t]={'att':min(max(w*att_raw+(1-w),E.ATT_BOUNDS[0]),E.ATT_BOUNDS[1]),
                        'def':min(max(w*def_raw+(1-w),E.DEF_BOUNDS[0]),E.DEF_BOUNDS[1])}
            cur=new
        return cur
    return f
def raws(split,lam=None,iters=1):
    E.build_table=bt
    E.strength_from_table=make_sos(lam,iters) if lam else os_
    rows=tune.lambdas(data,split)
    E.build_table=ob; E.strength_from_table=os_
    return tune.raw_probs(rows)
def fitcal(rw):
    best=None
    for a in [x/100 for x in range(95,176,5)]:
        for b in [-0.6,-0.45,-0.3,-0.15,0]:
            per,_,_=tune.score_raw(rw,cal={'a':a,'b':b}); m=sum(per)/len(per)
            if best is None or m<best[0]: best=(m,a,b)
    return best
def boot(x,y,n=1000):
    d=[a-b for a,b in zip(x,y)]; r=random.Random(1); N=len(d)
    ms=[sum(d[r.randrange(N)] for _ in range(N))/N for _ in range(n)]
    return round(sum(d)/N,4), sum(1 for m in ms if m>0)/n
live=E.CALIBRATION; print('live',live)
base={s:raws(s) for s in('fit','check')}
bp={s:tune.score_raw(base[s],cal=live)[0] for s in base}
print({s:len(v) for s,v in base.items()},flush=True)
for lam,it in [(0.5,1),(1.0,1),(1.0,3)]:
    rw={s:raws(s,lam,it) for s in base}
    _,a,b=fitcal(rw['fit']); rc={'a':a,'b':b}
    for mode,cal in(('live',live),('refit',rc)):
        print(lam,it,mode,cal if mode=='refit' else '',{s:boot(tune.score_raw(rw[s],cal=cal)[0],bp[s]) for s in rw},flush=True)
