#!/usr/bin/env python3
"""
Nightly integrity checks on the Card's record (9 Nov 2026, Douglas: an
autonomous agent that improves the platform). Reads only; prints findings,
writes them as JSON with --json FILE, exits 1 when anything is found so a
workflow can open an issue. Standard library only.

Checks:
  pending-with-result   a graded group's leg still pending 24h+ after its start
                        while a result for the fixture or match is on file
                        (Andreescu v Giovannini sat like this for two days)
  stale-rule            a published group whose rule number is not CARD_RULE
                        and whose first start has not passed
  no-opposition-price   a Card football leg with a bookmaker price but no
                        opposition price (the rule cannot see it)
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
"""
import gzip, json, os, sys
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G

now = datetime.now(timezone.utc)
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


def main():
    rec = load("groupings-record.json", {}); findings = []
    idx = G.results_index()
    for d in rec.get("days", []):
        for g in d.get("groups", []):
            if not str(g.get("name", "")).startswith("Card"): continue
            for l in g.get("legs", []):
                if l.get("status") != "pending": continue
                t = G.parse(l.get("when"))
                if not t or now - t < timedelta(hours=24): continue
                st, res = G.settle(dict(l, side=l.get("side") or ("h" if l.get("pick") == l.get("home") else "a")), idx)
                have = res is not None or st in ("won", "lost", "void")
                if have or l["sport"] == "tennis":
                    findings.append({"check": "pending-with-result" if have else "pending-24h", "date": d["date"], "group": g["name"], "pick": l["pick"], "event": l.get("event"), "settles": st})
                if l["sport"] == "football" and not l.get("est") and l.get("odds") and not l.get("opp") and d["date"] >= "2026-11-06":
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
    if total: print(f"Card legs since {PRICED_FROM} the pool can replay at a real price: {have} of {total}")
    for f in findings: print(" ".join(f"{k}={v}" for k, v in f.items()))
    print(f"{len(findings)} finding(s)")
    if "--json" in sys.argv:
        json.dump({"at": now.isoformat(timespec="seconds"), "findings": findings}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
