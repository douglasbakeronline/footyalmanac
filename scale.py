"""Scale: Daily List winners with a second condition added, so the price is
bigger (15 Nov 2026).

Douglas, 14 Nov 2026: "it's not really about scaling the stake so much. It's
actually more about scaling the odds and even reducing the stake ... create
another tab on this website called Scale." And: "I don't want to come down
from confidence banding. I still want to make sure we're picking results that
are definitely going to win ... The important thing is to track and have
visibility on that tracking." Then, on the first mock-up: "I wasn't able to
find the Hungary NB third league or the Greece Gamma Ethniki league ... those
aren't available on William Hill."

So a Scale pick is a Daily List pick, at the list's own confidence, plus one
more thing that must happen:

  football   the pick wins AND both teams score. Only fixtures William Hill
             prices for that bet (markets.py's archive: `wbtts` with `h`);
             a list pick it does not price is counted as left off. The chance
             is the model's own win-and-both-score number.
  tennis     the pick wins in straight sets. The chance shown is the record's
             own rate for picks at that confidence (a tally, never a fit:
             Rule 1), and there is no price feed for the bet yet, so tennis
             picks are tracked and never priced.

Other sports' margin bets (the NBA by 10+, the NFL by 7+, rugby by 8+) wait
for a price feed check; SPORTS is where they will be added.

Each UK day's picks are archived in scale-archive/<day>.json as they stood
before their starts (a pick is replaced until it starts, never after; a past
day with no file is filled once from the same pre-start archives), with
the day's groups: a threefold, fourfold and fivefold of the picks most likely
to land, nested, each frozen once its first leg starts. Everything is graded
from the records score.py and score_tennis.py write. A group is won when
every leg landed its Scale bet; a retirement voids a tennis leg and the group
is settled on the rest. A group's return is only counted when every leg had a
William Hill price.

    python3 scale.py        # CI: archive today's and tomorrow's, grade, write scale.json / scale.js

Writes scale.json and scale.js (window.__SCALE__) for the Scale tab. Display
and record only: nothing here feeds a model, the Daily List or the Card.
Standard library only. claude/scale-2026-11-15.md.
"""
import gzip, json, os, re, sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ARCHIVE = "scale-archive"
RULE = 1                    # the pick and group rule; bump on any change
LIVE_FROM = "2026-11-15"    # the tab's first day; earlier days are filled once from the pre-start archives and tallied apart
BOOK = "William Hill"
DAYS_AHEAD = 2              # UK days built: today and tomorrow
GLANCE_DAYS = 14            # days shown on the tab's glance strip
KINDS = ((3, "Scale threefold"), (4, "Scale fourfold"), (5, "Scale fivefold"))
TENNIS_BANDS = (0.75, 0.80, 0.85, 0.90, 1.01)
TENNIS_BAND_MIN = 30        # a band's own straight-sets rate needs this many picks; else the pooled rate
BETS = {"football": "And both teams score", "tennis": "In straight sets"}


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


# --------------------------------------------------------------------- tennis

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


def tennis_rates(trec):
    """The record's straight-sets rate for tennis picks by confidence band,
    over every graded pick at 75%+: [{"from", "to", "n", "won", "straight"}]
    and the pooled row. A tally shown as the pick's chance."""
    bands = [{"from": lo, "to": min(hi, 1.0), "n": 0, "won": 0, "straight": 0} for lo, hi in zip(TENNIS_BANDS, TENNIS_BANDS[1:])]
    pool = {"from": TENNIS_BANDS[0], "to": 1.0, "n": 0, "won": 0, "straight": 0}
    for g in (trec or {}).get("graded") or []:
        c = g.get("confidence") or 0
        if c < TENNIS_BANDS[0] or g.get("void") or g.get("retired"):
            continue
        ss = straight_sets(g) if g.get("ok") else False
        if g.get("ok") and ss is None:
            continue
        for b in bands + [pool]:
            if b["from"] <= c < (b["to"] if b["to"] < 1.0 else 1.01):
                b["n"] += 1; b["won"] += bool(g.get("ok")); b["straight"] += bool(ss)
    return bands, pool


