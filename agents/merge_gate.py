"""Office agents: merge window, failing closed.

A pull request labelled office-agent merges only if every condition holds for
its CURRENT head commit (see decide()). Labels are never evidence: checks are
read from the check-runs API for the head SHA, evaluation evidence from the
artifact of the verified evaluation run, approvals from the owner's reviews
of that exact commit. Anything missing, pending, failed, skipped, neutral or
unknown holds the pull request. The merge is pinned with --match-head-commit.

    python3 agents/merge_gate.py            # run the merge window
    python3 agents/merge_gate.py --dry-run  # decide and report, merge nothing
    python3 agents/merge_gate.py --pr 12 --wait --no-deploy   # the sprint: one pull request,
                                            # waiting for its checks to finish first
"""
import argparse, io, json, os, subprocess, sys, time, zipfile
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("GITHUB_REPOSITORY", "douglasbakeronline/footyalmanac")


def load_policy(path=os.path.join(HERE, "policy.json")):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# pure decision logic (tested in tests/test_merge_gate.py)
# ---------------------------------------------------------------------------

def classify(path, policy):
    """Every class a path belongs to. Unknown paths get 'unknown'."""
    hit = [c for c, prefixes in policy["classes"].items()
           if any(path == p or path.startswith(p) for p in prefixes)]
    return hit or ["unknown"]


def classes_for(files, policy):
    out = set()
    for f in files:
        out.update(classify(f, policy))
    return out


def latest_checks(check_runs, sha, policy):
    """Newest run per required name, trusting only the GitHub Actions app and this SHA."""
    best = {}
    for c in check_runs:
        if c.get("name") not in policy["required_checks"]:
            continue
        if (c.get("app") or {}).get("id") != policy["actions_app_id"] or c.get("head_sha") != sha:
            continue
        key = c.get("started_at") or ""
        if c["name"] not in best or key > (best[c["name"]].get("started_at") or ""):
            best[c["name"]] = c
    return best


def decide(pr, check_runs, reviews, policy, now, evidence=None, main_commits_since_base=None):
    """(merge: bool, reasons: list[str]). Fails closed.

    pr: {number, headRefOid, createdAt, labels:[names], files:[paths], mergeable, mergeStateStatus}
    check_runs: check runs for the head SHA, as the API returns them
    reviews: PR reviews, as the API returns them
    evidence: evaluation evidence.json from the verified evaluation run, or None
    main_commits_since_base: [{"sha", "files": [paths]}] on main after the evidence's base SHA, or None if unknown
    """
    reasons = []
    sha = pr.get("headRefOid")
    if not sha:
        return False, ["no head SHA"]
    labels = set(pr.get("labels") or [])
    if "office-agent" not in labels:
        reasons.append("not an office-agent pull request")
    if "hold" in labels:
        reasons.append("on hold")
    files = pr.get("files") or []
    if not files:
        reasons.append("no changed files reported")
    try:
        made = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
        if now - made < timedelta(hours=policy["min_age_hours"]):
            reasons.append(f"younger than {policy['min_age_hours']} hours")
    except Exception:
        reasons.append("unknown age")

    # 1. required checks on this exact SHA, from GitHub Actions, completed and successful
    best = latest_checks(check_runs or [], sha, policy)
    for name in policy["required_checks"]:
        c = best.get(name)
        if not c:
            reasons.append(f"check '{name}' missing for {sha[:7]}")
        elif c.get("status") != "completed":
            reasons.append(f"check '{name}' is {c.get('status')}")
        elif c.get("conclusion") != "success":
            reasons.append(f"check '{name}' concluded {c.get('conclusion')}")

    # 2. mergeability confirmed
    if pr.get("mergeable") != "MERGEABLE":
        reasons.append(f"mergeable is {pr.get('mergeable')}")
    if pr.get("mergeStateStatus") in ("DIRTY", "BLOCKED", "BEHIND", "UNKNOWN", None):
        reasons.append(f"merge state is {pr.get('mergeStateStatus')}")

    # 3. evaluation evidence for this SHA, and no non-bot drift on main since its base
    if evidence is None:
        reasons.append("no evaluation evidence")
    else:
        if evidence.get("candidate_sha") != sha:
            reasons.append("evaluation evidence is for another commit")
        if evidence.get("verdict") not in ("pass", "n/a"):
            reasons.append(f"evaluation verdict is {evidence.get('verdict')}")
        if main_commits_since_base is None:
            reasons.append("cannot confirm main has not moved since the evaluation base")
        else:
            bot = policy["bot_paths"]
            drift = [c["sha"][:7] for c in main_commits_since_base
                     if not c.get("files") or any(not any(f == b or f.startswith(b) for b in bot) for f in c["files"])]
            if drift:
                reasons.append("main changed since evaluation (" + ", ".join(drift[:3]) + "): re-run evaluation")

    # 4. model and calibration changes need a passing evaluation, not just n/a
    cls = classes_for(files, policy)
    if cls & set(policy.get("model_classes", [])) and (evidence or {}).get("verdict") != "pass":
        reasons.append("model or calibration change without an evaluation pass")

    # 5. owner approval of this exact commit, where the change needs it (workflow/security only)
    needs_owner = bool(cls - set(policy["auto_merge_classes"]))
    if needs_owner:
        ok = any(r.get("state") == "APPROVED" and (r.get("user") or {}).get("login") == policy["owner"]
                 and r.get("author_association") == "OWNER" and r.get("commit_id") == sha
                 for r in reviews or [])
        if not ok:
            reasons.append("needs owner approval of " + sha[:7] + " (" + ", ".join(sorted(cls)) + ")")
    return (not reasons), reasons


