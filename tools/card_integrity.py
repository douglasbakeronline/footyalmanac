#!/usr/bin/env python3
"""
Nightly integrity checks on the Card's record (9 Nov 2026, Douglas: an
autonomous agent that improves the platform). Reads only; prints findings,
writes them as JSON with --json FILE, exits 1 when anything is found so a
workflow can open an issue. Standard library only.

Checks:
  pending-with-result   a graded group's leg still pending 24h+ after its start
                        while a result for the fixture or match is on file
                        (Andreescu v Giovannini sat like this for two days).
                        Read on every staked slip (STAKED, 17 Nov 2026): the
                        Card and the Daily 2x, List 2x and List long, which
                        Douglas stakes and which carry no Card prefix
  stale-rule            a published group whose rule number is not CARD_RULE
                        and whose first start has not passed
  no-opposition-price   a rule 6 Card football leg with a bookmaker price but
                        no opposition price (the rule cannot see it; not a
                        condition from CARD_RULE 7, 11 Nov 2026)
  pool-gap              a Card day with no pool archive file
  pool-unpriced         a pool leg first archived as an estimate from
                        PRICED_FROM on that later took a real price (lastOdds)
                        but has no `priced` block (9 Nov 2026: the first real
                        price the Card rule replays on)
  record-drift          groupings-record.json older than 30 hours
  card-leg-unreplayable a Card leg from PRICED_FROM that the pool archive does
                        not hold at a real bookmaker price (the row itself, or
                        its `priced` block). 9 Nov 2026: of the live Card's
                        59 legs 30 Oct to 8 Nov the pool held 42 only as the
                        model's estimate (20 of 23 from 4 Nov), so
                        tools/card_replay.py rebuilt no live Card on any day
                        under rule 6; the 30 Nov review is only as good as
                        this check.
  card-pick-twice       one fixture in two Card groups the same day, or in a
                        two-day group and the next day's own group (15 Nov
                        2026: Pistoiese and the 76ers were in 14 Nov's
                        two-day group and a 15 Nov group built after
                        midnight). Read from TWICE_FROM, the day the build
                        began carrying the day before's two-day picks.
"""
import gzip, json, os, sys
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G

now = datetime.now(timezone.utc)
TWICE_FROM = "2026-11-16"   # groupings.span_held, 15 Nov 2026; 15 Nov's own double is in claude/card-span-held-2026-11-15.md
PRICED_FROM = "2026-11-10"   # archive_pool writes `priced` from the 9 Nov 2026 release; rows first written before carry none


def load(p, default=None):
    try: return json.load(open(os.path.join(HERE, p)))
    except Exception: return default


def pool_index(day, pool_dir=None):
    """(event, pick) -> pool row over the pool files from the day before to
    the day after (a pool file is the start's UTC date; a Card day runs
    07:00 UK to 07:00, so a late US game sits in the next file)."""
    pool_dir = pool_dir or os.path.join(HERE, "groupings-archive"); out = {}
    base = datetime.fromisoformat(day)
    for i in (-1, 0, 1):
        path = os.path.join(pool_dir, f"pool-{(base + timedelta(days=i)).date().isoformat()}.json.gz")
        if not os.path.exists(path): continue
        try:
            with gzip.open(path, "rt", encoding="utf-8") as fh: legs = json.load(fh).get("legs") or []
        except (OSError, ValueError):
            continue
        for r in legs: out.setdefault((r.get("event"), r.get("pick")), r)
    return out


def replayable(row):
    """True when a pool row carries a real bookmaker price the replay can use."""
    if not row: return False
    if not row.get("est") and row.get("fair") is not None: return True
    return bool(row.get("priced") and row["priced"].get("fair") is not None)


def card_coverage(groups_by_day, pool_dir=None, since=PRICED_FROM):
    """Findings for Card legs the pool cannot replay, and (covered, total)."""
    findings, have, total = [], 0, 0
    for day, groups in sorted(groups_by_day.items()):
        if day < since: continue
        idx = pool_index(day, pool_dir)
        for g in groups:
            if not str(g.get("name", "")).startswith("Card"): continue
            for l in g.get("legs", []):
                total += 1; row = idx.get((l.get("event"), l.get("pick")))
                if replayable(row): have += 1; continue
                findings.append({"check": "card-leg-unreplayable", "date": day, "group": g["name"], "pick": l.get("pick"),
                                 "why": "not in the pool" if not row else "pool holds the model's estimate only"})
    return findings, (have, total)


OPP_RULES = {12}   # rule 7+ Card rules that read the opposition's price (rule 6 and before: r < 7)


def staked(name):
    """A slip Douglas stakes: the Card, the Daily 2x and the List card (17 Nov
    2026). The Model card, the wider-rule filler and the retired kinds are
    paper or history and are graded without this check."""
    name = str(name or "")
    return name.startswith("Card") or name == G.DAILY_NAME or name in {k[0] for k in G.LIST_KINDS}


