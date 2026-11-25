"""Two-legged ties and play-off series among the Card's football legs.

25 Nov 2026. The Card keeps cups and internationals out (`card_league`), but a
league's own play-offs arrive under the league's code: Liga MX's Liguilla
(Toluca v Atlas on 26 Nov, Atlas v Toluca on 29 Nov), MLS's best-of-three
first round (Nashville v FC Cincinnati on 22 Nov, the reverse on 28 Nov),
promotion play-offs and the lower leagues' knockout rounds. The model rates
each leg as a league game: it cannot see the aggregate, so a side protecting
a lead in a second leg, or resting for it in the first, is outside what it
knows (the same blindness Celtic's Law flags for cross-division cup ties).

A fixture is a tie leg when the same league's archive also holds the
reverse fixture (away v home) 1 to `TIE_DAYS` days away. Regular seasons do
not repeat a pairing that fast; the check needs nothing but the published
fixtures (predictions/), so it reads every past day too.

Advisory: printed in the nightly Card review (`section`). Nothing here
changes a rule or the page. claude/card-ties-2026-11-25.md.
"""
import json, math, os, sys
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))

TIE_DAYS = 8          # a reverse fixture this close is the same tie or series
SINCE = "2026-09-01"  # the predictions archive's useful span for the index
PRED_DIR = os.path.join(HERE, "predictions")


def tie_index(pred_dir=PRED_DIR, since=SINCE, days=TIE_DAYS):
    """(league, date, home, away) -> {"leg": 1 or 2, "other": the reverse
    fixture's date}, for every archived fixture whose reverse the same league
    holds 1 to `days` days away. A fixture archived under two dates (a moved
    or nominal round date) keeps each; the nearest reverse decides."""
    dates = defaultdict(set)
    if not pred_dir or not os.path.isdir(pred_dir): return {}
    for f in sorted(os.listdir(pred_dir)):
        if not f.endswith(".json") or f[:10] < since: continue
        try: rows = json.load(open(os.path.join(pred_dir, f)))
        except (OSError, ValueError): continue
        for x in rows if isinstance(rows, list) else []:
            if x.get("league") and x.get("date") and x.get("home") and x.get("away"):
                dates[(x["league"], x["home"], x["away"])].add(x["date"])
    out = {}
    for (lg, h, a), ds in dates.items():
        rev = dates.get((lg, a, h))
        if not rev: continue
        for d in ds:
            best = None
            for r in rev:
                gap = (date.fromisoformat(r) - date.fromisoformat(d)).days
                if 1 <= abs(gap) <= days and (best is None or abs(gap) < abs(best[0])): best = (gap, r)
            if best: out[(lg, d, h, a)] = {"leg": 1 if best[0] > 0 else 2, "other": best[1]}
    return out


def tie_of(leg, idx):
    """The tie entry for a football leg (pool or Card shape), or None."""
    if leg.get("sport", "football") != "football" or not idx: return None
    d = leg.get("date") or (leg.get("when") or "")[:10]
    return idx.get((leg.get("code") or leg.get("league"), d, leg.get("home"), leg.get("away")))


def tally(legs):
    """Settled legs -> n, landed, the model's chance and the bookmakers'
    fair chance (each averaged), z of landed against the model."""
    n = len(legs)
    if not n: return {"n": 0}
    won = sum(1 for l in legs if l.get("won"))
    pm = [l.get("pModel") or l.get("p") or 0 for l in legs]
    fair = [l["fair"] for l in legs if l.get("fair") is not None]
    var = sum(p * (1 - p) for p in pm)
    return {"n": n, "landed": won, "model": round(sum(pm) / n, 4),
            "fair": round(sum(fair) / len(fair), 4) if fair else None,
            "z": round((won - sum(pm)) / math.sqrt(var), 2) if var else None}


