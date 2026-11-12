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


def already_posted(title):
    """10 Nov 2026: the 03:40 UTC schedule did not fire on 10 Nov (GitHub drops
    scheduled runs under load) and the review was dispatched by hand at 08:40.
    A second, later schedule makes a missed night post itself, so a run whose
    day already has its review posts nothing: one issue a night, as before.
    Looks at the last few card-review issues by title, open or closed."""
    got = gh(f"repos/{REPO}/issues?labels=card-review&state=all&per_page=10")
    return isinstance(got, list) and any((i or {}).get("title") == title for i in got)


def pct(x): return f"{x * 100:+.1f}%" if x is not None else "n/a"


GATE_LEGS, GATE_P = 100, 0.30   # CLAUDE.md, the delegated decisions (9 Nov 2026)


def candidates(rep):
    """Variants that beat live on the archive at the decision gate: p(worse)
    at most 0.30 on 100+ legs, ahead per day. 10 Nov 2026: the gate is legs,
    as CLAUDE.md states it; before this the line read 30+ groups."""
    return [(v, r) for v, r in (rep.get("variants") or {}).items()
            if v != "live" and r.get("pWorse") is not None and r["pWorse"] <= GATE_P
            and gate_legs(r) >= GATE_LEGS and (r.get("vsLivePerDay") or 0) > 0]


def gate_legs(r):
    """The legs a variant is gated on. An empty-day filler (10 Nov 2026, #155)
    differs from live only on the days live leaves empty, so its own legs,
    not live's plus its own, are what the gate counts."""
    return ((r.get("fill") or {}).get("legs") or 0) if "fill" in r else (r.get("legs") or 0)


def fill_lines(rep):
    """10 Nov 2026 (#155): each empty-day filler on its own days. fillwide is
    the page's fallback today; a filler is worth its place only if its own
    groups pay."""
    rows = [(v, r["fill"], r) for v, r in (rep.get("variants") or {}).items() if "fill" in r]
    if not rows: return []
    out = ["Empty-day fillers on the days live left empty (fillwide is the page's fallback today; gated on the filler's own legs):"]
    for v, f, r in rows:
        if not f.get("groups"):
            out.append(f"- {v}: no groups on the empty days"); continue
        out.append(f"- {v}: {f['days']} days, {f['groups']} groups, {f['won']} won (expected {f['expected']}), {f['legs']} legs, "
                   f"return {pct((f['return'] or 1) - 1) if f.get('return') else 'n/a'}, v live {r.get('vsLivePerDay', '')} a day, p(worse) {r.get('pWorse', '')}")
    return out + [""]


def funnel_section(today_=None, days=14):
    """10 Nov 2026 (#155): which Card condition keeps groups off the page,
    over the last two weeks of the pool (tools/card_funnel.py). Read here,
    not in the workflow, so the section needs no workflow change. Legs
    archived before 10 Nov are read at their last price (`--recover`)."""
    try:
        from datetime import date, timedelta
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import card_funnel as CF
        t = date.fromisoformat(today_ or today)
        since = max("2026-11-06", (t - timedelta(days=days)).isoformat())   # every day read under the live rule (rule 8 from 11 Nov 2026)
        by, unpriced = CF.pool_days(since, None, recover=True)   # to the last pool file: days not yet played read too
        fn = CF.funnel(by, unpriced)
    except Exception as e:   # advisory: never stop the review over it
        return [f"## Card funnel", f"Not read: {type(e).__name__}: {e}", ""]
    try:
        # 12 Nov 2026: the legs a missing price alone kept off. From 10 Nov
        # only, when every leg began carrying its first real price; before
        # that an estimate in the archive is the archive's gap, not the feed's.
        gaps = CF.gap_lines(CF.price_gaps(max(since, "2026-11-10"), None, today_ or today))
    except Exception as e:
        gaps = [f"Price gaps not read: {type(e).__name__}: {e}", ""]
    return ([f"## Card funnel from {since} (the pool to its last file, each leg's first condition failed)", ""]
            + CF.report_lines(fn)
            + ["A volume read: a condition that costs groups is not a reason to drop it unless the replay says the extra groups pay "
               "(card_replay.py variants, the 30 Nov review). Legs archived before 10 Nov are read at their last price.", ""]
            + ["### Legs kept off by a missing price (from 10 Nov)", ""] + gaps)


