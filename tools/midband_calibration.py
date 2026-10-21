#!/usr/bin/env python3
"""
Do 60-80% football calls land more often than quoted? (21 Oct 2026, advisory, writes nothing)

    python3 tools/midband_calibration.py

Reads record-graded.json, every graded win pick, and compares landed with
quoted by 5-point band and, for 60-80% calls, by segment (flag, side, list,
competition family, draw probability, month, competition). Strict result:
the pick won. score.py's "ok" also credits some draws ("draw read"), which
is the wrong test for a win bet and inflates low bands by 20-30 points.

Rule 1 applies: this is the scoreboard, so nothing here is ever fitted. A
gap found here is a lead to test on the walk-forward replay, not a fix.
See claude/midband-calibration-2026-10-21.md.
"""
import json,math,sys,collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
import engine as E, sources as S
rec=json.load(open(__import__('os').path.join(sys.path[0], 'record-graded.json')))['graded']
G=[g for g in rec if g['pick']!='d' and g.get('result')]
for g in G: g['won']=g['actual']==g['pick']
AFX=set(getattr(S,'AF_EXTRA',()))
def fam(g):
    L=g['league']; m=E.LEAGUES.get(L,{})
    if L in getattr(S,'AF_CUPS',set()): return 'domestic cups'
    if m.get('international'): return 'internationals'
    if L in AFX: return 'wider AF leagues (227)'
    if L in getattr(S,'AF',{}) : return 'English step 3 / AF'
    if any(x in L for x in ('uefa','champions','europa','conf')) or m.get('cup'): return 'European / cups'
    return 'core leagues'
def row(name,v,minn=25):
    n=len(v)
    if n<minn: return None
    h=sum(g['won'] for g in v); q=sum(g['confidence'] for g in v)
    sd=math.sqrt(sum(g['confidence']*(1-g['confidence']) for g in v))
    print(f"  {name:36} n={n:5}  landed {h/n:5.1%}  quoted {q/n:5.1%}  gap {100*(h-q)/n:+5.1f}  z {(h-q)/sd:+5.1f}")
    return (h-q)/n
band=lambda c: f"{int(c*20)*5}-{int(c*20)*5+5}%"
print(f'{len(G)} graded win picks, {min(g["date"] for g in G)} to {max(g["date"] for g in G)}\n\nAll, 5-point bands')
for b in sorted({band(g['confidence']) for g in G}, key=lambda s:int(s.split('-')[0])): row(b,[g for g in G if band(g['confidence'])==b])
mid=[g for g in G if 0.60<=g['confidence']<0.80]
print('\n60-80% by segment'); row('all 60-80',mid)
for k,f in [('clean (no flag, rated)',lambda g:not g['celtic'] and not g['unrated']),('Celtic-flagged',lambda g:g['celtic']),
            ('home pick',lambda g:g['pick']=='h'),('away pick',lambda g:g['pick']=='a'),
            ('on Daily List',lambda g:g['list']),('reserve',lambda g:g['reserve']),('neither',lambda g:not g['list'] and not g['reserve'])]:
    row(k,[g for g in mid if f(g)])
fc=collections.defaultdict(list)
for g in mid: fc[fam(g)].append(g)
for k,v in sorted(fc.items()): row('family: '+k,v,15)
for lo,hi in [(0,0.18),(0.18,0.24),(0.24,1)]: row(f'draw prob {lo:.2f}-{hi:.2f}',[g for g in mid if lo<=g['p'][1]<hi])
for m in ('2026-08','2026-09','2026-10'): row('month '+m,[g for g in mid if g['date'].startswith(m)],15)
print('\nclean 60-80% by competition, n>=20, sorted by gap')
lg=collections.defaultdict(list)
for g in mid:
    if not g['celtic'] and not g['unrated']: lg[g['league']].append(g)
out=[]
for k,v in lg.items():
    if len(v)>=20:
        h=sum(g['won'] for g in v); q=sum(g['confidence'] for g in v)
        out.append(((h-q)/len(v),k,len(v),h/len(v),q/len(v)))
for x in sorted(out,reverse=True): print(f"  {x[1]:8} {(E.LEAGUES.get(x[1],{}).get('country','')+' '+E.LEAGUES.get(x[1],{}).get('name',''))[:30]:30} n={x[2]:3} landed {x[3]:5.1%} quoted {x[4]:5.1%} gap {100*x[0]:+5.1f}")
core=[g for g in G if fam(g)=='core leagues']
print('\ncore leagues, 60-80% by band')
for lo in (0.6,0.65,0.7,0.75):
    row(f'{int(lo*100)}-{int(lo*100)+5}%',[g for g in core if lo<=g['confidence']<lo+0.05],10)
