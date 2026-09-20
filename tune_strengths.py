#!/usr/bin/env python3
"""
Fit the LEAGUES strength coefficients from real cross-country match results,
instead of leaving them hand-set. This is the item engine.py's own header
comment points at ("values fitted from European competition results") and
the one roadmap.md calls the single highest-impact open item.

    python3 tune_strengths.py --report          fetch, fit, print the table, write nothing
    python3 tune_strengths.py --fit              as above, write engine_strengths.json if it PASSES
    python3 tune_strengths.py --fit --dry-run    fit and print the verdict, write nothing regardless

Data
----
openfootball/champions-league carries every Champions League, Europa League
and Conference League match back to 2011/12, with each club's country coded
inline ("Real Madrid CF (ESP)"), so no name-matching against domestic tables
is needed to know which league a side belongs to. Only single-match, 90 (or
120, non-shootout) minute results are used — two-legged aggregate ties and
penalty shootouts are dropped, because a Poisson goal model doesn't mean the
same thing applied to a scoreline like "4-2 pen. 1-0 a.e.t.".

Method
------
A Poisson log-linear model over one parameter per country, log(strength):

    E[home goals] = mu * HOME_MULT[1] * strength[home] / strength[away]
    E[away goals] = mu * AWAY_MULT[1] * strength[away] / strength[home]

England is fixed at 1.00, matching the existing anchor. Every other country
is fit by gradient ascent on the Poisson log-likelihood, regularised toward
its CURRENT hand-set value: a country's own data has to outweigh REG_K
matches of that prior before it moves it much, so a league that has played
Europe six times in five years stays close to where it started and a league
that has played it two hundred times can move a long way.

Same three rules as tune.py, applied here instead of to the eight small
constants:

  1. Fit on everything up to and including the last COMPLETE season. Check
     on the one after it, never touched during fitting.
  2. The comparison on the check season is paired and bootstrapped.
  3. Nothing ships unless it clears gates tuned to the same standard as
     calibration.json: enough holdout data, not likely to be worse, worth
     the churn. See MIN_HOLDOUT / MAX_P_WORSE / MIN_GAIN below.

Standard library only, like the rest of the project.
"""
import argparse, glob, json, math, os, random, re, sys
from datetime import date as _date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "https://codeload.github.com/openfootball/champions-league/tar.gz/refs/heads/master"
EPS = 1e-12
MAXG = E.MAX_GOALS
FACT = [math.factorial(i) for i in range(MAXG + 1)]

# Same bar as calibration.json, except MIN_HOLDOUT is lower: a season of CL
# + EL + ECL is a few hundred matches, not a few thousand, so 250 fixtures
# the way tune.py means it is not achievable here. 150 cross-country
# results is still a real check, just a noisier one — which is exactly why
# MAX_P_WORSE matters more here than it does there.
MIN_HOLDOUT = 150
MAX_P_WORSE = 0.30
MIN_GAIN = 0.0003

# UEFA's inline country code differs from our own `iso` field in exactly
# the cases below (three-letter abbreviation vs our flag/ISO spelling).
# Monaco has no domestic league of its own — AS Monaco plays in the French
# pyramid — so it maps to fr.1 rather than being its own entry.
MANUAL_MAP = {
    "SCO": "sco.1", "SUI": "ch.1", "CRO": "hrv.1", "DEN": "dnk.1",
    "GRE": "gr.1", "POR": "pt.1", "GER": "de.1", "NED": "nl.1",
    "BUL": "bgr.1", "MCO": "fr.1", "RUS": "ru.1",
    "ENG": "en.1", "ESP": "es.1", "ITA": "it.1", "FRA": "fr.1",
}


# ---------------------------------------------------------------------------
# data: fetch + parse
# ---------------------------------------------------------------------------

def fetch_repo(cache_dir):
    """Download and extract openfootball/champions-league once; reused on
    every later run exactly like backfill.py's cached history/ files."""
    root = os.path.join(cache_dir, "champions-league-master")
    if os.path.isdir(root):
        return root
    import tarfile, urllib.request, io
    os.makedirs(cache_dir, exist_ok=True)
    req = urllib.request.Request(REPO, headers={"User-Agent": "footyalmanac-tune"})
    data = urllib.request.urlopen(req, timeout=60).read()
    tarfile.open(fileobj=io.BytesIO(data)).extractall(cache_dir)
    return root


