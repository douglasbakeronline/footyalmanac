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
        src = rep.get("source") or {}
        if src.get("pool"):
            # 9 Nov 2026: the legs come from the archived pool from poolFrom
            legs = ", ".join(f"{k} {v}" for k, v in sorted((src.get("poolLegs") or {}).items(), key=lambda x: -x[1])) or "none"
            out = ", ".join(f"{k} {v}" for k, v in sorted((src.get("poolLeftOut") or {}).items())) or "none"
            lines.append(f"Source: the archived pool from {src['poolFrom']} (settled priced legs: {legs}; left out: {out})"
                         f"{', closing prices' if src.get('closing') else ''}; football-data archive rows before that. "
                         "A leg archived before any bookmaker priced it counts only once its first real price is on file (`priced`, 9 Nov 2026).")
        lines.append("")
        cands = [(v, r) for v, r in rep["variants"].items() if v != "live" and r.get("pWorse") is not None and r["pWorse"] <= 0.30 and r["groups"] >= 30 and (r.get("vsLivePerDay") or 0) > 0]
        if cands:
            lines += ["**Candidates beating live on the archive (p(worse) <= 0.30, 30+ groups):** " + ", ".join(v for v, _ in cands) + ". A rule change still needs the football-data replay to agree on both seasons (tune.yml, Mondays) and a human to merge.", ""]
    if pt.get("timing"):
        t = pt["timing"]
        lines += [f"## Price timing ({pt['legs']} Card-rule legs)", f"- first price to last pre-start price: drifted {t['drifted']}, shortened {t['shortened']}, unchanged {t['unchanged']}; mean move {t['meanMovePct']:+.2f}% ({t['read']})"]
        for b, r in sorted(pt.get("books", {}).items(), key=lambda kv: -kv[1]["vsAvgPct"]):
            lines.append(f"- {b}: {r['vsAvgPct']:+.2f}% v the average price, best price {r['bestShare'] * 100:.0f}% of the time (n {r['n']})")
        for sp, r in (pt.get("bySport") or {}).items():
            # 9 Nov 2026 (#156): each sport apart; a book ranked on football says nothing about tennis or the NBA
            t = r["timing"]; best = max(r["books"].items(), key=lambda kv: kv[1]["vsAvgPct"]) if r.get("books") else None
            lines.append(f"- {sp}: {t['n']} legs, mean move {t['meanMovePct']:+.2f}% ({t['read']})" + (f"; best book {best[0]} {best[1]['vsAvgPct']:+.2f}% (n {best[1]['n']})" if best else "; no book priced 10+ legs"))
        # 9 Nov 2026 (#156): the move by how far ahead the first price was taken, for the push time
        if pt.get("leads"):
            lines.append("- by first price's lead on the start: " + "; ".join(f"{k} {v['meanMovePct']:+.2f}% (n {v['n']})" for k, v in pt["leads"].items()))
        ll = pt.get("lastLead") or {}
        if ll.get("n"):
            lines.append(f"- last price a median {ll['medianH']}h before the start, {ll['within3h']} of {ll['n']} within 3h")
        if pt.get("lastAfterStart"):
            by = ", ".join(f"{k} {v}" for k, v in (pt.get("lastAfterStartBySport") or {}).items())
            lines.append(f"- left out: {pt['lastAfterStart']} leg(s) whose last price came after the start on file" + (f" ({by})" if by else ""))
        lines.append("")
    for k in ("replay", "live"):
        s = st.get(k) or {}
        if s.get("flat1pct"):
            fl = s["flat1pct"]
            lines += [f"## Staking, {k} ({s['groups']} groups, landed/expected {s['landedOverExpected']})",
                      f"- flat 1% a group: median season {pct(fl['median'])}, 10th-90th {pct(fl['p10'])} to {pct(fl['p90'])}, worst drawdown (95%) {fl['p95Drawdown'] * 100:.0f}%",
                      f"- quarter Kelly: median {pct(s['quarterKelly']['median'])}, drawdown (95%) {s['quarterKelly']['p95Drawdown'] * 100:.0f}%; half Kelly: median {pct(s['halfKelly']['median'])}, drawdown (95%) {s['halfKelly']['p95Drawdown'] * 100:.0f}%",
                      ] + [f"- {lab} ({b['groups']} groups at {s.get('groupsPerDay')} a day, the page's stakes): 95%-worst drawdown {b['p95DrawdownUnits']} units, "
                           f"median {b['medianPnlUnits']:+} units on {b['staked']} staked; a bankroll of {b['units']} units keeps that drawdown to half"
                           for lab, b in ((k2, (s.get("bankroll") or {}).get(k2)) for k2 in ("month", "season")) if b] + [""]
    by = load("groupings-record.json").get("cardLegsBySport") or {}
    if by:
        # 9 Nov 2026: the Card's legs by sport from the record, with the sport-off
        # test (CLAUDE.md, the delegated decisions: tennis off the Card at 50
        # legs two standard errors under quote). The scoreboard read, never a fit.
        lines += ["## Legs by sport (the Card's full rule, the record)", "", "| sport | legs | landed | quoted | z | tripwire |", "|---|---|---|---|---|---|"]
        for sp, t in by.items():
            lines.append(f"| {sp} | {t['legs']} | {t['landed']} ({t['rate'] * 100:.0f}%) | {t['quoted'] * 100:.0f}% | {t['z'] if t['z'] is not None else 'n/a'} | {'**fired**' if t['tripwire'] else 'no'} |")
        fired = [sp for sp, t in by.items() if t["tripwire"]]
        lines += [("**Tripwire fired for " + ", ".join(fired) + ": the next build session adds it to `CARD_SPORTS_OFF` (CARD_RULE bump, note, release).**" if fired
                   else "A sport comes off the Card at 50+ legs two standard errors or more under quote (the Daily List's rule)."), ""]
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
