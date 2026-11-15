#!/usr/bin/env python3
"""
Where and when the Card's legs get their best price (9 Nov 2026). Advisory.

From the pool archives (groupings-archive/pool-<date>.json.gz: first price
as published, last price before the start, every UK book's price):
  timing   first price v last pre-start price on legs that pass the Card's
           rule: how often the price shortened or drifted, and the mean move.
           A mean drift (last > first) says take the price late; a mean
           shortening says take it when published.
  books    for the same legs, each UK bookmaker's price against the average
           and how often it was the best: the book to write the Card for.
  hours    the first-price hour of day (UTC) v the move to the start.
  bySport  timing and books for each sport apart (9 Nov 2026, issue #156):
           the Card is mostly tennis and NBA, football a leg at most, and a
           book that is best on football says nothing about the rest.
  leads    the move by how long before the start the first price was taken
           (under 6h, 6-24h, 24-48h, 48-72h, 72h+), overall and by sport, and
           how close to the start the last price sat (9 Nov 2026, #156): the
           question behind the push time in notify.py.
A leg whose last price was taken after its latest known start (`whenLast`,
else `when`) is left out of every table and counted as `lastAfterStart`:
nothing shows that price was pre-start (tennis `when` is the session's first
start, so a match later in the session lands here too). 48 of 1,394 pool legs
to 9 Nov, 45 of them tennis, one of them a Card-rule leg; `whenLast` is
recorded from 10 Nov.
The first price is the first real bookmaker price: the row's own, or its
`priced` block when the leg was archived before any book priced it (9 Nov
2026, #159); `pricedAt` in that block dates the first price for `hours`.
The read (10 Nov 2026, #156): "take the price late" or "take the price when
published" only on MIN_READ (50) legs or more with a bootstrap p of the
opposite sign at most READ_P (0.10); else "no clear read". Until then the
sign of the mean was printed as the read on any sample, 2 legs included.
  settled  the singles return on settled legs at the first price and at the
           last pre-start price, paired, with p(late worse): the move only
           matters on legs that won, so this is the test the push time needs.
  vsBook   each UK book against the Card's own book (CARD_BOOK), paired on
           the legs both priced (13 Nov 2026, #156): the mean price ratio at
           the first and at the last pre-start price, day-resampled, the
           singles return at each book's first price on settled legs, and
           the best of the UK books against CARD_BOOK (what shopping around
           adds). `book_table` ranks each book against the average on
           different legs; this one asks the question CARD_BOOK needs.
           A side is read only on MIN_READ (50) paired legs at p <= READ_P.
Writes price-timing.json with --json FILE. Standard library only.
"""
import glob, gzip, json, os, random, sys
from collections import defaultdict
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as CR

MIN_BOOK = 10    # a book needs this many priced legs before it is ranked
MIN_READ = 50    # legs before the move is read as "take late" or "take when published" (10 Nov 2026)
READ_P = 0.10    # bootstrap p of the opposite sign at most this for a read
BOOT = 2000
LEADS = ((6, "<6h"), (24, "6-24h"), (48, "24-48h"), (72, "48-72h"), (None, "72h+"))


def _t(s):
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (AttributeError, ValueError): return None


def hours_before(l, at):
    """Hours from `at` to the leg's latest known start, or None."""
    st, a = _t(l.get("whenLast") or l.get("when") or ""), _t(at or "")
    return (st - a).total_seconds() / 3600 if st and a else None


def lead_bucket(h):
    for top, name in LEADS:
        if top is None or h < top: return name


