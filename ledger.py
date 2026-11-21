"""The results ledger: every prediction, its result and its price, all sports.

14 Nov 2026 (Douglas: "are we storing every result against our prediction so
we can learn from it?"). Football and tennis kept every graded pick, the
other sports only 14 days of rows (now sports-graded.json), and no file held
a pick's result beside the price it could have been backed at. This joins
them into one permanent table, results-ledger.json.gz, one row a prediction:

- the prediction: the latest archived copy published before the start
  (predictions*/), the same rule the records grade by; a fixture moved to
  another day keeps its latest placement only, so it is not counted twice;
- the result: record-graded.json (football), tennis-record.json (tennis),
  sports-graded.json (the other sports); "pending" until one of them has it;
- the price, before the start, from every source the site already reads:
  the football archive's own market block (API-Football's average and best
  for the picked side, at publish), the pool archive (groupings-archive/
  pool-*: the first real price and the last pre-start price, with William
  Hill's where a UK slate was read), and this build's board prices
  (groupings.json "prices"), so a game priced on any build keeps that price
  after it starts. Estimates are never kept as prices.

Merged with the ledger already on file, never trimmed: a row outlives the
archive or history file it came from. A price keeps its earliest `first`
and its latest pre-start `last`.

The ungraded report (Douglas, 14 Nov 2026): a pick still pending three days
after its start has fallen out of the record without anyone seeing; it is
counted by sport and competition, printed on every build, and raised as a
::warning:: on the first build of each UK Monday (once a week, not noise).
Past UNGRADED_STALE days it is counted apart as unlikely ever to settle
(postponed, or a feed with no result).

Nothing is fitted, priced or graded anew here: a read of what the site
already wrote. Standard library only.
"""
import glob, gzip, json, os, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
UK = ZoneInfo("Europe/London")
LEDGER = os.path.join(HERE, "results-ledger.json.gz")
BOOK = "William Hill"         # groupings.CARD_BOOK; read from groupings when it imports
UNGRADED_DAYS = 3             # pending this long after the start: report it
UNGRADED_STALE = 14           # pending this long: counted apart, unlikely to settle
MOVE_DAYS = 10                # two copies of one pairing this close are one fixture, moved
TENNIS_MOVE_DAYS = 2          # tennis: a moved match is a day or two late, a rematch is days later
MATCH_DAYS = 2                # a price joins a prediction within this many days of its start
BANDS = (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.62, 0.0)


def parse_utc(s):
    if not s: return None
    s = str(s)
    if len(s) == 16: s += ":00"          # "2026-11-15T14:30Z"-style sports stamps
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def iso(d): return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def low(x): return str(x or "").strip().lower()


