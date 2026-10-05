"""Evaluation harness, step 2: paired comparison of baseline and candidate.

Runs from main (trusted). Reads the two prediction files, requires identical
fixture keys and outcomes, and scores both with the same code: log loss,
Brier score, accuracy, and a paired bootstrap of the per-fixture log-loss
difference. The verdict uses the CLAUDE.md gates on the check split; anything
short of clear evidence is "insufficient", which the merge gate treats as hold.

    python3 evaluation/score_pair.py --base B.jsonl --cand C.jsonl --out evidence.json --summary summary.md \
        [--meta-base MB.json --meta-cand MC.json --context ctx.json]
"""
import argparse, json, math, random

GATES = {"min_check": 250, "max_p_worse": 0.30, "min_gain": 0.0005, "fit_max_p_worse": 0.50}
BOOT = {"B": 2000, "seed": 20261003}


def load(path):
    out = {}
    with open(path) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r["key"] in out:
                    raise ValueError(f"duplicate fixture key {r['key']}")
                out[r["key"]] = r
    return out


def metrics(rows):
    n = len(rows)
    if not n:
        return {"n": 0}
    ll = sum(-math.log(max(r["p"][r["y"]], 1e-12)) for r in rows) / n
    br = sum(sum((r["p"][j] - (j == r["y"])) ** 2 for j in range(3)) for r in rows) / n
    acc = sum(r["p"].index(max(r["p"])) == r["y"] for r in rows) / n
    return {"n": n, "logLoss": ll, "brier": br, "accuracy": acc}


def paired(base_rows, cand_rows, B=BOOT["B"], seed=BOOT["seed"]):
    """Per-fixture log-loss gain (base - cand; positive = candidate better), bootstrapped."""
    d = [-math.log(max(b["p"][b["y"]], 1e-12)) + math.log(max(c["p"][c["y"]], 1e-12))
         for b, c in zip(base_rows, cand_rows)]
    n = len(d)
    if not n:
        return {"n": 0}
    mean = sum(d) / n
    if all(abs(x) < 1e-12 for x in d):
        return {"n": n, "gain": 0.0, "ci95": [0.0, 0.0], "p_worse": None, "identical": True}
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        s = 0.0
        for _ in range(n):
            s += d[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    return {"n": n, "gain": mean, "ci95": [means[int(0.025 * B)], means[int(0.975 * B) - 1]],
            "p_worse": sum(m < 0 for m in means) / B, "identical": False}


def compare(base, cand):
    """Dict of per-split results plus the verdict and its reasons."""
    reasons = []
    kb, kc = set(base), set(cand)
    if kb != kc:
        reasons.append(f"fixture keys differ: {len(kb - kc)} only in baseline, {len(kc - kb)} only in candidate")
        return {"verdict": "insufficient", "reasons": reasons,
                "key_diff": {"base_only": sorted(kb - kc)[:20], "cand_only": sorted(kc - kb)[:20]}}
    bad_y = [k for k in kb if base[k]["y"] != cand[k]["y"]]
    if bad_y:
        return {"verdict": "insufficient", "reasons": [f"{len(bad_y)} fixtures have different outcomes"]}
    out = {"splits": {}}
    for split in ("fit", "check"):
        keys = sorted(k for k in kb if base[k]["split"] == split)
        b = [base[k] for k in keys]; c = [cand[k] for k in keys]
        out["splits"][split] = {"baseline": metrics(b), "candidate": metrics(c), "paired": paired(b, c)}
    chk, fit = out["splits"]["check"]["paired"], out["splits"]["fit"]["paired"]
    if chk.get("n", 0) and chk.get("identical") and fit.get("identical", True):
        out.update(verdict="n/a", reasons=["candidate predictions are identical to the baseline on the snapshot"])
        return out
    if chk.get("n", 0) < GATES["min_check"]:
        reasons.append(f"only {chk.get('n', 0)} check fixtures (need {GATES['min_check']})")
    else:
        if chk["gain"] < 0 and (chk["p_worse"] or 0) >= 1 - GATES["max_p_worse"]:
            out.update(verdict="fail", reasons=[f"check log loss worse by {-chk['gain']:.4f}, p(worse) {chk['p_worse']:.2f}"])
            return out
        if (chk["p_worse"] if chk["p_worse"] is not None else 1) > GATES["max_p_worse"]:
            reasons.append(f"check p(worse) {chk['p_worse']:.2f} > {GATES['max_p_worse']}")
        if chk["gain"] < GATES["min_gain"]:
            reasons.append(f"check gain {chk['gain']:.4f} < {GATES['min_gain']}")
        if fit.get("n") and fit.get("p_worse") is not None and fit["p_worse"] > GATES["fit_max_p_worse"]:
            reasons.append(f"worse on the fit split too (p(worse) {fit['p_worse']:.2f})")
    out.update(verdict="pass" if not reasons else "insufficient", reasons=reasons or ["all gates passed"])
    return out


def summary_md(ev):
    lines = [f"### Evaluation: **{ev['verdict']}**", ""]
    lines += [f"- {r}" for r in ev.get("reasons", [])]
    c = ev.get("context", {})
    lines += ["", f"Baseline `{(c.get('base_sha') or '')[:7]}` vs candidate `{(c.get('candidate_sha') or '')[:7]}` · "
              f"snapshot `{(c.get('snapshot_sha256') or 'none')[:12]}` · gates {json.dumps(GATES)} · bootstrap {json.dumps(BOOT)}"]
    for split, s in (ev.get("splits") or {}).items():
        b, k, p = s["baseline"], s["candidate"], s["paired"]
        if not b.get("n"):
            continue
        lines += ["", f"**{split}** · {b['n']} fixtures", "",
                  "| | log loss | Brier | accuracy |", "|---|---|---|---|",
                  f"| baseline | {b['logLoss']:.4f} | {b['brier']:.4f} | {b['accuracy']:.1%} |",
                  f"| candidate | {k['logLoss']:.4f} | {k['brier']:.4f} | {k['accuracy']:.1%} |", "",
                  (f"Paired log-loss gain {p['gain']:+.4f} (95% {p['ci95'][0]:+.4f} to {p['ci95'][1]:+.4f}), p(worse) {p['p_worse']:.2f}"
                   if p.get("p_worse") is not None else "Predictions identical.")]
    lines += ["", "Evidence only: nothing was refitted, applied or deployed. Raw data stays in the private snapshot store."]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--cand", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--summary", required=True)
    ap.add_argument("--meta-base"); ap.add_argument("--meta-cand"); ap.add_argument("--context")
    a = ap.parse_args()
    ev = compare(load(a.base), load(a.cand))
    ctx = json.load(open(a.context)) if a.context else {}
    mb = json.load(open(a.meta_base)) if a.meta_base else {}
    mc = json.load(open(a.meta_cand)) if a.meta_cand else {}
    if mb.get("snapshot_sha256") != mc.get("snapshot_sha256"):
        ev.update(verdict="insufficient", reasons=ev.get("reasons", []) + ["baseline and candidate used different snapshots"])
    ctx["snapshot_sha256"] = mb.get("snapshot_sha256")
    ev.update(context=ctx, gates=GATES, bootstrap=BOOT, params={"base": mb, "candidate": mc},
              base_sha=ctx.get("base_sha"), candidate_sha=ctx.get("candidate_sha"))
    with open(a.out, "w") as f:
        json.dump(ev, f, indent=1)
    with open(a.summary, "w") as f:
        f.write(summary_md(ev))
    print(ev["verdict"])


if __name__ == "__main__":
    main()
