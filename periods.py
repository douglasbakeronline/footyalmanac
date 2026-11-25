"""Half-time scores for the football the site graded, kept for good.

16 Nov 2026, Douglas: "we need to make sure we get to the level where
everything is captured". The graded record holds full-time scores only, so a
half-time bet (win both halves, half-time/full-time, first-half goals) could
never be settled from it. API-Football's day sweep, which the build already
makes for every date (sources._af_day), carries each fixture's half-time
score; since 16 Nov 2026 the day cache keeps it (sources._compact). This
reads those cached day files, makes no API call, matches them to the graded
fixtures by names and kick-off (odds.match_af, the matcher the prices use)
and writes periods/football-YYYY-MM.json:

    {"league|date|home|away": [ht home, ht away, ft home, ft away, AF fixture id]}

The full time is kept beside the half time so a mismatch shows (it must equal
the graded result; `check` counts any that do not). Only graded fixtures are
kept, so the files stay small (about 40 KB a month at today's volume).

A graded fixture whose day file scores it another way is not kept as a half
time; since 25 Nov 2026 (#472, a second source for the graded results) it is
named in periods/disagree.json (both scores, API-Football's names and how
closely they match) and in the build log, and dropped again when the record is
regraded. tools/card_integrity.py reads it for the legs Douglas stakes.

The US sports, rugby and college sports keep their points by period in
history-sports/ (sports._game, `hp` / `ap`); tennis keeps every set score in
tennis-record.json's notes. So this file is football's only.

Standard library only. Run after score.py in deploy.yml; allowed to fail.
"""
import glob
import gzip
import json
import os
import sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "periods")
LOOKBACK = 180       # days of graded fixtures looked for on each run (10 until 16 Nov 2026: sources
                     # now fills older day files' half times once, HT_BACK_DAYS, so the season fills in)
MISSED = "missed.json"   # fixtures tried against a day file with half times and not matched: never tried again
DISAGREE = "disagree.json"  # 25 Nov 2026 (#472): graded results API-Football scores another way, named
LOG_NAMES = 5            # disagreements named in the build log


def _load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(dict(sorted(obj.items())), f, separators=(",", ":"), ensure_ascii=False)
    os.replace(path + ".tmp", path)


def want_keys(games):
    return [key_of(g) for g in games]


def disagreements(here=HERE):
    """{(date, home, away): entry} from periods/disagree.json: graded football
    results API-Football's day file scores another way (25 Nov 2026, #472).
    Keyed without the league so a Card leg (which keeps no league code) finds it."""
    out = {}
    for k, v in (_load(os.path.join(here, "periods", DISAGREE), {}) or {}).items():
        _, d, h, a = (k.split("|") + ["", "", "", ""])[:4]
        out[(d, h, a)] = dict(v, league=k.split("|")[0])
    return out


def key_of(g):
    return f"{g.get('league')}|{g.get('date')}|{g.get('home')}|{g.get('away')}"


def cached_days(cache_dir, dates):
    """{fid: (kick-off datetime, home, away, [ht h, ht a], [ft h, ft a])} from
    the day files already on disk for these dates. No network."""
    import sources as S
    out = {}
    for d in dates:
        path = os.path.join(cache_dir, f"day-{d.isoformat()}.json.gz")
        try:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                rows = [S._expand(c) for c in json.load(fh).get("rows") or []]
        except Exception:
            continue
        for f in rows:
            ht = (f.get("score") or {}).get("halftime")
            ft = (f.get("score") or {}).get("fulltime") or {}
            if not ht or ht.get("home") is None or ft.get("home") is None:
                continue
            when = (f.get("fixture") or {}).get("date")
            try:
                t = datetime.fromisoformat(when.replace("Z", "+00:00")) if when else None
            except ValueError:
                t = None
            out[str(f["fixture"]["id"])] = (t, f["teams"]["home"]["name"], f["teams"]["away"]["name"],
                                            [ht["home"], ht["away"]], [ft.get("home"), ft.get("away")])
    return out


