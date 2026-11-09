#!/usr/bin/env python3
"""Turn the nightly review's JSON into one GitHub issue (card-review) and,
when the integrity checker found something, an office-backlog issue for the
engineer. Run by card-review.yml; needs GH_TOKEN and REPO. Standard library
only (gh CLI for the API)."""
import json, os, subprocess, sys
from datetime import datetime, timezone

REPO = os.environ.get("REPO", "douglasbakeronline/footyalmanac")
today = datetime.now(timezone.utc).date().isoformat()


def load(p):
    try: return json.load(open(p))
    except Exception: return {}


def gh(*args):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def ensure_label(name, colour, desc):
    if gh(f"repos/{REPO}/labels/{name}") is None:
        gh("-X", "POST", f"repos/{REPO}/labels", "-f", f"name={name}", "-f", f"color={colour}", "-f", f"description={desc}")


def pct(x): return f"{x * 100:+.1f}%" if x is not None else "n/a"


def main():
    integ, rep, pt, st = load("integrity.json"), load("card-replay.json"), load("price-timing.json"), load("staking.json")
    lines = [f"# Card review {today}", ""]
    f = integ.get("findings", [])
    lines += [f"## Integrity: {len(f)} finding(s)"] + [f"- `{x['check']}` " + " ".join(f"{k}={v}" for k, v in x.items() if k != "check") for x in f[:20]] + [""]
    if rep.get("variants"):
        lines += [f"## The Card on the archive, {rep['from']} to {rep['to']} ({rep['days']} days)", "",
                  "| variant | groups | won | expected | return | empty days | v live / day | p(worse) |", "|---|---|---|---|---|---|---|---|"]
        for v, r in rep["variants"].items():
            lines.append(f"| {v} | {r['groups']} | {r['won']} | {r['expected']} | {pct((r['return'] or 1) - 1) if r['return'] else 'n/a'} | {r['emptyDays']} | {r.get('vsLivePerDay', '')} | {r.get('pWorse', '')} |")
        lines.append("")
        cands = [(v, r) for v, r in rep["variants"].items() if v != "live" and r.get("pWorse") is not None and r["pWorse"] <= 0.30 and r["groups"] >= 30 and (r.get("vsLivePerDay") or 0) > 0]
        if cands:
            lines += ["**Candidates beating live on the archive (p(worse) <= 0.30, 30+ groups):** " + ", ".join(v for v, _ in cands) + ". A rule change still needs the football-data replay to agree on both seasons (tune.yml, Mondays) and a human to merge.", ""]
    if pt.get("timing"):
        t = pt["timing"]
        lines += [f"## Price timing ({pt['legs']} Card-rule legs)", f"- first price to last pre-start price: drifted {t['drifted']}, shortened {t['shortened']}, unchanged {t['unchanged']}; mean move {t['meanMovePct']:+.2f}% ({t['read']})"]
        for b, r in sorted(pt.get("books", {}).items(), key=lambda kv: -kv[1]["vsAvgPct"]):
            lines.append(f"- {b}: {r['vsAvgPct']:+.2f}% v the average price, best price {r['bestShare'] * 100:.0f}% of the time (n {r['n']})")
        lines.append("")
    for k in ("replay", "live"):
        s = st.get(k) or {}
        if s.get("flat1pct"):
            fl = s["flat1pct"]
            lines += [f"## Staking, {k} ({s['groups']} groups, landed/expected {s['landedOverExpected']})",
                      f"- flat 1% a group: median season {pct(fl['median'])}, 10th-90th {pct(fl['p10'])} to {pct(fl['p90'])}, worst drawdown (95%) {fl['p95Drawdown'] * 100:.0f}%",
                      f"- quarter Kelly: median {pct(s['quarterKelly']['median'])}, drawdown (95%) {s['quarterKelly']['p95Drawdown'] * 100:.0f}%; half Kelly: median {pct(s['halfKelly']['median'])}, drawdown (95%) {s['halfKelly']['p95Drawdown'] * 100:.0f}%",
                      f"- a bankroll of about {s['unitsForSeason']} group-stakes keeps a 95%-worst season's drawdown to half", ""]
    lines += ["Artifacts: integrity.json, card-replay.json, price-timing.json, staking.json on this run. Advisory: nothing here changes a rule."]
    body = "\n".join(lines)
    ensure_label("card-review", "c8102e", "The nightly Card review")
    ensure_label("office-backlog", "0e8a16", "A task for the office sprint")
    gh("-X", "POST", f"repos/{REPO}/issues", "-f", f"title=Card review {today}", "-f", f"body={body}", "-f", "labels[]=card-review")
    if f:
        fb = "\n".join(f"- `{x['check']}` " + " ".join(f"{k}={v}" for k, v in x.items() if k != "check") for x in f[:30])
        gh("-X", "POST", f"repos/{REPO}/issues", "-f", f"title=Card integrity: {len(f)} finding(s) on {today}",
           "-f", f"body=The nightly checker (tools/card_integrity.py) found:\n\n{fb}\n\nFix the cause in the pipeline (grading, pricing or archiving), not the record by hand; add a test that would have caught it. Deliverable: a change that passes the gates.",
           "-f", "labels[]=office-backlog", "-f", "labels[]=agent:engineer")
    print(body)


if __name__ == "__main__":
    main()
