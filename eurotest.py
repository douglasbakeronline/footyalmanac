#!/usr/bin/env python3
"""
The cross-competition harness. Prices every European tie of a past season the
way build.py would have priced it on the morning of the match, and scores it.

    python3 eurotest.py --report          coverage and every variant, changes nothing
    python3 eurotest.py --fit             refit europe.json if it passes the gates
    python3 eurotest.py --fit --dry-run   as above, write nothing

Why this exists
---------------
A league walk-forward cannot test anything that only matters between leagues:
the strength coefficients cancel inside a league. In a European tie they are
the whole answer, so this is the only place they can be tested at all.

Same rules as tune.py. Nothing is fitted on record.json. Every comparison is
paired and bootstrapped. The fit is made on one European season and must
survive on the next, which it has never seen.

The fit is structural, so unlike calibration.json it is never refitted on a
schedule. The weekly job runs --report for a human to read; --fit is run by
hand, and europe.json is committed like any other change to the model.

Standard library only.
"""
import argparse, json, math, os, random, re, sys
from collections import defaultdict
from datetime import date as _date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "europe.json")
COMPS = ("eu.cl", "eu.el", "eu.ec", "eu.clq", "eu.elq", "eu.ecq")
SEASONS = ("2024-25", "2025-26", "2026-27")
EPS = 1e-12

# Same three gates as tune.py.
MIN_HOLDOUT = 250
MAX_P_WORSE = 0.30
MIN_GAIN = 0.0005
LAMBDAS = (0.008, 0.03, 0.1, 0.3)   # ridge strengths tried by cross-validation

# openfootball tags every European club with a FIFA-style country code.
CC = {"ENG": "en.1", "ESP": "es.1", "ITA": "it.1", "GER": "de.1", "POR": "pt.1",
      "NED": "nl.1", "BEL": "be.1", "FRA": "fr.1", "CZE": "cze.1", "TUR": "tr.1",
      "NOR": "nor.1", "CYP": "cyp.1", "SWE": "swe.1", "GRE": "gr.1", "POL": "pol.1",
      "DEN": "dnk.1", "SVN": "svn.1", "AUT": "at.1", "SUI": "ch.1", "SCO": "sco.1",
      "ROU": "rou.1", "HUN": "hun.1", "AZE": "aze.1", "UKR": "ukr.1", "ISL": "isl.1",
      "ARM": "arm.1", "IRL": "irl.1", "SVK": "svk.1", "SRB": "srb.1", "BUL": "bgr.1",
      "MDA": "mda.1", "LVA": "lva.1", "ISR": "isr.1", "BIH": "bih.1", "FIN": "fin.1",
      "BLR": "blr.1", "CRO": "hrv.1", "NIR": "nir.1", "LTU": "ltu.1", "EST": "est.1",
      "FRO": "fro.1", "GEO": "geo.1", "WAL": "wal.1", "MLT": "mlt.1", "MNE": "mne.1",
      "LUX": "lux.1", "ALB": "alb.1", "MKD": "mkd.1"}
_TAG = re.compile(r"\s*\(([A-Z]{3})\)\s*$")


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

def domestic_seasons(code, euro):
    """(prior, current) domestic seasons for a European season."""
    y = int(euro[:4])
    meta = E.LEAGUES[code]
    if "season" in meta and "-" not in meta["season"]:
        return [str(y - 1), str(y - 2)], str(y)
    return [f"{y-1}-{str(y)[2:]}", f"{y-2}-{str(y-1)[2:]}"], f"{y}-{str(y+1)[2:]}"


_seasons = {}
def season(code, s, dated=True):
    """A domestic season. dated=True keeps only rows whose date can be trusted,
    for walk-forward use; a mis-dated result would otherwise leak from the
    future. Priors take every row, since they never read a date."""
    if (code, s) not in _seasons:
        rows, _ = S.fetch_season(code, s)
        _seasons[(code, s)] = sorted(rows or [])
    rows = _seasons[(code, s)]
    return S.in_window(rows, s) if dated else rows


def ties(euro):
    """Every played European tie in a season, with each side's domestic code."""
    out = []
    for comp in COMPS:
        rows, _ = S.fetch_fixtures(comp, euro)
        for r in rows or []:
            if r.get("hg") is None:
                continue
            sides = []
            for t in (r["home"], r["away"]):
                m = _TAG.search(t)
                sides.append((_TAG.sub("", t).strip(), CC.get(m.group(1)) if m else None))
            out.append(dict(comp=comp, date=r["date"], round=(r.get("round") or "").strip(),
                            home=sides[0], away=sides[1], hg=r["hg"], ag=r["ag"]))
    return out


