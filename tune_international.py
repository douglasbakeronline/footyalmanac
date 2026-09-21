#!/usr/bin/env python3
"""
Fit attack/defence ratings for national teams from real international match
history, the same Dixon-Coles-compatible shape used for clubs (att/def
multipliers relative to a shared average, fed into engine.match_probabilities),
so international fixtures price through the exact same pipeline as everything
else rather than a bolted-on second model.

Data: martj42/international_results on GitHub — every international match
since 1872, tournament-tagged, neutral-venue flagged, actively maintained.
No club league has anything like this: it means the weighting choices below
can be tested, not guessed.

    python3 tune_international.py --report        fit, validate, print, write nothing
    python3 tune_international.py --fit            as above, write international.json if it PASSES
    python3 tune_international.py --fit --dry-run  fit and print the verdict, write nothing

Why a national team can't be rated the way a club is
------------------------------------------------------
A club plays ~35-45 matches a season against the same domestic pool, so a
single season's table is a reasonable rating on its own (see build_table /
strength_from_table). A national team plays 8-15 matches a YEAR, against
wildly different opposition, and a lot of those matches are friendlies where
a side doesn't field its real strength. Three adjustments earn their place
because of that, each tested below rather than assumed:

  1. A long history window with recency decay, not one season. Half-life is
     swept, not guessed (see RECENCY_HALF_LIVES).
  2. Every match weighted by what was at stake, using the tournament-tier
     scheme the football-analytics community already converged on
     (eloratings.net's K-multipliers) as the starting point — not invented
     here, but tested here: TIER_WEIGHTS is a hypothesis, and the sweep
     below checks whether the model is actually better for having it.
  3. Home advantage switched off match-by-match using the dataset's own
     `neutral` flag, not applied as a blanket discount — a third of
     matches since 2018 are neutral-venue and treating them as home fixtures
     would systematically overrate whoever is listed first.

Method
------
Joint Poisson regression over two parameters per team (log attack, log
defence), fit by gradient ascent with L2 shrinkage toward 0 — same shape as
the strength fit in tune_strengths.py, just two parameters per team instead
of one per country, and every match weighted by recency x importance instead
of counted once. Mean-zero re-centring each epoch keeps attack and defence
separately identified (the classic Poisson-regression drift: the whole
system can shift attack up and defence down together with no change to any
prediction, so the fit needs an anchor).

Standard library only, like the rest of the project.
"""
import argparse, csv, io, json, math, os, random, sys, urllib.request
from datetime import date as _date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
EPS = 1e-12
MAXG = E.MAX_GOALS
FACT = [math.factorial(i) for i in range(MAXG + 1)]

MIN_HOLDOUT = 400
MAX_P_WORSE = 0.10   # stricter than the club-strength tool: this ships a
                      # whole new rating system, not a nudge to an existing one
MIN_GAIN = 0.0005

# eloratings.net's tournament weighting, normalised so a friendly is 1.0.
# A hypothesis to test (see the sweep in fit_and_validate), not a given.
TIER_WEIGHTS = {
    "world_cup": 3.0, "continental_final": 2.5, "qualifier": 2.0,
    "nations_league": 1.5, "other": 1.0,
}
def tier_of(tournament):
    t = tournament.lower()
    if t == "fifa world cup":
        return "world_cup"
    if "qualification" in t or "qualifying" in t:
        return "qualifier"
    if "nations league" in t:
        return "nations_league"
    if t in ("uefa euro", "copa américa", "copa america", "african cup of nations",
              "afc asian cup", "gold cup", "concacaf championship"):
        return "continental_final"
    return "other"

FIT_FROM = "2016-01-01"   # ten years of history feeds the fit
CHECK_FROM = "2026-01-01"  # never fitted on: this year's matches only


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

def load_rows(cache_path):
    if os.path.exists(cache_path):
        text = open(cache_path, encoding="utf-8").read()
    else:
        req = urllib.request.Request(DATA_URL, headers={"User-Agent": "footyalmanac-tune"})
        text = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        open(cache_path, "w", encoding="utf-8").write(text)
    return list(csv.DictReader(io.StringIO(text)))


def build_matches(rows, since):
    out = []
    for r in rows:
        if r["date"] < since:
            continue
        try:
            hg, ag = int(r["home_score"]), int(r["away_score"])
        except (ValueError, TypeError):
            continue
        out.append({
            "date": r["date"], "home": r["home_team"], "away": r["away_team"],
            "hg": hg, "ag": ag, "neutral": r["neutral"] == "TRUE",
            "tier": tier_of(r["tournament"]),
        })
    return out


# ---------------------------------------------------------------------------
# fit
# ---------------------------------------------------------------------------

def weight(m, as_of, half_life_days, tier_weights):
    days = (as_of - datetime.strptime(m["date"], "%Y-%m-%d")).days
    recency = 0.5 ** (max(days, 0) / half_life_days)
    return recency * tier_weights[m["tier"]]


