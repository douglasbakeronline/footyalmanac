import sys, pickle, random, math, os
sys.path.insert(0,'/home/runner/work/footyalmanac/footyalmanac')
import tune, replay as R, engine as E
P='/tmp/work/data.pkl'
if os.path.exists(P): data=pickle.load(open(P,'rb'))
else:
    data=tune.load('/tmp/work/cache'); pickle.dump(data,open(P,'wb'))
orig=E.build_table
def capped(c):
    def bt(matches):
        return orig([(d,h,a,min(hg,c),min(ag,c)) for d,h,a,hg,ag in matches])
    return bt
def raws(split,cap=None):
    E.build_table = capped(cap) if cap else orig
    # replay_league calls E.build_table; ratings use capped goals; results (W/D/L) would change if capped -> keep via flag
    rows=tune.lambdas(data,split)
    E.build_table=orig
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
    return sum(d)/N, sum(1 for m in ms if m>0)/n
live=E.CALIBRATION
res={}
for cap in [None,5,4,3]:
    res[cap]={s:raws(s,cap) for s in('fit','check')}
    print(cap,{s:len(v) for s,v in res[cap].items()},flush=True)
base_fit,base_chk=res[None]['fit'],res[None]['check']
bp={s:tune.score_raw(res[None][s],cal=live)[0] for s in('fit','check')}
for cap in [5,4,3]:
    for mode in('live','refit'):
        out=[]
        for s in('fit','check'):
            rw=res[cap][s]
            if mode=='live': cal=live
            else:
                _,a,b=fitcal(res[cap]['fit']); cal={'a':a,'b':b}
            per=tune.score_raw(rw,cal=cal)[0]
            out.append((s,)+boot(per,bp[s])+((cal,) if mode=='refit' else ()))
        print(cap,mode,out,flush=True)
