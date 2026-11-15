"""Scale: winners with a second condition added, so the price is bigger
(15 Nov 2026; tiers and the margin bets the same day, RULE 2).

Douglas, 14 Nov 2026: "it's not really about scaling the stake so much. It's
actually more about scaling the odds and even reducing the stake ... create
another tab on this website called Scale." On the first mock-up: "I wasn't
able to find the Hungary NB third league or the Greece Gamma Ethniki league
... those aren't available on William Hill." On the first live day (two
football picks, no group), 15 Nov 2026: "it's just kind of showing like one
game per day ... we're going to have to be a little bit more flexible with
our floor ... at least 10 games per day ... break it down into tiers with
lines on that infographic that say daily list pick, daily list reserve pick,
everything else, and list it from strongest to weakest ... NFL, basketball,
you're going to need to propose something based on the data ... I need every
day to have at least 5 games, to add into some sort of scale accumulator."

So a Scale pick is the model's pick to win plus one more thing that must
happen (SPORTS):

  football   the pick wins AND both teams score. Only fixtures William Hill
             prices for that bet (markets.py's archive: `wbtts` with `h`).
             The chance is the model's own win-and-both-score number.
  tennis     the pick wins in straight sets.
  nba        the pick wins by 10 or more (Hill's handicap -9.5).
  nfl        the pick wins by 7 or more (handicap -6.5).
  rugby      the pick wins by 8 or more (handicap -7.5).

For every sport but football the chance shown is the record's own rate for
picks at that confidence (`band_rate`: a tally, never a fit, Rule 1) and
there is no price feed for the bet yet, so those picks are tracked and never
priced. College basketball and college football are left out: UK books
rarely price them.

Three tiers, shown in that order (TIERS):

  list       a Daily List pick, at the list's own bar
  reserve    a Daily List reserve pick (below the bar, Firm 62%+, clean)
  else       everything else the model picks at FLOOR (55%+), strongest
             first, and only as many as bring the day up to TARGET (10) games

Within a tier the order is the chance the Scale bet lands. Each UK day's
picks are archived in scale-archive/<day>.json as they stood before their
starts (a pick is replaced until it starts, never after), with the day's
groups (KINDS): a threefold, fourfold and fivefold from the top of that
order, and a football threefold (every leg priced at William Hill), each
frozen once its first leg starts. Everything is graded from the records
score.py, score_tennis.py and sports.py write. A group is won when every leg
landed its Scale bet; a void leg (a retirement) is settled on the rest. A
group's return is only counted when every leg had a William Hill price.

The days before the tab (LIVE_FROM) are replayed once under the current rule
(`replay_day`), from what was archived before each start and results dated
before the day, so the glance shows how the rule would have gone without any
pick having seen its own result. They are tallied apart (`before`), have no
prices, and are replayed again only when RULE changes.

    python3 scale.py        # CI: archive today's and tomorrow's, grade, write scale.json / scale.js

Writes scale.json and scale.js (window.__SCALE__) for the Scale tab. Display
and record only: nothing here feeds a model, the Daily List or the Card.
Standard library only. claude/scale-2026-11-15.md, claude/scale-tiers-2026-11-15.md.
"""
import gzip, json, os, re, sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ARCHIVE = "scale-archive"
RULE = 2                    # the pick and group rule; bump on any change (1: Daily List picks only, football and tennis)
LIVE_FROM = "2026-11-15"    # the tab's first day; earlier days are filled once from the pre-start archives and tallied apart
BOOK = "William Hill"
DAYS_AHEAD = 2              # UK days built: today and tomorrow
GLANCE_DAYS = 14            # days shown on the tab's glance strip
FLOOR = 0.55                # the model's confidence in the winner: nothing under it is a Scale pick
TARGET = 10                 # games a day: the "else" tier tops the day up to this many, never past it
BAND_MIN = 30               # a confidence band's own rate needs this many graded picks; else a wider band
TIERS = ("list", "reserve", "else")
SPORTS = {
    "football": {"name": "Football", "bet": "And both teams score", "long": "Win and both teams score"},
    "tennis": {"name": "Tennis", "bet": "In straight sets", "long": "Win in straight sets", "find": "set betting 2-0"},
    "nba": {"name": "NBA", "bet": "By 10 or more", "long": "Win by 10 or more", "margin": 10, "find": "handicap -9.5"},
    "nfl": {"name": "NFL", "bet": "By 7 or more", "long": "Win by 7 or more", "margin": 7, "find": "handicap -6.5"},
    "rugby": {"name": "Rugby", "bet": "By 8 or more", "long": "Win by 8 or more", "margin": 8, "find": "handicap -7.5"},
}
# (id, legs, name, sport or None for any): built in this order from the picks still to start
KINDS = ((3, 3, "Scale threefold", None), (4, 4, "Scale fourfold", None), (5, 5, "Scale fivefold", None),
         ("f3", 3, "Football threefold", "football"))
