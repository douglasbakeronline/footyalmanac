#!/usr/bin/env python3
"""
Surface-aware Elo ratings for ATP and WTA singles, built and validated the
same way as every other rating system in this project: real historical data,
constants chosen on one holdout and never touched again, a final check on
data neither the fit nor the constant search ever saw.

    python3 tune_tennis.py --report        fit, validate, print, write nothing
    python3 tune_tennis.py --fit            as above, write tennis.json if it PASSES
    python3 tune_tennis.py --fit --dry-run  fit and print the verdict, write nothing regardless

Why Elo and not the Dixon-Coles Poisson model everywhere else in this project
-------------------------------------------------------------------------
Every other sport here is a team scoring goals against another team, which a
shared-average attack/defence model fits naturally. Tennis is one player
against another with no draws and no "goals" — the natural unit of evidence
is just "this player beat that player", which is exactly what Elo was built
for. It's also the standard the tennis analytics community already
converged on (this is the same shape of model FiveThirtyEight and Jeff
Sackmann's own published tennis Elo use), so this isn't a novel design,
just one tested here against this project's own data rather than assumed.

Data
----
A maintained mirror of Jeff Sackmann's ATP/WTA match files (the originals
moved), match-level, back to 2000, current through 2026. Walkovers are
dropped outright (no tennis was played); retirements are kept but
down-weighted, a choice that is swept below rather than assumed, the same
as every other weighting decision in this project.

Method
------
Two Elo ratings per player: an overall rating and a per-surface rating
(Hard / Clay / Grass), blended for the surface the match is actually on.
K-factor shrinks as a player accumulates matches (Sackmann's own dynamic-K
shape: K = k_base / (matches_played + 5)^0.4), so a newcomer's rating moves
fast and an established player's moves slowly. Because Elo only ever uses
information strictly before the match it's predicting, there's no separate
"fit" step to leak future information — the walk-forward discipline is
built into the model itself. What still needs a genuine held-out check is
the CONSTANTS (surface_weight, k_base, retirement_weight): those are swept
against 2025 only, then locked and checked once, cleanly, against 2026 —
data the constant search never saw.

Standard library only, like the rest of the project.
"""
import argparse, csv, io, json, math, os, random, sys, urllib.request
from datetime import date as _date

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main"
YEARS = list(range(2019, 2027))
TUNE_YEAR = "2025"
CHECK_YEAR = "2026"

MIN_HOLDOUT = 500
MAX_P_WORSE = 0.05   # the strictest bar of any tool this project has built —
                      # a brand new sport, brand new model, deserves it
MIN_GAIN = 0.005

SWEEP = {"surface_weight": [0.3, 0.5, 0.7],
         "k_base": [150, 250],
         "retirement_weight": [0.5, 1.0]}


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

def fetch(path, cache_dir):
    fp = os.path.join(cache_dir, path.replace("/", "_"))
    if os.path.exists(fp):
        return open(fp, encoding="utf-8", errors="replace").read()
    req = urllib.request.Request(f"{RAW}/{path}", headers={"User-Agent": "footyalmanac-tune"})
    text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    os.makedirs(cache_dir, exist_ok=True)
    open(fp, "w", encoding="utf-8").write(text)
    return text


def load_tour(tour, cache_dir):
    rows = []
    for y in YEARS:
        try:
            text = fetch(f"{tour}/{tour}_matches_{y}.csv", cache_dir)
        except Exception:
            continue
        for r in csv.DictReader(io.StringIO(text)):
            score = r.get("score") or ""
            if not score or "W/O" in score or "Walkover" in score:
                continue
            if not r.get("winner_name") or not r.get("loser_name"):
                continue
            try:
                int(r["best_of"])
            except (KeyError, ValueError):
                continue
            rows.append({
                "date": r["tourney_date"], "surface": r["surface"] or "Hard",
                "level": r["tourney_level"], "winner": r["winner_name"],
                "loser": r["loser_name"], "retired": " RET" in score,
                "w_rank": r.get("winner_rank"), "l_rank": r.get("loser_rank"),
            })
    rows.sort(key=lambda x: x["date"])
    return rows


# ---------------------------------------------------------------------------
# Elo
# ---------------------------------------------------------------------------

def dynamic_k(matches_played, k_base):
    return k_base / ((matches_played + 5) ** 0.4)


def run_elo(matches, surface_weight, k_base, retirement_weight, start=1500.0):
    """Returns per-match pre-match log-loss (the winner's predicted
    probability, log-scored) plus the final overall/surface ratings."""
    overall, surf, n_matches = {}, {}, {}
    losses = []
    for m in matches:
        w, l, s = m["winner"], m["loser"], m["surface"]
        ow, ol = overall.setdefault(w, start), overall.setdefault(l, start)
        sw, sl = surf.setdefault((w, s), start), surf.setdefault((l, s), start)

        bw = (1 - surface_weight) * ow + surface_weight * sw
        bl = (1 - surface_weight) * ol + surface_weight * sl
        p_w = 1.0 / (1.0 + 10 ** ((bl - bw) / 400.0))
        losses.append(-math.log(max(p_w, 1e-12)))

        nw, nl = n_matches.get(w, 0), n_matches.get(l, 0)
        kw, kl = dynamic_k(nw, k_base), dynamic_k(nl, k_base)
        wt = retirement_weight if m["retired"] else 1.0

        e_ow = 1.0 / (1.0 + 10 ** ((ol - ow) / 400.0))
        overall[w] = ow + kw * wt * (1 - e_ow)
        overall[l] = ol + kl * wt * (0 - (1 - e_ow))
        e_sw = 1.0 / (1.0 + 10 ** ((sl - sw) / 400.0))
        surf[(w, s)] = sw + kw * wt * (1 - e_sw)
        surf[(l, s)] = sl + kl * wt * (0 - (1 - e_sw))
        n_matches[w], n_matches[l] = nw + 1, nl + 1

    return losses, overall, surf, n_matches


