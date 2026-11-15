#!/usr/bin/env python3
"""
The briefing watchdog (15 Nov 2026). Run by briefing-watch.yml every 20
minutes around each briefing slot (notify.SLOTS: 07:00, 11:00, 16:00 and
21:00 UK).

Why: the briefings go out from the first deploy build at or after each
slot, and GitHub drops or delays scheduled runs at busy times. The 07:40 UTC
deploy cron did not run once from 10 to 15 Nov (the scheduled runs those
mornings are the 05:15 cron, an hour or more late), the 11:07 backup was
dropped too, and the briefing log has the morning push 123 and 138 minutes
late on 14 and 15 Nov (claude/briefing-watch-2026-11-15.md). A late briefing
is a late price: Douglas bets at those times.

What it does: if a slot is due today, not yet in groupings-archive/briefed.json,
at least GRACE_MIN past its hour, no deploy run is queued or running, and the
watchdog has dispatched fewer than MAX_KICKS deploys since the slot's hour,
it dispatches deploy.yml on main. The build then sends the briefing exactly
as a cron build would (notify.due_slot / mark_sent; nothing sends twice).
Builds nothing itself, reads nothing but briefed.json and the run list.

    GH_TOKEN=... REPO=owner/name python3 tools/briefing_watch.py [--dry-run]

Standard library only.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import notify as N

GRACE_MIN = 10        # minutes after a slot's hour before the watchdog acts
MAX_KICKS = 2         # dispatches a slot at most (a failed build gets one retry)
ACTIVE = {"queued", "in_progress", "waiting", "pending", "requested"}
WORKFLOW = "deploy.yml"
WATCH_FILE = os.path.join(HERE, ".github", "workflows", "briefing-watch.yml")


def _ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def slot_start(now, slot):
    uk = now.astimezone(N.UK)
    h = dict(N.SLOTS)[slot]
    return uk.replace(hour=h, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def decide(now, runs, path=None):
    """(dispatch?, reason). `runs` are deploy.yml runs from the REST API
    (created_at, status, event), any order."""
    slot = N.due_slot(now, path)
    if not slot:
        return False, "no slot due"
    start = slot_start(now, slot)
    if now < start + timedelta(minutes=GRACE_MIN):
        return False, f"{slot}: inside the {GRACE_MIN}-minute grace"
    if any(r.get("status") in ACTIVE for r in runs):
        return False, f"{slot}: a deploy is running or queued, it will send it"
    kicks = [r for r in runs if r.get("event") == "workflow_dispatch" and _ts(r["created_at"]) >= start]
    if len(kicks) >= MAX_KICKS:
        return False, f"{slot}: already dispatched {len(kicks)} deploy(s) for this slot"
    late = int((now - start).total_seconds() // 60)
    return True, f"{slot}: unsent {late} minutes after its hour, no deploy running"


def watched_utc_hours(path=WATCH_FILE):
    """UTC hours the watchdog's crons cover (for the test that every slot is
    watched in both GMT and BST)."""
    hours = set()
    with open(path) as f:
        for m in re.finditer(r'cron:\s*"\S+\s+(\d+)(?:-(\d+))?\s', f.read()):
            a = int(m.group(1)); b = int(m.group(2) or a)
            hours.update(range(a, b + 1))
    return hours


def _api(method, url, token, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    return json.loads(raw) if raw else {}


def main(argv):
    token, repo = os.environ.get("GH_TOKEN"), os.environ.get("REPO")
    if not token or not repo:
        print("briefing_watch: GH_TOKEN or REPO not set"); return 0
    now = datetime.now(timezone.utc)
    since = (now - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = f"https://api.github.com/repos/{repo}/actions/workflows/{WORKFLOW}"
    runs = _api("GET", f"{base}/runs?per_page=50&created=%3E%3D{since}", token).get("workflow_runs") or []
    go, why = decide(now, runs)
    print(f"briefing_watch: {why}")
    if go and "--dry-run" not in argv:
        _api("POST", f"{base}/dispatches", token, {"ref": "main"})
        print("briefing_watch: deploy dispatched")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
