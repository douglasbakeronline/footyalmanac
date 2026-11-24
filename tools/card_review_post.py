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
    return posted_issue(title) is not None


def posted_issue(title):
    """The day's card-review issue (number, body), or None."""
    got = gh(f"repos/{REPO}/issues?labels=card-review&state=all&per_page=10")
    if not isinstance(got, list): return None
    return next((i for i in got if (i or {}).get("title") == title), None)


def close_older(title):
    """23 Nov 2026: one review was opened a night and none was ever closed, so
    fifteen card-review issues sat open at once and the newest was one of
    many. Once tonight's review is posted, every older open card-review issue
    is closed with a line pointing to it; they stay readable, and
    posted_issue still finds them (it reads state=all). Returns the numbers
    closed."""
    got = gh(f"repos/{REPO}/issues?labels=card-review&state=open&per_page=50")
    if not isinstance(got, list): return []
    done = []
    for i in got:
        i = i or {}
        if i.get("pull_request") or not i.get("number") or i.get("title") == title: continue
        if not str(i.get("title") or "").startswith("Card review "): continue
        gh("-X", "PATCH", f"repos/{REPO}/issues/{i['number']}", "-f", "state=closed", "-f", "state_reason=completed")
        done.append(i["number"])
    return done


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
        g0 = max(since, "2026-11-10")
        gaps = CF.gap_lines(CF.price_gaps(g0, None, today_ or today), empty=empty_card_days(g0, today_ or today))
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


def star_section():
    """23 Nov 2026 (Douglas: "keep track"): the likely winner star's record,
    the live rule beside the football-and-tennis-at-85% variant he chose not
    to ship (tools/star_record.py, claude/likely-winner-star-2026-11-23.md).
    Advisory: a tally for Douglas, no tripwire acts on it."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import star_record as SR
        body = SR.lines(SR.report("."))
    except Exception as e:   # advisory: never stop the review over it
        return ["## Likely winner star", f"Not read: {type(e).__name__}: {e}", ""]
    return ["## Likely winner star (live rule v football and tennis at 85%+)", ""] + body + [
        "Read beside each other at 14 days live; the variant is put to Douglas only if it is ahead on both spans.", ""]


def market_pass_lines(name, mk, x, rec, goals=None):
    """23 Nov 2026: one line under a passing market rule saying where the
    pass comes from (each selection, the days, William Hill) and how many
    rules the gate reads, so a pass by luck is read as one; for over / under
    2.5, the same value rule on the football-data seasons (goals-value.json,
    tools/goals_value.py). Advisory; the verdict is the gate's."""
    pc = lambda v: f"{v * 100:+.1f}%" if v is not None else "n/a"
    bits = []
    sel = x.get("bySel") or {}
    if sel:
        lab = {"h": "home", "a": "away", "d": "draw"}
        bits.append(", ".join(f"{lab.get(k, k)} {t['n']} picks {pc(t.get('retBest'))}" for k, t in sel.items()) + " at the best price")
    if x.get("days"):
        bits.append(f"{x['days']} days, {round((x.get('top3') or 0) * 100)}% of the picks on the busiest three")
    h = x.get("hill")
    if h is not None:
        bits.append(f"{BOOK_NAME} priced none of them" if not h.get("n")
                    else f"{BOOK_NAME} priced {h['n']} of {x.get('n')}, {pc(h.get('ret'))} at its price")
    out = [f"- {name}: " + "; ".join(bits) + "." if bits else None]
    seasons = ((goals or {}).get("seasons") or {}) if mk == "o25" else {}
    fd = []
    for s in seasons.values():
        if not s or s.get("roi") is None: continue
        side = ", ".join(f"{k} {pc(t.get('roi'))} ({t.get('bets')} bets)" for k, t in (s.get("bySide") or {}).items())
        fd.append(f"{s.get('season')} {pc(s['roi'])} on {s.get('bets')} bets" + (f", {side}" if side else ""))
    if fd:
        out.append("  The same value rule on football-data prices (goals-value.json): " + "; ".join(fd)
                   + ". CLAUDE.md: no goals-market bets without a goals calibration that passes the gates.")
    return [l for l in out if l]


BOOK_NAME = "William Hill"


def markets_section(rec, goals=None):
    """14 Nov 2026: the football markets beyond the match winner
    (markets.py, markets-record.json): landed against the model, the return
    at the best UK price on live priced picks, and each market's gate. A
    pass is said in bold; nothing here changes the page."""
    if not rec or not rec.get("markets"):
        return []
    lv, rp = rec.get("live") or {}, rec.get("replay") or {}
    g = rec.get("gate") or {}
    out = [f"## Football markets ({lv.get('fixtures', 0)} fixtures priced and graded"
           + (f" from {lv['from']}" if lv.get("from") else "") + f"; {rp.get('fixtures', 0)} replayed without prices)", "",
           "| market | landed v model (all) | priced picks | landed v bookies | average price | best price | William Hill | value rule | every pick |",
           "|---|---|---|---|---|---|---|---|---|"]
    pc = lambda x: f"{x * 100:+.1f}%" if x is not None else ""
    passed, why = [], []
    for mk, m in rec["markets"].items():
        a, l, gt = m.get("all") or {}, m.get("live") or {}, m.get("gate") or {}
        if not a.get("n"): continue
        def verdict(x):
            if not x or not x.get("n"): return "no picks yet"
            if x["verdict"] == "wait": return f"{x['n']} of {x['need']}" + (f", {pc(x.get('retBest'))}" if x.get("retBest") is not None else "")
            return f"{'**passes**' if x['verdict'] == 'pass' else 'fails'}: {x['n']} picks, {pc(x.get('retBest'))}, p(loss) {x.get('pLoss')}"
        for rule in ("value", "all"):
            if (gt.get(rule) or {}).get("verdict") == "pass":
                if rule == "value": passed.append(m["name"])
                why += market_pass_lines(m["name"] + ("" if rule == "value" else ", every pick"), mk, gt[rule], rec, goals)
        out.append(f"| {m['name']} | {a['rate'] * 100:.1f}% v {a['quoted'] * 100:.1f}% (n {a['n']}, z {a.get('z', 0):+.1f}) | {l.get('priced', 0)} | "
                   + (f"{l['fairRate'] * 100:.0f}% v {l['fair'] * 100:.0f}%" if l.get("fairN") else "") + f" | {pc(l.get('ret'))} | {pc(l.get('retBest'))} | "
                   + (f"{pc(l.get('retHill'))} (n {l['atHill']})" if l.get("atHill") else "") + f" | {verdict(gt.get('value'))} | {verdict(gt.get('all'))} |")
    if passed:
        out.append("**Passed the value gate: " + ", ".join(passed) + ". Ready to be offered on the Bets tab (a release, Douglas's call).**")
    if why:
        n = rec.get("tests") or 2 * len(rec["markets"])
        p = g.get("pLoss", 0.1)
        out += ["Where each pass comes from (the gate's verdict stands as pre-registered):"] + why + [
            f"{n} rules are read against the gate at p(loss) {p}, so about {round(n * p)} would pass by chance alone; "
            "a pass carried by one selection, a few days or a book Douglas does not use is a reason to wait."]
    return out + [f"Value rule: the model {int((g.get('edge') or 0.05) * 100)}+ points above the bookmakers' fair chance. A rule passes at "
                  f"{g.get('n', 150)}+ settled priced picks that landed above the bookmakers, a positive return at the best UK price and "
                  f"p(loss) {g.get('pLoss', 0.1)} or less (markets.py, claude/football-markets-2026-11-14.md).", ""]


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