def legs(pool_dir=os.path.join(HERE, "groupings-archive"), dropped=None, now=None, pending=None):
    """Card-rule legs with a first and a last real price. `dropped`, a list,
    collects the legs left out because the last price came after the start.
    With `now` (an aware datetime), a leg not started by then is left out
    and counted in `pending`: its last price so far is not its last
    (10 Nov 2026; the nightly run read 11 Nov legs as if closed)."""
    out = []
    # 13 Nov 2026: one row a fixture (G.pool_rows), not a moved fixture twice
    for _, row in G.pool_rows(pool_dir):
        mk = CR.pool_market(row)
        if mk is None or not row.get("lastOdds"): continue
        l = dict(row, **mk, est=False)
        if G.card_fault(dict(l)) is not None and G.card_fault(dict(l), wide=True) is not None: continue
        l["firstPriceAt"] = (row.get("priced") or {}).get("at") or row.get("firstAt") or row.get("pricedAt")
        h = hours_before(l, l.get("lastAt"))
        if h is not None and h < 0:
            if dropped is not None: dropped.append(l)
            continue
        st = _t(l.get("whenLast") or l.get("when") or "")
        if now is not None and (st is None or st > now):
            if pending is not None: pending.append(l)
            continue
        out.append(l)
    return out


def p_not_positive(xs, days=None, reps=BOOT, seed=7):
    """Bootstrap share of resampled means at or under zero: small says the
    mean is above zero beyond noise, near 1 says it is below. With `days`
    (one label per value) whole days are resampled, as legs on one day share
    a market (13 days and 112 legs at 10 Nov)."""
    if not xs: return None
    r = random.Random(seed)
    if days:
        by = defaultdict(list)
        for x, d in zip(xs, days): by[d].append(x)
        keys = list(by)
        hits = 0
        for _ in range(reps):
            tot = cnt = 0
            for _ in keys:
                v = by[r.choice(keys)]; tot += sum(v); cnt += len(v)
            hits += tot <= 0
        return round(hits / reps, 3)
    n = len(xs)
    return round(sum(sum(r.choice(xs) for _ in range(n)) <= 0 for _ in range(reps)) / reps, 3)


def read_of(xs, days=None, late="take the price late", early="take the price when published"):
    """The read on a list of moves (or late-minus-first returns): a side only
    on MIN_READ+ values with the opposite sign at bootstrap p <= READ_P."""
    if len(xs) < MIN_READ: return "too few legs to read", None
    p = p_not_positive(xs, days)
    if p <= READ_P: return late, p
    if 1 - p <= READ_P: return early, p
    return "no clear read", p


def timing(L):
    mv = [l["lastOdds"] / l["odds"] - 1 for l in L]
    read, p = read_of(mv, [l.get("date") for l in L])
    return {"n": len(L), "drifted": sum(m > 0.005 for m in mv), "shortened": sum(m < -0.005 for m in mv), "unchanged": sum(abs(m) <= 0.005 for m in mv),
            "meanMovePct": round(sum(mv) / len(mv) * 100, 2), "pNoDrift": p, "read": read}


def settle(L, idx=None):
    """Card-rule legs with a result (card_replay's settle on each sport's
    graded history), each marked `won`; void and pending legs are left out."""
    idx = idx or G.results_index(); names = CR.name_indexes(idx)
    out = []
    for l in L:
        l = dict(l)
        if l.get("sport") == "football" and not l.get("side"): l["side"] = "h" if l["pick"] == l.get("home") else "a"
        st, _ = CR.settle_pool(l, idx, names)
        if st in ("won", "lost"): out.append(dict(l, won=st == "won"))
    return out


def settled(S):
    """Singles at one unit on settled legs: return at the first price v at
    the last pre-start price, paired by leg (10 Nov 2026, #156)."""
    if not S: return {"n": 0}
    d = [(l["lastOdds"] - l["odds"]) if l["won"] else 0.0 for l in S]
    read, p = read_of(d, [l.get("date") for l in S])
    n, won = len(S), sum(l["won"] for l in S)
    return {"n": n, "won": won,
            "returnFirstPct": round((sum(l["odds"] for l in S if l["won"]) / n - 1) * 100, 2),
            "returnLastPct": round((sum(l["lastOdds"] for l in S if l["won"]) / n - 1) * 100, 2),
            "lateGainPct": round(sum(d) / n * 100, 2), "pLateNoBetter": p, "read": read}