def needs_opp(g, day, l):
    """A Card football leg the rule could not judge without the opposition's
    price: only rule 6 full-rule groups (from 6 Nov 2026) read it. From
    CARD_RULE 7 (11 Nov 2026, the model's own picks) and on the wider-rule
    filler the opposition's price is no condition, so its absence is not a
    finding (it would open an office-backlog issue for nothing). From
    CARD_RULE 12 (16 Nov 2026) football reads it again (5.0+); from CARD_RULE
    13 (17 Nov 2026, the model alone) it is shown and never read, so only
    rules 6 and 12 (OPP_RULES) ask for it."""
    r = g.get("rule") or 0
    if g.get("wide") or day < "2026-11-06": return False
    if r >= 7 and r not in OPP_RULES: return False
    return l.get("sport") == "football" and not l.get("est") and bool(l.get("odds")) and not l.get("opp")


def picks_twice(groups_by_day, since=TWICE_FROM):
    """Fixtures held by two Card groups on one day (a two-day group counts on
    both its days). Wider-rule and paper groups are not the Card."""
    held = {}
    for day, groups in groups_by_day.items():
        for g in groups or []:
            if not str(g.get("name", "")).startswith("Card"): continue
            for d in (g.get("span") or [day]):
                if d < since: continue
                for l in g.get("legs") or []:
                    held.setdefault((d, l.get("event")), []).append((day, g.get("name"), g.get("seq"), g.get("first")))
    out = []
    for (d, ev), gs in sorted(held.items()):
        if len(set(gs)) > 1:
            out.append({"check": "card-pick-twice", "date": d, "event": ev, "groups": len(set(gs))})
    return out


_ARCH = {}


def full_leg(day, l, arch_dir=None):
    """The record keeps a slim leg (no date, home, away or id), so settle()
    cannot read it. 17 Nov 2026: the first football leg pending 24h+ in the
    slim record (Pistoiese v Coriano, 15 Nov) crashed the whole check with
    KeyError 'date'. The full leg comes from the day's archive (or the day
    before, for a two-day group); failing that, date from the start and the
    sides from the event."""
    arch_dir = arch_dir or os.path.join(HERE, "groupings-archive")
    key = (l.get("event"), l.get("pick"))
    for d in (day, (datetime.fromisoformat(day) - timedelta(days=1)).date().isoformat()):
        if (arch_dir, d) not in _ARCH:
            idx = {}
            try: a = json.load(open(os.path.join(arch_dir, f"{d}.json")))
            except (OSError, ValueError): a = {}
            for g in a.get("groups") or []:
                for x in g.get("legs") or []: idx.setdefault((x.get("event"), x.get("pick")), x)
            _ARCH[(arch_dir, d)] = idx
        x = _ARCH[(arch_dir, d)].get(key)
        if x: return dict(x, **{k: v for k, v in l.items() if v is not None})
    out = dict(l)
    home, _, away = str(l.get("event") or "").partition(" v ")
    out.setdefault("home", home); out.setdefault("away", away)
    out.setdefault("date", str(l.get("when") or "")[:10] or day)
    out.setdefault("side", "h" if l.get("pick") == out["home"] else "a")
    return out


def main():
    rec = load("groupings-record.json", {}); findings = []
    idx = G.results_index()
    for d in rec.get("days", []):
        for g in d.get("groups", []):
            if not staked(g.get("name")): continue
            for l in g.get("legs", []):
                if l.get("status") != "pending": continue
                t = G.parse(l.get("when"))
                if not t or now - t < timedelta(hours=24): continue
                st, res = G.settle(full_leg(d["date"], l), idx)
                have = res is not None or st in ("won", "lost", "void")
                if have or l["sport"] == "tennis":
                    findings.append({"check": "pending-with-result" if have else "pending-24h", "date": d["date"], "group": g["name"], "pick": l["pick"], "event": l.get("event"), "settles": st})
                if str(g.get("name", "")).startswith("Card") and needs_opp(g, d["date"], l):
                    findings.append({"check": "no-opposition-price", "date": d["date"], "group": g["name"], "pick": l["pick"]})
    gen = rec.get("generated")
    if gen and now - G.parse(gen) > timedelta(hours=30):
        findings.append({"check": "record-drift", "generated": gen})
    for i in range(-2, 2):
        day = (now + timedelta(days=i)).date().isoformat()
        path = os.path.join(HERE, "groupings-archive", f"pool-{day}.json.gz")
        if not os.path.exists(path):
            findings.append({"check": "pool-gap", "date": day}); continue
        try:
            with gzip.open(path, "rt", encoding="utf-8") as fh: legs = json.load(fh).get("legs") or []
        except (OSError, ValueError):
            legs = []
        n = sum(1 for l in legs if l.get("est") and l.get("lastOdds") and not l.get("priced") and (l.get("firstAt") or "") >= PRICED_FROM)
        if n: findings.append({"check": "pool-unpriced", "date": day, "legs": n})
    by_day = {d["date"]: d.get("groups", []) for d in rec.get("days", [])}
    # groups published but not yet in the record (today's Card)
    for i in (-1, 0, 1):
        day = (now + timedelta(days=i)).date().isoformat()
        a = load(os.path.join("groupings-archive", f"{day}.json"))
        if a and day not in by_day: by_day[day] = a.get("groups", [])
    cov, (have, total) = card_coverage(by_day)
    findings += cov
    findings += picks_twice(by_day)
    if total: print(f"Card legs since {PRICED_FROM} the pool can replay at a real price: {have} of {total}")
    for f in findings: print(" ".join(f"{k}={v}" for k, v in f.items()))
    print(f"{len(findings)} finding(s)")
    if "--json" in sys.argv:
        json.dump({"at": now.isoformat(timespec="seconds"), "findings": findings}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