LINE_RE = re.compile(
    r'^(?P<home>.+? \(\w{3}\))\s+v\s+(?P<away>.+? \(\w{3}\))\s+'
    r'(?P<hg>\d+)-(?P<ag>\d+)\s*(?:\(\d+-\d+\))?\s*$'
)
TEAM_RE = re.compile(r'^(.*)\((\w{3})\)$')


def parse_file(path, season):
    rows = []
    for raw in open(path, encoding="utf-8", errors="replace"):
        s = raw.rstrip("\r\n").strip()
        if " v " not in s or any(t in s.lower() for t in ("pen.", "a.e.t", "agg")):
            continue   # two-legged / shootout ties: a single Poisson score
                       # doesn't mean the same thing there, so they're dropped
        m = LINE_RE.match(s)
        if not m:
            continue
        hm, am = TEAM_RE.match(m["home"].strip()), TEAM_RE.match(m["away"].strip())
        if not hm or not am:
            continue
        rows.append((season, hm.group(2), am.group(2), int(m["hg"]), int(m["ag"])))
    return rows


def load_matches(cache_dir):
    root = fetch_repo(cache_dir)
    cmap = dict(MANUAL_MAP)
    for code, meta in E.LEAGUES.items():
        if meta.get("cup") or meta.get("tier") != 1:
            continue
        cmap.setdefault(meta["iso"].upper(), code)

    rows, unmapped = [], set()
    for season_dir in sorted(glob.glob(os.path.join(root, "20*-*"))):
        season = os.path.basename(season_dir)
        for fname in ("cl.txt", "el.txt", "conf.txt"):
            fp = os.path.join(season_dir, fname)
            if not os.path.exists(fp):
                continue
            for season_, hc, ac, hg, ag in parse_file(fp, season):
                h, a = cmap.get(hc), cmap.get(ac)
                if h and a:
                    rows.append((season_, h, a, hg, ag))
                else:
                    unmapped.add(hc if not h else ac)
    return rows, unmapped, sorted({d for d, *_ in rows})


# ---------------------------------------------------------------------------
# fit
# ---------------------------------------------------------------------------

def fit_strengths(train_rows, countries, reg_k=40, lr=0.02, epochs=400):
    mu = sum(hg + ag for *_, hg, ag in train_rows) / (2 * len(train_rows))
    ha, aa = E.HOME_MULT[1], E.AWAY_MULT[1]
    n = {}
    for _, h, a, _, _ in train_rows:
        n[h] = n.get(h, 0) + 1
        n[a] = n.get(a, 0) + 1

    prior = {c: math.log(E.LEAGUES[c]["strength"]) for c in countries}
    beta = dict(prior)
    for _ in range(epochs):
        grad = {c: 0.0 for c in countries}
        for _, h, a, hg, ag in train_rows:
            lh = mu * ha * math.exp(beta[h] - beta[a])
            la = mu * aa * math.exp(beta[a] - beta[h])
            grad[h] += (hg - lh) - (ag - la)
            grad[a] += -(hg - lh) + (ag - la)
        for c in countries:
            if c == "en.1":
                continue
            reg = -2 * (beta[c] - prior[c]) * (reg_k / max(n.get(c, 1), 1))
            beta[c] += lr * (grad[c] + reg) / max(n.get(c, 1), 1)

    strength = {c: round(math.exp(beta[c]), 3) for c in countries}
    return strength, mu, ha, aa, n


def outcome(lh, la, rho=None):
    rho = E.RHO if rho is None else rho
    ph = [math.exp(-lh) * lh ** i / FACT[i] for i in range(MAXG + 1)]
    pa = [math.exp(-la) * la ** i / FACT[i] for i in range(MAXG + 1)]
    run = home = draw = total = 0.0
    for x in range(MAXG + 1):
        home += ph[x] * run
        draw += ph[x] * pa[x]
        run += pa[x]
        total += ph[x]
    total *= sum(pa)
    d00 = ph[0] * pa[0] * (-lh * la * rho)
    d01 = ph[0] * pa[1] * (lh * rho)
    d10 = ph[1] * pa[0] * (la * rho)
    d11 = ph[1] * pa[1] * (-rho)
    home += d10; draw += d00 + d11; total += d00 + d01 + d10 + d11
    return home / total, draw / total, (total - home - draw) / total