def rank_baseline_loss(m, p_favorite=0.65):
    try:
        wr, lr = float(m["w_rank"]), float(m["l_rank"])
    except (TypeError, ValueError):
        return -math.log(0.5)
    if wr == lr:
        return -math.log(0.5)
    p = p_favorite if wr < lr else (1 - p_favorite)
    return -math.log(max(p, 1e-9))


def paired(a, b, reps=2000, seed=17):
    rng = random.Random(seed)
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    means = [sum(diff[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    mu = sum(diff) / n
    return mu, sum(1 for x in means if x > 0) / len(means)


def tune_and_validate(matches, verbose, label):
    tune_idx = [i for i, m in enumerate(matches) if m["date"].startswith(TUNE_YEAR)]
    final_idx = [i for i, m in enumerate(matches) if m["date"].startswith(CHECK_YEAR)]

    best = None
    for sw in SWEEP["surface_weight"]:
        for kb in SWEEP["k_base"]:
            for rw in SWEEP["retirement_weight"]:
                losses, *_ = run_elo(matches, sw, kb, rw)
                loss = sum(losses[i] for i in tune_idx) / len(tune_idx)
                if best is None or loss < best[0]:
                    best = (loss, sw, kb, rw)
    _, sw, kb, rw = best

    losses, overall, surf, n_matches = run_elo(matches, sw, kb, rw)
    check_losses = [losses[i] for i in final_idx]
    hit = sum(1 for i in final_idx if losses[i] < -math.log(0.5))
    base_losses = [rank_baseline_loss(matches[i]) for i in final_idx]
    m_delta, pw = paired(check_losses, base_losses)

    verdict = {
        "tour": label, "trainMatches": len(matches) - len(final_idx),
        "checkMatches": len(final_idx), "constants": {"surfaceWeight": sw, "kBase": kb, "retirementWeight": rw},
        "checkLogLoss": {"baseline": round(sum(base_losses)/len(base_losses), 4),
                          "elo": round(sum(check_losses)/len(check_losses), 4),
                          "delta": round(m_delta, 4), "pWorse": round(pw, 3)},
        "checkAccuracy": round(hit / len(final_idx), 4),
        "gates": {"enoughData": len(final_idx) >= MIN_HOLDOUT,
                  "notWorse": pw <= MAX_P_WORSE, "worthIt": -m_delta >= MIN_GAIN},
    }
    verdict["pass"] = all(verdict["gates"].values())

    if verbose:
        print(f"\n{label}: {len(matches)} matches, constants chosen on {TUNE_YEAR} "
              f"(surface_weight={sw}, k_base={kb}, retirement_weight={rw})")
        c = verdict["checkLogLoss"]
        print(f"  clean {CHECK_YEAR} check (n={verdict['checkMatches']}, never touched by tuning):")
        print(f"    log loss  rank-baseline {c['baseline']}  ->  Elo {c['elo']}  "
              f"({c['delta']:+.4f}, p(worse) {c['pWorse']:.1%})")
        print(f"    accuracy  {verdict['checkAccuracy']:.2%}")
        for k, v in verdict["gates"].items():
            print(f"    {'PASS' if v else 'FAIL'}  {k}")

    ratings = {p: {"overall": round(e, 1),
                    **{f"surface_{s}": round(v, 1) for (pl, s), v in surf.items() if pl == p},
                    "matches": n_matches.get(p, 0)}
               for p, e in overall.items()}
    return verdict, ratings, {"surfaceWeight": sw, "kBase": kb, "retirementWeight": rw}


def run(cache_dir, verbose=True):
    out = {}
    for tour, label in (("atp", "ATP"), ("wta", "WTA")):
        matches = load_tour(tour, cache_dir)
        verdict, ratings, constants = tune_and_validate(matches, verbose, label)
        out[tour] = {"verdict": verdict, "ratings": ratings, "constants": constants}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cache", default=os.path.join(HERE, ".tenniscache"))
    args = ap.parse_args()
    if not (args.report or args.fit):
        ap.error("nothing to do: pass --report or --fit")

    result = run(args.cache)
    both_pass = all(result[t]["verdict"]["pass"] for t in ("atp", "wta"))

    if args.fit:
        out = os.path.join(HERE, "tennis.json")
        if args.dry_run:
            print("\ndry run, nothing written")
        elif both_pass:
            payload = {"generated": _date.today().isoformat(),
                       "atp": {"constants": result["atp"]["constants"], "ratings": result["atp"]["ratings"]},
                       "wta": {"constants": result["wta"]["constants"], "ratings": result["wta"]["ratings"]}}
            json.dump(payload, open(out, "w"), separators=(",", ":"))
            print(f"\nwrote {os.path.basename(out)} — {len(result['atp']['ratings'])} ATP + "
                  f"{len(result['wta']['ratings'])} WTA players rated")
        else:
            failed = {t: [k for k, v in result[t]["verdict"]["gates"].items() if not v]
                      for t in ("atp", "wta") if not result[t]["verdict"]["pass"]}
            print(f"\nnot written: failed gates {failed}")
            json.dump({t: result[t]["verdict"] for t in result},
                      open(os.path.join(HERE, "tennis-report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