def tennis_chance(conf, rates):
    bands, pool = rates
    for b in bands:
        if b["from"] <= conf < (b["to"] if b["to"] < 1.0 else 1.01) and b["n"] >= TENNIS_BAND_MIN:
            return round(b["straight"] / b["n"], 4), b["straight"], b["n"]
    if pool["n"]:
        return round(pool["straight"] / pool["n"], 4), pool["straight"], pool["n"]
    return None, 0, 0


# ---------------------------------------------------------------------- picks

def league_name(code):
    try:
        import engine as E
        lg = E.LEAGUES.get(code) or {}
        return f"{lg.get('country', '')} · {lg.get('name', code)}".strip(" ·")
    except Exception:
        return code


def day_picks(day, now, here, market_rows, rates):
    """(picks, left off) for one UK day: the Daily List's football and tennis
    picks as pinned before their starts (daylist.pinned), football only where
    BOOK prices win-and-both-score. `left off` lists the football picks it
    does not price."""
    import daylist as D
    items = [i for i in D.pinned(day, D.read_archives(day, here), now) if i.get("list")]
    picks, off = [], []
    for i in sorted(items, key=lambda i: (i["start"], i["key"])):
        base = {"key": i["key"], "sport": i["sport"], "start": i["start"], "timed": i.get("timed", True),
                "comp": i.get("comp"), "home": i["home"], "away": i["away"], "pick": i["pick"],
                "side": i.get("side"), "conf": i.get("confidence")}
        if i["sport"] == "football":
            row = market_rows.get((i.get("league"), i.get("date"), i["home"], i["away"]))
            w = ((row or {}).get("m") or {}).get("wbtts") or {}
            base.update(league=i.get("league"), date=i.get("date"), comp=league_name(i.get("league")))
            if not w.get("h") or w.get("s") != i.get("side"):
                off.append({k: base[k] for k in ("key", "start", "comp", "pick")})
                continue
            base.update(bet=BETS["football"], chance=w.get("p"), basis="model", price=w["h"], book=BOOK,
                        best=w.get("b"), bestBook=w.get("bb"), fair=w.get("f"))
        elif i["sport"] == "tennis":
            ch, k, n = tennis_chance(i.get("confidence") or 0, rates)
            if ch is None:
                continue
            base.update(id=i.get("id"), date=i.get("date"), bet=BETS["tennis"], chance=ch, basis=f"{k} of {n} picks like it", price=None)
        else:
            continue
        picks.append(base)
    return picks, off


def build_groups(picks, now):
    """The day's nested groups from the picks still to start: the three most
    likely to land their Scale bet, then four, then five."""
    cand = sorted([p for p in picks if parse_utc(p["start"]) > now and p.get("chance")],
                  key=lambda p: (-p["chance"], p["start"], p["key"]))
    out = []
    for k, name in KINDS:
        legs = cand[:k]
        if len(legs) < k:
            break
        ch = 1.0
        for p in legs: ch *= p["chance"]
        price = None
        if all(p.get("price") for p in legs):
            price = 1.0
            for p in legs: price *= p["price"]
            price = round(price, 2)
        win = 1.0
        for p in legs: win *= (p.get("conf") or 0)
        out.append({"kind": k, "name": name, "legs": [p["key"] for p in legs], "chance": round(ch, 4),
                    "winners": round(win, 4), "price": price, "first": min(p["start"] for p in legs)})
    return out