def rule13_split_section(r):
    """17 Nov 2026 (CARD_RULE 13): the rule 13 Card's groups and picks split
    by what rule 12 would have said (groupings.card_rule13_split), so the 30
    Nov review reads what the switch added without a replay. A tally of the
    record, never a fit."""
    if not r: return []
    a, b = r.get("rule12") or {}, r.get("rule13only") or {}
    if not (a.get("groups") or b.get("groups") or r.get("unknown")): return []
    def row(lab, t, lg):
        ret = pct(t["returned"] / t["staked"] - 1) if t.get("staked") else ""
        legs = (f"{lg['landed']} of {lg['legs']} v {lg['expected']} expected" if lg.get("legs") else "none settled")
        return (f"| {lab} | {t.get('groups', 0)} | {t.get('settled', 0)} | {t.get('won', 0)} v {t.get('expected', 0)} | "
                f"{ret} | {legs} |")
    lg = r.get("legs") or {}
    out = ["## Rule 13's groups, split by what rule 12 would have said", "",
           "| groups | built | settled | won v expected | return (1 unit) | picks landed |", "|---|---|---|---|---|---|",
           row("rule 12 would have built it too", a, lg.get("rule12") or {}),
           row("holds a pick only rule 13 admits", b, lg.get("rule13only") or {})]
    if r.get("derived"): out.append(f"\n{r['derived']} group(s) read from their legs as frozen at the start: the re-check had dropped "
                                    "`rule12Fault` until 18 Nov (claude/card-rule12-fault-recheck-2026-11-18.md).")
    if r.get("unknown"): out.append(f"\n{r['unknown']} rule 13 group(s) built before `rule12Fault` was kept, left out.")
    return out + ["Read beside the `rule12` replay at the 30 Nov review (claude/card-rule13-split-2026-11-17.md).", ""]


CONTEXT_REVIEW_AT = 30   # "against" picks settled before the veto is judged (claude/context-check-2026-11-11.md)


def context_pause_line(ledger, now=None):
    """14 Nov 2026: the context check pauses itself when the API key reaches
    its usage limit (context_review.PAUSE_KEY in the ledger). Said in bold,
    because no Card pick is read while it lasts and nothing vetoes."""
    from datetime import datetime as _dt, timezone as _tz
    t = (ledger or {}).get("pausedUntil")
    if not t: return []
    try: until = _dt.fromisoformat(str(t).replace("Z", "+00:00"))
    except ValueError: return []
    if until <= (now or _dt.now(_tz.utc)): return []
    return [f"**The context check is paused until {t}: the API key reached its usage limit. No pick is read and nothing "
            "is vetoed until then; raising the limit in the Anthropic console resumes it on the next build.**", ""]


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


# 18 Nov 2026: every pre-registered Card decision in one table, so the 30 Nov
# review and each build session see what is waiting, what is due and what has
# fired without reading ten notes. Each trigger is copied from the note named
# in the row; nothing here decides anything, and the counts are the record's
# (a tally of the scoreboard, never a fit, Rule 1) or the pool replay's.
REVIEW_DAY = "2026-11-30"


def _settled(t): return (t or {}).get("settled", 0) or 0


def _ret(t):
    t = t or {}
    us, ur = t.get("unitsStaked") or t.get("staked") or 0, t.get("unitsReturned") if t.get("unitsStaked") else t.get("returned")
    return f"{pct(ur / us - 1)} at the page's stakes" if us else "no return yet"


def _tally(t):
    t = t or {}
    if not _settled(t): return "none settled"
    z = t.get("z")
    return f"{t.get('won', 0)} of {_settled(t)} won v {t.get('expected', 0):.2f} expected (z {z if z is not None else 'n/a'}), {_ret(t)}"


def _pool(rep, v):
    r = ((rep or {}).get("variants") or {}).get(v)
    if not r: return f"`{v}` not in tonight's replay"
    if r.get("pWorse") is None: return f"`{v}` identical to live on the pool"
    return f"`{v}` v live {r.get('vsLivePerDay', 0):+.2f} a day, p(worse) {r['pWorse']}, {r.get('legs', 0)} legs"


def card_tennis_since(rec, rule=10):
    """Settled tennis legs on full-rule Card groups from CARD_RULE `rule` (the
    tennis75 review counts legs under the 85% floor's rule)."""
    n = 0
    for d in (rec or {}).get("days") or []:
        for g in d.get("groups") or []:
            if not str(g.get("name", "")).startswith("Card") or g.get("wide") or g.get("late") or (g.get("rule") or 0) < rule:
                continue
            n += sum(1 for l in g.get("legs") or [] if l.get("sport") == "tennis" and l.get("status") in ("won", "lost"))
    return n


