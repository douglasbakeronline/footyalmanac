#!/usr/bin/env python3
"""Championship (en.2): is the model's total-goals level off? Scale both
expected-goal rates by a constant before the grid, raw output into the live
curve, paired bootstrap against the live configuration. History only;
record.json is never read. See claude/championship-goals-scale-2026-10-29.md.

    python3 tools/championship_goals_scale.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

SEASONS = {"2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}


def rows(s):
    r, ok = S.fetch_season("en.2", s, None)
    return r if ok else []


def outcome_of(m):
    return 0 if m[3] > m[4] else 1 if m[3] == m[4] else 2


def main():
    base = T.live_baseline()
    print("live", T.describe(base))
    for test_s, prior_s in SEASONS.items():
        prior, test = rows(prior_s), rows(test_s)
        if not prior or not test:
            print(test_s, "unavailable"); continue
        rep = list(R.replay_league(prior, test, 2))
        pg = sum(lh + la for _, lh, la, _ in rep) / len(rep)
        ag = sum(m[3] + m[4] for m, _, _, _ in rep) / len(rep)
        ref_raw = [T.outcome(lh, la, E.RHO) + (outcome_of(m),) for m, lh, la, _ in rep]
        ref, acc0, _ = T.score_under(ref_raw, base)
        print(f"\n== {test_s}: n={len(ref)} ll {T.mean(ref):.4f} acc {acc0:.3f} "
              f"pred goals {pg:.2f} actual {ag:.2f}")
        for s in (0.90, 0.95, 1.05, 1.10):
            raws = [T.outcome(lh * s, la * s, E.RHO) + (outcome_of(m),) for m, lh, la, _ in rep]
            per, acc, _ = T.score_under(raws, base)
            d, sd, pw = T.paired(per, ref)
            print(f"  scale {s:.2f}  delta {d:+.4f}  p(worse) {pw:.3f}  acc {acc:.3f}")


if __name__ == "__main__":
    main()