def merge_day(old, picks, off, groups, now, stamp):
    """The day's archive after this build. A pick, and a left-off entry, is
    replaced until it starts and kept as it stood from then on. One that has
    started and is not on file is still added: every field of it comes from
    copies archived before its start (daylist.pinned, markets.live_rows), so
    a missed build loses nothing. A group is replaced until its first leg
    starts, and is never built from a leg that has started."""
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
    return {"date": old.get("date"), "rule": RULE, "picks": sorted(new_picks, key=lambda p: (p["start"], p["key"])),
            "off": sorted(new_off, key=lambda p: (p["start"], p["key"])),
            "groups": sorted(new_groups, key=lambda g: g["kind"])}


# -------------------------------------------------------------------- grading

def results(here=HERE):
    import markets as M
    fb = M.results(here)
    tn, tn2 = {}, {}
    for g in (_load(os.path.join(here, "tennis-record.json"), {}) or {}).get("graded") or []:
        if g.get("key"): tn[str(g["key"])] = g
        tn2[(g.get("date"), g.get("playerA"), g.get("playerB"))] = g
    return fb, tn, tn2


def settle(p, res):
    """(state, detail) for a pick: "scale" (the winner and the Scale bet),
    "won" (the winner only), "lost", "void" or None while there is no result."""
    import markets as M
    fb, tn, tn2 = res
    if p["sport"] == "football":
        g = M._result_for({"league": p.get("league"), "home": p["home"], "away": p["away"], "date": p.get("date") or p["start"][:10]}, fb)
        if not g: return None, None
        hg, ag = g["result"]
        won = hg > ag if p.get("side") == "h" else ag > hg
        return ("scale" if won and hg and ag else "won" if won else "lost"), f"{hg}-{ag}"
    g = tn.get(str(p.get("id"))) or tn2.get((p.get("date"), p["home"], p["away"]))
    if not g: return None, None
    if g.get("void"): return "void", g.get("note")
    if not g.get("ok"): return "lost", g.get("note")
    ss = straight_sets(g)
    return ("void" if ss is None else "scale" if ss else "won"), g.get("note")


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
    """Football Daily List picks graded before the Scale archive, in leagues
    BOOK now prices (`covered`): how often the winner and the Scale bet
    landed. Results only, no prices."""
    t = _tally()
    for g in (_load(os.path.join(here, "record-graded.json"), {}) or {}).get("graded") or []:
        if not g.get("list") or not g.get("result") or g["league"] not in covered or g["date"] >= since:
            continue
        hg, ag = g["result"]
        won = hg > ag if g.get("pick") == "h" else ag > hg
        _add(t, {"state": "scale" if won and hg and ag else "won" if won else "lost"})
    return _done(t)


