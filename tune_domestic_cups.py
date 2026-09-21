#!/usr/bin/env python3
"""
Fit the within-country tier gap (en.1 vs en.2 vs en.3...) from real domestic
cup cross-division results, instead of leaving it hand-set.

Why this is a different question to tune_strengths.py
-------------------------------------------------------
tune_strengths.py fits COUNTRY strength from European ties — but Champions
League, Europa League and Conference League entrants are overwhelmingly
each country's TOP-FLIGHT clubs. That fit has never seen a single en.2 or
es.2 side, so it carries zero information about whether the gap from a
country's tier 1 to its tier 2 (or 2 to 3, or 3 to 4) is sized correctly.
Domestic cups are the one place that gap actually gets tested: an FA Cup or
EFL Cup tie routinely pits a Premier League side against a League One or
National League one. This tool fits from those ties instead.

    python3 tune_domestic_cups.py --report        fit, validate, print, write nothing
    python3 tune_domestic_cups.py --fit            as above, write domestic_tiers.json if it PASSES
    python3 tune_domestic_cups.py --fit --dry-run  fit and print the verdict, write nothing regardless

Data
----
openfootball/england carries FA Cup (facup.txt) and EFL Cup (eflcup.txt) for
each season back to 2019/20, in the same clean single-match format as every
other tool in this project — two-legged/replay/shootout ties are dropped for
the same reason they're dropped everywhere else: a Poisson goal model
doesn't mean the same thing applied to them.

A tie only enters the fit if BOTH sides can be placed in a specific tier
(1 through 5) for that specific season, from that season's own league
fixture file — not the current tier, the tier they were actually in when
the tie was played. Ties involving a side below tier 5 (National League)
are dropped: this project doesn't carry ratings that deep, so there's
nothing to fit them against.

Only England is covered. Spain's Copa del Rey, Germany's DFB-Pokal and
Italy's Coppa Italia would extend this the same way, but none of the
obvious openfootball paths for them resolve — see the coverage note this
tool prints if you try. Worth another look if openfootball adds them.

Standard library only, like the rest of the project.
"""
import argparse, glob, json, math, os, random, re, sys
from datetime import date as _date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/openfootball"
EPS = 1e-12
MAXG = E.MAX_GOALS
FACT = [math.factorial(i) for i in range(MAXG + 1)]

MIN_HOLDOUT = 150
MAX_P_WORSE = 0.20
MIN_GAIN = 0.0005

TIERS = ["en.1", "en.2", "en.3", "en.4", "en.5"]
TIER_FILES = {"en.1": "1-premierleague", "en.2": "2-championship",
              "en.3": "3-league1", "en.4": "4-league2", "en.5": "5-nationalleague"}
SEASONS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
CHECK_SEASON = "2024-25"

CLEAN_MATCH = [
    re.compile(r'^(.+?)\s{2,}(\d+)-(\d+)(?:\s*\(\d+-\d+\))?\s{2,}(.+?)$'),
    re.compile(r'^(.+?)\s+v\s+(.+?)\s+(\d+)-(\d+)(?:\s*\(\d+-\d+\))?\s*$'),
]


def fetch(path, cache_dir):
    fp = os.path.join(cache_dir, path.replace("/", "_"))
    if os.path.exists(fp):
        return open(fp, encoding="utf-8", errors="replace").read()
    import urllib.request
    req = urllib.request.Request(f"{RAW}/{path}", headers={"User-Agent": "footyalmanac-tune"})
    text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    os.makedirs(cache_dir, exist_ok=True)
    open(fp, "w", encoding="utf-8").write(text)
    return text


def parse_clean(text, season):
    """Single-match ties only — replays, extra time and shootouts dropped,
    same reasoning as every other clean-match parser in this project."""
    rows = []
    for raw in text.splitlines():
        s = raw.rstrip("\r\n").strip()
        if not s or s.startswith(("=", "#", "▪", "•")):
            continue
        if any(t in s.lower() for t in ("pen.", "a.e.t", "agg")):
            continue
        m = CLEAN_MATCH[0].match(s)
        if m:
            home, hg, ag, away = m.group(1).strip(), int(m.group(2)), int(m.group(3)), m.group(4).strip()
        else:
            m = CLEAN_MATCH[1].match(s)
            if not m:
                continue
            home, away, hg, ag = m.group(1).strip(), m.group(2).strip(), int(m.group(3)), int(m.group(4))
        rows.append((season, home, away, hg, ag))
    return rows