def decisions_section(rec, rep, hist=None, today_=None, floor_z=-2.0, floor_n=50, rep_close=None):
    """The pre-registered decisions table: decision, trigger, where it stands,
    status (waiting / **due** / **fired**) and who acts."""
    today_ = today_ or today
    rec, rep = rec or {}, rep or {}
    days_left = (datetime.fromisoformat(REVIEW_DAY).date() - datetime.fromisoformat(today_).date()).days
    vs = rep.get("variants") or {}
    rows = []

    def row(name, trigger, now, status, who): rows.append(f"| {name} | {trigger} | {now} | {status} | {who} |")

    # 1. A sport off the Card (claude/card-tripwire-at-floor-2026-11-14.md)
    for sp, t in (rec.get("cardLegsBySport") or {}).items():
        a = t.get("atFloor") if t.get("atFloor") is not None else t
        z = a.get("z")
        if not (t.get("tripwire") or sp == "tennis"): continue
        row(f"{sp.capitalize()} off the Card", f"{floor_n}+ legs{' at the floor' if t.get('atFloor') is not None else ''}, z {floor_z:g} or under",
            f"{a.get('legs', 0)} legs, z {z if z is not None else 'n/a'}", "**fired**" if t.get("tripwire") else "waiting",
            "the next session, without asking")
    # 2. The floor line (CARD_FLOOR_Z, the page's verdict on the Card record)
    k = rec.get("card") or {}
    z = k.get("z")
    fired = z is not None and _settled(k) >= floor_n and z <= floor_z
    row("The Card's floor line", f"{floor_n}+ settled groups, z {floor_z:g} or under", _tally(k),
        "**fired**" if fired else "waiting", "the page says so; the rule is Douglas's")
    # 22 Nov 2026: the table read rule 13's decisions for three days after
    # rule 14 (19 Nov) set rule 8's constants live: "Rule 13 v rule 12" asked
    # about a rule no longer staked, and the tennis 75% and core-league rows
    # waited on changes rule 14 had already made (their variants equal live).
    # From the record's live rule (`cardLiveRule`) 14 on, the row is rule 14 v
    # the rules it replaced, read on 30 Nov with no change before
    # (claude/card-rule14-rule8-2026-11-19.md); the settled rows become a line.
    live_rule = rec.get("cardLiveRule") or 0
    settled_by14 = []
    if live_rule >= 14:
        t14 = rec.get("cardLive") if rec.get("cardLive") is not None else (rec.get("cardByRule") or {}).get(str(live_rule))
        r13 = vs.get("rule13") or {}
        lead = ""
        if r13.get("pWorse") is not None:
            ahead = (r13.get("vsLivePerDay") or 0) > 0 and r13["pWorse"] <= 0.30
            lead = (f"; **rule 13 ahead on the pool** ({r13.get('legs', 0)} legs; on football-data, dropping the value demand was behind in all five seasons)"
                    if ahead else "; rule 14 not behind on the pool")
        # 24 Nov 2026: the same pairs at each leg's last pre-start price. Rule
        # 14's value demand is read on the price, and the first price is often
        # three days out: Hammarby (23 Nov) passed at 1.22 and failed at 1.16,
        # so the replay at first prices built a group the page refused, while
        # rule 13 (no value demand) barely moves. Read both before the 30 Nov
        # call (claude/card-replay-price-fidelity-2026-11-24.md).
        close = ""
        if (rep_close or {}).get("variants"):
            close = (f"; at the last pre-start price: {_pool(rep_close, 'rule13')}; {_pool(rep_close, 'rule12')}")
        row(f"Rule {live_rule} (rule 8's constants) v rule 13 and rule 12",
            f"{REVIEW_DAY}, read beside `rule13` and `rule12` on the same days; no Card rule change before then",
            f"{_tally(t14)}; {_pool(rep, 'rule13')}; {_pool(rep, 'rule12')}{lead}{close}",
            "**due**" if days_left <= 0 else "waiting", "Douglas (the switch was his)")
        settled_by14 = ["Settled by rule 14 (19 Nov): tennis back at 75% and core leagues only, so `tennis75` and `m7core` "
                        "equal live and their rows are retired (claude/card-rule14-rule8-2026-11-19.md)."]
    else:
        # 3. Rule 13 v rule 12 (claude/card-rule13-model-only-2026-11-17.md)
        t13 = (rec.get("cardByRule") or {}).get("13")
        due = days_left <= 0 or _settled(t13) >= 50
        r12 = vs.get("rule12") or {}
        lead = ""
        if r12.get("pWorse") is not None:
            lead = "; rule 12 ahead on the pool" if (r12.get("vsLivePerDay") or 0) > 0 and r12["pWorse"] <= 0.30 else "; rule 13 not behind on the pool"
        row("Rule 13 (the model alone) v rule 12", f"{REVIEW_DAY} or 50 settled rule 13 groups; rule 12 ahead at p(worse) 0.30 or under",
            f"{_tally(t13)}; {_pool(rep, 'rule12')}{lead}", "**due**" if due else "waiting", "Douglas (the switch was his)")
        # 4. Tennis floor back to 75% (claude/tennis-floor-85-2026-11-11.md)
        n_t = card_tennis_since(rec)
        t75 = vs.get("tennis75") or {}
        beat = t75.get("pWorse") is not None and (t75.get("vsLivePerDay") or 0) > 0 and t75["pWorse"] <= 0.30
        row("Tennis floor back to 75%", "30 tennis Card legs under rule 10+, `tennis75` ahead at p(worse) 0.30 or under",
            f"{n_t} tennis legs; {_pool(rep, 'tennis75')}", "**due**" if n_t >= 30 and beat else "waiting", "the next session")
        # 5. Core leagues only again (claude/card-wider-leagues-2026-11-11.md)
        mc = vs.get("m7core") or {}
        beat = mc.get("pWorse") is not None and (mc.get("vsLivePerDay") or 0) > 0 and mc["pWorse"] <= 0.30
        row("Core leagues only again", f"{REVIEW_DAY}, `m7core` ahead at p(worse) 0.30 or under", _pool(rep, "m7core"),
            "**due**" if days_left <= 0 and beat else ("waiting (ahead)" if beat else "waiting"), "the 30 Nov review")
    # 6. The opposition floor again (claude/card-m7opp-2026-11-15.md, overtaken by rule 13)
    for v in ("m7opp5", "m7opp9"):
        r = vs.get(v) or {}
        legs = (r.get("legs") or 0)
        pool = r.get("pWorse") is not None and (r.get("vsLivePerDay") or 0) > 0 and r["pWorse"] <= 0.30 and legs >= 100
        fd = fd_side(hist, v)
        fd_ok = len(fd) >= 2 and all(fd_beats(x) for _, x, _ in fd)
        fd_txt = (f"; football-data ahead in {sum(1 for _, x, _ in fd if fd_beats(x))} of {len(fd)} season(s)" if fd
                  else "; no football-data read on file")
        row(f"Opposition floor `{v}`", "beats live on both football-data seasons and the pool, 100+ legs", _pool(rep, v) + fd_txt,
            "**due**" if pool and fd_ok else "waiting",
            "Douglas (no Card rule change before the 30 Nov read)" if live_rule >= 14 else "Douglas (rule 13 dropped it at his call)")
    # 7. The context veto (claude/context-check-2026-11-11.md)
    a = (rec.get("cardContext") or {}).get("against") or {}
    n = a.get("legs", 0)
    fired = n >= CONTEXT_REVIEW_AT and a.get("rate", 0) >= a.get("model", 1)
    row("Context veto off", f"{CONTEXT_REVIEW_AT} settled \"against\" picks landing at or above the model",
        f"{n} settled" + (f", {a['rate'] * 100:.0f}% v {a['model'] * 100:.0f}%" if n else ""),
        "**fired**" if fired else ("reviewed, stays" if n >= CONTEXT_REVIEW_AT else "waiting"), "the next session, without asking")
    # 8. The Daily 2x (claude/daily-2x-2026-11-17.md)
    d = rec.get("cardDaily") or {}
    dz = d.get("z")
    row("The Daily 2x's rule", "50 settled slips, z -2 or under", _tally(d),
        "**fired**" if _settled(d) >= 50 and dz is not None and dz <= -2 else ("**due**" if _settled(d) >= 50 else "waiting"), "the next session")
    # 9. The List 2x and List long (claude/list-card-2026-11-17.md)
    for key, name, rule in (("cardList", "The List 2x as a method", "30 settled, positive, p(loss) under 0.30"),
                            ("cardListLong", "The List long dropped", "30 settled, under the stake")):
        t = rec.get(key) or {}
        row(name, rule, _tally(t), "**due**" if _settled(t) >= 30 else "waiting", "the next session reads it; a stake line is Douglas's")
    head = [f"## Pre-registered decisions ({REVIEW_DAY} review in {days_left} day(s))" if days_left > 0
            else f"## Pre-registered decisions (the {REVIEW_DAY} review is due)", "",
            "| decision | trigger | now | status | who acts |", "|---|---|---|---|---|"]
    live = [r for r in rows if "**fired**" in r or "**due**" in r]
    tail = [f"**{len(live)} decision(s) due or fired: the next build session acts on each as its row says.**" if live
            else "Nothing due or fired; every trigger is copied from the note behind it."]
    return head + rows + [""] + tail + settled_by14 + [""]


