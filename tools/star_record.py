#!/usr/bin/env python3
"""The likely winner star's record (23 Nov 2026, Douglas: "keep track").

The ⭐ (index.html `likelyWinner`) marks a Daily List pick that also passes the
checks the record backs. Looking back on 23 Nov, football and tennis stars
under 85% landed worst (football 80% v 91% at 85%+, tennis 81% v 90%), so a
stricter star was proposed: football and tennis at 85%+. Douglas kept the star
as it is and asked for the two to be tracked. This tallies, on the graded
record, the live star, the 85% variant beside it, and the list picks with no
star, overall, by sport and from `LIVE_FROM` (out of sample). A tally, never a
fit; nothing on the page reads it. Printed in the nightly Card review
(card_review_post.star_section). claude/likely-winner-star-2026-11-23.md.

The rule here follows the page's, from the archived rows:
- football: on the list, not Celtic's Law or unrated, the pick's best price on
  file under 1.40 (no price passes), the model under 10 points above the
  bookmakers' fair chance;
- college basketball and football: no away or neutral pick at 70%+ (the
  losing-record mark needs the season record, which the graded rows do not
  keep, so it is not applied);
- other sports: the model under 10 points above ESPN's moneyline where one
  is kept;
- tennis: 80%+.
The context check is not applied (paused to 1 Dec, and not archived on rows).
Standard library only.
"""
import glob, json, os, re, sys

LIVE_FROM = "2026-11-23"     # the star went live this day
REPLAY_FROM = "2026-09-28"
FB_MAX = 1.40
GAP = 0.10
STRICT = {"football": 0.85, "tennis": 0.85}   # the variant Douglas chose to track, not ship

_norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def _load(p):
    try:
        return json.load(open(p))
    except Exception:
        return {}


def ml_fair(line, side):
    if not line:
        return None
    imp = lambda ml: (-ml / (-ml + 100) if ml < 0 else 100 / (ml + 100)) if ml else None
    h, a = imp(line.get("mlH")), imp(line.get("mlA"))
    if h is None or a is None or h + a <= 0:
        return None
    return (h if side == "h" else a) / (h + a)


def football_star(p):
    """p: an archived football prediction row. (star, side) or (False, None)."""
    pp = p.get("p") or {}
    if not pp:
        return False, None
    side = max(("h", "d", "a"), key=lambda s: pp.get(s, 0))
    if side == "d" or not p.get("list") or p.get("celtic") or p.get("unrated"):
        return False, side
    i = 0 if side == "h" else 2
    m = p.get("market") or {}
    price = (m.get("best") or [None] * 3)[i]
    fair = (m.get("p") or [None] * 3)[i]
    if price and price >= FB_MAX:
        return False, side
    if fair and p.get("confidence", 0) - fair >= GAP:
        return False, side
    return True, side


def sport_star(x):
    side = "h" if x.get("pick") == x.get("home") else "a"
    if x.get("sport") in ("ncaab", "cfb") and x.get("confidence", 0) >= 0.70 and (x.get("neutral") or side == "a"):
        return False
    f = ml_fair(x.get("line"), side)
    return not (f is not None and x.get("confidence", 0) - f >= GAP)


def picks(root=".", since=REPLAY_FROM):
    """Every graded Daily List pick from `since`: sport, date, confidence, won, star."""
    out = []
    res = {}
    for r in (_load(os.path.join(root, "record-graded.json")).get("graded") or []):
        if r.get("result") is not None:
            res[(r["date"], _norm(r["home"]), _norm(r["away"]))] = r
    for f in sorted(glob.glob(os.path.join(root, "predictions", "20*.json"))):
        d = os.path.basename(f)[:10]
        if d < since:
            continue
        for p in (_load(f) or []):
            if not isinstance(p, dict) or p.get("date") != d or not p.get("list"):
                continue
            g = res.get((d, _norm(p.get("home")), _norm(p.get("away"))))
            if not g:
                continue
            star, side = football_star(p)
            if side in (None, "d"):
                continue
            h, a = g["result"][:2]
            act = "h" if h > a else "a" if a > h else "d"
            out.append({"sport": "football", "date": d, "conf": p.get("confidence", 0), "won": act == side, "star": star})
    for x in (_load(os.path.join(root, "sports-graded.json")).get("graded") or []):
        d = str(x.get("when", ""))[:10]
        if d < since or not x.get("list") or x.get("ok") is None:
            continue
        out.append({"sport": x.get("sport"), "date": d, "conf": x.get("confidence", 0), "won": bool(x["ok"]), "star": sport_star(x)})
    for x in (_load(os.path.join(root, "tennis-record.json")).get("graded") or []):
        d = x.get("date", "")
        if d < since or not x.get("list") or x.get("void") or x.get("ok") is None:
            continue
        out.append({"sport": "tennis", "date": d, "conf": x.get("confidence", 0), "won": bool(x["ok"]), "star": x.get("confidence", 0) >= 0.80})
    return out


def strict(r):
    return r["star"] and r["conf"] >= STRICT.get(r["sport"], 0)


def tally(rows):
    n = len(rows)
    w = sum(1 for r in rows if r["won"])
    return {"n": n, "won": w, "rate": round(w / n, 4) if n else None}


def report(root=".", since=REPLAY_FROM, live_from=LIVE_FROM):
    rows = picks(root, since)
    out = {}
    for span, xs in (("replay", [r for r in rows if r["date"] < live_from]), ("live", [r for r in rows if r["date"] >= live_from])):
        part = {"star": tally([r for r in xs if r["star"]]), "strict85": tally([r for r in xs if strict(r)]),
                "starNot85": tally([r for r in xs if r["star"] and not strict(r)]),
                "noStar": tally([r for r in xs if not r["star"]]), "bySport": {}}
        for sp in sorted({r["sport"] for r in xs}):
            ys = [r for r in xs if r["sport"] == sp]
            part["bySport"][sp] = {"star": tally([r for r in ys if r["star"]]), "strict85": tally([r for r in ys if strict(r)]),
                                   "noStar": tally([r for r in ys if not r["star"]])}
        out[span] = part
    return out


def _fmt(t):
    return f"{t['won']} of {t['n']} ({t['rate'] * 100:.0f}%)" if t.get("n") else "none"


def lines(rep):
    out = []
    for span, lab in (("live", f"live, from {LIVE_FROM}"), ("replay", f"replayed, {REPLAY_FROM} to the day before")):
        p = rep.get(span) or {}
        out += [f"**{lab}**: star {_fmt(p.get('star', {}))} · football and tennis at 85%+ (variant) {_fmt(p.get('strict85', {}))}"
                f" · stars the variant drops {_fmt(p.get('starNot85', {}))} · list picks with no star {_fmt(p.get('noStar', {}))}"]
        for sp in ("football", "tennis"):
            b = (p.get("bySport") or {}).get(sp)
            if b:
                out.append(f"- {sp}: star {_fmt(b['star'])}, 85%+ {_fmt(b['strict85'])}, no star {_fmt(b['noStar'])}")
    return out


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print("\n".join(lines(report(root))))