def build(here=HERE, today=None, cache_dir=None, log=None):
    """Adds the half-time scores found for graded fixtures of the last
    LOOKBACK days. Returns (fixtures looked for, found, written files)."""
    import odds as O
    import sources as S
    log = log if log is not None else []
    today = today or date.today()
    since = (today - timedelta(days=LOOKBACK)).isoformat()
    graded = [g for g in (_load(os.path.join(here, "record-graded.json"), {}) or {}).get("graded") or []
              if g.get("date", "") >= since and g.get("result")]
    files, have, stale = {}, set(), set()
    for g in graded:
        path = os.path.join(here, "periods", f"football-{g['date'][:7]}.json")
        if path not in files:
            files[path] = _load(path, {}) or {}
        kept = files[path].get(key_of(g))
        if kept and list(kept[2:4]) == list(g["result"]):
            have.add(key_of(g))
        elif kept:
            # 17 Nov 2026: the result was corrected after the half time was kept (Quindio v Real Cartagena,
            # kept at 0-1 and regraded 0-2). Drop the stale entry and look again; it comes back only when
            # the day file's full time agrees with the record.
            del files[path][key_of(g)]
            stale.add(path)
    for path in stale:              # written now, so a stale entry goes even when nothing new is found
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(dict(sorted(files[path].items())), f, separators=(",", ":"), ensure_ascii=False)
        os.replace(path + ".tmp", path)
    mpath = os.path.join(here, "periods", MISSED)
    missed = {k: d for k, d in (_load(mpath, {}) or {}).items() if d >= since}
    # 25 Nov 2026 (#472): a disagreement is kept while the record still grades the
    # fixture as it did; a regrade (or the fixture leaving the window) drops it and
    # the fixture is looked for again, so a corrected result can take its half time.
    dpath = os.path.join(here, "periods", DISAGREE)
    results = {key_of(g): list(g["result"]) for g in graded}
    old_dis = _load(dpath, {}) or {}
    disagree = {k: v for k, v in old_dis.items() if results.get(k) == list(v.get("graded") or [])}
    retry = {k for k in old_dis if k not in disagree and k in results}
    missed = {k: d for k, d in missed.items() if k not in retry}
    want = [g for g in graded if key_of(g) not in have and key_of(g) not in missed and key_of(g) not in disagree]
    if disagree != old_dis:
        _write(dpath, disagree)
    if not want:
        return 0, 0, []
    dates = {date.fromisoformat(g["date"]) + timedelta(days=o) for g in want for o in (-1, 0, 1)}
    days = cached_days(cache_dir or S.AF_CACHE_DIR, dates)
    # Only fixtures whose own day has half times on file are tried; the rest wait for sources to fill it.
    ready = {t.date().isoformat() for t, *_ in days.values() if t}
    want = [g for g in want if g["date"] in ready]
    if not days or not want:
        log.append("periods: no cached day files with half-time scores yet" if not days else
                   "periods: no new graded fixtures on days with half-time scores")
        return len(want), 0, []
    index = [(fid, t, h, a) for fid, (t, h, a, _, _) in days.items()]

    def ko(g):
        try:
            return datetime.fromisoformat(str(g.get("kickoff")).replace("Z", "+00:00")) if g.get("kickoff") else None
        except ValueError:
            return None
    hit = O.match_af([(i, ko(g), g["date"], g["home"], g["away"]) for i, g in enumerate(want)], index)
    found, bad, touched = 0, 0, set()
    for i, fid in hit.items():
        g = want[i]
        t, h, a, ht, ft = days[fid]
        if list(ft) != list(g["result"]):
            # the full time disagrees with the graded result: not kept as a half
            # time, but named (25 Nov 2026, #472) as a second source's read of the
            # score: a wrong grade, or a wrong match, for a person to tell apart
            bad += 1
            disagree[key_of(g)] = {"graded": list(g["result"]), "af": list(ft), "fid": int(fid),
                                   "afHome": h, "afAway": a, "sim": [round(O.name_sim(g["home"], h), 2),
                                                                    round(O.name_sim(g["away"], a), 2)]}
            continue
        path = os.path.join(here, "periods", f"football-{g['date'][:7]}.json")
        files[path][key_of(g)] = [ht[0], ht[1], ft[0], ft[1], int(fid)]
        touched.add(path)
        found += 1
    for i, g in enumerate(want):
        if key_of(g) in disagree:
            continue
        if key_of(g) not in files[os.path.join(here, "periods", f"football-{g['date'][:7]}.json")]:
            missed[key_of(g)] = g["date"]
    if bad:
        _write(dpath, disagree)
    os.makedirs(os.path.join(here, "periods"), exist_ok=True)
    with open(mpath + ".tmp", "w", encoding="utf-8") as f:
        json.dump(dict(sorted(missed.items())), f, separators=(",", ":"), ensure_ascii=False)
    os.replace(mpath + ".tmp", mpath)
    for path in touched:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(files[path].items())), f, separators=(",", ":"), ensure_ascii=False)
        os.replace(tmp, path)
    log.append(f"periods: {found} of {len(want)} graded football fixtures given a half-time score"
               + (f", {bad} refused (full time disagreed)" if bad else ""))
    named = [k for k in want_keys(want) if k in disagree][:LOG_NAMES]
    if named:
        log.append("periods: API-Football scores these graded results another way: " + "; ".join(
            f"{k.split('|')[2]} v {k.split('|')[3]} {k.split('|')[1]} graded {disagree[k]['graded'][0]}-{disagree[k]['graded'][1]}, "
            f"API-Football {disagree[k]['af'][0]}-{disagree[k]['af'][1]} ({disagree[k]['afHome']} v {disagree[k]['afAway']})"
            for k in named))
    return len(want), found, sorted(touched)


def check(here=HERE):
    """(kept, disagreeing with the graded result): a health line for QA."""
    graded = {key_of(g): g.get("result") for g in (_load(os.path.join(here, "record-graded.json"), {}) or {}).get("graded") or []}
    kept = bad = 0
    for path in glob.glob(os.path.join(here, "periods", "football-*.json")):
        for k, v in (_load(path, {}) or {}).items():
            kept += 1
            if k in graded and graded[k] and list(graded[k]) != v[2:4]:
                bad += 1
    return kept, bad


if __name__ == "__main__":
    log = []
    build(log=log)
    for line in log:
        print(line, file=sys.stderr)
    k, b = check()
    print(f"periods: {k} football fixtures with a half-time score on file" + (f", {b} disagree with the record" if b else ""),
          file=sys.stderr)