# ---------------------------------------------------------------------------
# GitHub I/O
# ---------------------------------------------------------------------------

def gh(args, check=False):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r


def api(path):
    r = gh(["api", "-H", "Accept: application/vnd.github+json", path])
    if r.returncode:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def pr_state(n, policy):
    fields = "number,headRefOid,createdAt,labels,files,mergeable,mergeStateStatus,baseRefName"
    for i in range(policy["mergeable_retries"]):
        r = gh(["pr", "view", str(n), "--json", fields])
        if r.returncode:
            return None
        p = json.loads(r.stdout)
        if p.get("mergeable") != "UNKNOWN":
            break
        time.sleep(5 * (i + 1))
    p["labels"] = [l["name"] for l in p.get("labels", [])]
    p["files"] = [f["path"] for f in p.get("files", [])]
    return p


def evidence_for(sha, policy):
    """evidence.json from the newest successful evaluation run for this SHA, or None."""
    runs = (api(f"repos/{REPO}/actions/workflows/{os.path.basename(policy['evaluation_workflow'])}/runs?head_sha={sha}&per_page=20") or {})
    runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
    runs = [r for r in runs if r.get("head_sha") == sha and r.get("path", "").startswith(policy["evaluation_workflow"])
            and r.get("status") == "completed" and r.get("conclusion") == "success"]
    if not runs:
        return None
    run = max(runs, key=lambda r: r.get("created_at", ""))
    arts = (api(f"repos/{REPO}/actions/runs/{run['id']}/artifacts") or {}).get("artifacts", [])
    art = next((a for a in arts if a["name"] == policy["evaluation_artifact"] and not a.get("expired")), None)
    if not art:
        return None
    r = subprocess.run(["gh", "api", f"repos/{REPO}/actions/artifacts/{art['id']}/zip"], capture_output=True)
    if r.returncode:
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(r.stdout)) as z:
            ev = json.loads(z.read("evidence.json"))
    except Exception:
        return None
    ev["_run"] = run.get("html_url")
    return ev


def main_commits_since(base_sha):
    if not base_sha:
        return None
    cmp = api(f"repos/{REPO}/compare/{base_sha}...main")
    if not isinstance(cmp, dict) or cmp.get("status") not in ("ahead", "identical"):
        return None
    out = []
    for c in cmp.get("commits", []):
        d = api(f"repos/{REPO}/commits/{c['sha']}") or {}
        out.append({"sha": c["sha"], "files": [f["filename"] for f in d.get("files", [])]})
    return out


