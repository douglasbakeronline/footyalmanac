#!/usr/bin/env python3
"""Advisory: does shrinking picks that involve a thin-history player help?
Fit year 2025, check year 2026, live constants. Writes nothing.
Run from the repo root after a tune_tennis.py run (cache dir below)."""
import sys,math; sys.path.insert(0,'.')
import tune_tennis as T
def run(matches,sw,kb,rw,shrink,thr):
    overall,surf,n={}, {},{}
    out=[]
    for m in matches:
        w,l,s=m["winner"],m["loser"],m["surface"]
        ow,ol=overall.setdefault(w,1500.),overall.setdefault(l,1500.)
        sW,sL=surf.setdefault((w,s),1500.),surf.setdefault((l,s),1500.)
        bw=(1-sw)*ow+sw*sW; bl=(1-sw)*ol+sw*sL
        p=1/(1+10**((bl-bw)/400))
        nw,nl=n.get(w,0),n.get(l,0)
        if min(nw,nl)<thr: p=0.5+(p-0.5)*shrink
        out.append((m["date"],p,min(nw,nl)))
        kw,kl=T.dynamic_k(nw,kb),T.dynamic_k(nl,kb)
        wt=rw if m["retired"] else 1
        e=1/(1+10**((ol-ow)/400)); overall[w]=ow+kw*wt*(1-e); overall[l]=ol-kl*wt*(1-e)
        e=1/(1+10**((sL-sW)/400)); surf[(w,s)]=sW+kw*wt*(1-e); surf[(l,s)]=sL-kl*wt*(1-e)
        n[w],n[l]=nw+1,nl+1
    return out
for tour,sw,kb,rw in(("atp",.3,150,1.0),("wta",.3,150,.5)):
    M=T.load_tour(tour,'.tenniscache')
    print(tour)
    for yr in("2025","2026"):
        for shrink,thr in((1,0),(0.8,20),(0.6,20),(0.8,40)):
            o=run(M,sw,kb,rw,shrink,thr)
            sel=[x for x in o if x[0].startswith(yr)]
            ll=sum(-math.log(x[1]) for x in sel)/len(sel)
            thin=[x for x in sel if x[2]<thr]
            acc=sum(x[1]>.5 for x in thin)/max(1,len(thin))
            print(yr,shrink,thr,round(ll,4),'thin n',len(thin),'acc',round(acc,3))