def book_table(L, min_n=MIN_BOOK):
    books = defaultdict(lambda: {"n": 0, "vsAvgPct": 0.0, "best": 0})
    for l in L:
        bo = l.get("bookOdds") or {}
        if not bo: continue
        top = max(bo.values())
        for b, o in bo.items():
            books[b]["n"] += 1; books[b]["vsAvgPct"] += (o / l["odds"] - 1) * 100; books[b]["best"] += o >= top - 1e-9
    return {b: {"n": v["n"], "vsAvgPct": round(v["vsAvgPct"] / v["n"], 2), "bestShare": round(v["best"] / v["n"], 2)} for b, v in books.items() if v["n"] >= min_n}


def _pair(L, key, base, other):
    """(ratio - 1, day) for legs with both books' price under `key`;
    other=None compares the best UK price with `base`."""
    out = []
    for l in L:
        bo = l.get(key) or {}
        if not bo.get(base): continue
        o = max(bo.values()) if other is None else bo.get(other)
        if other is None and len(bo) < 2: continue
        if o: out.append((o / bo[base] - 1, l.get("date"), l.get("sport") or "?"))
    return out


def _read_pair(xs, days, other, base):
    """A side on MIN_READ+ paired values: `other` when the resampled mean is
    at or under zero at most READ_P of the time, `base` when it is at or
    over zero at most READ_P of the time (both tails tested, so equal
    prices read as neither). Returns (read, p) with p as p_not_positive."""
    if len(xs) < MIN_READ: return "too few legs to read", None
    p, q = p_not_positive(xs, days), p_not_positive([-x for x in xs], days)
    if p <= READ_P: return f"{other} pays more", p
    if q <= READ_P: return f"{base} pays more", p
    return "no clear read", p


def _side(pairs, other, base):
    if not pairs: return {"n": 0}
    xs, days = [x for x, _, _ in pairs], [d for _, d, _ in pairs]
    read, p = _read_pair(xs, days, other, base)
    m = sum(xs) / len(xs)
    return {"n": len(xs), "days": len(set(days)), "meanPct": round(m * 100, 2), "aheadShare": round(sum(x > 1e-9 for x in xs) / len(xs), 2),
            "behindShare": round(sum(x < -1e-9 for x in xs) / len(xs), 2), "p": p, "read": read,
            "group3Pct": round(((1 + m) ** 3 - 1) * 100, 2)}


def book_vs(L, S=None, base=None, min_n=MIN_BOOK):
    """Each UK book against CARD_BOOK on the legs both priced (13 Nov 2026,
    #156). `p` is the day-resampled share of means at or under zero: small
    says the other book pays more, near 1 says CARD_BOOK does. `group3Pct`
    is the mean ratio compounded over a three-pick group. `settled`: singles
    at one unit on settled legs at each book's first price, paired."""
    base = base or G.CARD_BOOK
    books = sorted({b for l in L for b in (l.get("bookOdds") or {})} - {base})
    out = {}
    for b in books + [None]:
        name = b or "best UK price"
        first = _pair(L, "bookOdds", base, b)
        if len(first) < min_n: continue
        r = {"first": _side(first, name, base), "last": _side(_pair(L, "lastBooks", base, b), name, base)}
        if S:
            T = [l for l in S if (l.get("bookOdds") or {}).get(base) and (max((l.get("bookOdds") or {}).values()) if b is None else (l.get("bookOdds") or {}).get(b))]
            if b is None: T = [l for l in T if len(l["bookOdds"]) > 1]
            if T:
                at = (lambda l: max(l["bookOdds"].values())) if b is None else (lambda l: l["bookOdds"][b])
                d = [(at(l) - l["bookOdds"][base]) if l["won"] else 0.0 for l in T]
                read, p = _read_pair(d, [l.get("date") for l in T], name, base)
                n = len(T)
                r["settled"] = {"n": n, "won": sum(l["won"] for l in T),
                                "returnBasePct": round((sum(l["bookOdds"][base] for l in T if l["won"]) / n - 1) * 100, 2),
                                "returnPct": round((sum(at(l) for l in T if l["won"]) / n - 1) * 100, 2),
                                "gainPct": round(sum(d) / n * 100, 2), "p": p, "read": read}
        sp = defaultdict(int)
        for _, _, k in first: sp[k] += 1
        r["sports"] = dict(sorted(sp.items(), key=lambda kv: -kv[1]))
        out[name] = r
    return {"base": base, "books": out}