class Rater:
    """Domestic ratings as build.py would have seen them on a given morning,
    prior season chosen by the same completeness guard."""

    def __init__(self, euro):
        self.euro, self.priors = euro, {}

    def prior(self, code):
        if code not in self.priors:
            pv, _ = domestic_seasons(code, self.euro)
            pick = None
            for i, s in enumerate(pv):
                rows = season(code, s, dated=False)
                if not rows:
                    continue
                older = season(code, pv[i + 1], dated=False) if i + 1 < len(pv) else None
                share, _ = S.completeness(rows, older)
                if share >= S.PRIOR_MIN_SHARE:
                    pick = rows
                    break
            tbl = E.build_table(pick) if pick else {}
            self.priors[code] = (E.strength_from_table(tbl) if tbl else {}, tbl,
                                 E.league_goal_rate(tbl) if tbl else 1.35)
        return self.priors[code]

    def rating(self, name, code, day):
        rat, tbl, mu = self.prior(code)
        if not tbl:
            return None
        pn = name if name in tbl else S.match_team(name, set(tbl))
        if pn is None:
            return None
        _, cs = domestic_seasons(code, self.euro)
        played = [r for r in season(code, cs) if r[0] < day]
        ctbl = E.build_table(played) if played else {}
        cn = pn if pn in ctbl else (S.match_team(pn, set(ctbl)) if ctbl else None)
        row = ctbl.get(cn) if cn else None
        cur = E.strength_from_table(ctbl).get(cn) if row else None
        return dict(r=E.blend(rat[pn], cur, row["P"] if row else 0),
                    form=E.form_factor(E.form_points(row)), mu=mu)


def build(euro):
    """[(tie, home rating, away rating)] and a tally of what was skipped."""
    rater, rows, skipped = Rater(euro), [], defaultdict(int)
    allt = ties(euro)
    for t in allt:
        hc, ac = t["home"][1], t["away"][1]
        if hc not in E.LEAGUES or ac not in E.LEAGUES:
            skipped["no domestic league on file"] += 1
            continue
        h = rater.rating(t["home"][0], hc, t["date"])
        a = rater.rating(t["away"][0], ac, t["date"])
        if h is None or a is None:
            skipped["club not matched"] += 1
            continue
        rows.append((t, h, a))
    return rows, dict(skipped), len(allt)


# ---------------------------------------------------------------------------
# pricing and scoring
# ---------------------------------------------------------------------------

def hand():
    return {c: m["strength"] for c, m in E.LEAGUES.items()}


def price(t, h, a, strength, frame_k):
    s_h, s_a = strength[t["home"][1]], strength[t["away"][1]]
    return E.cup_match(h["r"], s_h, a["r"], s_a, (h["mu"] + a["mu"]) / 2, tier=1,
                       neutral=(t["round"].lower() == "final"),
                       form_h=h["form"], form_a=a["form"], frame_k=frame_k)


def outcome(t):
    return "home" if t["hg"] > t["ag"] else ("away" if t["ag"] > t["hg"] else "draw")


def score(rows, strength=None, frame_k=E.CONTINENTAL_FRAME_K):
    strength = strength or hand()
    lls, hits, confs = [], [], []
    for t, h, a in rows:
        p = price(t, h, a, strength, frame_k)
        k = outcome(t)
        lls.append(-math.log(max(p[k], EPS)))
        hits.append(max(("home", "draw", "away"), key=lambda x: p[x]) == k)
        confs.append(p["confidence"])
    return lls, hits, confs


