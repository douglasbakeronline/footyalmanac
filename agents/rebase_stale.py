#!/usr/bin/env python3
"""
Rebase every open office-agent pull request that is behind main, so its
checks and evaluation run again and the merge gate can judge it fresh
(5 Nov 2026, Douglas). Run by office-merge.yml with the App token before
agents/merge_gate.py; pushes with --force-with-lease to the agent's branch
only. A branch that does not rebase cleanly is left as it is, with one
comment saying so. Never touches main. Standard library only.
"""
import json, os, subprocess, sys

REPO = os.environ.get("GITHUB_REPOSITORY", "douglasbakeronline/footyalmanac")
PREFIX = "office-agent/"


def sh(*args, check=True, **kw):
    return subprocess.run(args, text=True, capture_output=True, check=check, **kw)


def gh_json(path):
    r = sh("gh", "api", path, check=False)
    try:
        return json.loads(r.stdout) if r.returncode == 0 else None
    except ValueError:
        return None


def main():
    prs = gh_json(f"repos/{REPO}/pulls?state=open&per_page=100") or []
    mine = [p for p in prs if (p.get("head") or {}).get("ref", "").startswith(PREFIX)
            and (p.get("head") or {}).get("repo", {}).get("full_name") == REPO]
    if not mine:
        print("no open office-agent pull requests"); return 0
    sh("git", "config", "user.name", "footyalmanac-office[bot]")
    sh("git", "config", "user.email", "footyalmanac-office[bot]@users.noreply.github.com")
    sh("git", "fetch", "origin", "main")
    token = os.environ.get("GH_TOKEN", "")
    push_url = f"https://x-access-token:{token}@github.com/{REPO}.git"
    for p in mine:
        n, br = p["number"], p["head"]["ref"]
        sh("git", "fetch", "origin", br)
        behind = sh("git", "rev-list", "--count", f"origin/{br}..origin/main", check=False).stdout.strip()
        if behind in ("", "0"):
            print(f"#{n} {br}: up to date"); continue
        sh("git", "checkout", "-q", "-B", br, f"origin/{br}")
        r = sh("git", "rebase", "origin/main", check=False)
        if r.returncode != 0:
            sh("git", "rebase", "--abort", check=False)
            files = sh("git", "diff", "--name-only", "--diff-filter=U", check=False).stdout.split()
            print(f"#{n} {br}: does not rebase cleanly, left alone")
            marker = "<!-- rebase_stale -->"
            comments = gh_json(f"repos/{REPO}/issues/{n}/comments?per_page=100") or []
            if not any(marker in (c.get("body") or "") for c in comments):
                sh("gh", "api", "-X", "POST", f"repos/{REPO}/issues/{n}/comments", "-f",
                   "body=" + marker + f" This branch is {behind} commits behind main and does not rebase cleanly "
                   "(the merge gate needs a fresh evaluation on the current main). Rebase it by hand or close it; "
                   "the planner can re-raise the objective on today's code.", check=False)
            continue
        pr_ = sh("git", "push", "--force-with-lease", push_url, f"HEAD:refs/heads/{br}", check=False)
        print(f"#{n} {br}: rebased over {behind} commit(s) and pushed" if pr_.returncode == 0 else f"#{n} {br}: push failed: {pr_.stderr.strip()[:200]}")
    sh("git", "checkout", "-q", "main", check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
