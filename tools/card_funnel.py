#!/usr/bin/env python3
"""
Which of the Card's conditions keeps groups off the page. Advisory: fits
nothing, changes nothing, needs no results. 10 Nov 2026 (issue #155).

    python3 tools/card_funnel.py [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--json FILE]

Since rule 6 (the opposition priced 9+, 6 Nov 2026) the full rule has built
no Card 3x, and 9 Nov had no full-rule group at all (the wider-rule fill
stood in). tools/card_replay.py asks whether a variant would have *won*
more; this asks the earlier question, how many groups each condition costs,
and it can read days whose games have not been played yet.

For every Card day in the pool archive (groupings-archive/pool-<date>.json.gz,
legs at their first real bookmaker price, as card_replay reads them):
  1. every priced leg's first failing condition (card_fault, the live
     function, so the funnel and the live Card cannot drift apart), by sport;
  2. the legs that clear every condition, by sport;
  3. whether a Card 2x and a Card 3x can be built (best_card, live), and the
     same with one condition relaxed at a time ("relief"): the under-market
     band, the opposition's price, the tennis floor, the price range, the
     bookmakers' 60% floor and the core-league limit.
A condition whose relief adds many group-days is the one starving the Card.
That is a volume read only: whether the extra groups would pay is the
replay's question (card_replay.py variants, gated at the 30 Nov review).
Nothing here changes a rule. Standard library only.

11 Nov 2026: the Card became the model's own picks (CARD_RULE 7, model_fault)
and builds the 2x alone (CARD_RULE 8). The funnel reads whichever rule is live:
under rule 7 its own fault keys and reliefs (MODEL_PATTERNS, MODEL_RELIEF;
the under-market band and the opposition's price are not conditions any
more), and only the kinds the Card builds (built_kinds), counting every
group a day can take (up to three 2x), not just the first. Before this the
rule 6 patterns read rule 7's messages: 337 football legs outside the core
leagues were counted as "price-range" and 129 legs as "other".
"""
import gzip, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as R

# Each relief relaxes exactly one condition, with the live machinery. Keys
# are the fault keys of fault_key() so the two tables read together.
RELIEF = {
    "under-market": {"CARD_UNDER_MARKET": 0, "CARD_UNDER_MAX": 0},
    "opposition": {"CARD_OPP_MIN": {}},
    "sport-floor": {"CARD_SPORT_MIN": {}},
    "price-range": {"CARD_ODDS": G.CARD_WIDE_ODDS},
    "fair-floor": {"CARD_FAIR_MIN": G.CARD_WIDE_FAIR_MIN},
    "league": {"CARD_CORE_ONLY": False},
    # not a leg condition: a group's spread (groupings.COMP_MAX), so it shows
    # in the days table only (10 Nov 2026)
    "comp-cap": {"COMP_MAX": 3},
}

# 11 Nov 2026 (CARD_RULE 7): model_fault's conditions, one relief each.
# The league limit is hard-coded in model_fault (core leagues only), so it
# has a key but no relief.
MODEL_RELIEF = {
    "price-range": {"CARD_ODDS": G.CARD_WIDE_ODDS},
    "sport-floor": {"CARD_SPORT_MIN": {}},
    "model-floor": {"CARD_FAIR_MIN": 0.55},
    "no-value": {"CARD_MODEL_EDGE": -0.05},      # the model up to 5 points under the bookmakers
    "comp-cap": {"COMP_MAX": 3},
}

# card_fault's messages, in its own order, to a short key. A message no
# pattern matches is "other" (tests/test_card_funnel.py covers every branch).
PATTERNS = [
    ("sport-off", ("off the Daily List", "off the Card")),
    ("league", ("outside the leagues",)),
    ("under-market", ("is not at least", "more than")),
    ("opposition", ("opposition",)),
    ("sport-floor", ("needs the model and its tested rate",)),
    ("no-time", ("order of play",)),
    ("no-price", ("no bookmaker price",)),
    ("price-range", ("outside",)),
    ("fair-floor", ("the bookmakers give",)),
    ("model-floor", ("the model gives",)),
    ("model-above", ("points above the bookmakers",)),
]
KEYS = ["sport-off", "league", "under-market", "opposition", "sport-floor", "no-time", "price-range",
        "fair-floor", "model-floor", "model-above", "other"]