def wait_for_checks(n, policy):
    """Wait until every required check on the head SHA has completed (or the wait runs out)."""
    deadline = time.time() + 60 * policy.get("check_wait_minutes", 45)
    while time.time() < deadline:
        sha = (pr_state(n, policy) or {}).get("headRefOid")
        runs = (api(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100") or {}) if sha else {}
        best = latest_checks(runs.get("check_runs", []) if isinstance(runs, dict) else [], sha, policy)
        done = [k for k, c in best.items() if c.get("status") == "completed"]
        print(f"#{n}: {len(done)} of {len(policy['required_checks'])} required checks finished")
        if len(done) == len(policy["required_checks"]):
            # the evaluation artifact is uploaded just before its check completes; give it a moment
            time.sleep(20); return
        time.sleep(30)


def comment(n, body):
    gh(["pr", "comment", str(n), "--body", body])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pr", default="")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--no-deploy", action="store_true")
    a = ap.parse_args()
    policy = load_policy()
    if a.pr:
        r = gh(["pr", "view", a.pr, "--json", "number,title,state"])
        one = json.loads(r.stdout or "{}") if r.returncode == 0 else {}
        prs = [one] if one.get("state") == "OPEN" else []
        if a.wait and prs:
            wait_for_checks(int(a.pr), policy)
    else:
        lst = gh(["pr", "list", "--label", "office-agent", "--state", "open", "-L", "30", "--json", "number,title"])
        prs = json.loads(lst.stdout or "[]") if lst.returncode == 0 else []
    now = datetime.now(timezone.utc)
    merged, report = [], []
    for item in prs:
        n = item["number"]
        pr = pr_state(n, policy)
        if not pr:
            report.append({"pr": n, "merge": False, "reasons": ["could not read pull request"]}); continue
        sha = pr["headRefOid"]
        checks = (api(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100") or {})
        checks = checks.get("check_runs", []) if isinstance(checks, dict) else []
        reviews = api(f"repos/{REPO}/pulls/{n}/reviews?per_page=100") or []
        ev = evidence_for(sha, policy)
        drift = main_commits_since(ev.get("base_sha")) if ev else None
        ok, reasons = decide(pr, checks, reviews, policy, now, ev, drift)
        report.append({"pr": n, "sha": sha[:7], "merge": ok, "reasons": reasons})
        print(f"#{n} {sha[:7]}: {'MERGE' if ok else 'hold'}" + ("" if ok else " - " + "; ".join(reasons)))
        if a.dry_run:
            continue
        if not ok:
            body = f"<!-- office-gate -->\n**Office merge window: held** at `{sha[:7]}`\n\n" + "\n".join(f"- {r}" for r in reasons)
            prev = [c for c in (api(f"repos/{REPO}/issues/{n}/comments?per_page=100") or []) if "<!-- office-gate -->" in c.get("body", "")]
            if not prev or prev[-1]["body"].strip() != body.strip():
                comment(n, body)
            continue
        r = gh(["pr", "merge", str(n), "--squash", "--delete-branch", "--match-head-commit", sha])
        if r.returncode == 0:
            merged.append(item)
            comment(n, f"Merged by the office merge window at `{sha[:7]}`: required checks green on this commit, "
                       f"evaluation {ev.get('verdict')} ({ev.get('_run')}), mergeable, no owner review needed for this class. "
                       "Roll back with `git revert` on the squash commit.")
        else:
            print(f"#{n} merge refused: {r.stderr.strip()}")
    os.makedirs("/tmp/office-gate", exist_ok=True)
    with open("/tmp/office-gate/report.json", "w") as f:
        json.dump({"time": now.isoformat(), "decisions": report}, f, indent=1)
    if merged and not a.dry_run:
        subprocess.run(["git", "pull", "-q"]); subprocess.run(["git", "fetch", "-q", "--tags"])
        day = now.strftime("%Y-%m-%d")
        tags = subprocess.run(["git", "tag", "-l", f"release-{day}*"], capture_output=True, text=True).stdout.split()
        tag = f"release-{day}" + (f"-{len(tags)+1}" if tags else "")
        msg = "Office agents: " + "; ".join(f"#{p['number']} {p['title']}" for p in merged)
        subprocess.run(["git", "-c", "user.name=footyalmanac-hq[bot]", "-c",
                        "user.email=41898282+github-actions[bot]@users.noreply.github.com", "tag", "-a", tag, "-m", msg])
        tok = os.environ.get("GH_TOKEN")
        dest = f"https://x-access-token:{tok}@github.com/{REPO}.git" if tok else "origin"
        subprocess.run(["git", "push", "-q", dest, tag])
        if not a.no_deploy:
            gh(["workflow", "run", "deploy.yml"])
        print("Tagged", tag, "" if a.no_deploy else "and started a deploy")


if __name__ == "__main__":
    main()
