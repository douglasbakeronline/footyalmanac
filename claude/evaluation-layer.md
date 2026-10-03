# Evaluation layer and hardened merge gate (3 Oct 2026)

This automates the evaluation method developed in the 2 Oct review (shared replay, frozen snapshots,
paired comparisons). Human review of the evidence stays separate and is still required for model changes.

## Why
- Agent pull requests were opened with the workflow token, so GitHub never ran `Tests` on them.
- The merge gate trusted `checks-passed` and `auto-merge-ok` labels that the agent workflow set itself.
- Nothing pinned the commit being merged, checked that CI was fresh, or required approval of the exact commit.

## Merge gate (`agents/merge_gate.py`, policy `agents/policy.json`)
`decide()` is pure and tested in `tests/test_merge_gate.py` (22 cases). A pull request merges only if all of these hold:

- **Required checks** (`test (3.12)`, `test (3.13)`, `evaluation`): the newest run of each, from the GitHub
  Actions app (id 15368), for the current head SHA, completed with `success`. Missing, pending,
  neutral, skipped, cancelled or failed all hold.
- **Evaluation evidence:**
  - `evidence.json` is downloaded from the artifact of the newest successful `evaluation.yml` run for that SHA
  - `candidate_sha` must equal the head
  - the verdict must be `pass` or `n/a`
- **Mergeability:** `mergeable == MERGEABLE`, re-queried while UNKNOWN. A merge state of
  DIRTY, BLOCKED, BEHIND or UNKNOWN holds.
- **Base drift:** every `main` commit since the evidence's `base_sha` touches only bot paths. Otherwise re-run the evaluation.
- **Owner approval:** any class other than `docs` (including unknown paths) needs an APPROVED review whose
  user is the owner, `author_association == OWNER` and `commit_id ==` head. Bot reviews never count.
- **Age** of at least 12 hours. A `hold` label always holds.
- **Pinned merge:** `gh pr merge --squash --match-head-commit <sha>`.

## Evaluation (`.github/workflows/evaluation.yml`)
1. **Check out** main into `base/` (trusted harness and policy) and the pull request head into `cand/`.
   Neither keeps credentials.
2. **Classify** the changed paths with main's policy. With no model or calibration change, the verdict is `n/a`.
3. **Fetch** the last approved snapshot from the private store with a read-only token, available to that step only.
   Verify its sha256 with main's code against `approved-snapshots.json`.
4. **Predict:** `evaluation/predict.py` (main) imports each checkout's `tune` and `engine` and prices every
   fixture of the snapshot through `tune.lambdas` (the shared walk-forward replay) with that checkout's
   shipped calibration. It runs under `unshare --net` with an empty environment. The output is key, probabilities and outcome only.
5. **Score:** `evaluation/score_pair.py` (main):
   - keys and outcomes must match exactly
   - log loss, Brier and accuracy for both
   - paired bootstrap of the per-fixture log-loss gain (B 2000, seed 20261003)
   - verdict on the check split by the Rule 3 gates (≥250 fixtures, p(worse) ≤ 0.30, gain ≥ 0.0005),
     and the candidate must not be worse on the fit split (p(worse) ≤ 0.50)
   - anything short of that is `insufficient`, which is a hold
6. **Publish:** upload `evidence.json` and `summary.md` (metrics only) as the artifact `evaluation-evidence`.
   Update one pull request comment. The check is green only for `pass` or `n/a`.

## Snapshots
- `evaluation-freeze.yml` is manual and owner only. It runs `replay.py --freeze` and stores `snapshot.json` as a release in the private
  repo `douglasbakeronline/footyalmanac-eval-data`. Raw rows include API-Football and ESPN data, whose
  redistribution terms are uncertain, so they never go to this public repo or its artifacts.
- The workflow then opens a pull request adding the snapshot to `evaluation/approved-snapshots.json`. Merging it is the approval.

## Limits (be honest about them)
- The candidate computes its own probabilities in-process, so a malicious change could read outcomes from
  the snapshot. Running it offline, scoring with main's code and requiring owner approval for model
  changes reduce this but do not remove it. Treat the evidence as evidence, not proof.
- Changes that do not act through `tune.lambdas`, `tune.outcome` or the shipped calibration (for example
  Daily List selection in `build.py`) show `n/a` when the predictions are identical. They still need owner approval.
- Until the `footyalmanac-office` GitHub App secrets exist, agent pull requests get no checks and are held.