def report(by, idx, fault=None):
    """`by` is card_replay.pool_legs' day -> settled legs. Football legs at
    60%+ on the model in a league the Card may take, split into tie legs
    (first and second legs apart) and the rest; `fault` (the live card_fault)
    narrows each to the legs clear of the live rule."""
    import groupings as G
    rows = [l for d in sorted(by) for l in by[d]
            if l.get("sport") == "football" and (l.get("pModel") or 0) >= 0.60 and G.card_league(l.get("code"))]
    out = {}
    for name, keep in (("all", lambda l: True), ("clear", lambda l: fault is not None and fault(l) is None)):
        pick = [l for l in rows if keep(l)]
        ties = [(l, tie_of(l, idx)) for l in pick]
        out[name] = {"tie": tally([l for l, t in ties if t]),
                     "first": tally([l for l, t in ties if t and t["leg"] == 1]),
                     "second": tally([l for l, t in ties if t and t["leg"] == 2]),
                     "other": tally([l for l, t in ties if not t])}
    return out


def open_ties(idx, now, archive=os.path.join(HERE, "groupings-archive")):
    """Card groups the page holds (the latest read of each Card day in
    card-short.json) with a pick on a tie leg still to start at `now` (an
    ISO UTC time): [(day, pick, event, leg, the reverse fixture's date)].
    The pick is found by name among the pool rows of its Card day and the
    next (a Card day runs 07:00 to 07:00 UK, so a late kick-off is dated
    the next day in UTC)."""
    import gzip
    from datetime import timedelta
    try: log = json.load(open(os.path.join(archive, "card-short.json")))
    except (OSError, ValueError): return []
    out, seen = [], set()
    for day in sorted(log):
        if not log[day] or day < (date.fromisoformat(now[:10]) - timedelta(days=1)).isoformat(): continue
        picks = {p for g in log[day][-1].get("groups") or [] for p in g}
        if not picks: continue
        for d in (day, (date.fromisoformat(day) + timedelta(days=1)).isoformat()):
            try: pool = json.load(gzip.open(os.path.join(archive, f"pool-{d}.json.gz"))).get("legs") or []
            except (OSError, ValueError): continue
            for r in pool:
                if r.get("pick") not in picks or r.get("sport") != "football" or (r.get("when") or "") <= now: continue
                t = tie_of(r, idx)
                key = (r["pick"], r.get("event"))
                if t and key not in seen:
                    seen.add(key); out.append((day, r["pick"], r.get("event"), t["leg"], t["other"]))
    return out


def _cell(t):
    if not t.get("n"): return "0 | | | | "
    fair = f"{t['fair'] * 100:.0f}%" if t.get("fair") is not None else ""
    return f"{t['n']} | {t['landed']} ({t['landed'] / t['n'] * 100:.0f}%) | {t['model'] * 100:.0f}% | {fair} | {t['z'] if t['z'] is not None else ''}"


def lines(rep, opened=()):
    out = ["| football legs at 60%+ | legs | landed | model | bookmakers | z v model |", "|---|---|---|---|---|---|"]
    for scope, lab in (("all", "any Card league"), ("clear", "clear of the live rule")):
        r = rep.get(scope) or {}
        for k, name in (("tie", "on a tie"), ("first", "  first leg"), ("second", "  second leg"), ("other", "not a tie")):
            out.append(f"| {lab}, {name} | {_cell(r.get(k) or {})} |")
    for day, pick, ev, leg, other in opened:
        out.append(f"- **Open Card group, {day}: {pick} ({ev}) is leg {leg} of a tie (the reverse fixture on {other}).**")
    out.append(f"A tie leg: the same league's archive holds the reverse fixture 1 to {TIE_DAYS} days away (play-offs, "
               "two-legged rounds, best-of-three series). Watch only: no Card rule reads it; a variant is "
               "pre-registered at 30 settled tie legs clear of the live rule (claude/card-ties-2026-11-25.md).")
    return out


def section(now=None):
    """The review's section; never stops the review."""
    try:
        import card_replay as CR, groupings as G
        idx = tie_index()
        by, _ = CR.pool_legs()
        rep = report(by, idx, fault=G.card_fault)
        from datetime import datetime, timezone
        opened = open_ties(idx, now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    except Exception as e:   # advisory
        return ["## Two-legged ties and play-off series", f"Not read: {type(e).__name__}: {e}", ""]
    return ["## Two-legged ties and play-off series (the pool, settled football legs)", ""] + lines(rep, opened) + [""]


if __name__ == "__main__":
    print("\n".join(section()))