# model_fault's messages (CARD_RULE 7), in its own order.
MODEL_PATTERNS = [
    ("sport-off", ("off the Daily List", "off the Card")),
    ("no-time", ("order of play",)),
    ("no-price", ("no bookmaker price",)),
    ("league", ("outside the core leagues",)),
    ("list-excluded", ("the Daily List excludes",)),
    ("price-range", ("is outside",)),
    ("sport-floor", (" pick needs ",)),
    ("model-floor", (") is under ",)),
    ("no-value", ("sees no value",)),
]
MODEL_KEYS = ["sport-off", "no-time", "league", "list-excluded", "price-range", "sport-floor", "model-floor",
              "no-value", "other"]


def model_rule():
    return bool(getattr(G, "CARD_MODEL_RULE", False))


def rule_sets():
    """(patterns, reliefs, table keys) for the Card rule that is live."""
    if model_rule(): return MODEL_PATTERNS, MODEL_RELIEF, MODEL_KEYS
    return PATTERNS, RELIEF, KEYS


def leg_relief():
    return [k for k in rule_sets()[1] if k != "comp-cap"]


def kinds():
    """The Card kinds the live rule builds (CARD_BUILD; both before rule 8)."""
    f = getattr(G, "built_kinds", None)
    return [k[0] for k in (f() if f else G.CARD_KINDS)]


def fault_key(msg):
    if msg is None: return None
    for key, subs in rule_sets()[0]:
        if any(s in msg for s in subs): return key
    return "other"


def pool_days(since=None, until=None, pool_dir=R.POOL_DIR, recover=False):
    """Card day -> legs at their first real price, settled or not, one per
    (event, pick). A leg with no real price is counted, not kept."""
    by, seen, unpriced = defaultdict(list), set(), Counter()
    for fn in sorted(os.listdir(pool_dir)) if os.path.isdir(pool_dir) else []:
        if not fn.startswith("pool-") or not fn.endswith(".json.gz"): continue
        d = fn[5:15]
        if d < R.POOL_FROM or (since and d < since) or (until and d > until): continue
        with gzip.open(os.path.join(pool_dir, fn), "rt", encoding="utf-8") as f: a = json.load(f)
        for row in a.get("legs") or []:
            key = (row.get("event"), row.get("pick"))
            if key in seen: continue
            seen.add(key)
            mk = R.pool_market(row, recover=recover)
            slot = G.uk_slot(row)
            if not slot or (since and slot[0] < since) or (until and slot[0] > until): continue
            if mk is None:
                unpriced[(slot[0], row.get("sport"))] += 1; continue
            l = dict(row, **mk, est=False)
            l.setdefault("pTested", l.get("p")); l.setdefault("hit", l.get("pTested"))
            l["implied"] = round(1 / l["odds"], 4)
            l["p"] = round(min(l["pTested"], l["fair"]), 4)
            by[slot[0]].append(l)
    return by, unpriced


