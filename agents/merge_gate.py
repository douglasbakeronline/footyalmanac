"""Office agents: merge window. Merges agent pull requests that are safe to ship unattended.

A pull request merges only if it is labelled office-agent + auto-merge-ok + checks-passed,
is not labelled hold or needs-owner, is at least 12 hours old, touches no protected path,
and GitHub says it merges cleanly. Each merge is tagged and the site is redeployed.
"""
import json, subprocess, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from pick_task import PROTECTED

def gh(args, ok=False):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if r.returncode and not ok: print(r.stderr)
    return r

def main():
    prs = json.loads(gh(["pr", "list", "--label", "office-agent", "--state", "open", "-L", "30", "--json",
                         "number,title,labels,createdAt,files,mergeable"]).stdout or "[]")
    now = datetime.now(timezone.utc); merged = []
    for p in prs:
        labels = {l["name"] for l in p["labels"]}
        age = now - datetime.fromisoformat(p["createdAt"].replace("Z", "+00:00"))
        bad = [f["path"] for f in p.get("files", []) if any(f["path"] == x or f["path"].startswith(x) for x in PROTECTED)]
        why = None
        if not {"auto-merge-ok", "checks-passed"} <= labels: why = "not marked safe"
        elif labels & {"hold", "needs-owner"}: why = "on hold / needs owner"
        elif age < timedelta(hours=12): why = "younger than 12 hours"
        elif bad: why = "touches protected files: " + ", ".join(bad)
        elif p.get("mergeable") == "CONFLICTING": why = "has conflicts"
        if why:
            print(f"#{p['number']} skipped: {why}"); continue
        r = gh(["pr", "merge", str(p["number"]), "--squash", "--delete-branch"])
        if r.returncode == 0:
            merged.append(p); gh(["pr", "comment", str(p["number"]), "--body", "Merged by the office merge window after passing every gate. Roll back with `git revert` on the squash commit."])
            print(f"#{p['number']} merged")
    if merged:
        subprocess.run(["git", "pull", "-q"]); day = now.strftime("%Y-%m-%d")
        tags = subprocess.run(["git", "tag", "-l", f"release-{day}*"], capture_output=True, text=True).stdout.split()
        tag = f"release-{day}" + (f"-{len(tags)+1}" if tags else "")
        msg = "Office agents: " + "; ".join(f"#{p['number']} {p['title']}" for p in merged)
        subprocess.run(["git", "-c", "user.name=footyalmanac-hq[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com", "tag", "-a", tag, "-m", msg])
        subprocess.run(["git", "push", "origin", tag])
        gh(["workflow", "run", "deploy.yml"])
        print("Tagged", tag, "and started a deploy")

if __name__ == "__main__":
    main()
