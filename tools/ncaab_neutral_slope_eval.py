"""College basketball: a separate (flatter) slope at a neutral site, early season. Advisory, writes nothing.
Rejected 28 Nov 2026: check-season gain +0.00028 under the 0.0005 bar. claude/ncaab-neutral-slope-2026-11-28.md"""
import sys, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import sports, ncaab_neutral_eval as ev
from datetime import date
sp=sports.load_params().get("ncaab") or {}
params=sp.get("params") or {**sports.DEFAULTS,**sports.EARLY_K.get("ncaab",{})}
games=[g for g in sports.history_for("ncaab") if g["final"]]
preds=sports.replay(games,params)[1]
months=sports.PHASE_MONTHS["ncaab"]
base=sports.fit_phase_calibration(preds,sports.FIT,months,neutral0=True)
# neutral slope s fitted on FIT neutral games (a=0): p=sigmoid(s*(a0-free logit))
def fitslope(win,early_only):
    xs=[(sports._logit(ph),1 if g['hs']>g['as'] else 0) for g,ph,w in preds if w and g.get('neutral') and sports.in_window(g,win) and g['hs']!=g['as'] and (int(g['when'][5:7]) in months or not early_only)]
    s=1.0
    for _ in range(50):
        gr=h=0
        for x,y in xs:
            p=1/(1+math.exp(-s*x));gr+=(p-y)*x;h+=p*(1-p)*x*x
        s-=gr/h
    return s,len(xs)
for eo in (False,True):
    s,n=fitslope(sports.FIT,eo);print('early_only',eo,'slope',s,n)
    def cal_p(ph,g):
        c=sports.calibrate(ph,base,g['when'],g.get('neutral'))
        if g.get('neutral') and (not eo or int(g['when'][5:7]) in months):
            c=1/(1+math.exp(-s*sports._logit(c)))
        return c
    SEASON=(date(2026,7,1),date(2027,7,1))
    for name,win in (('fit',sports.FIT),('check',sports.CHECK),('season',SEASON)):
        A=[(g,sports.calibrate(ph,base,g['when'],g.get('neutral'))) for g,ph,w in preds if w and sports.in_window(g,win) and g['hs']!=g['as']]
        B=[(g,cal_p(ph,g)) for g,ph,w in preds if w and sports.in_window(g,win) and g['hs']!=g['as']]
        la,lb=ev.loss(A),ev.loss(B);mu,sd,pw=sports.paired(lb,la)
        nn=sum(1 for g,_ in A if g.get('neutral'))
        print(name,len(la),'neutral',nn,round(sum(la)/len(la),4),round(sum(lb)/len(lb),4),'gain',round(-mu,5),'pworse',round(pw,3))