def build(now=None, here=HERE):
    import markets as M
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    market_rows = {(r["league"], r["date"], r["home"], r["away"]): r for r in M.live_rows(here)}
    trec = _load(os.path.join(here, "tennis-record.json"), {}) or {}
    rates = tennis_rates(trec)
    adir = os.path.join(here, ARCHIVE)
    os.makedirs(adir, exist_ok=True)
    today = date.fromisoformat(uk_day(now))
    for k in range(-GLANCE_DAYS, DAYS_AHEAD):
        day = (today + timedelta(days=k)).isoformat()
        path = os.path.join(adir, f"{day}.json")
        if k < 0 and os.path.exists(path):
            continue                # a past day on file is never rebuilt
        try:
            picks, off = day_picks(day, now, here, market_rows, rates)
        except Exception as e:      # a bad archive never stops the days already on file
            print(f"scale: {day} not built ({type(e).__name__}: {e})", file=sys.stderr)
            continue
        if day < LIVE_FROM:         # before the tab: the picks only, no price archive to say what was left off
            off = []
        merged = merge_day(_load(path, {}) or {}, picks, off, build_groups(picks, now), now, stamp)
        merged["date"] = day
        if day < LIVE_FROM:
            merged["replay"] = True
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(merged, f, separators=(",", ":"), ensure_ascii=False)
        os.replace(path + ".tmp", path)

    res = results(here)
    files = sorted(fn for fn in os.listdir(adir) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", fn))
    by_sport, before, kinds, graded_groups, days_out, glance = {}, {}, {}, [], [], []
    for fn in files:
        d = _load(os.path.join(adir, fn), {}) or {}
        day = fn[:-5]
        by_key = {}
        for p in d.get("picks") or []:
            st, detail = settle(p, res)
            p["state"], p["detail"] = st, detail
            if st is None and (parse_utc(p["start"]) or now) <= now: p["state_live"] = "started"
            by_key[p["key"]] = p
            _add((before if d.get("replay") else by_sport).setdefault(p["sport"], _tally()), p)
        groups = []
        for g in d.get("groups") or []:
            gg = dict(g, **grade_group(g, by_key))
            groups.append(gg)
            t = kinds.setdefault(str(g["kind"]), {"n": 0, "won": 0, "void": 0, "priced": 0, "returned": 0.0})
            if gg["state"] in ("won", "lost"):
                t["n"] += 1; t["won"] += gg["state"] == "won"
                if "ret" in gg:
                    t["priced"] += 1; t["returned"] += gg["ret"]
                graded_groups.append({"date": day, "name": g["name"], "kind": g["kind"], "state": gg["state"], "price": g.get("price"),
                                      "ret": gg.get("ret"), "legs": [by_key[k]["pick"] for k in g["legs"] if k in by_key]})
            elif gg["state"] == "void":
                t["void"] += 1
        entry = {"date": day, "picks": d.get("picks") or [], "off": d.get("off") or [], "groups": groups}
        if day >= today.isoformat():
            days_out.append(entry)
        if day >= (today - timedelta(days=GLANCE_DAYS)).isoformat() and day <= today.isoformat():
            glance.append({"date": day, "off": len(entry["off"]), "replay": bool(d.get("replay")),
                           "dots": [{"k": p["key"], "sport": p["sport"], "pick": p["pick"], "start": p["start"],
                                     "state": p["state"] or ("started" if (parse_utc(p["start"]) or now) <= now else "up"),
                                     "detail": p.get("detail")} for p in entry["picks"]]})
    cov = coverage(market_rows, now)
    out = {"generated": stamp, "rule": RULE, "book": BOOK, "today": today.isoformat(), "from": LIVE_FROM,
           "days": days_out, "glance": glance,
           "record": {"bySport": {s: _done(t) for s, t in sorted(by_sport.items())},
                      "groups": {k: {"n": t["n"], "won": t["won"], "void": t["void"], "priced": t["priced"],
                                     **({"ret": round(t["returned"] / t["priced"] - 1, 4)} if t["priced"] else {})}
                                 for k, t in sorted(kinds.items())},
                      "recent": graded_groups[-30:][::-1]},
           "before": {s: _done(t) for s, t in sorted(before.items())},
           "replay": {"football": replay(here, {c["league"] for c in cov}, LIVE_FROM),
                      "tennis": {"bands": rates[0], "pool": rates[1]}},
           "leagues": cov}
    with open(os.path.join(here, "scale.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    with open(os.path.join(here, "scale.js"), "w", encoding="utf-8") as f:
        f.write("window.__SCALE__=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/") + ";")
    return out


def main():
    out = build()
    for d in out["days"]:
        fb = sum(1 for p in d["picks"] if p["sport"] == "football"); tn = sum(1 for p in d["picks"] if p["sport"] == "tennis")
        print(f"scale {d['date']}: {fb} football at {BOOK}, {tn} tennis, {len(d['off'])} football left off, "
              f"{len(d['groups'])} group(s)")
    r = out["record"]["bySport"]
    print("scale record: " + ("; ".join(f"{s} {t['scale']} of {t['n']} landed the Scale ({t['won']} won)" for s, t in r.items()) or "nothing graded yet"))
    print(f"scale: {len(out['leagues'])} leagues priced at {BOOK} for win and both score in the last 14 days")


if __name__ == "__main__":
    main()