def score(rows, strength, mu, ha, aa):
    per, hit = [], 0
    for _, h, a, hg, ag in rows:
        lh = max(0.15, mu * ha * (strength[h] / strength[a]))
        la = max(0.15, mu * aa * (strength[a] / strength[h]))
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run(cache_dir, verbose=True):
    rows, unmapped, seasons = load_matches(cache_dir)
    if unmapped and verbose:
        print(f"  no LEAGUES entry for: {', '.join(sorted(unmapped))} "
              f"(too small to carry a UEFA place we track) — dropped", file=sys.stderr)

    check_season = seasons[-1]
    train = [r for r in rows if r[0] != check_season]
    check = [r for r in rows if r[0] == check_season]
    countries = sorted({c for _, h, a, _, _ in rows for c in (h, a)})

    fitted, mu, ha, aa, n = fit_strengths(train, countries)
    shipped = {c: E.LEAGUES[c]["strength"] for c in countries}

    per_s, acc_s = score(check, shipped, mu, ha, aa)
    per_f, acc_f = score(check, fitted, mu, ha, aa)
    m, pw = paired(per_f, per_s)

    verdict = {
        "generated": _date.today().isoformat(),
        "trainMatches": len(train), "checkSeason": check_season,
        "checkMatches": len(check),
        "checkLogLoss": {"shipped": round(sum(per_s) / len(per_s), 4),
                          "fitted": round(sum(per_f) / len(per_f), 4),
                          "delta": round(m, 4), "pWorse": round(pw, 3)},
        "checkAccuracy": {"shipped": round(acc_s, 4), "fitted": round(acc_f, 4)},
        "gates": {
            "enoughData": len(check) >= MIN_HOLDOUT,
            "notWorse": pw <= MAX_P_WORSE,
            "worthIt": -m >= MIN_GAIN,
        },
        "strengths": fitted, "matchesPerLeague": n,
    }
    verdict["pass"] = all(verdict["gates"].values())

    if verbose:
        print(f"\n{len(rows)} single-match UEFA results, {len(countries)} leagues, "
              f"train on all but {check_season} ({len(train)}), check on {check_season} ({len(check)})\n")
        print(f"{'league':10}{'n':>6}{'shipped':>9}{'fitted':>9}{'delta':>8}")
        for c in sorted(countries, key=lambda c: shipped[c], reverse=True):
            d = fitted[c] - shipped[c]
            flag = "  <-" if abs(d) >= 0.05 else ""
            print(f"  {c:10}{n.get(c,0):>5}{shipped[c]:>9.3f}{fitted[c]:>9.3f}{d:>+8.3f}{flag}")
        c = verdict["checkLogLoss"]
        print(f"\ncheck season {check_season} ({verdict['checkMatches']} fixtures, never fitted on)")
        print(f"  log loss  shipped {c['shipped']}  ->  fitted {c['fitted']}  "
              f"({c['delta']:+.4f}, p(worse) {c['pWorse']:.1%})")
        print(f"  accuracy  shipped {verdict['checkAccuracy']['shipped']:.2%}  "
              f"->  fitted {verdict['checkAccuracy']['fitted']:.2%}")
        print("\ngates")
        for k, v in verdict["gates"].items():
            print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cache", default=os.path.join(HERE, ".strengthcache"))
    args = ap.parse_args()
    if not (args.report or args.fit):
        ap.error("nothing to do: pass --report or --fit")

    verdict = run(args.cache)

    if args.fit:
        out = os.path.join(HERE, "engine_strengths.json")
        if args.dry_run:
            print("\ndry run, nothing written")
        elif verdict["pass"]:
            json.dump(verdict, open(out, "w"), indent=1)
            print(f"\nwrote {os.path.basename(out)} — apply the `strengths` values to "
                  f"LEAGUES by hand (this does not edit engine.py itself; the strength "
                  f"list is read and reasoned about by people, not machine-owned like "
                  f"calibration.json)")
        else:
            failed = [k for k, v in verdict["gates"].items() if not v]
            print(f"\nnot written: failed {', '.join(failed)}. The hand-set strengths stay.")
            json.dump(verdict, open(os.path.join(HERE, "strength-tuning-report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