def kinds_built(legs, date, patch=None):
    """{kind: groups}: how many groups of each kind the Card builds can be
    made from the day's legs (no fixture shared), in build_card's order (seq
    by seq, up to CARD_MAX_GROUPS a day), under a patch."""
    patch = patch or {}
    saved = {k: getattr(G, k) for k in patch}
    for k, v in patch.items(): setattr(G, k, v)
    try:
        after, used, names = G.lock_time(date, "Day"), set(), kinds()
        out = {n: 0 for n in names}
        seqs = max(1, -(-G.CARD_MAX_GROUPS // len(G.CARD_KINDS)))
        for _ in range(seqs):
            for name in names:
                if sum(out.values()) >= G.CARD_MAX_GROUPS: break
                g = G.best_card(legs, used, after, name)
                if not g: continue
                out[name] += 1
                used |= {l["event"] for l in g["legs"]}
        return out
    finally:
        for k, v in saved.items(): setattr(G, k, v)


def clears_with(l, patch):
    """True when the leg passes card_fault with one condition relaxed."""
    saved = {k: getattr(G, k) for k in patch}
    for k, v in patch.items(): setattr(G, k, v)
    try: return G.card_fault(l) is None
    finally:
        for k, v in saved.items(): setattr(G, k, v)


def funnel(by, unpriced=None):
    unpriced = unpriced or Counter()
    days, faults, clear, sole = [], defaultdict(Counter), Counter(), defaultdict(Counter)
    _, relief_set, keys = rule_sets()
    names, legr = kinds(), leg_relief()
    relief = {k: {n: 0 for n in names} for k in ["live"] + list(relief_set)}
    groups = {k: 0 for k in relief}
    for d in sorted(by):
        legs = by[d]
        row = {"date": d, "priced": len(legs), "unpriced": sum(v for (dd, _), v in unpriced.items() if dd == d),
               "clear": Counter(), "built": {}}
        for l in legs:
            k = fault_key(G.card_fault(l))
            if k is None:
                clear[l["sport"]] += 1; row["clear"][l["sport"]] += 1
            else:
                faults[l["sport"]][k] += 1
                # the legs this one condition alone keeps off (every other passes)
                for name in legr:
                    if clears_with(l, relief_set[name]): sole[l["sport"]][name] += 1
        for name, patch in [("live", None)] + list(relief_set.items()):
            b = kinds_built(legs, d, patch)
            row["built"][name] = b
            for kind, n in b.items():
                relief[name][kind] += n > 0; groups[name] += n
        row["clear"] = dict(row["clear"])
        days.append(row)
    return {"days": days, "faults": {s: dict(c) for s, c in faults.items()}, "clear": dict(clear),
            "sole": {s: dict(c) for s, c in sole.items()}, "relief": relief, "groups": groups,
            "rule": getattr(G, "CARD_RULE", None), "model": model_rule(), "keys": keys, "legRelief": legr, "kinds": names}


def report_lines(f):
    """Markdown lines for the nightly Card review."""
    n = len(f["days"])
    if not n: return ["No pool days to read."]
    out = []
    keys = f.get("keys") or KEYS
    legr = f.get("legRelief") or [k for k in RELIEF if k != "comp-cap"]
    names = f.get("kinds") or ["Card 2x", "Card 3x"]
    if f.get("rule") is not None:
        out += [f"Read under CARD_RULE {f['rule']}" + (" (the model's own picks, model_fault)" if f.get("model") else "")
                + ", building " + ", ".join(names) + ".", ""]
    sports = sorted(f["faults"].keys() | f["clear"].keys())
    out.append("| sport | clear | " + " | ".join(keys) + " |")
    out.append("|---|---|" + "---|" * len(keys))
    for s in sports:
        c = f["faults"].get(s, {})
        out.append(f"| {s} | {f['clear'].get(s, 0)} | " + " | ".join(str(c.get(k, 0)) for k in keys) + " |")
    out.append("")
    out.append("Legs kept off by one condition alone (every other condition passed):")
    out.append("")
    out.append("| sport | " + " | ".join(legr) + " |")
    out.append("|---|" + "---|" * len(legr))
    for s in sorted(f["sole"]):
        out.append(f"| {s} | " + " | ".join(str(f["sole"][s].get(k, 0)) for k in legr) + " |")
    out.append("")
    out.append(f"Days with a group, of {n}, and groups in all (one condition relaxed at a time):")
    out.append("")
    out.append("| rule | " + " | ".join(names) + " | groups |")
    out.append("|---|" + "---|" * len(names) + "---|")
    for name, b in f["relief"].items():
        lab = ("live" if name == "live" else "three legs a competition" if name == "comp-cap"
               else "no value demand (model up to 5 under)" if name == "no-value" else f"no {name} condition")
        out.append(f"| {lab} | " + " | ".join(str(b.get(k, 0)) for k in names) + f" | {(f.get('groups') or {}).get(name, '')} |")
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    arg = lambda k: argv[argv.index(k) + 1] if k in argv else None
    since, until = arg("--since") or "2026-11-06", arg("--until")
    by, unpriced = pool_days(since, until, recover="--recover" in argv)
    f = funnel(by, unpriced)
    print(f"Card funnel, pool {since} to {until or 'the last pool file'}: {len(f['days'])} days, "
          f"{sum(d['priced'] for d in f['days'])} legs at a real price, {sum(unpriced.values())} estimate only (left out)")
    for d in f["days"]:
        b = d["built"]["live"]
        print(f"  {d['date']}: {d['priced']:>3} priced, clear {d['clear'] or '-'}; live "
              + ", ".join(f"{k} {v}" for k, v in b.items()))
    print("\n".join(report_lines(f)))
    if arg("--json"):
        with open(arg("--json"), "w") as fh: json.dump(dict(f, since=since, until=until), fh, indent=1)
    return f


if __name__ == "__main__":
    main()