def team_tiers(cache_dir):
    """{season: {team: tier_code}} from each season's own league files."""
    out = {}
    for s in SEASONS:
        out[s] = {}
        for code, fname in TIER_FILES.items():
            try:
                text = fetch(f"england/master/{s}/{fname}.txt", cache_dir)
            except Exception:
                continue
            for _, home, away, _, _ in parse_clean(text, s):
                out[s][home] = code
                out[s][away] = code
    return out


def load_cup_ties(cache_dir):
    tiers = team_tiers(cache_dir)
    resolved = []
    coverage_notes = []
    for comp, fname in (("FA Cup", "facup"), ("EFL Cup", "eflcup")):
        for s in SEASONS:
            try:
                text = fetch(f"england/master/{s}/{fname}.txt", cache_dir)
            except Exception as e:
                coverage_notes.append(f"{comp} {s}: not available ({e})")
                continue
            for season, home, away, hg, ag in parse_clean(text, s):
                ht, at = tiers.get(s, {}).get(home), tiers.get(s, {}).get(away)
                if ht and at:
                    resolved.append((comp, season, home, ht, away, at, hg, ag))
    # Spain/Germany/Italy: checked, nothing resolves at the obvious paths.
    for country, guess in (("Spain (Copa del Rey)", "espana/master/2023-24/copa-del-rey.txt"),
                            ("Germany (DFB-Pokal)", "deutschland/master/2023-24/dfb-pokal.txt"),
                            ("Italy (Coppa Italia)", "italy/master/2023-24/coppa-italia.txt")):
        coverage_notes.append(f"{country}: no data at {guess} (and no working alternative found)")
    return resolved, coverage_notes


# ---------------------------------------------------------------------------
# fit + score (same machinery as tune_strengths.py)
# ---------------------------------------------------------------------------

def fit_tiers(train, reg_k=25, lr=0.03, epochs=400):
    prior = {t: E.LEAGUES[t]["strength"] for t in TIERS}
    mu = sum(r[6] + r[7] for r in train) / (2 * len(train))
    ha, aa = E.HOME_MULT[1], E.AWAY_MULT[1]
    n = {t: 0 for t in TIERS}
    for r in train:
        n[r[3]] += 1
        n[r[5]] += 1
    beta = {t: math.log(prior[t]) for t in TIERS}
    for _ in range(epochs):
        grad = {t: 0.0 for t in TIERS}
        for _, _, _, ht, _, at, hg, ag in train:
            lh = mu * ha * math.exp(beta[ht] - beta[at])
            la = mu * aa * math.exp(beta[at] - beta[ht])
            grad[ht] += (hg - lh) - (ag - la)
            grad[at] += -(hg - lh) + (ag - la)
        for t in TIERS:
            if t == "en.1":
                continue
            reg = -2 * (beta[t] - math.log(prior[t])) * (reg_k / max(n[t], 1))
            beta[t] += lr * (grad[t] + reg) / max(n[t], 1)
    return {t: round(math.exp(beta[t]), 3) for t in TIERS}, mu, ha, aa, n


def outcome(lh, la, rho=None):
    rho = E.RHO if rho is None else rho
    ph = [math.exp(-lh) * lh ** i / FACT[i] for i in range(MAXG + 1)]
    pa = [math.exp(-la) * la ** i / FACT[i] for i in range(MAXG + 1)]
    run = home = draw = total = 0.0
    for x in range(MAXG + 1):
        home += ph[x] * run; draw += ph[x] * pa[x]; run += pa[x]; total += ph[x]
    total *= sum(pa)
    d00 = ph[0]*pa[0]*(-lh*la*rho); d01 = ph[0]*pa[1]*(lh*rho)
    d10 = ph[1]*pa[0]*(la*rho);     d11 = ph[1]*pa[1]*(-rho)
    home += d10; draw += d00+d11; total += d00+d01+d10+d11
    return home/total, draw/total, (total-home-draw)/total