def edge_section(since="2026-11-11"):
    """10 Nov 2026: the green Edge flag tested on every sport
    (tools/edge_sports.py). The short-favourite candidate was registered on
    the pool to 10 Nov, so it is judged only on legs from `since`, out of
    sample. Read here, not in the workflow, so no workflow change."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import card_replay as CR, edge_sports as ES
        by, _ = CR.pool_legs(since=since)
        rep = ES.report(ES.favourites(by))
    except Exception as e:   # advisory: never stop the review over it
        return ["## Edge flag, every sport", f"Not read: {type(e).__name__}: {e}", ""]
    out = [f"## Edge flag, every sport (pool from {since}, first real prices, out of sample)", "",
           "| sport | candidate legs | landed v bookies | best-price return | short 1.15-1.30 legs | landed v bookies | best-price return |",
           "|---|---|---|---|---|---|---|"]
    fmt = lambda x: (f"{x['n']} | {x['landed'] * 100:.0f}% v {x['quoted'] * 100:.0f}% | {x['returnBest'] * 100:+.1f}%{' **passes**' if ES.passes(x) else ''}"
                     if x.get("n") else "0 | | ")
    for sp, r in rep.items():
        out.append(f"| {'all sports' if sp == '_all' else sp} | {fmt(r['candidate'])} | {fmt(r['short'])} |")
    rec = (load("record.json").get("edge") or {})
    for k, lab in (("all", "every flagged football fixture graded (live and replayed on archived prices)"), ("live", "flagged as published, from 10 Nov")):
        e = rec.get(k) or {}
        if e.get("n"):
            out.append(f"- Football flag, {lab}: {e['won']} of {e['n']} landed v {e['quoted'] * 100:.0f}% quoted, "
                       f"{e['return'] * 100:+.1f}% at the average price, {e['returnBest'] * 100:+.1f}% at the best")
    return out + ["A sport earns the green flag only when a candidate passes: 100+ legs, landed above the bookmakers, "
                  "best-price return positive, p(loss) <= 0.30 (tools/edge_sports.py, claude/edge-sports-2026-11-10.md).", ""]


def list_book_section(r):
    """10 Nov 2026: the Daily List at the book Douglas places with
    (groupings.list_at_book): settled picks it priced, landed and the return
    at its price, and how many it did not offer. A tally, never a fit."""
    if not r: return []
    a, off, none = r.get("atBook") or {}, r.get("notAtBook") or {}, r.get("unchecked") or {}
    out = [f"## The Daily List at {r['book']} (since {r['from']})", "",
           "| | picks | landed | quoted | return at its price |", "|---|---|---|---|---|"]
    def row(lab, t):
        if not t.get("n"): return f"| {lab} | 0 | | | |"
        return (f"| {lab} | {t['n']} | {t['won']} ({t['rate'] * 100:.0f}%) | {t['quoted'] * 100:.0f}% | "
                f"{pct(t['ret']) if t.get('ret') is not None else ''} |")
    out += [row(f"priced at {r['book']}", a), row("UK books, not this one", off), row("no UK price read", none)]
    for sp, t in (r.get("bySport") or {}).items():
        tot = sum((t.get(k) or {}).get("n", 0) for k in ("atBook", "notAtBook", "unchecked"))
        if tot: out.append(f"| {sp} | {tot} settled | {(t.get('atBook') or {}).get('n', 0)} at {r['book']} | | |")
    return out + [""]


CONTEXT_REVIEW_AT = 30   # "against" picks settled before the veto is judged (claude/context-check-2026-11-11.md)


def context_section(r):
    """11 Nov 2026 (CARD_CONTEXT, CARD_RULE 9): the context check graded
    forward, by verdict, from the record (groupings.context_record). The
    pre-registered review: at 30 settled "against" picks, if they land at or
    above the model's own number the veto is not earning its place and the
    next build session sets CARD_CONTEXT = False (reads still show). A tally
    of the scoreboard, never a fit (Rule 1)."""
    if not r: return []
    out = ["## The context check (since 11 Nov)", "",
           "| verdict | picks settled | landed | model | bookmakers | z v model |", "|---|---|---|---|---|---|"]
    for v in ("clear", "caution", "against"):
        t = r.get(v)
        if not t: continue
        fair = f"{t['fair'] * 100:.0f}%" if t.get("fair") is not None else "n/a"
        out.append(f"| {v} | {t['legs']} | {t['landed']} ({t['rate'] * 100:.0f}%) | {t['model'] * 100:.0f}% | "
                   f"{fair} | "
                   f"{t['zModel'] if t.get('zModel') is not None else 'n/a'} |")
    a = r.get("against") or {}
    n = a.get("legs", 0)
    if n >= CONTEXT_REVIEW_AT and a["rate"] >= a["model"]:
        out.append(f"**Context tripwire fired: {n} \"against\" picks landed {a['rate'] * 100:.0f}%, at or above the model's "
                   f"{a['model'] * 100:.0f}%. The next build session sets `CARD_CONTEXT = False` (CARD_RULE bump, note, release).**")
    elif n >= CONTEXT_REVIEW_AT:
        out.append(f"Reviewed at {n} \"against\" picks: they land under the model's number ({a['rate'] * 100:.0f}% v "
                   f"{a['model'] * 100:.0f}%), so the veto stays.")
    else:
        out.append(f"The veto is judged at {CONTEXT_REVIEW_AT} settled \"against\" picks ({n} so far): if they land at or above "
                   "the model's number, `CARD_CONTEXT = False`.")
    return out + [""]


def coverage_lines(rep, record):
    """10 Nov 2026: the live row of the replay beside the live Card the record
    holds over the same days. Until 10 Nov most live legs were archived only as
    estimates, so the replay rebuilt none of the live Card (0 groups against 21
    from 29 Oct to 9 Nov) and its "live" row read as if the Card had made
    nothing. Full-rule groups only: the wider-rule filler and late groups apart."""
    live = (rep.get("variants") or {}).get("live")
    if not live or not rep.get("from") or not rep.get("to"): return []
    held = sum(1 for d in record.get("days") or [] if rep["from"] <= d.get("date", "") <= rep["to"]
               for g in d.get("groups") or [] if str(g.get("name", "")).startswith("Card") and not g.get("wide") and not g.get("late"))
    if not held: return []
    if live["groups"] >= held:
        return [f"Coverage: the replay's live row rebuilt {live['groups']} groups; the record holds {held} live Card groups over these days."]
    return [f"Coverage: the record holds **{held}** live Card groups over these days; the replay rebuilt {live['groups']}. "
            "The gap is legs archived only as estimates (every leg from 10 Nov carries its first real price), so the replay "
            "reads the rules against each other on the legs it has, not the live Card's own return."]


def kelly_line(s):
    """Kelly stakes nothing when the sample lands at or under the bookmakers'
    chance (tools/staking.py `sim`): say so rather than print a 0% return and
    a 0% drawdown, which read as a safe strategy (10 Nov 2026)."""
    if (s.get("landedOverExpected") or 0) <= 1:
        return (f"- Kelly (quarter and half): stakes nothing, the groups landed {s.get('landedOverExpected')} times the bookmakers' "
                "expectation, so no group shows an edge to size")
    q, h = s["quarterKelly"], s["halfKelly"]
    return (f"- quarter Kelly: median {pct(q['median'])}, drawdown (95%) {q['p95Drawdown'] * 100:.0f}%; "
            f"half Kelly: median {pct(h['median'])}, drawdown (95%) {h['p95Drawdown'] * 100:.0f}%")


def rule6_lines(rep):
    """11 Nov 2026: the variants pre-registered on the rule 6 Card are built on
    it (card_replay.RULE6_FAMILY) and also paired against `rule6`, their own
    base: whether the change helps the old rule, apart from rule 6 v live."""
    fam = [(v, r) for v, r in sorted(rep.get("variants", {}).items()) if r.get("base") == "rule6" and "vsRule6PerDay" in r]
    if not fam: return []
    return ["Rule 6 family (each one change to the rule 6 Card, as pre-registered before 11 Nov; v live above, v rule6 here): "
            + "; ".join(f"{v} {r['vsRule6PerDay']:+.2f} a day" + (f", p(worse) {r['pWorseVsRule6']}" if r.get("pWorseVsRule6") is not None else ", identical")
                        for v, r in fam) + "."]


def fd_side(hist, v):
    """One variant's football-data read, season by season (12 Nov 2026): the
    rule 7 variants are paired by day against live in each replayed season
    (`card_legs_history.py` `cardM7Paired`, committed by tune.yml on Mondays).
    Returns [(season, paired)] in file order, or [] when none is on file."""
    out = []
    for k, r in ((hist or {}).get("seasons") or {}).items():
        x = (r.get("cardM7Paired") or {}).get(v) if isinstance(r, dict) else None
        if x: out.append((r.get("season") or k, x, k))
    return out


def fd_beats(x):
    """A football-data season the variant beats live on, at the gate's p(worse)."""
    return (not x.get("identical")) and (x.get("perDay") or 0) > 0 and x.get("pWorse") is not None and x["pWorse"] <= GATE_P