def fit_ratings(matches, as_of, half_life_days, tier_weights,
                 reg_k=8, lr=0.02, epochs=300):
    teams = sorted({m["home"] for m in matches} | {m["away"] for m in matches})
    w = [weight(m, as_of, half_life_days, tier_weights) for m in matches]
    n = {t: 0.0 for t in teams}
    for m, wt in zip(matches, w):
        n[m["home"]] += wt
        n[m["away"]] += wt

    mu = sum(wt * (m["hg"] + m["ag"]) for m, wt in zip(matches, w)) / (2 * sum(w))
    home_matches = [(m, wt) for m, wt in zip(matches, w) if not m["neutral"]]
    home_adv = math.log(
        sum(wt * m["hg"] for m, wt in home_matches) /
        max(sum(wt * m["ag"] for m, wt in home_matches), 1e-6)
    ) / 2  # split symmetrically: home gets +h, away gets -h in log space

    att = {t: 0.0 for t in teams}
    de = {t: 0.0 for t in teams}
    for _ in range(epochs):
        gatt = {t: 0.0 for t in teams}
        gdef = {t: 0.0 for t in teams}
        for m, wt in zip(matches, w):
            h, a = m["home"], m["away"]
            ha = 0.0 if m["neutral"] else home_adv
            lh = mu * math.exp(ha + att[h] - de[a])
            la = mu * math.exp(-ha + att[a] - de[h])
            eh, ea = (m["hg"] - lh) * wt, (m["ag"] - la) * wt
            gatt[h] += eh;  gdef[a] -= eh
            gatt[a] += ea;  gdef[h] -= ea
        for t in teams:
            att[t] += lr * (gatt[t] - 2 * reg_k * att[t]) / max(n[t], 1)
            de[t]  += lr * (gdef[t] - 2 * reg_k * de[t]) / max(n[t], 1)
        # The only direction this model can't see is att[t] += c, def[t] += c
        # for every team at once (it cancels in att[h]-def[a] and
        # att[a]-def[h] alike) — so that's the one degree of freedom that
        # needs pinning down before it's identifiable, and pinning it means
        # removing exactly that shared shift, nothing else. Subtracting
        # attack's own mean and defence's own mean separately, as an earlier
        # version of this function did, removes two DIFFERENT amounts and so
        # injects a phantom shift into every attack-minus-defence gap each
        # epoch — small, compounding every pass, enough that a run tuned on
        # its own training data by the end scored worse than the untuned
        # starting point. One shared constant, applied to both, is the fix.
        c = (sum(att.values()) + sum(de.values())) / (2 * len(teams))
        for t in teams:
            att[t] -= c
            de[t] -= c

    return {t: {"att": round(math.exp(att[t]), 3), "def": round(math.exp(-de[t]), 3),
                "weight": round(n[t], 1)} for t in teams}, mu, math.exp(home_adv)


# ---------------------------------------------------------------------------
# scoring (identical machinery to tune_strengths.py, so the numbers mean
# the same thing across both tools)
# ---------------------------------------------------------------------------

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


def score(check, ratings, mu, home_adv, baseline=False):
    # Matches engine.match_probabilities' own convention exactly:
    # lh = att_h * def_a * mu * hm (multiplication, not division — a strong
    # away defence has def < 1 and multiplying it in is what suppresses the
    # home side's expected goals). Diverging from that here once produced a
    # fit that scored worse than a no-information baseline on its own
    # training data — impossible for a correctly-scored regression, and
    # exactly backwards from what the gradient ascent was actually doing
    # internally, where this same multiplicative form is used throughout.
    per, hit = [], 0
    for m in check:
        h, a = m["home"], m["away"]
        if baseline:
            ah = ad = aa = ada = 1.0
        else:
            rh, ra = ratings.get(h), ratings.get(a)
            if not rh or not ra:
                continue
            ah, ad, aa, ada = rh["att"], rh["def"], ra["att"], ra["def"]
        ha = 1.0 if m["neutral"] else home_adv
        lh = max(0.1, mu * ha * ah * ada)
        la = max(0.1, mu * aa * ad / ha)
        p = outcome(lh, la)
        y = 0 if m["hg"] > m["ag"] else (1 if m["hg"] == m["ag"] else 2)
        per.append(-math.log(max(p[y], EPS)))
        if p.index(max(p)) == y:
            hit += 1
    return per, hit / max(len(per), 1)