FINE = (0.55, 0.62, 0.70, 0.75, 0.80, 0.85, 0.90, 1.01)
WIDE = ((0.55, 0.70, 0.80, 1.01), (0.55, 0.70, 1.01), (0.55, 1.01))


def _load(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default


def parse_utc(s):
    if not s: return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else None


# ------------------------------------------------- the second condition, by sport

SET = re.compile(r"\b(\d{1,2})-(\d{1,2})(?:\s*\(\d+(?:-\d+)?\))?")


def straight_sets(row):
    """True when a graded tennis row's winner lost no set, False when they
    dropped one, None when it cannot be said (no score, a retirement or a
    walkover: bookmakers void the bet)."""
    if not row or row.get("void") or row.get("retired"):
        return None
    sets = SET.findall(str(row.get("note") or ""))
    if len(sets) < 2:
        return None
    lost = sum(1 for a, b in sets if int(b) > int(a))
    won = sum(1 for a, b in sets if int(a) > int(b))
    if won < 2:
        return None
    return lost == 0


def margin_of(row):
    """The pick's winning margin in a graded sports row (negative: it lost)."""
    h, a = row["score"]
    return (h - a) if row.get("pick") == row.get("home") else (a - h)


def samples(trec, sgraded):
    """{sport: [(confidence, won, landed the Scale bet, date)]} over every
    graded pick at FLOOR+, for the sports whose chance is a tally of the record."""
    out = {s: [] for s in SPORTS if s != "football"}
    for g in (trec or {}).get("graded") or []:
        c = g.get("confidence") or 0
        if c < FLOOR or g.get("void") or g.get("retired"):
            continue
        ss = straight_sets(g) if g.get("ok") else False
        if ss is None:
            continue
        out["tennis"].append((c, bool(g.get("ok")), bool(ss), g.get("date") or ""))
    for g in (sgraded or {}).get("graded") or []:
        cfg = SPORTS.get(g.get("sport")) or {}
        c = g.get("confidence") or 0
        if not cfg.get("margin") or c < FLOOR or g.get("void") or not g.get("score"):
            continue
        m = margin_of(g)
        out[g["sport"]].append((c, m > 0, m >= cfg["margin"], str(g.get("when") or "")[:10]))
    return out


def band_rate(conf, sample):
    """(chance, landed, picks) for a pick at `conf`: the record's rate in the
    narrowest confidence band around it holding BAND_MIN picks (FINE, then
    each of WIDE), or in every pick at FLOOR+ when none does."""
    best = (None, 0, 0)
    for edges in (FINE,) + WIDE:
        for lo, hi in zip(edges, edges[1:]):
            if lo <= conf < hi:
                rows = [x for x in sample if lo <= x[0] < hi]
                k = sum(1 for x in rows if x[2])
                if len(rows) >= BAND_MIN:
                    return round(k / len(rows), 4), k, len(rows)
                if rows:
                    best = (round(k / len(rows), 4), k, len(rows))
    return best


# ---------------------------------------------------------------------- picks

def league_name(code):
    try:
        import engine as E
        lg = E.LEAGUES.get(code) or {}
        return f"{lg.get('country', '')} · {lg.get('name', code)}".strip(" ·")
    except Exception:
        return code


def tier_of(i):
    return "list" if i.get("list") else "reserve" if i.get("reserve") else "else"


def rank(p):
    """The page's order: tier, then the chance the Scale bet lands."""
    return (TIERS.index(p.get("tier") or "list"), -(p.get("chance") or 0), p["start"], p["key"])


def day_picks(day, now, here, market_rows, sample, proxy=None):
    """(candidates, left off) for one UK day: every game the model picks at
    FLOOR+ in a Scale sport, as archived before its start (daylist.pinned),
    with its tier and Scale bet; football only where BOOK prices
    win-and-both-score. `left off` lists the Daily List football picks it
    does not price. The "else" tier is cut to the day's top-up by `choose`.

    `proxy` is for a day before the price archive (`replay_day`): a football
    fixture counts as priced at BOOK when the pool holds BOOK's match price
    for it or its league is one BOOK prices the bet in now, its chance is the
    model's number worked from the archived expected goals, and it has no
    price."""
    import daylist as D
    archives = D.read_archives(day, here)
    items = D.pinned(day, archives, now, every=True)
    rows = {}
    if proxy is not None:
        for kind, g in archives:
            if kind == "football" and g.get("league"):
                rows[(f"f|{g['league']}|{g.get('date')}|{g.get('home')}|{g.get('away')}", g.get("published"))] = g
    picks, off = [], []
    for i in sorted(items, key=lambda i: (i["start"], i["key"])):
        cfg = SPORTS.get(i["sport"])
        conf = i.get("confidence") or 0
        if not cfg or i.get("side") not in ("h", "a") or i.get("tier") == "No read":
            continue
        tier = tier_of(i)
        if conf < FLOOR and tier == "else":
            continue
        base = {"key": i["key"], "sport": i["sport"], "tier": tier, "start": i["start"], "timed": i.get("timed", True),
                "comp": i.get("comp"), "home": i["home"], "away": i["away"], "pick": i["pick"],
                "side": i.get("side"), "conf": conf, "bet": cfg["bet"]}
        if i["sport"] == "football":
            base.update(league=i.get("league"), date=i.get("date"), comp=league_name(i.get("league")))
            if proxy is None:
                row = market_rows.get((i.get("league"), i.get("date"), i["home"], i["away"]))
                w = ((row or {}).get("m") or {}).get("wbtts") or {}
                if not w.get("h") or not w.get("p") or w.get("s") != i.get("side"):
                    w = None
            else:
                w = proxy_football(i, rows.get((i["key"], i.get("published"))), proxy)
            if not w:
                if tier == "list":
                    off.append({k: base[k] for k in ("key", "start", "comp", "pick")})
                continue
            base.update(chance=w["p"], basis="model", price=w.get("h"), book=BOOK,
                        best=w.get("b"), bestBook=w.get("bb"), fair=w.get("f"))
        else:
            ch, k, n = band_rate(conf, sample.get(i["sport"]) or [])
            if ch is None:
                continue
            base.update(id=i.get("id"), date=i.get("date"), chance=ch, basis=f"{k} of {n} picks like it",
                        price=None, find=cfg.get("find"))
        picks.append(base)
    return picks, off


def proxy_football(i, g, proxy):
    """The win-and-both-score number for an archived football pick on a day
    before the price archive, or None when BOOK is not known to price it."""
    import markets as M
    if not g or not g.get("xg") or not g.get("p") or g.get("unrated"):
        return None
    if i.get("league") not in proxy["leagues"] and (i.get("date"), i["home"], i["away"]) not in proxy["fixtures"]:
        return None
    side, nums = M.numbers(g["xg"][0], g["xg"][1], g["p"], g.get("btts"), g.get("over25"))
    w = nums.get("wbtts") or {}
    if side != i.get("side") or w.get("s") != side or not w.get("p"):
        return None
    return {"p": w["p"]}


def book_fixtures():
    """{(date, home, away)} of football fixtures the priced pool holds BOOK's
    match price for: the fixture-level sign that BOOK offered the game."""
    out = set()
    try:
        import groupings as G
        for _, x in G.pool_rows():
            if x.get("sport") != "football": continue
            for bo in (x.get("bookOdds"), (x.get("priced") or {}).get("bookOdds")):
                if isinstance(bo, dict) and bo.get(BOOK):
                    out.add((x.get("date"), x.get("home"), x.get("away")))
    except Exception as e:
        print(f"scale: pool not read for the replay ({type(e).__name__}: {e})", file=sys.stderr)
    return out


def replay_day(day, here, sample, proxy):
    """A day before the tab, rebuilt under the current rule from what was
    archived before each start and nothing else: the same tiers, order,
    top-up and groups, as they would have stood before the day's first
    start. The tallied chances use only results dated before the day, so no
    pick or its place in the order has seen its own result. Football has no
    price on file for these days (`proxy`), so nothing here has a return."""
    far = datetime(2100, 1, 1, tzinfo=timezone.utc)
    early = datetime(2000, 1, 1, tzinfo=timezone.utc)
    seen = {s: [x for x in rows if x[3] and x[3] < day] for s, rows in sample.items()}
    cands, off = day_picks(day, far, here, {}, seen, proxy)
    top = [p for p in cands if p["tier"] != "else"]
    rest = sorted([p for p in cands if p["tier"] == "else"], key=rank)
    picks = top + rest[:max(0, TARGET - len(top))]
    return {"date": day, "rule": RULE, "replay": True,
            "picks": sorted(picks, key=lambda p: (p["start"], p["key"])),
            "off": sorted(off, key=lambda p: (p["start"], p["key"])),
            "groups": build_groups(picks, early)}


def choose(cands, old, now):
    """The day's picks from its candidates: every list and reserve pick, and
    from "else" only games still to start, strongest first, as many as bring
    the day to TARGET with the "else" picks already frozen on file. A started
    "else" game is never added after the fact."""
    started = lambda s: (parse_utc(s) or now) <= now
    top = [p for p in cands if p["tier"] != "else"]
    held = [p for p in (old or {}).get("picks") or [] if p.get("tier") == "else" and started(p["start"])]
    held_keys = {p["key"] for p in held}
    need = max(0, TARGET - len(top) - len(held))
    opened = sorted([p for p in cands if p["tier"] == "else" and not started(p["start"]) and p["key"] not in held_keys], key=rank)
    return top + opened[:need]


def build_groups(picks, now):
    """The day's groups from the picks still to start, in the page's order:
    the top three, four and five of any sport, and the top three football
    picks (the one group priced on every leg)."""
    cand = sorted([p for p in picks if parse_utc(p["start"]) > now and p.get("chance")], key=rank)
    out = []
    for kind, k, name, sport in KINDS:
        legs = [p for p in cand if sport in (None, p["sport"])][:k]
        if len(legs) < k:
            continue
        if sport and any(g["legs"] == [p["key"] for p in legs] for g in out):
            continue                # the football threefold is the threefold already
        ch = win = 1.0
        for p in legs:
            ch *= p["chance"]; win *= (p.get("conf") or 0)
        price = None
        if all(p.get("price") for p in legs):
            price = 1.0
            for p in legs: price *= p["price"]
            price = round(price, 2)
        out.append({"kind": kind, "name": name, "legs": [p["key"] for p in legs], "chance": round(ch, 4),
                    "winners": round(win, 4), "price": price, "first": min(p["start"] for p in legs)})
    return out


def merge_day(old, picks, off, groups, now, stamp):
    """The day's archive after this build. A pick, and a left-off entry, is
    replaced until it starts and kept as it stood from then on. One that has
    started and is not on file is still added: every field of it comes from
    copies archived before its start (daylist.pinned, markets.live_rows), so
    a missed build loses nothing (`choose` never passes a started "else"
    pick). A group is replaced until its first leg starts, and is never built
    from a leg that has started."""
    started = lambda s: (parse_utc(s) or now) <= now
    old = old or {}
    keep = [p for p in old.get("picks") or [] if started(p["start"])]
    keys = {p["key"] for p in keep}
    new_picks = keep + [p for p in picks if p["key"] not in keys]
    have = {p["key"] for p in new_picks}
    off_keep = [p for p in old.get("off") or [] if started(p["start"]) and p["key"] not in have]
    okeys = {p["key"] for p in off_keep} | have
    new_off = off_keep + [p for p in off if p["key"] not in okeys]
    frozen = {g["kind"]: g for g in old.get("groups") or [] if started(g["first"])}
    new_groups = list(frozen.values())
    for g in groups:
        if g["kind"] not in frozen and all(k in have for k in g["legs"]):
            new_groups.append(dict(g, published=stamp))
    order = [k[0] for k in KINDS]
    return {"date": old.get("date"), "rule": RULE, "picks": sorted(new_picks, key=lambda p: (p["start"], p["key"])),
            "off": sorted(new_off, key=lambda p: (p["start"], p["key"])),
            "groups": sorted(new_groups, key=lambda g: order.index(g["kind"]) if g["kind"] in order else 99)}


# -------------------------------------------------------------------- grading

def results(here=HERE):
    """(football, tennis by id, tennis by pairing, other sports by id)."""
    import markets as M
    fb = M.results(here)
    tn, tn2, sp = {}, {}, {}
    for g in (_load(os.path.join(here, "tennis-record.json"), {}) or {}).get("graded") or []:
        if g.get("key"): tn[str(g["key"])] = g
        tn2[(g.get("date"), g.get("playerA"), g.get("playerB"))] = g
    for g in (_load(os.path.join(here, "sports-graded.json"), {}) or {}).get("graded") or []:
        if g.get("id"): sp[(g.get("sport"), str(g["id"]))] = g
    return fb, tn, tn2, sp


def settle(p, res):
    """(state, detail) for a pick: "scale" (the winner and the Scale bet),
    "won" (the winner only), "lost", "void" or None while there is no result.
    The score in `detail` is the pick's first."""
    import markets as M
    fb, tn, tn2 = res[:3]
    sp = res[3] if len(res) > 3 else {}
    if p["sport"] == "football":
        g = M._result_for({"league": p.get("league"), "home": p["home"], "away": p["away"], "date": p.get("date") or p["start"][:10]}, fb)
        if not g: return None, None
        hg, ag = g["result"]
        won = hg > ag if p.get("side") == "h" else ag > hg
        mine, theirs = (hg, ag) if p.get("side") == "h" else (ag, hg)       # the pick's score first, as the row reads
        return ("scale" if won and hg and ag else "won" if won else "lost"), f"{mine}-{theirs}"
    if p["sport"] == "tennis":
        g = tn.get(str(p.get("id"))) or tn2.get((p.get("date"), p["home"], p["away"]))
        if not g: return None, None
        if g.get("void"): return "void", g.get("note")
        if not g.get("ok"): return "lost", g.get("note")
        ss = straight_sets(g)
        return ("void" if ss is None else "scale" if ss else "won"), g.get("note")
    g = sp.get((p["sport"], str(p.get("id"))))
    if not g: return None, None
    if g.get("void") or not g.get("score"): return "void", None
    m = margin_of(g)
    line = (SPORTS.get(p["sport"]) or {}).get("margin") or 1
    h, a = g["score"]
    mine, theirs = (h, a) if g.get("pick") == g.get("home") else (a, h)
    return ("scale" if m >= line else "won" if m > 0 else "lost"), f"{mine}-{theirs}"


def grade_group(g, by_key):
    """A group's state from its legs: lost as soon as one leg missed its
    Scale bet, won when every leg that stood landed it, void when none stood;
    `ret` the return on a unit stake when every standing leg was priced."""
    legs = [by_key.get(k) for k in g["legs"]]
    if any(l is None for l in legs):
        return {"state": "pending"}
    states = [l.get("state") for l in legs]
    if any(s in ("won", "lost") for s in states):
        out = {"state": "lost"}
        if g.get("price"): out["ret"] = 0.0
        return out
    if any(s is None for s in states):
        return {"state": "pending"}
    stand = [l for l in legs if l["state"] == "scale"]
    if not stand:
        return {"state": "void"}
    out = {"state": "won"}
    if all(l.get("price") for l in stand):
        ret = 1.0
        for l in stand: ret *= l["price"]
        out["ret"] = round(ret, 2)
    return out


def priced_keys(here=HERE):
    """The ledger's picks a bookmaker feed priced before the start (ledger.py:
    the football archive's market, the pool, the board prices), as
    {(sport, id)} and {(sport, home, away, date)}, with the book where it was
    William Hill. The sign that a game could be bet on (15 Nov 2026, Douglas:
    "make sure all games were a game / league available to bet on")."""
    rows = (_load(os.path.join(here, "results-ledger.json.gz"), {}) or {}).get("rows") or []
    out = {}
    for r in rows:
        src = r.get("last") or r.get("first") or {}
        if not src.get("o"): continue
        book = BOOK if (r.get("last") or {}).get("h") or (r.get("first") or {}).get("h") else "a bookmaker"
        if r.get("id"):
            out[(r["sport"], str(r["id"]))] = book
        out[(r["sport"], str(r.get("home", "")).lower(), str(r.get("away", "")).lower(), str(r.get("start", ""))[:10])] = book
    return out


def priced_by(p, keys):
    """The book that priced a Scale pick before its start, or None. Football
    carries its own answer (the win-and-both-score price, or the proxy for
    a replayed day); the other sports are looked up in the ledger."""
    if p.get("sport") == "football":
        return BOOK if p.get("price") else (BOOK if keys.get(("football", p["home"].lower(), p["away"].lower(), p["start"][:10])) else None)
    if p.get("id") and (p["sport"], str(p["id"])) in keys:
        return keys[(p["sport"], str(p["id"]))]
    return keys.get((p["sport"], p["home"].lower(), p["away"].lower(), p["start"][:10]))


def both_scored(p):
    """True / False for a settled football pick (from its score), else None."""
    if p.get("sport") != "football" or not p.get("detail"):
        return None
    m = re.fullmatch(r"(\d+)-(\d+)", str(p["detail"]).strip())
    return bool(m and int(m.group(1)) > 0 and int(m.group(2)) > 0) if m else None


def _tally():
    return {"n": 0, "won": 0, "scale": 0, "lost": 0, "void": 0, "priced": 0, "returned": 0.0}


def _add(t, p):
    s = p.get("state")
    if s is None: return
    if s == "void":
        t["void"] += 1; return
    t["n"] += 1; t["won"] += s in ("won", "scale"); t["scale"] += s == "scale"; t["lost"] += s == "lost"
    if p.get("price"):
        t["priced"] += 1; t["returned"] += p["price"] if s == "scale" else 0.0


def _done(t):
    out = {k: t[k] for k in ("n", "won", "scale", "lost", "void")}
    if t["priced"]:
        out["priced"] = t["priced"]; out["ret"] = round(t["returned"] / t["priced"] - 1, 4)
    return out


# ---------------------------------------------------------------------- build

def uk_day(dt):
    import daylist as D
    return D.uk_day(dt)


def coverage(market_rows, now, days=14):
    """Leagues BOOK priced win-and-both-score in over the last `days`, from
    the markets archive: [{"league", "name", "n"}], most fixtures first."""
    since = (now.date() - timedelta(days=days)).isoformat()
    by = {}
    for r in market_rows.values():
        if r["date"] < since: continue
        if (((r.get("m") or {}).get("wbtts")) or {}).get("h"):
            by[r["league"]] = by.get(r["league"], 0) + 1
    return [{"league": c, "name": league_name(c), "n": n} for c, n in sorted(by.items(), key=lambda kv: (-kv[1], kv[0]))]


def replay(here, covered, since):
    """Football picks graded before the Scale archive, in leagues BOOK prices
    now (`covered`), by tier: how often the winner and the Scale bet landed.
    Results only, no prices."""
    by = {t: _tally() for t in TIERS}
    for g in (_load(os.path.join(here, "record-graded.json"), {}) or {}).get("graded") or []:
        if not g.get("result") or g["league"] not in covered or g["date"] >= since or g.get("pick") not in ("h", "a"):
            continue
        tier = tier_of(g)
        if tier == "else" and ((g.get("confidence") or 0) < FLOOR or g.get("unrated")):
            continue
        hg, ag = g["result"]
        won = hg > ag if g["pick"] == "h" else ag > hg
        _add(by[tier], {"state": "scale" if won and hg and ag else "won" if won else "lost"})
    return {t: _done(v) for t, v in by.items()}


def basis(sample):
    """What the tallied chances rest on: per sport, every graded pick at
    FLOOR+ and those at 75%+ (won, landed the Scale bet)."""
    def tot(rows):
        return {"n": len(rows), "won": sum(1 for x in rows if x[1]), "scale": sum(1 for x in rows if x[2])}
    return {s: {"all": tot(rows), "strong": tot([x for x in rows if x[0] >= 0.75])} for s, rows in sample.items()}


def build(now=None, here=HERE):
    import markets as M
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    market_rows = {(r["league"], r["date"], r["home"], r["away"]): r for r in M.live_rows(here)}
    sample = samples(_load(os.path.join(here, "tennis-record.json"), {}), _load(os.path.join(here, "sports-graded.json"), {}))
    adir = os.path.join(here, ARCHIVE)
    os.makedirs(adir, exist_ok=True)
    today = date.fromisoformat(uk_day(now))
    proxy = None
    for k in range(-GLANCE_DAYS, DAYS_AHEAD):
        day = (today + timedelta(days=k)).isoformat()
        path = os.path.join(adir, f"{day}.json")
        old = _load(path, {}) or {}
        if day < LIVE_FROM:
            # before the tab: replayed once under the current rule, and again only when the rule changes
            if old and (old.get("rule") or 1) >= RULE:
                continue
        elif k < 0 and old:
            continue                # a past live day on file is never rebuilt
        try:
            if day < LIVE_FROM:
                if proxy is None:
                    proxy = {"leagues": {c["league"] for c in coverage(market_rows, now)}, "fixtures": book_fixtures()}
                merged = replay_day(day, here, sample, proxy)
            else:
                cands, off = day_picks(day, now, here, market_rows, sample)
                picks = choose(cands, old, now)
                merged = merge_day(old, picks, off, build_groups(picks, now), now, stamp)
                merged["date"] = day
        except Exception as e:      # a bad archive never stops the days already on file
            print(f"scale: {day} not built ({type(e).__name__}: {e})", file=sys.stderr)
            continue
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(merged, f, separators=(",", ":"), ensure_ascii=False)
        os.replace(path + ".tmp", path)

    res = results(here)
    pkeys = priced_keys(here)
    files = sorted(fn for fn in os.listdir(adir) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", fn))
    by_sport, by_tier, before, before_tier, kinds, before_kinds, graded_groups, days_out, glance = {}, {}, {}, {}, {}, {}, [], [], []
    for fn in files:
        d = _load(os.path.join(adir, fn), {}) or {}
        day = fn[:-5]
        by_key = {}
        for p in d.get("picks") or []:
            p.setdefault("tier", "list")        # rule 1 files: Daily List picks only
            st, detail = settle(p, res)
            p["state"], p["detail"] = st, detail
            by_key[p["key"]] = p
            if d.get("replay"):
                _add(before.setdefault(p["sport"], _tally()), p)
                _add(before_tier.setdefault(p["tier"], _tally()), p)
            else:
                _add(by_sport.setdefault(p["sport"], _tally()), p)
                _add(by_tier.setdefault(p["tier"], _tally()), p)
        groups = []
        for g in d.get("groups") or []:
            gg = dict(g, **grade_group(g, by_key))
            groups.append(gg)
            t = (before_kinds if d.get("replay") else kinds).setdefault(str(g["kind"]), {"name": g["name"], "n": 0, "won": 0, "void": 0, "priced": 0, "returned": 0.0})
            if gg["state"] in ("won", "lost"):
                t["n"] += 1; t["won"] += gg["state"] == "won"
                if "ret" in gg:
                    t["priced"] += 1; t["returned"] += gg["ret"]
                if not d.get("replay"): graded_groups.append({"date": day, "name": g["name"], "kind": g["kind"], "state": gg["state"], "price": g.get("price"),
                                      "ret": gg.get("ret"), "legs": [by_key[k]["pick"] for k in g["legs"] if k in by_key]})
            elif gg["state"] == "void":
                t["void"] += 1
        entry = {"date": day, "picks": sorted(d.get("picks") or [], key=rank), "off": d.get("off") or [], "groups": groups}
        in_glance = (today - timedelta(days=GLANCE_DAYS)).isoformat() <= day <= today.isoformat()
        if day >= today.isoformat() or in_glance:
            days_out.append(dict(entry, replay=bool(d.get("replay")), past=day < today.isoformat()))
        if in_glance:
            glance.append({"date": day, "off": len(entry["off"]), "replay": bool(d.get("replay")),
                           # every pick of the day in the tab's order (tier, then the chance the bet lands), with
                           # what the page needs to show the top ten as a table (15 Nov 2026, Douglas: "10 games
                           # shown with what the recommendation was ... whether or not that won or lost ... and if
                           # both teams scored")
                           "dots": [{"k": p["key"], "sport": p["sport"], "tier": p["tier"], "pick": p["pick"], "start": p["start"],
                                     "home": p["home"], "away": p["away"], "side": p.get("side"), "comp": p.get("comp"),
                                     "conf": p.get("conf"), "chance": p.get("chance"),
                                     "state": p["state"] or ("started" if (parse_utc(p["start"]) or now) <= now else "up"),
                                     "detail": p.get("detail"), "btts": both_scored(p),
                                     "priced": priced_by(p, pkeys)} for p in entry["picks"]]})
    cov = coverage(market_rows, now)
    order = [str(k[0]) for k in KINDS]
    out = {"generated": stamp, "rule": RULE, "book": BOOK, "today": today.isoformat(), "from": LIVE_FROM,
           "floor": FLOOR, "target": TARGET, "tiers": list(TIERS),
           "sports": {s: {k: v for k, v in c.items() if k in ("name", "bet", "long", "find")} for s, c in SPORTS.items()},
           "days": days_out, "glance": glance,
           "record": {"bySport": {s: _done(t) for s, t in sorted(by_sport.items())},
                      "byTier": {t: _done(by_tier[t]) for t in TIERS if t in by_tier},
                      "groups": {k: {"name": t["name"], "n": t["n"], "won": t["won"], "void": t["void"], "priced": t["priced"],
                                     **({"ret": round(t["returned"] / t["priced"] - 1, 4)} if t["priced"] else {})}
                                 for k, t in sorted(kinds.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 99)},
                      "recent": graded_groups[-30:][::-1]},
           "before": {"bySport": {s: _done(t) for s, t in sorted(before.items())},
                      "byTier": {t: _done(before_tier[t]) for t in TIERS if t in before_tier},
                      "groups": {k: {"name": t["name"], "n": t["n"], "won": t["won"], "void": t["void"]}
                                 for k, t in sorted(before_kinds.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 99)}},
           "replay": {"football": replay(here, {c["league"] for c in cov}, LIVE_FROM), "basis": basis(sample)},
           "leagues": cov}
    with open(os.path.join(here, "scale.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    with open(os.path.join(here, "scale.js"), "w", encoding="utf-8") as f:
        f.write("window.__SCALE__=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/") + ";")
    return out


def main():
    out = build()
    for d in out["days"]:
        if d.get("past"): continue
        by = {}
        for p in d["picks"]:
            by[p["tier"]] = by.get(p["tier"], 0) + 1
        print(f"scale {d['date']}: {len(d['picks'])} picks (" + ", ".join(f"{by.get(t, 0)} {t}" for t in TIERS) +
              f"), {len(d['off'])} list football left off, {len(d['groups'])} group(s)")
    r = out["record"]["bySport"]
    print("scale record: " + ("; ".join(f"{s} {t['scale']} of {t['n']} landed the Scale ({t['won']} won)" for s, t in r.items()) or "nothing graded yet"))
    bt = out["before"]["byTier"]
    if bt:
        print("scale replay before the tab: " + "; ".join(f"{t} {v['scale']} of {v['n']} landed ({v['won']} won)" for t, v in bt.items()) +
              "; groups " + ", ".join(f"{g['name']} {g['won']} of {g['n']}" for g in out["before"]["groups"].values()))
    print(f"scale: {len(out['leagues'])} leagues priced at {BOOK} for win and both score in the last 14 days")


if __name__ == "__main__":
    main()