def fd_gate_lines(rep, hist):
    """12 Nov 2026: both sides of the gate in one place. CLAUDE.md's rule
    needs a variant to beat live on the pool (p(worse) <= 0.30 on 100+ legs)
    and on both football-data seasons (fit and check). Until now the review
    showed only the pool, so a pool lead the seasons had already refused
    (m7under5 on 12 Nov: pool p(worse) 0.014, football-data behind in all
    five seasons, pooled 0.99) read as a variant to watch. Rule 7 variants
    only: the rule 6 family is not paired on football-data."""
    vs = rep.get("variants") or {}
    rows = [(v, r, fd_side(hist, v)) for v, r in vs.items() if v != "live" and r.get("vsLivePerDay") is not None]
    rows = [x for x in rows if x[2]]
    if not rows:
        return ["Football-data side: no paired season read on file yet (`cardM7Paired` in card-legs-history.json, tune.yml on Mondays).", ""]
    seasons = [s for s, _, _ in rows[0][2]]
    out = ["### Both sides of the gate (the rule 7 variants)", "",
           "| variant | pool v live / day | pool p(worse) | pool legs | " + " | ".join(f"{s} v live / day, p(worse)" for s in seasons) + " | gate |",
           "|---|---|---|---|" + "---|" * len(seasons) + "---|"]
    passed = []
    for v, r, fd in rows:
        by = {k: x for _, x, k in fd}
        cells = []
        for _, x, _ in fd:
            cells.append("identical" if x.get("identical") else f"{x.get('perDay', 0):+.2f}, {x.get('pWorse')}")
        pool_ok = (r.get("pWorse") is not None and r["pWorse"] <= GATE_P and gate_legs(r) >= GATE_LEGS and (r.get("vsLivePerDay") or 0) > 0)
        fd_ok = all(fd_beats(by.get(k) or {}) for k in ("fit", "check")) and "fit" in by and "check" in by
        if all(x.get("identical") for _, x, _ in fd):
            verdict = "no football-data read (identical to live there)"
        elif pool_ok and fd_ok:
            verdict = "**passes**"; passed.append(v)
        else:
            why = []
            if (r.get("vsLivePerDay") or 0) <= 0: why.append("behind on the pool")
            elif r.get("pWorse") is None or r["pWorse"] > GATE_P: why.append(f"pool p(worse) {r.get('pWorse')}")
            elif gate_legs(r) < GATE_LEGS: why.append(f"pool {gate_legs(r)} legs of {GATE_LEGS}")
            if not fd_ok:
                bad = [s for s, x, k in fd if k in ("fit", "check") and not fd_beats(x)]
                why.append("football-data " + (", ".join(bad) if bad else "fit and check not both on file"))
            verdict = "fails: " + ", ".join(why)
        out.append(f"| {v} | {r['vsLivePerDay']:+.2f} | {r.get('pWorse') if r.get('pWorse') is not None else 'identical'} | {gate_legs(r)} | " + " | ".join(cells) + f" | {verdict} |")
    refused = [v for v, r, fd in rows if (r.get("vsLivePerDay") or 0) > 0 and any((not x.get("identical")) and (x.get("perDay") or 0) < 0 for _, x, _ in fd)]
    if refused:
        out.append("Ahead on the pool but behind live on football-data in at least one season, so not a candidate however the pool reads: " + ", ".join(refused) + ".")
    if passed:
        out.append("**Full gate passed: " + ", ".join(passed) + ". The next build session changes the rule (CARD_RULE bump with these numbers, note, release).**")
    return out + [""]


