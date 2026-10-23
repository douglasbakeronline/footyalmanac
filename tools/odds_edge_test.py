#!/usr/bin/env python3
"""Edge-over-bookmaker test (23 Oct 2026, claude/odds-edge-test-2026-10-23.md).
Fetches football-data.co.uk history for the fit and check seasons, writes every
(model, fair, hit) leg to the path given as argv[1] (default /tmp/legs.json).
Advisory; changes nothing. Analysis: bootstrap mean(hit - fair) per cell."""
import sys, json, time, random
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import odds, tune, engine as E
data = tune.load(None)
out = {}
for split in ("fit","check"):
    preds = odds.model_probs(tune.lambdas(data, split, meta=True))
    prices=[]
    for div, code in odds.DIVS.items():
        if code not in E.LEAGUES: continue
        s = tune.splits(code)[split][0]
        if "-" not in s: continue
        prices += odds.parse(odds._get(odds.HIST_URL.format(yy=odds._yy(s), div=div)))
        time.sleep(0.5)
    prices=[r for r in prices if r["result"] is not None]
    fx=[((c,d,h,a),c,d,h,a) for (c,d,h,a) in preds]
    j=odds.match(prices,fx)
    legs=[]
    for k,r in j.items():
        mp=preds[k]; f=odds.fair(r["avg"]); c=odds.fair(r["close"]) if r.get("close") else None
        for i in range(3):
            legs.append(dict(code=k[0],i=i,p=mp[i],f=f[i],fc=c[i] if c else None,odds=r["avg"][i],hit=int(r["result"]==i)))
    out[split]=legs
json.dump(out,open(sys.argv[1] if len(sys.argv)>1 else '/tmp/legs.json','w'))
print({k:len(v) for k,v in out.items()})