CHAIN_FROM = "2026-11-17"   # first full UK day of the briefing chain (16 Nov's morning predates it)
BRIEF_LATE = 60    # minutes: a slot whose median push is later than this is named in bold


def briefing_section(st, days=14, today_=None):
    """13 Nov 2026: how late each briefing push went, from
    groupings-archive/briefed.json "log" (notify.mark_sent). The pushes come
    from the first build at or after each slot's hour, and GitHub runs
    scheduled builds late at busy times (12 Nov lunch 2h18 late, night 1h40),
    so a late slot is a late price for Douglas. Health only."""
    from datetime import date as _d, timedelta as _td
    log = [e for e in ((st or {}).get("log") or []) if isinstance(e, dict)]
    if today_: log = [e for e in log if e.get("date", "") >= (_d.fromisoformat(today_) - _td(days=days)).isoformat()]
    if not log: return []
    out = [f"## Briefing pushes (last {days} days, minutes after the slot's hour)", "",
           "| slot | sent | median | worst | skipped |", "|---|---|---|---|---|"]
    late = []
    for name in ("morning", "lunch", "evening", "night"):
        sent = sorted(e["late"] for e in log if e.get("slot") == name and e.get("late") is not None)
        skip = sum(1 for e in log if e.get("slot") == name and e.get("skipped"))
        if not sent and not skip: continue
        med = sent[len(sent) // 2] if sent else None
        out.append(f"| {name} | {len(sent)} | {med if med is not None else 'n/a'} | {sent[-1] if sent else 'n/a'} | {skip} |")
        if (med is not None and med > BRIEF_LATE) or skip: late.append(name)
    out.append(f"**Late or skipped: {', '.join(late)}.**" if late else f"Every slot's median push within {BRIEF_LATE} minutes, none skipped.")
    # 16 Nov 2026: the 14-day medians mix the cron days with the chain's
    # (briefing_watch.py --wait from CHAIN_FROM), so the chain gets its own line.
    chain = sorted(e["late"] for e in log if e.get("date", "") >= CHAIN_FROM and e.get("late") is not None)
    cskip = sum(1 for e in log if e.get("date", "") >= CHAIN_FROM and e.get("skipped"))
    if chain or cskip:
        med = chain[len(chain) // 2] if chain else None
        out.append(f"Since the briefing chain ({CHAIN_FROM}, `briefing_watch.py --wait`): {len(chain)} sent, median "
                   f"{med if med is not None else 'n/a'} minutes late, worst {chain[-1] if chain else 'n/a'}, {cskip} skipped. "
                   "A slot the chain sends lands about five minutes after its hour; later means the chain broke "
                   "(a build that did not dispatch `briefing-next`).")
    return out + [""]


def coverage_lines(rep, record):
    """10 Nov 2026: the live row of the replay beside the live Card the record
    holds over the same days. Until 10 Nov most live legs were archived only as
    estimates, so the replay rebuilt none of the live Card (0 groups against 21
    from 29 Oct to 9 Nov) and its "live" row read as if the Card had made
    nothing. Full-rule groups only: the wider-rule filler and late groups apart."""
    live = (rep.get("variants") or {}).get("live")
    if not live or not rep.get("from") or not rep.get("to"): return []
    by_rule = rule_coverage(rep, record)
    if by_rule is not None: return by_rule
    held = sum(1 for d in record.get("days") or [] if rep["from"] <= d.get("date", "") <= rep["to"]
               for g in d.get("groups") or [] if str(g.get("name", "")).startswith("Card") and not g.get("wide") and not g.get("late"))
    if not held: return []
    if live["groups"] >= held:
        return [f"Coverage: the replay's live row rebuilt {live['groups']} groups; the record holds {held} live Card groups over these days."]
    return [f"Coverage: the record holds **{held}** live Card groups over these days; the replay rebuilt {live['groups']}. "
            "The gap is legs archived only as estimates (every leg from 10 Nov carries its first real price), so the replay "
            "reads the rules against each other on the legs it has, not the live Card's own return."]


POOL_REAL_FROM = "2026-11-10"  # every pool leg from here carries its first real price


def rule_coverage(rep, record, today_=None):
    """24 Nov 2026: the record's Card groups beside the replay of the rule each
    one ran under, on that rule's own live days. The old line set every live
    group over the window (rules 1 to 14) against the replay's live row (rule
    14 alone) and blamed the gap on estimate-only legs: 33 v 10 on 24 Nov, when
    most of the gap was the rule. None when the replay predates `groupDays`."""
    rules = rep.get("rules") or []
    if not rules or any("groupDays" not in r for r in rules): return None
    today_ = today_ or today
    lo, hi = rep["from"], min(rep["to"], today_)
    held, pending = {}, set()
    for d in record.get("days") or []:
        day = d.get("date", "")
        if not (lo <= day < hi): continue
        for g in d.get("groups") or []:
            if not str(g.get("name", "")).startswith("Card") or g.get("wide") or g.get("late"): continue
            if g.get("status") not in ("won", "lost"): pending.add(day); continue
            held.setdefault(g.get("rule"), []).append(day)
    if not held: return []
    spans = {r["rule"]: r for r in rules}
    parts, n_held, n_rep, early = [], 0, 0, 0
    for rule in sorted(held, key=lambda x: (x is None, x if isinstance(x, int) else 0)):
        days = held[rule]; r = spans.get(rule)
        if not r:
            parts.append(f"rule {rule} {len(days)} v not replayed"); n_held += len(days); continue
        a, b = max(r["from"], lo), min(r["to"] or hi, hi)
        live_days = {d for d in r["groupDays"] if a <= d <= b and d < hi and d not in pending}
        h = sum(1 for d in days if a <= d <= b)
        out = len(days) - h  # held on a day outside the rule's own span (a group built the day before a switch)
        k = sum(r["groupDays"][d] for d in live_days)
        n_held += len(days); n_rep += k
        early += sum(1 for d in days if d < POOL_REAL_FROM)
        parts.append(f"rule {rule} {len(days)} v {k}" + (f" ({out} dated outside its span)" if out else ""))
    last = max(d for v in held.values() for d in v)
    return [f"Coverage, by the rule each day ran: the record holds {n_held} settled live Card group(s) from {lo} to {last}; the replay of the rule live that day rebuilt {n_rep} on the same days ({'; '.join(parts)}). "
            + (f"{early} of the record's groups fall before {POOL_REAL_FROM}, when most legs were archived only as estimates, "
               "so the replay misses them; from then on a gap is the price the rule was read on (the Fidelity line). "
               if early else "")
            + "The variant table reads the rules against each other on the legs the pool has, not the live Card's own return."]


def _published(rec, rule, start, end):
    """{date: [picks]} of the record's full-rule Card groups under `rule`,
    settled days only (a pending leg is not in the replay's pool)."""
    out, pending = {}, set()
    for d in rec.get("days") or []:
        day = d.get("date", "")
        if not (start <= day <= end): continue
        for g in d.get("groups") or []:
            if not str(g.get("name", "")).startswith("Card") or g.get("wide") or g.get("late") or g.get("rule") != rule:
                continue
            if g.get("status") not in ("won", "lost"): pending.add(day); continue
            out.setdefault(day, []).append(sorted(l.get("pick") for l in g.get("legs") or []))
    return out, pending


def fidelity_lines(rec, rep, rep_close=None, today_=None):
    """24 Nov 2026: the replay's live row against the Card the page published
    on the live rule's own days, at first and at last pre-start prices. The
    pool replay reads each leg at its first real price, written up to three
    days before the start; the page rebuilds every group until its first
    kick-off on that build's prices. A rule that reads the price (rule 14's
    value demand) can pass a leg at the first price that the page refused
    later, so the replay's live row is not the page's Card. This names how
    often they agree, so the 30 Nov read knows which price to trust."""
    rec, rep = rec or {}, rep or {}
    rule = rec.get("cardLiveRule")
    if not rule or not (rep.get("variants") or {}).get("live"): return []
    start = next((r.get("from") for r in rep.get("rules") or [] if r.get("rule") == rule and r.get("from")), None)
    if not start: return []
    today_ = today_ or today
    end = min(rep.get("to") or today_, today_)
    pub, pending = _published(rec, rule, start, end)
    # every settled day of the live rule counts, a day with no group included
    alld = [d for d in sorted({x.get("date", "") for x in rec.get("days") or []}) if start <= d < today_ and d not in pending]
    if not alld: return []
    n_pub = sum(len(pub.get(d, [])) for d in alld)
    parts = []
    for label, r in (("first", rep), ("last pre-start", rep_close)):
        gl = ((r or {}).get("variants") or {}).get("live", {}).get("groupList")
        if gl is None: continue
        if any("picks" not in g for g in gl): continue
        rp = {}
        for g in gl:
            if g.get("date") in alld: rp.setdefault(g["date"], []).append(sorted(g["picks"]))
        same = sum(1 for d in alld for p in rp.get(d, []) if p in pub.get(d, []))
        off = [d for d in alld if bool(rp.get(d)) != bool(pub.get(d))]
        parts.append(f"at {label} prices {sum(len(v) for v in rp.values())} group(s), {same} with the page's picks"
                     + (f", a group on one side only on {', '.join(d[5:] for d in off)}" if off else ""))
    if not parts: return []
    return [f"Fidelity (rule {rule}, {alld[0]} to {alld[-1]}, {len(alld)} settled day(s)): the page published {n_pub} group(s); "
            f"the replay's live row {'; '.join(parts)}. The replay reads a leg at one price, the page at each build's; "
            "a gap here is the price the rule was read on, not a different rule."]


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


def rules_section(rep, rec):
    """19 Nov 2026 (Douglas: "which rule has performed the best over the entire
    timeline"): every CARD_RULE rebuilt on the whole pool (card_replay.RULES),
    the same days for each, beside its own live record (groupings-record.json
    cardByRule, the days it ran). The replay column is the comparison; the
    live column is what the page staked."""
    rules = (rep or {}).get("rules") or []
    if not rules: return []
    by = (rec or {}).get("cardByRule") or {}
    lines = [f"## Every Card rule on the same days ({rep.get('from')} to {rep.get('to')})", "",
             "| rule | live | replayed on the whole archive: groups | won / expected | return | v live / day | p(worse) | live record: groups | won / expected | return at stakes |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rules:
        t = by.get(str(r["rule"])) or {}
        live = f"{t.get('settled', 0)}" if t else "0"
        lret = pct(t["unitsReturned"] / t["unitsStaked"] - 1) if t.get("unitsStaked") else "n/a"
        lines.append(f"| {r['rule']}: {r['what']} | {r['from']} to {r['to'] or 'now'} | {r['groups']} | {r['won']} / {r['expected']} | "
                     f"{pct(r['return'] - 1) if r['groups'] else 'n/a'} | {r['vsLivePerDay'] if r.get('vsLivePerDay') is not None else ('live' if r['variant'] == 'live' else '')} | "
                     f"{r['pWorse'] if r.get('pWorse') is not None else ''} | {live} | {t.get('won', 0)} / {t.get('expected', 0)} | {lret} |")
    lines += ["", "Rule 9 (the context veto) is not rebuilt: it depends on reads made on the day. Rules 2 and 3 changed the windows and the page, not the picks. "
              "The replay column reads every rule on the same legs; the live column is only the days each ran, so it is the smaller sample.", ""]
    return lines


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
            if r.get("pWorse") is None and not (r.get("vsLivePerDay") or 0): why.append("identical to live on the pool")
            elif (r.get("vsLivePerDay") or 0) <= 0: why.append("behind on the pool")
            elif r.get("pWorse") is None or r["pWorse"] > GATE_P: why.append(f"pool p(worse) {r.get('pWorse')}")
            elif gate_legs(r) < GATE_LEGS: why.append(f"pool {gate_legs(r)} legs of {GATE_LEGS}")
            if not fd_ok:
                bad = [s + (" identical" if x.get("identical") else "") for s, x, k in fd if k in ("fit", "check") and not fd_beats(x)]
                why.append("football-data " + (", ".join(bad) if bad else "fit and check not both on file"))
            verdict = "fails: " + ", ".join(why)
        out.append(f"| {v} | {r['vsLivePerDay']:+.2f} | {r.get('pWorse') if r.get('pWorse') is not None else 'identical'} | {gate_legs(r)} | " + " | ".join(cells) + f" | {verdict} |")
    refused = [v for v, r, fd in rows if (r.get("vsLivePerDay") or 0) > 0 and any((not x.get("identical")) and (x.get("perDay") or 0) < 0 for _, x, _ in fd)]
    if refused:
        out.append("Ahead on the pool but behind live on football-data in at least one season, so not a candidate however the pool reads: " + ", ".join(refused) + ".")
    if passed:
        out.append("**Full gate passed: " + ", ".join(passed) + ". The next build session changes the rule (CARD_RULE bump with these numbers, note, release).**")
    return out + [""]


def book_vs_lines(vb):
    """13 Nov 2026 (#156): each UK book against the Card's own book on the
    picks both priced, paired, and the best UK price against it. A side is
    read only on 50+ paired picks at day-resampled p <= 0.10. The Card's book
    is Douglas's account, so a book that pays more is a question for him."""
    if not vb or not vb.get("books"): return []
    base, out, ahead = vb["base"], [], []
    for b, r in sorted(vb["books"].items(), key=lambda kv: (kv[0] == "best UK price", -kv[1]["first"]["meanPct"])):
        f, se = r["first"], r.get("settled") or {}
        line = (f"- {b} v {base}, the same picks: {f['meanPct']:+.2f}% a pick at the first price (n {f['n']} over {f.get('days', '?')} days, ahead {f['aheadShare'] * 100:.0f}%, behind {f['behindShare'] * 100:.0f}%"
                + (f", p {f['p']:.3f}" if f.get("p") is not None else "") + f"; {f['read']}), about {f['group3Pct']:+.1f}% on a three-pick group")
        if se.get("n"): line += f"; settled singles {se['returnBasePct']:+.2f}% at {base} v {se['returnPct']:+.2f}% (n {se['n']})"
        if r.get("sports"): line += "; " + ", ".join(f"{k} {v}" for k, v in r["sports"].items())
        out.append(line)
        if b != "best UK price" and f["read"].endswith("pays more") and f["read"].startswith(b) and se.get("read", "").startswith(b): ahead.append((b, f))
    for b, f in ahead:
        out.append(f"- **{b} pays more than {base} on {f['n']} paired picks (about {f['group3Pct']:+.1f}% a Card 2x). `CARD_BOOK` is Douglas's book, so this is his call, not the session's.**")
    return out


def empty_card_days(since, today_, archive="groupings-archive"):
    """18 Nov 2026: the started days from `since` to yesterday on which the
    live Card published no group (the full-rule Card only, as in
    live_days_section: not the filler, the paper cards or retired kinds).
    The archive holds a day file only for days that published something."""
    import re as _re
    from datetime import date as _date, timedelta as _td
    end = _date.fromisoformat(today_) - _td(days=1)
    d, days = _date.fromisoformat(since), []
    while d <= end:
        days.append(d.isoformat()); d += _td(days=1)
    have = set()
    if os.path.isdir(archive):
        for f in os.listdir(archive):
            if _re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", f) and f[:-5] in days:
                gs = load(os.path.join(archive, f)).get("groups") or []
                if any(str(g.get("name") or "").startswith("Card ") and not g.get("wide") for g in gs):
                    have.add(f[:-5])
    return {x for x in days if x not in have}


def live_days_section(archive="groupings-archive", today_=None, days=14, record=None):
    """13 Nov 2026: the live Card's own output, day by day. The Card has built
    nothing since 10 Nov (rule 6's last group; rules 7 to 11 went live on
    11 Nov), and nothing in the review said so: the replay tables read rules
    against each other, not what the page published. Counts the groups in each
    day archive (the archive holds days that published a group) over the last
    `days` finished days and the run of empty days to yesterday. A tally of the
    record, nothing fitted (Rule 1)."""
    import re as _re
    from datetime import date as _date, timedelta as _td
    end = _date.fromisoformat(today_ or today) - _td(days=1)
    span = [(end - _td(days=i)).isoformat() for i in range(days - 1, -1, -1)]
    got, last = {}, None
    files = sorted(f for f in os.listdir(archive) if _re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", f)) if os.path.isdir(archive) else []
    for f in files:
        d = f[:-5]
        if d > end.isoformat(): continue
        # the full-rule Card only: not the wider-rule filler (`wide`), the paper Model card or retired kinds
        gs = [g for g in (load(os.path.join(archive, f)).get("groups") or [])
              if str(g.get("name") or "").startswith("Card ") and not g.get("wide")]
        if gs:
            last = d
            if d in got or d >= span[0]: got[d] = gs
    run = 0
    for d in reversed(span):
        if d in got: break
        run += 1
    built = sum(1 for d in span if d in got)
    lines = [f"## The live Card, {span[0]} to {span[-1]}", "",
             f"Days with a group: {built} of {len(span)}; groups {sum(len(got.get(d, [])) for d in span)}; "
             f"last group published for {last or 'no day on file'}."]
    rules = sorted({g['rule'] for d in span for g in got.get(d, [])})
    if rules: lines[-1] += " Rules: " + ", ".join(str(r) for r in rules) + "."
    # 15 Nov 2026: two-day groups (CARD_SPAN, 12 Nov) named, and the record of
    # the model's-picks Card (CARD_RULE 7 on, 11 Nov) on its own, so the review
    # says whether the Card as it is now built is landing, not the mix of rules
    two = sum(1 for d in span for g in got.get(d, []) if g.get("span"))
    if two: lines[-1] += f" Two-day groups (`CARD_SPAN`): {two}."
    rec = load("groupings-record.json") if record is None else record
    by = {int(k): v for k, v in (rec.get("cardByRule") or {}).items() if str(k).isdigit() and int(k) >= 7}
    if by:
        n = sum(v.get("groups", 0) for v in by.values()); done = sum(v.get("settled", 0) for v in by.values())
        won = sum(v.get("won", 0) for v in by.values()); exp = sum(v.get("expected", 0) for v in by.values())
        us = sum(v.get("unitsStaked", 0) for v in by.values()); ur = sum(v.get("unitsReturned", 0) for v in by.values())
        line = (f"The model's-picks Card (rules {', '.join(str(r) for r in sorted(by))}, from 11 Nov): {n} group(s), "
                f"{done} settled, {won} won v {exp:.2f} expected")
        line += f", {pct(ur / us - 1)} at the page's stakes." if us else "; none settled yet."
        lines.append(line)
    if run >= 3:
        lines.append(f"**{run} days running with no Card group (to {span[-1]}).** Empty days stay empty by Douglas's decision "
                     "(11 Nov, `CARD_FILLER` False); the funnel below names the condition that costs them, and every volume "
                     "relief replayed so far (m7under5, m7legs2, pay25, with3x) failed the gate.")
    return lines + [""]


def review_body():
    """The review's markdown, built from the files on disk (16 Nov 2026:
    split from main so a later run can refresh the day's issue)."""
    integ, rep, pt, st = load("integrity.json"), load("card-replay.json"), load("price-timing.json"), load("staking.json")
    rep_close = load("card-replay-closing.json")   # 24 Nov 2026: the same replay at last pre-start prices
    lines = [f"# Card review {today}", ""]
    f = integ.get("findings", [])
    lines += [f"## Integrity: {len(f)} finding(s)"] + [f"- `{x['check']}` " + " ".join(f"{k}={v}" for k, v in x.items() if k != "check") for x in f[:20]] + [""]
    lines += live_days_section()
    lines += decisions_section(load("groupings-record.json"), rep, load("card-legs-history.json"), rep_close=rep_close)
    if rep.get("variants"):
        lines += [f"## The Card on the archive, {rep['from']} to {rep['to']} ({rep['days']} days)", "",
                  "| variant | groups | won | expected | legs | return | empty days | v live / day | p(worse) |", "|---|---|---|---|---|---|---|---|---|"]
        for v, r in rep["variants"].items():
            lines.append(f"| {v} | {r['groups']} | {r['won']} | {r['expected']} | {r.get('legs', '')} | {pct((r['return'] or 1) - 1) if r['return'] else 'n/a'} | {r['emptyDays']} | {r.get('vsLivePerDay', '')} | {r.get('pWorse', '')} |")
        src = rep.get("source") or {}
        if src.get("pool"):
            # 9 Nov 2026: the legs come from the archived pool from poolFrom
            legs = ", ".join(f"{k} {v}" for k, v in sorted((src.get("poolLegs") or {}).items(), key=lambda x: -x[1])) or "none"
            lo = src.get("poolLeftOut") or {}
            # 16 Nov 2026: legs kept with an opposition price from the football
            # archive are counted apart from the legs left out
            out = ", ".join(f"{k} {v}" for k, v in sorted(lo.items()) if "(kept)" not in k) or "none"
            kept = "".join(f"; {k.replace(' (kept)', '')}: {v} legs" for k, v in sorted(lo.items()) if "(kept)" in k)
            lines.append(f"Source: the archived pool from {src['poolFrom']} (settled priced legs: {legs}; left out: {out}{kept})"
                         f"{', closing prices' if src.get('closing') else ''}; football-data archive rows before that. "
                         "A leg archived before any bookmaker priced it counts only once its first real price is on file (`priced`, 9 Nov 2026).")
        lines += coverage_lines(rep, load("groupings-record.json"))
        lines += fidelity_lines(load("groupings-record.json"), rep, rep_close)
        lines += rule6_lines(rep)
        lines.append("")
        lines += rules_section(rep, load("groupings-record.json"))
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
        lines += book_vs_lines(pt.get("vsBook"))
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
    # 18 Nov 2026: the replay row is the live rule on football-data (it was
    # rule 5/6 football only), and the pool row the live rule on every sport
    stake_label = {"replay": "replay, football-data, the live rule", "pool": "replay, the archived pool, the live rule", "live": "live"}
    for k in ("replay", "pool", "live"):
        s = st.get(k) or {}
        if s.get("flat1pct"):
            fl = s["flat1pct"]
            lines += [f"## Staking, {stake_label[k]} ({s['groups']} groups, landed/expected {s['landedOverExpected']})",
                      f"- flat 1% a group: median season {pct(fl['median'])}, 10th-90th {pct(fl['p10'])} to {pct(fl['p90'])}, worst drawdown (95%) {fl['p95Drawdown'] * 100:.0f}%",
                      kelly_line(s),
                      ] + [f"- {lab} ({b['groups']} groups at {s.get('groupsPerDay')} a day{' since ' + s['rateFrom'] if s.get('rateFrom') else ''}, the page's stakes): 95%-worst drawdown {b['p95DrawdownUnits']} units, "
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
        # 14 Nov 2026: a sport with its own floor (CARD_SPORT_MIN) is judged on
        # the legs today's floor admits (`atFloor`), the row above is every leg.
        for sp, t in by.items():
            a = t.get("atFloor")
            if a is None: continue
            got = (f"{a['landed']} of {a['legs']} landed ({a['rate'] * 100:.0f}%) v {a['quoted'] * 100:.0f}% quoted, z {a['z'] if a['z'] is not None else 'n/a'}"
                   if a["legs"] else "none yet")
            lines.append(f"- {sp} at today's {t['floor'] * 100:.0f}% floor (the legs the sport-off test counts): {got}; "
                         f"every leg {'would fire' if t.get('tripwireAll') else 'would not fire'} on its own.")
        fired = [sp for sp, t in by.items() if t["tripwire"]]
        lines += [("**Tripwire fired for " + ", ".join(fired) + ": the next build session adds it to `CARD_SPORTS_OFF` (CARD_RULE bump, note, release).**" if fired
                   else "A sport comes off the Card at 50+ legs two standard errors or more under quote (the Daily List's rule)."), ""]
    lines += context_pause_line(load("groupings-archive/context-ledger.json"))
    lines += rule13_split_section(load("groupings-record.json").get("cardRule13Split"))
    lines += context_section(load("groupings-record.json").get("cardContext"))
    lines += list_book_section(load("groupings-record.json").get("listAtBook"))
    lines += funnel_section()
    lines += edge_section()
    lines += star_section()
    lines += markets_section(load("markets-record.json"), load("goals-value.json"))
    lines += briefing_section(load("groupings-archive/briefed.json"), today_=today)
    lines += ["Artifacts: integrity.json, card-replay.json, price-timing.json, staking.json on this run. Advisory: nothing here changes a rule."]
    return "\n".join(lines)


REFRESHED = "\n\n_Refreshed "


def refreshed(body, when):
    """The body with a closing line naming when a later run rewrote it."""
    return body + REFRESHED + when + " UTC by a later run, on newer files (tune.yml's Monday football-data read lands after the morning review)._"


def unrefreshed(body):
    """The body without its refreshed line, to compare two runs' reviews."""
    i = (body or "").rfind(REFRESHED)
    return body[:i] if i >= 0 else (body or "")


def main():
    body = review_body()
    f = load("integrity.json").get("findings", [])
    title = f"Card review {today}"
    issue = posted_issue(title)
    if issue and os.environ.get("FORCE_POST") != "1":
        # 16 Nov 2026: the day's review posted at 12:02, tune.yml committed the
        # football-data paired read at 13:16, and the 19:41 run posted nothing,
        # so the issue said "no paired season read on file yet" all day. A
        # later run now rewrites the day's body when its files say something
        # new; it never opens a second review or a second integrity issue.
        if issue.get("number") and unrefreshed(issue.get("body")).strip() != body.strip():
            gh("-X", "PATCH", f"repos/{REPO}/issues/{issue['number']}", "-f",
               "body=" + refreshed(body, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")))
            print(f"{title} was already posted; its body was refreshed with this run's read.")
        else:
            print(f"{title} is already posted and unchanged; nothing posted this run (FORCE_POST=1 posts anyway).")
        print(body)
        return
    ensure_label("card-review", "c8102e", "The nightly Card review")
    ensure_label("office-backlog", "0e8a16", "A task for the office sprint")
    posted = gh("-X", "POST", f"repos/{REPO}/issues", "-f", f"title={title}", "-f", f"body={body}", "-f", "labels[]=card-review")
    if isinstance(posted, dict) and posted.get("number"):
        closed = close_older(title)
        if closed: print(f"closed the older card-review issue(s): {', '.join('#' + str(n) for n in closed)}")
    if f:
        fb = "\n".join(f"- `{x['check']}` " + " ".join(f"{k}={v}" for k, v in x.items() if k != "check") for x in f[:30])
        gh("-X", "POST", f"repos/{REPO}/issues", "-f", f"title=Card integrity: {len(f)} finding(s) on {today}",
           "-f", f"body=The nightly checker (tools/card_integrity.py) found:\n\n{fb}\n\nFix the cause in the pipeline (grading, pricing or archiving), not the record by hand; add a test that would have caught it. Deliverable: a change that passes the gates.",
           "-f", "labels[]=office-backlog", "-f", "labels[]=agent:engineer")
    print(body)

if __name__ == "__main__":
    main()