def score(rows, strength, mu, ha, aa):
    per, hit = [], 0
    for _, _, _, ht, _, at, hg, ag in rows:
        lh = max(0.15, mu * ha * (strength[ht] / strength[at]))
        la = max(0.15, mu * aa * (strength[at] / strength[ht]))
        p = outcome(lh, la)
        y = 0 if hg > ag else (1 if hg == ag else 2)
        per.append(-math.log(max(p[y], EPS)))
        if p.index(max(p)) == y:
            hit += 1
    return per, hit / len(rows)


def paired(a, b, reps=2000, seed=17):
    rng = random.Random(seed)
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    means = [sum(diff[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    mu = sum(diff) / n
    return mu, sum(1 for m in means if m > 0) / len(means)


def run(cache_dir, verbose=True):
    resolved, notes = load_cup_ties(cache_dir)
    train = [r for r in resolved if r[1] != CHECK_SEASON]
    check = [r for r in resolved if r[1] == CHECK_SEASON]
    shipped = {t: E.LEAGUES[t]["strength"] for t in TIERS}

    fitted, mu, ha, aa, n = fit_tiers(train)
    per_s, acc_s = score(check, shipped, mu, ha, aa)
    per_f, acc_f = score(check, fitted, mu, ha, aa)
    m, pw = paired(per_f, per_s)

    verdict = {
        "generated": _date.today().isoformat(),
        "trainTies": len(train), "checkSeason": CHECK_SEASON, "checkTies": len(check),
        "checkLogLoss": {"shipped": round(sum(per_s)/len(per_s), 4),
                          "fitted": round(sum(per_f)/len(per_f), 4),
                          "delta": round(m, 4), "pWorse": round(pw, 3)},
        "checkAccuracy": {"shipped": round(acc_s, 4), "fitted": round(acc_f, 4)},
        "gates": {"enoughData": len(check) >= MIN_HOLDOUT,
                  "notWorse": pw <= MAX_P_WORSE, "worthIt": -m >= MIN_GAIN},
        "tiers": fitted, "tiesPerTier": n, "coverage": notes,
    }
    verdict["pass"] = all(verdict["gates"].values())

    if verbose:
        print(f"{len(resolved)} cross-division FA Cup + EFL Cup ties resolved to a tier on both "
              f"sides, {len(train)} to fit on, {len(check)} held out ({CHECK_SEASON}, never fitted)\n")
        print(f"{'tier':8}{'ties':>6}{'shipped':>9}{'fitted':>9}")
        for t in TIERS:
            print(f"  {t:8}{n[t]:>6}{shipped[t]:>9.3f}{fitted[t]:>9.3f}")
        c = verdict["checkLogLoss"]
        print(f"\ncheck ({verdict['checkTies']} ties): log loss shipped {c['shipped']} -> "
              f"fitted {c['fitted']} ({c['delta']:+.4f}, p(worse) {c['pWorse']:.1%})")
        print(f"accuracy: shipped {verdict['checkAccuracy']['shipped']:.2%} -> "
              f"fitted {verdict['checkAccuracy']['fitted']:.2%}")
        print("\ngates")
        for k, v in verdict["gates"].items():
            print(f"  {'PASS' if v else 'FAIL'}  {k}")
        print("\ncoverage")
        for line in notes:
            print(f"  {line}")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cache", default=os.path.join(HERE, ".domesticcupcache"))
    args = ap.parse_args()
    if not (args.report or args.fit):
        ap.error("nothing to do: pass --report or --fit")

    verdict = run(args.cache)

    if args.fit:
        out = os.path.join(HERE, "domestic_tiers.json")
        if args.dry_run:
            print("\ndry run, nothing written")
        elif verdict["pass"]:
            json.dump(verdict, open(out, "w"), indent=1)
            print(f"\nwrote {os.path.basename(out)} — apply the `tiers` values to "
                  f"LEAGUES by hand, same as tune_strengths.py's output")
        else:
            failed = [k for k, v in verdict["gates"].items() if not v]
            print(f"\nnot written: failed {', '.join(failed)}. The hand-set tiers stay.")
            json.dump(verdict, open(os.path.join(HERE, "domestic-tier-report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