def paired(a, b, reps=1500, seed=17):
    """Mean change, sd, probability the change is actually worse."""
    rng = random.Random(seed)
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    ms = [sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    mu = sum(d) / n
    return mu, math.sqrt(sum((m - mu) ** 2 for m in ms) / reps), sum(m > 0 for m in ms) / reps


def bands(hits, confs, edges=(0, .45, .55, .62, .70, 1.01)):
    out = []
    for lo, hi in zip(edges, edges[1:]):
        xs = [(h, c) for h, c in zip(hits, confs) if lo <= c < hi]
        if xs:
            out.append((lo, hi, len(xs), sum(c for _, c in xs) / len(xs),
                        sum(h for h, _ in xs) / len(xs)))
    return out


# ---------------------------------------------------------------------------
# fitting
# ---------------------------------------------------------------------------

def fit(rows, lam, frame_k=E.CONTINENTAL_FRAME_K, steps=(0.08, 0.04, 0.02, 0.01)):
    """Coordinate descent on log strength, ridge back toward the hand-set value.

    Only the ties involving the league being moved are repriced, so a full fit
    takes seconds. A league with no ties never moves.
    """
    H = hand()
    S_ = dict(H)
    by = defaultdict(list)
    for i, (t, _, _) in enumerate(rows):
        by[t["home"][1]].append(i)
        by[t["away"][1]].append(i)
    n = len(rows)

    def one(i):
        t, h, a = rows[i]
        return -math.log(max(price(t, h, a, S_, frame_k)[outcome(t)], EPS))

    cur = [one(i) for i in range(n)]
    pen = lambda c: lam * (math.log(S_[c]) - math.log(H[c])) ** 2
    for step in steps:
        for _ in range(4):
            moved = False
            for c in sorted(by, key=lambda c: -len(by[c])):
                orig = S_[c]
                best = (sum(cur[i] for i in by[c]) / n + pen(c), orig, None)
                for f in (math.exp(step), math.exp(-step)):
                    S_[c] = orig * f
                    new = {i: one(i) for i in by[c]}
                    obj = sum(new.values()) / n + pen(c)
                    if obj < best[0] - 1e-9:
                        best = (obj, S_[c], new)
                S_[c] = best[1]
                if best[2]:
                    for i, v in best[2].items():
                        cur[i] = v
                    moved = True
            if not moved:
                break
    return S_


def choose_lambda(rows, folds=5, seed=7):
    """Ridge strength by k-fold CV inside the fit season. Never looks at the
    check season: choosing it there would be fitting on the holdout."""
    idx = list(range(len(rows)))
    random.Random(seed).shuffle(idx)
    parts = [idx[i::folds] for i in range(folds)]
    res = {}
    for lam in LAMBDAS:
        tot = 0.0
        for p in parts:
            ps = set(p)
            tr = [rows[i] for i in idx if i not in ps]
            tot += sum(score([rows[i] for i in p], fit(tr, lam))[0])
        res[lam] = tot / len(rows)
    return min(res, key=res.get), res


def pair_of_seasons():
    """(fit, check): the two most recent European seasons with enough ties."""
    got = []
    for s in SEASONS:
        rows, skipped, n = build(s)
        if len(rows) >= MIN_HOLDOUT:
            got.append((s, rows, skipped, n))
    return got[-2:] if len(got) >= 2 else None


# ---------------------------------------------------------------------------

def report():
    pair = pair_of_seasons()
    if not pair:
        print("not enough European ties on file")
        return
    for s, rows, skipped, n in pair:
        print(f"{s}: {n} ties, {len(rows)} priced, skipped {skipped}")
        old = score(rows, frame_k=None)
        new = score(rows)
        for tag, (l, h, c) in (("shipped (frame pull)", old), ("no frame pull", new)):
            print(f"  {tag:22s} log loss {sum(l)/len(l):.4f}  correct {sum(h)/len(h):.1%}")
            for lo, hi, k, q, landed in bands(h, c):
                print(f"      {lo:>4.0%}-{min(hi,1):<4.0%} n {k:4d}  quoted {q:.1%}  landed {landed:.1%}")
        mu, sd, pw = paired(new[0], old[0])
        print(f"  no frame pull vs shipped: {mu:+.4f} (sd {sd:.4f}, p worse {pw:.2f})")
    if CONT := E.CONTINENTAL:
        (_, _, _, _), (s, rows, _, _) = pair
        l = score(rows, {**hand(), **CONT})[0]
        mu, sd, pw = paired(l, score(rows, frame_k=None)[0])
        print(f"europe.json in force, on {s} vs shipped: {mu:+.4f} (sd {sd:.4f}, p worse {pw:.2f})")


def do_fit(dry=False):
    pair = pair_of_seasons()
    if not pair:
        print("not enough European ties on file; europe.json unchanged")
        return 1
    (fs, frows, _, _), (cs, crows, _, _) = pair
    lam, cv = choose_lambda(frows)
    print(f"fit {fs} ({len(frows)} ties), check {cs} ({len(crows)} ties)")
    print("  ridge by 5-fold CV inside fit season: " +
          ", ".join(f"{k}: {v:.4f}" for k, v in cv.items()) + f"  -> {lam}")
    fitted = fit(frows, lam)
    base = score(crows, frame_k=None)[0]           # what the site did before
    l, h, c = score(crows, fitted)
    mu, sd, pw = paired(l, base)
    print(f"  check: {mu:+.4f} log loss (sd {sd:.4f}, p worse {pw:.2f}), correct {sum(h)/len(h):.1%}")
    for lo, hi, k, q, landed in bands(h, c):
        print(f"      {lo:>4.0%}-{min(hi,1):<4.0%} n {k:4d}  quoted {q:.1%}  landed {landed:.1%}")
    H = hand()
    # Every league with ties in the fit, moved or not: being in the file is
    # what tells build.py a tie was priced off fitted numbers.
    covered = {t["home"][1] for t, _, _ in frows} | {t["away"][1] for t, _, _ in frows}
    moved = {k: round(fitted[k], 3) for k in sorted(covered)}
    for k in sorted(moved, key=lambda k: moved[k] / H[k]):
        if abs(moved[k] / H[k] - 1) > 0.005:
            print(f"      {k:7s} {H[k]:.2f} -> {moved[k]:.2f}")
    ok = len(crows) >= MIN_HOLDOUT and pw <= MAX_P_WORSE and -mu >= MIN_GAIN
    if not ok:
        print("  gates not passed; europe.json unchanged")
        return 0
    if dry:
        print("  gates passed (dry run, nothing written)")
        return 0
    json.dump({"strength": moved, "lambda": lam, "fitted": fs, "checked": cs,
               "written": _date.today().isoformat(),
               "check": {"n": len(crows), "delta": round(mu, 4), "sd": round(sd, 4),
                         "pWorse": round(pw, 3), "correct": round(sum(h) / len(h), 4)}},
              open(OUT, "w"), indent=1, sort_keys=True)
    print(f"  gates passed; wrote {os.path.basename(OUT)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.fit:
        sys.exit(do_fit(a.dry_run))
    report()