def main():
    integ, rep, pt, st = load("integrity.json"), load("card-replay.json"), load("price-timing.json"), load("staking.json")
    lines = [f"# Card review {today}", ""]
    f = integ.get("findings", [])
    lines += [f"## Integrity: {len(f)} finding(s)"] + [f"- `{x['check']}` " + " ".join(f"{k}={v}" for k, v in x.items() if k != "check") for x in f[:20]] + [""]
    if rep.get("variants"):
        lines += [f"## The Card on the archive, {rep['from']} to {rep['to']} ({rep['days']} days)", "",
                  "| variant | groups | won | expected | legs | return | empty days | v live / day | p(worse) |", "|---|---|---|---|---|---|---|---|---|"]
        for v, r in rep["variants"].items():
            lines.append(f"| {v} | {r['groups']} | {r['won']} | {r['expected']} | {r.get('legs', '')} | {pct((r['return'] or 1) - 1) if r['return'] else 'n/a'} | {r['emptyDays']} | {r.get('vsLivePerDay', '')} | {r.get('pWorse', '')} |")
        src = rep.get("source") or {}
        if src.get("pool"):
            # 9 Nov 2026: the legs come from the archived pool from poolFrom
            legs = ", ".join(f"{k} {v}" for k, v in sorted((src.get("poolLegs") or {}).items(), key=lambda x: -x[1])) or "none"
            out = ", ".join(f"{k} {v}" for k, v in sorted((src.get("poolLeftOut") or {}).items())) or "none"
            lines.append(f"Source: the archived pool from {src['poolFrom']} (settled priced legs: {legs}; left out: {out})"
                         f"{', closing prices' if src.get('closing') else ''}; football-data archive rows before that. "
                         "A leg archived before any bookmaker priced it counts only once its first real price is on file (`priced`, 9 Nov 2026).")
        lines += coverage_lines(rep, load("groupings-record.json"))
        lines += rule6_lines(rep)
        lines.append("")
        lines += fill_lines(rep)
        cands = candidates(rep)
        if cands:
            lines += ["**Candidates beating live on the archive (p(worse) <= 0.30 on 100+ legs):** " + ", ".join(v for v, _ in cands) + ". A rule change still needs the football-data replay to agree on both seasons (tune.yml, Mondays), then CARD_RULE bumped with the numbers.", ""]
        # 12 Nov 2026: a variant that built nothing is "ahead" only because live
        # lost on those days (short, notennis, tennis80 read +0.44 a day on 0
        # legs); it is named apart, not listed as one to watch
        near = [v for v, r in rep["variants"].items() if v != "live" and r.get("pWorse") is not None and r["pWorse"] <= 0.30
                and (r.get("vsLivePerDay") or 0) > 0 and (v, r) not in cands and gate_legs(r) > 0]
        empty = [v for v, r in rep["variants"].items() if v != "live" and (r.get("vsLivePerDay") or 0) > 0 and not gate_legs(r)]
        if near:
            lines += ["Ahead of live but under the 100-leg gate (watch, do not act): " + ", ".join(f"{v} ({gate_legs(rep['variants'][v])} legs)" for v in near) + ".", ""]
        if empty:
            lines += ["Built nothing on these days, so ahead of live only by live's losses (not a read): " + ", ".join(empty) + ".", ""]
        lines += fd_gate_lines(rep, load("card-legs-history.json"))
    if pt.get("timing"):
        t = pt["timing"]
        lines += [f"## Price timing ({pt['legs']} Card-rule legs)", f"- first price to last pre-start price: drifted {t['drifted']}, shortened {t['shortened']}, unchanged {t['unchanged']}; mean move {t['meanMovePct']:+.2f}% ({t['read']})"]
        if t.get("pNoDrift") is not None: lines[-1] += f", day-resampled p(no drift) {t['pNoDrift']:.3f}"
        se = pt.get("settled") or {}
        if se.get("n"):
            # 10 Nov 2026 (#156): the move only pays on legs that won, so the return itself, first v last price, paired
            lines.append(f"- singles on {se['n']} settled legs ({se['won']} won): {se['returnFirstPct']:+.2f}% at the first price, {se['returnLastPct']:+.2f}% at the last pre-start price, "
                         f"late {se['lateGainPct']:+.2f} points" + (f", p(late no better) {se['pLateNoBetter']:.3f}" if se.get("pLateNoBetter") is not None else "") + f" ({se['read']})")
        if pt.get("notStarted"): lines.append(f"- not started yet, left out until their last price is in: {pt['notStarted']} leg(s)")
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
                      kelly_line(s),
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
    lines += context_section(load("groupings-record.json").get("cardContext"))
    lines += list_book_section(load("groupings-record.json").get("listAtBook"))
    lines += funnel_section()
    lines += edge_section()
    lines += ["Artifacts: integrity.json, card-replay.json, price-timing.json, staking.json on this run. Advisory: nothing here changes a rule."]
    body = "\n".join(lines)
    if already_posted(f"Card review {today}") and os.environ.get("FORCE_POST") != "1":
        print(f"Card review {today} is already posted; nothing posted this run (FORCE_POST=1 posts anyway).")
        print(body)
        return
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