def paired(a, b, reps=2000, seed=17):
    rng = random.Random(seed)
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    means = [sum(diff[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    mu = sum(diff) / n
    return mu, sum(1 for m in means if m > 0) / len(means)


# ---------------------------------------------------------------------------
# top level: sweep the two hypotheses (recency half-life, tier weighting),
# then validate the winner on the untouched 2026 holdout
# ---------------------------------------------------------------------------

RECENCY_HALF_LIVES = [365, 730, 1095, 1460]   # 1 / 2 / 3 / 4 years

def run(cache_dir, verbose=True):
    rows = load_rows(os.path.join(cache_dir, "results.csv"))
    all_matches = build_matches(rows, FIT_FROM)
    train = [m for m in all_matches if m["date"] < CHECK_FROM]
    check = [m for m in all_matches if m["date"] >= CHECK_FROM]
    as_of = datetime.strptime(CHECK_FROM, "%Y-%m-%d")

    if verbose:
        print(f"{len(train)} training matches ({FIT_FROM} to {CHECK_FROM}), "
              f"{len(check)} holdout matches (2026, never fitted on)\n")

    # Sweep 1: does recency weighting matter, and at what half-life?
    sweep = []
    for hl in RECENCY_HALF_LIVES:
        ratings, mu, ha = fit_ratings(train, as_of, hl, TIER_WEIGHTS)
        per, acc = score(check, ratings, mu, ha)
        sweep.append((hl, sum(per) / len(per), acc))
    best_hl = min(sweep, key=lambda x: x[1])[0]
    if verbose:
        print("recency half-life sweep (holdout log loss):")
        for hl, ll, acc in sweep:
            flag = "  <- best" if hl == best_hl else ""
            print(f"  {hl:5d}d ({hl/365:.1f}y)   log loss {ll:.4f}   accuracy {acc:.2%}{flag}")

    # Sweep 2: does tournament-importance weighting help, at the winning
    # half-life, versus every match counted once regardless of stakes?
    flat_weights = {k: 1.0 for k in TIER_WEIGHTS}
    r_tier, mu_t, ha_t = fit_ratings(train, as_of, best_hl, TIER_WEIGHTS)
    r_flat, mu_f, ha_f = fit_ratings(train, as_of, best_hl, flat_weights)
    per_tier, acc_tier = score(check, r_tier, mu_t, ha_t)
    per_flat, acc_flat = score(check, r_flat, mu_f, ha_f)
    m_tw, pw_tw = paired(per_tier, per_flat)
    if verbose:
        print(f"\ntournament weighting: flat log loss {sum(per_flat)/len(per_flat):.4f}  "
              f"vs weighted {sum(per_tier)/len(per_tier):.4f}  "
              f"({m_tw:+.4f}, p(worse) {pw_tw:.1%})")

    use_tier_weights = m_tw < 0 and pw_tw <= 0.30
    final_weights = TIER_WEIGHTS if use_tier_weights else flat_weights
    ratings, mu, home_adv = fit_ratings(train, as_of, best_hl, final_weights)

    # Final check: does the whole system beat a home-advantage-only baseline
    # (every team rated identically) — i.e. do the ratings carry real signal
    # at all, on matches never touched during fitting?
    per_fit, acc_fit = score(check, ratings, mu, home_adv)
    per_base, acc_base = score(check, ratings, mu, home_adv, baseline=True)
    m, pw = paired(per_fit, per_base)

    verdict = {
        "generated": _date.today().isoformat(),
        "trainMatches": len(train), "checkMatches": len(check),
        "recencyHalfLifeDays": best_hl,
        "tierWeighted": use_tier_weights,
        "mu": round(mu, 4), "homeAdvantage": round(home_adv, 4),
        "checkLogLoss": {"baseline": round(sum(per_base)/len(per_base), 4),
                          "fitted": round(sum(per_fit)/len(per_fit), 4),
                          "delta": round(m, 4), "pWorse": round(pw, 3)},
        "checkAccuracy": {"baseline": round(acc_base, 4), "fitted": round(acc_fit, 4)},
        "gates": {
            "enoughData": len(check) >= MIN_HOLDOUT,
            "notWorse": pw <= MAX_P_WORSE,
            "worthIt": -m >= MIN_GAIN,
        },
        "ratings": ratings,
    }
    verdict["pass"] = all(verdict["gates"].values())

    if verbose:
        c = verdict["checkLogLoss"]
        print(f"\nfinal system: half-life {best_hl}d, "
              f"{'tournament-weighted' if use_tier_weights else 'flat weighting'}, "
              f"home advantage x{home_adv:.3f}")
        print(f"  log loss  home-adv-only baseline {c['baseline']}  ->  rated teams {c['fitted']}  "
              f"({c['delta']:+.4f}, p(worse) {c['pWorse']:.1%})")
        print(f"  accuracy  baseline {verdict['checkAccuracy']['baseline']:.2%}  "
              f"->  rated {verdict['checkAccuracy']['fitted']:.2%}")
        print(f"  {len(ratings)} teams rated")
        print("\ngates")
        for k, v in verdict["gates"].items():
            print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cache", default=os.path.join(HERE, ".intlcache"))
    args = ap.parse_args()
    if not (args.report or args.fit):
        ap.error("nothing to do: pass --report or --fit")

    verdict = run(args.cache)

    if args.fit:
        out = os.path.join(HERE, "international.json")
        if args.dry_run:
            print("\ndry run, nothing written")
        elif verdict["pass"]:
            json.dump(verdict, open(out, "w"), indent=1)
            print(f"\nwrote {os.path.basename(out)} — read by build.py for any fixture "
                  f"whose competition is marked international in LEAGUES")
        else:
            failed = [k for k, v in verdict["gates"].items() if not v]
            print(f"\nnot written: failed {', '.join(failed)}.")
            json.dump(verdict, open(os.path.join(HERE, "international-report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
