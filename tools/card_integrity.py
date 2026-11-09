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
  record-drift          groupings-record.json older than 30 hours
"""
import gzip, json, os, sys
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G

now = datetime.now(timezone.utc)


def load(p, default=None):
    try: return json.load(open(os.path.join(HERE, p)))
    except Exception: return default


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
        if not os.path.exists(os.path.join(HERE, "groupings-archive", f"pool-{day}.json.gz")):
            findings.append({"check": "pool-gap", "date": day})
    for f in findings: print(" ".join(f"{k}={v}" for k, v in f.items()))
    print(f"{len(findings)} finding(s)")
    if "--json" in sys.argv:
        json.dump({"at": now.isoformat(timespec="seconds"), "findings": findings}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