def leads(L):
    b = defaultdict(list)
    for l in L:
        h = hours_before(l, l.get("firstPriceAt"))
        if h is not None: b[lead_bucket(h)].append(l["lastOdds"] / l["odds"] - 1)
    return {name: {"n": len(b[name]), "meanMovePct": round(sum(b[name]) / len(b[name]) * 100, 2),
                   "drifted": sum(m > 0.005 for m in b[name]), "shortened": sum(m < -0.005 for m in b[name])}
            for _, name in LEADS if b[name]}


def last_lead(L):
    hs = sorted(h for h in (hours_before(l, l.get("lastAt")) for l in L) if h is not None)
    return {"n": len(hs), "medianH": round(hs[len(hs) // 2], 1), "within3h": sum(h <= 3 for h in hs)} if hs else {"n": 0}


def page_read(pool_dir=os.path.join(HERE, "groupings-archive"), now=None, idx=None):
    """The compact read the Bets tab's playbook quotes (12 Nov 2026): the
    singles return late v first on settled legs under the live rule, so the
    page's "place late" line follows the evidence instead of a number typed
    on 10 Nov (+1.95 points on 104 legs, gone by 12 Nov: -0.25 on 174)."""
    now = now or datetime.now(timezone.utc)
    L = legs(pool_dir, now=now)
    s = settled(settle(L, idx))
    if not s.get("n"): return {"n": 0, "at": now.date().isoformat(), "rule": G.CARD_RULE}
    return {"n": s["n"], "won": s["won"], "lateGainPct": s["lateGainPct"], "p": s["pLateNoBetter"], "read": s["read"],
            "lastMedianH": last_lead(L).get("medianH"), "at": now.date().isoformat(), "rule": G.CARD_RULE}


def report(L, dropped=(), S=None, pending=()):
    rep = {"legs": len(L), "lastAfterStart": len(dropped)}
    if pending: rep["notStarted"] = len(pending)
    if dropped: rep["lastAfterStartBySport"] = {s: sum(1 for l in dropped if l.get("sport") == s) for s in sorted({l.get("sport") for l in dropped})}
    if not L: return rep
    rep["timing"] = timing(L)
    if S is not None: rep["settled"] = settled(S)
    rep["books"] = book_table(L)
    rep["vsBook"] = book_vs(L, S)
    hours = defaultdict(list)
    for l in L:
        fa = l.get("firstPriceAt")
        if fa: hours[fa[11:13]].append(l["lastOdds"] / l["odds"] - 1)
    rep["hours"] = {h: {"n": len(v), "meanMovePct": round(sum(v) / len(v) * 100, 2)} for h, v in sorted(hours.items())}
    by = defaultdict(list)
    for l in L: by[l.get("sport") or "?"].append(l)
    rep["leads"] = leads(L)
    rep["lastLead"] = last_lead(L)
    rep["bySport"] = {s: {"timing": timing(v), "books": book_table(v), "leads": leads(v)} for s, v in sorted(by.items(), key=lambda kv: -len(kv[1]))}
    return rep


def main():
    dropped, pending = [], []
    L = legs(dropped=dropped, now=datetime.now(timezone.utc), pending=pending)
    rep = report(L, dropped, settle(L), pending)
    print(json.dumps(rep, indent=1))
    if "--json" in sys.argv: json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