def _load(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default


# ---------------------------------------------------------------- predictions

def _football(g):
    p = g.get("p") or {}
    if not p or not g.get("home") or not g.get("away"): return None
    side = max(p, key=p.get)
    ko = parse_utc(g.get("kickoff"))
    start = ko or parse_utc(f"{g.get('date')}T00:00:00Z")
    if not start: return None
    m = g.get("market") or {}
    i = {"h": 0, "d": 1, "a": 2}[side]
    price = None
    if m.get("avg") and len(m["avg"]) == 3 and m["avg"][i]:
        price = {"o": m["avg"][i], "b": (m.get("best") or [None] * 3)[i], "n": m.get("books"),
                 "src": m.get("src") or "archive", "t": g.get("published"), "side": side}
    return {"sport": "football", "comp": g.get("league"), "date": g.get("date"),
            "start": iso(start), "timed": bool(ko), "home": g["home"], "away": g["away"],
            "pick": {"h": g["home"], "a": g["away"], "d": "Draw"}[side], "side": side,
            "conf": g.get("confidence"), "list": bool(g.get("list")), "reserve": bool(g.get("reserve")),
            "celtic": bool(g.get("celtic")), "why": g.get("why"), "published": g.get("published"),
            "_price": price}


def _tennis(m):
    if not m.get("date") or not m.get("playerA") or not m.get("playerB"): return None
    t = m.get("time")
    start = parse_utc(f"{m['date']}T{t}:00Z") if t else parse_utc(f"{m['date']}T00:00:00Z")
    if not start: return None
    return {"sport": "tennis", "comp": f"{m.get('tour') or ''} · {m.get('tournament') or ''}".strip(" ·"),
            "tour": m.get("tour"), "id": m.get("id"), "date": m["date"], "start": iso(start), "timed": bool(t),
            "home": m["playerA"], "away": m["playerB"], "pick": m.get("pick"),
            "side": "h" if m.get("pick") == m["playerA"] else "a",
            "conf": m.get("confidence"), "list": bool(m.get("list")), "reserve": bool(m.get("reserve")),
            "published": m.get("published")}


def _sport(g):
    start = parse_utc(g.get("when"))
    if not start or not g.get("home") or not g.get("away"): return None
    return {"sport": g.get("sport"), "comp": g.get("label") or g.get("sport"), "id": g.get("id"),
            "date": start.date().isoformat(), "start": iso(start), "timed": True,
            "home": g["home"], "away": g["away"], "pick": g.get("pick"),
            "side": "h" if g.get("pick") == g.get("home") else "a",
            "conf": g.get("confidence"), "list": bool(g.get("list")), "reserve": bool(g.get("reserve")),
            "published": g.get("published")}


FOLDERS = (("predictions", _football), ("predictions-tennis", _tennis), ("predictions-sports", _sport))


def predictions(here=HERE):
    """Every prediction: per fixture, the latest copy published before its
    start, a moved fixture once (its latest placement). Each row carries the
    football archive's prices from every pre-start copy (`_prices`)."""
    copies = {}          # (sport, home, away) -> [row]
    for folder, norm in FOLDERS:
        for path in sorted(glob.glob(os.path.join(here, folder, "*.json"))):
            for g in _load(path, []) or []:
                try: r = norm(g)
                except Exception: r = None
                if not r: continue
                pub, start = parse_utc(r.get("published")), parse_utc(r["start"])
                if not pub or pub >= start: continue     # no proof it predates the start
                # the US sports carry the feed's id, which a moved game keeps
                # and a series' next game does not (MLB, 29 Sep-1 Oct 2026: the
                # same pairing three nights running). Tennis is grouped by the
                # pairing: its archive before late September has no id, so the
                # same match came in twice (35 matches), and two players do not
                # meet twice in TENNIS_MOVE_DAYS. Football has no id.
                by_id = r.get("id") and r["sport"] not in ("football", "tennis")
                grp = (r["sport"], "id", str(r["id"])) if by_id else (r["sport"], low(r["home"]), low(r["away"]))
                copies.setdefault(grp, []).append(r)
    out = []
    for rows in copies.values():
        rows.sort(key=lambda r: r["published"])
        latest = rows[-1]
        # the latest copy decides the fixture's start; any copy whose start
        # is more than MOVE_DAYS off it is another meeting of the same pair
        clusters = []
        window = TENNIS_MOVE_DAYS if rows[0]["sport"] == "tennis" else MOVE_DAYS
        for r in sorted(rows, key=lambda r: r["start"]):
            for c in clusters:
                # two copies with different ids are two matches (the same
                # players a week apart at two tournaments, 3 and 11 Oct 2026)
                ids_ok = not r.get("id") or all(not x.get("id") or x["id"] == r["id"] for x in c)
                if ids_ok and abs((parse_utc(c[-1]["start"]) - parse_utc(r["start"])).days) <= window:
                    c.append(r); break
            else:
                clusters.append([r])
        for c in clusters:
            keep = max(c, key=lambda r: r["published"])
            keep = dict(keep)
            keep["_dates"] = sorted({r["date"] for r in c})
            keep["_prices"] = [r["_price"] for r in sorted(c, key=lambda r: r["published"]) if r.get("_price")]
            out.append(keep)
    return out


# -------------------------------------------------------------------- results

def results(here=HERE):
    """Lookups for the three graded files."""
    fb = {}
    graded = _load(os.path.join(here, "record-graded.json"), {}) or {}
    for g in graded.get("graded") or []:
        fb[(g.get("date"), g.get("league"), low(g.get("home")), low(g.get("away")))] = g
    # a second copy of a match graded under another spelling (score.py, #464):
    # counted once, so this copy is marked and never chased as ungraded
    for g in graded.get("duplicates") or []:
        fb.setdefault((g.get("date"), g.get("league"), low(g.get("home")), low(g.get("away"))),
                      {"duplicate": True})
    tn_id, tn_names = {}, {}
    for g in (_load(os.path.join(here, "tennis-record.json"), {}) or {}).get("graded") or []:
        if g.get("key"): tn_id[str(g["key"])] = g
        tn_names[(g.get("date"), low(g.get("playerA")), low(g.get("playerB")))] = g
    sp = {}
    for g in (_load(os.path.join(here, "sports-graded.json"), {}) or {}).get("graded") or []:
        if g.get("id") is not None: sp[str(g["id"])] = g
    return fb, tn_id, tn_names, sp


def result_of(r, look):
    fb, tn_id, tn_names, sp = look
    if r["sport"] == "football":
        for d in r.get("_dates") or [r["date"]]:
            g = fb.get((d, r["comp"], low(r["home"]), low(r["away"])))
            if g and g.get("duplicate"):
                return "duplicate", None
            if g and g.get("result"):
                won = g["won"] if g.get("won") is not None else bool(g.get("ok"))
                return "won" if won else "lost", f"{g['result'][0]}-{g['result'][1]}"
        return None, None
    if r["sport"] == "tennis":
        g = tn_id.get(str(r.get("id"))) if r.get("id") else None
        g = g or tn_names.get((r["date"], low(r["home"]), low(r["away"])))
        if not g: return None, None
        if g.get("void"): return "void", g.get("note")
        return ("won" if g.get("ok") else "lost"), g.get("note")
    g = sp.get(str(r.get("id")))
    if not g: return None, None
    sc = g.get("score")
    sc = f"{sc[0]}-{sc[1]}" if isinstance(sc, list) and len(sc) == 2 else None
    if g.get("void"): return "void", sc
    return ("won" if g.get("ok") else "lost"), sc


# --------------------------------------------------------------------- prices

def _pool_prices(row, book):
    """[(first-or-last, price)] from a pool row, real prices only."""
    out, when = [], parse_utc(row.get("when"))
    pr = row.get("priced") or {}
    if pr.get("odds"):
        books = pr.get("bookOdds") or {}
        out.append(("first", {"o": pr["odds"], "b": pr.get("best"), "bb": pr.get("bestBook"), "h": books.get(book),
                              "n": len(books) or None, "src": pr.get("src") or "pool", "t": pr.get("pricedAt") or pr.get("at")}))
    elif not row.get("est") and row.get("odds"):
        books = row.get("bookOdds") or {}
        out.append(("first", {"o": row["odds"], "b": row.get("best"), "bb": row.get("bestBook"), "h": books.get(book),
                              "n": len(books) or None, "src": row.get("src") or "pool", "t": row.get("pricedAt")}))
    at = parse_utc(row.get("lastAt"))
    if row.get("lastOdds") and at and (not when or at < when):
        books = row.get("lastBooks") or {}
        top = max(books.items(), key=lambda kv: kv[1]) if books else (None, None)
        out.append(("last", {"o": row["lastOdds"], "b": row.get("lastBest") or top[1], "bb": top[0],
                             "h": books.get(book), "n": len(books) or None, "src": "pool", "t": row.get("lastAt")}))
    return out


def pool_prices(here=HERE):
    """{(sport, home, away): [(date, kind, price)]} from the pool archive."""
    out = {}
    try:
        sys.path.insert(0, here)
        import groupings as G
        rows, book = G.pool_rows(os.path.join(here, "groupings-archive")), G.CARD_BOOK
        sides = G._lb_sides
    except Exception as e:
        print(f"ledger: pool archive not read ({e})", file=sys.stderr)
        return out, BOOK
    for d, row in rows:
        h, a = sides(row)
        if not h or not a: continue
        side = row.get("side") or ("h" if row.get("pick") == h else "a" if row.get("pick") == a else None)
        for kind, p in _pool_prices(row, book):
            p["pick"] = row.get("pick"); p["side"] = side
            out.setdefault((row.get("sport"), low(h), low(a)), []).append((row.get("date") or d, kind, p))
    return out, book


def board_prices(here=HERE):
    """{(sport, home, away): price} read this build (groupings.json "prices")."""
    g = _load(os.path.join(here, "groupings.json"), {}) or {}
    out = {}
    for k, v in (g.get("prices") or {}).items():
        try: sport, h, a = k.split("|", 2)
        except ValueError: continue
        if not v or not v.get("o"): continue
        out[(sport, h, a)] = {"o": v["o"], "b": v.get("b"), "bb": v.get("bb"), "h": v.get("h"), "n": v.get("n"),
                              "src": "board", "t": v.get("t"), "pick": v.get("p")}
    return out


def _earlier(a, b):
    if not a: return b
    if not b: return a
    return a if (a.get("t") or "") <= (b.get("t") or "") else b


def _later(a, b):
    if not a: return b
    if not b: return a
    return a if (a.get("t") or "") >= (b.get("t") or "") else b


def _pre_start(p, start):
    t = parse_utc(p.get("t")) if p else None
    return p if p and (t is None or t < start) else None


def _for_pick(p, r):
    """A price is the pick's price only if it was for the same side."""
    if not p: return None
    if p.get("pick") is not None and low(p["pick"]) != low(r["pick"]): return None
    return {k: v for k, v in p.items() if k not in ("pick", "side") and v is not None}


def attach_prices(r, pool, board):
    start = parse_utc(r["start"])
    first = last = None
    for p in r.get("_prices") or []:            # football archive market, oldest first
        if p.get("side") != r["side"]: continue  # an earlier copy that picked the other side
        p = _pre_start({k: v for k, v in p.items() if k != "side" and v is not None}, start)
        first, last = _earlier(first, p), _later(last, p)
    key = (r["sport"], low(r["home"]), low(r["away"]))
    for d, kind, p in pool.get(key, []):
        try:
            if abs((datetime.fromisoformat(d).date() - start.date()).days) > MATCH_DAYS: continue
        except ValueError:
            continue
        p = _pre_start(_for_pick(p, r), start)
        if kind == "first": first = _earlier(first, p)
        last = _later(last, p)
    b = board.get(key)
    if b and start > datetime.now(timezone.utc):    # board prices are this build's, before the start
        b = _for_pick(b, r)
        first, last = _earlier(first, b), _later(last, b)
    return first, last


# --------------------------------------------------------------------- ledger

def ledger_key(r):
    if r.get("id"):
        return f"{r['sport']}|id|{r['id']}"
    return f"{r['sport']}|{low(r['home'])}|{low(r['away'])}|{r['start'][:10]}"


KEEP = ("sport", "comp", "tour", "id", "date", "start", "timed", "home", "away", "pick", "side",
        "conf", "list", "reserve", "celtic", "why", "published")


def band(conf):
    c = conf or 0
    lo = next(b for b in BANDS if c >= b - 1e-9)
    i = BANDS.index(lo)
    return f"{int(lo * 100)}+" if i == 0 else f"{int(lo * 100)}-{int(BANDS[i - 1] * 100)}"


def merge(old_rows, new_rows):
    """Old rows kept; a new row replaces its fields, a result once known is
    never lost to a later pending read, and prices keep the earliest first
    and the latest pre-start last."""
    rows = {r["key"]: r for r in old_rows or []}
    for n in new_rows:
        o = rows.get(n["key"])
        if not o:
            rows[n["key"]] = n; continue
        m = {**o, **{k: v for k, v in n.items() if v is not None}}
        if n.get("result") is None and o.get("result") is not None:
            m["result"], m["score"] = o["result"], o.get("score")
        m["first"] = _earlier(o.get("first"), n.get("first"))
        m["last"] = _later(o.get("last"), n.get("last"))
        rows[n["key"]] = m
    return sorted(rows.values(), key=lambda r: (r.get("start") or "", r["key"]))


def build_rows(here=HERE):
    look = results(here)
    pool, book = pool_prices(here)
    board = board_prices(here)
    out = []
    for r in predictions(here):
        res, score = result_of(r, look)
        first, last = attach_prices(r, pool, board)
        row = {"key": ledger_key(r), **{k: r.get(k) for k in KEEP if r.get(k) is not None},
               "band": band(r.get("conf")), "result": res, "score": score, "first": first, "last": last}
        out.append(row)
    return out, book


def _tally():
    return {"n": 0, "won": 0, "quoted": 0.0, "priced": 0, "returned": 0.0, "bestReturned": 0.0,
            "hill": 0, "hillReturned": 0.0}


def _add(t, r):
    t["n"] += 1; won = r["result"] == "won"
    t["won"] += won; t["quoted"] += r.get("conf") or 0
    p = r.get("last") or r.get("first")
    if p and p.get("o"):
        t["priced"] += 1; t["returned"] += p["o"] if won else 0
        t["bestReturned"] += (p.get("b") or p["o"]) if won else 0
    h = (r.get("last") or {}).get("h") or (r.get("first") or {}).get("h")
    if h:
        t["hill"] += 1; t["hillReturned"] += h if won else 0


def _done(t):
    out = {"n": t["n"], "won": t["won"]}
    if t["n"]:
        out["rate"] = round(t["won"] / t["n"], 4); out["quoted"] = round(t["quoted"] / t["n"], 4)
    if t["priced"]:
        out["priced"] = t["priced"]
    if t["hill"]:
        out["atHill"] = t["hill"]
    return out


def summary(rows):
    """Settled picks by sport, list / reserve / board and band: landed,
    quoted, and the flat-stake return at the recorded price (`ret`, the
    average or pool price), at the best price recorded (`retBest`) and at
    William Hill (`retHill`), each on the picks priced that way only. A
    tally, nothing fitted."""
    by = {}
    for r in rows:
        if r.get("result") not in ("won", "lost"): continue
        grp = "list" if r.get("list") else "reserve" if r.get("reserve") else "board"
        for k in (("all", grp, r["band"]), (r["sport"], grp, r["band"]), ("all", grp, "all"), (r["sport"], grp, "all")):
            _add(by.setdefault("|".join(k), _tally()), r)
    out = {}
    for k, t in sorted(by.items()):
        d = _done(t)
        # the return is only over the priced picks, so it is computed on them
        if t["priced"]:
            d["ret"] = round(t["returned"] / t["priced"] - 1, 4)
            d["retBest"] = round(t["bestReturned"] / t["priced"] - 1, 4)
        if t["hill"]:
            d["retHill"] = round(t["hillReturned"] / t["hill"] - 1, 4)
        out[k] = d
    return out


def ungraded(rows, now):
    """Picks still pending UNGRADED_DAYS after their start: counted by sport
    and competition, the list picks named. Those past UNGRADED_STALE days are
    counted apart (`stale`)."""
    chase, stale = {}, {}
    names = []
    for r in rows:
        if r.get("result") is not None: continue
        start = parse_utc(r.get("start"))
        if not start: continue
        age = (now - start).total_seconds() / 86400
        if age < UNGRADED_DAYS: continue
        tgt = stale if age >= UNGRADED_STALE else chase
        k = f"{r['sport']}|{r.get('comp') or ''}"
        c = tgt.setdefault(k, {"n": 0, "list": 0, "reserve": 0})
        c["n"] += 1; c["list"] += bool(r.get("list")); c["reserve"] += bool(r.get("reserve"))
        if r.get("list") and tgt is chase:
            names.append(f"{r['start'][:10]} {r['sport']} {r['home']} v {r['away']}")
    tot = lambda t: {"n": sum(c["n"] for c in t.values()), "list": sum(c["list"] for c in t.values()),
                     "reserve": sum(c["reserve"] for c in t.values())}
    order = lambda t: dict(sorted(t.items(), key=lambda kv: (-kv[1]["n"], kv[0])))
    return {"days": UNGRADED_DAYS, "staleDays": UNGRADED_STALE, "chase": tot(chase), "stale": tot(stale),
            "byComp": order(chase), "staleByComp": order(stale), "listPicks": sorted(names)}


def price_cover(rows):
    """How many settled picks carry a price, by sport, so a thin return is
    read as thin."""
    out = {}
    for r in rows:
        if r.get("result") not in ("won", "lost"): continue
        c = out.setdefault(r["sport"], {"settled": 0, "priced": 0, "atHill": 0})
        c["settled"] += 1
        p = r.get("last") or r.get("first")
        c["priced"] += bool(p and p.get("o"))
        c["atHill"] += bool((r.get("last") or {}).get("h") or (r.get("first") or {}).get("h"))
    return out


def write(now=None, here=HERE, path=None):
    now = now or datetime.now(timezone.utc)
    path = path or os.path.join(here, os.path.basename(LEDGER))
    new, book = build_rows(here)
    old = (_load(path, {}) or {}).get("rows") or []
    rows = merge(old, new)
    ug = ungraded(rows, now)
    out = {"generated": iso(now), "book": book, "n": len(rows),
           "summary": summary(rows), "priceCover": price_cover(rows), "ungraded": ug, "rows": rows}
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    os.replace(tmp, path)
    return out


def report(out, now=None, warn=None):
    now = now or datetime.now(timezone.utc)
    if warn is None:   # the first build of each UK Monday (the 05:15 UTC cron)
        uk = now.astimezone(UK)
        warn = uk.weekday() == 0 and uk.hour < 9
    st = {}
    for r in out["rows"]:
        k = r.get("result") or "pending"
        st[k] = st.get(k, 0) + 1
    print(f"ledger: {out['n']} predictions ({', '.join(f'{k} {v}' for k, v in sorted(st.items()))})")
    for sport, c in sorted(out["priceCover"].items()):
        print(f"  {sport}: {c['settled']} settled, {c['priced']} with a price, {c['atHill']} with {out['book']}'s")
    ug = out["ungraded"]
    line = (f"ungraded: {ug['chase']['n']} picks {ug['days']}+ days past their start with no result "
            f"({ug['chase']['list']} on the Daily List, {ug['chase']['reserve']} reserve); "
            f"{ug['stale']['n']} past {ug['staleDays']} days")
    top = "; ".join(f"{k} {c['n']}" for k, c in list(ug["byComp"].items())[:8])
    print(f"{'::warning::' if warn and ug['chase']['n'] else ''}{line}" + (f". Most: {top}" if top else ""))
    if warn and ug["listPicks"]:
        print(f"::warning::Daily List picks with no result: {'; '.join(ug['listPicks'][:15])}")


def main():
    out = write()
    report(out)


if __name__ == "__main__":
    main()
