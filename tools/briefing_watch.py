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

    GH_TOKEN=... REPO=owner/name python3 tools/briefing_watch.py [--dry-run] [--wait]

--wait (16 Nov 2026): GitHub shed the watchdog's own crons too (on 16 Nov
not one of the nine 06:05-08:45 UTC runs started, and the morning push was
still unsent at 08:36). So every deploy run now ends by dispatching this
watchdog with --wait (deploy.yml `briefing-next`; a GITHUB_TOKEN dispatch
does start a run). It sleeps until the next unsent slot's hour plus the grace
if that is at most MAX_WAIT_MIN away, then checks every POLL_MIN minutes for
up to LOOP_MIN minutes, reading briefed.json and the run list fresh from the
API each time, and dispatches a deploy under the same rule as above. The
deploy that sends one slot starts the wait for the next, so the briefings no
longer depend on a cron firing near the slot. The wait acts on the slot's
hour itself (WAIT_GRACE_MIN 0, 16 Nov 2026 evening): the 10-minute grace is
for the cron watchdog, which leaves room for a late cron; on the chain it only
added ten minutes (16 Nov lunch: dispatched 11:15, pushed 11:19, 19 late).

Standard library only.
"""
import json, os, re, sys, tempfile, time, urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import notify as N

GRACE_MIN = 10        # minutes after a slot's hour before the watchdog acts
WAIT_GRACE_MIN = 0    # --wait (16 Nov 2026): the chain is the sender, so it acts on the hour;
                      # with the cron's 10 minutes on top of a ~5-minute build, lunch landed 19 late
MAX_KICKS = 2         # dispatches a slot at most (a failed build gets one retry)
ACTIVE = {"queued", "in_progress", "waiting", "pending", "requested"}
WORKFLOW = "deploy.yml"
MAX_WAIT_MIN = 300    # --wait: the furthest slot it will sleep for (job limit 6h; lunch to evening is ~290)
LOOP_MIN = 45         # --wait: how long after the slot's hour it keeps checking
POLL_MIN = 5          # --wait: minutes between checks once the slot is due
WATCH_FILE = os.path.join(HERE, ".github", "workflows", "briefing-watch.yml")


def _ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def slot_start(now, slot):
    uk = now.astimezone(N.UK)
    h = dict(N.SLOTS)[slot]
    return uk.replace(hour=h, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def decide(now, runs, path=None, grace=GRACE_MIN):
    """(dispatch?, reason). `runs` are deploy.yml runs from the REST API
    (created_at, status, event), any order. `grace`: minutes after the slot's
    hour before acting (the cron watchdog leaves room for a late cron; the
    --wait chain does not, WAIT_GRACE_MIN)."""
    slot = N.due_slot(now, path)
    if not slot:
        return False, "no slot due"
    start = slot_start(now, slot)
    if now < start + timedelta(minutes=grace):
        return False, f"{slot}: inside the {grace}-minute grace"
    if any(r.get("status") in ACTIVE for r in runs):
        return False, f"{slot}: a deploy is running or queued, it will send it"
    kicks = [r for r in runs if r.get("event") == "workflow_dispatch" and _ts(r["created_at"]) >= start]
    if len(kicks) >= MAX_KICKS:
        return False, f"{slot}: already dispatched {len(kicks)} deploy(s) for this slot"
    late = int((now - start).total_seconds() // 60)
    return True, f"{slot}: unsent {late} minutes after its hour, no deploy running"


def next_wait(now, path=None, grace=WAIT_GRACE_MIN):
    """(slot, seconds to sleep) for the next slot of the UK day still unsent,
    or None when there is none within MAX_WAIT_MIN. A slot already due and
    unsent waits 0 (or the rest of its grace); a due slot more than LOOP_MIN
    past its hour is left to the next build."""
    try:
        with open(path or N.brief_file()) as f: st = json.load(f)
    except (OSError, ValueError):
        st = {}
    uk = now.astimezone(N.UK)
    sent = (st.get("slots") or []) if st.get("date") == uk.date().isoformat() else []
    for name, _ in N.SLOTS:
        if name in sent:
            continue
        start = slot_start(now, name)
        if now > start + timedelta(minutes=LOOP_MIN):
            continue
        wake = start + timedelta(minutes=grace)
        secs = max(0, int((wake - now).total_seconds()))
        if secs > MAX_WAIT_MIN * 60:
            return None
        return name, secs
    return None


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


def _brief_now(repo, token, path):
    """briefed.json as main has it now (the checkout is stale after a sleep)."""
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/contents/groupings-archive/briefed.json?ref=main",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.raw+json",
                                          "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
            f.write(r.read())
    except Exception as e:
        print(f"briefing_watch: could not read briefed.json from main ({e}); using the checkout's")
        return None
    return path


def _runs(base, token, now):
    since = (now - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return _api("GET", f"{base}/runs?per_page=50&created=%3E%3D{since}", token).get("workflow_runs") or []


def wait_and_kick(repo, token, base, dry, sleep=time.sleep, clock=lambda: datetime.now(timezone.utc)):
    tmp = os.path.join(tempfile.mkdtemp(), "briefed.json")
    path = _brief_now(repo, token, tmp)
    nxt = next_wait(clock(), path)
    if not nxt:
        print(f"briefing_watch: no unsent slot within {MAX_WAIT_MIN} minutes"); return 0
    slot, secs = nxt
    print(f"briefing_watch: waiting {secs // 60} minutes for the {slot} slot")
    sleep(secs)
    end = slot_start(clock(), slot) + timedelta(minutes=LOOP_MIN)
    while True:
        now = clock()
        path = _brief_now(repo, token, tmp)
        go, why = decide(now, _runs(base, token, now), path, grace=WAIT_GRACE_MIN)
        print(f"briefing_watch: {now:%H:%M} UTC {why}")
        if go:
            if not dry:
                _api("POST", f"{base}/dispatches", token, {"ref": "main"})
                print("briefing_watch: deploy dispatched")
            return 0
        if N.due_slot(now, path) is None and now >= slot_start(now, slot):
            return 0   # sent (or nothing due): done
        if now + timedelta(minutes=POLL_MIN) > end:
            print(f"briefing_watch: {slot} still unsent {LOOP_MIN} minutes after its hour; left to the next build")
            return 0
        sleep(POLL_MIN * 60)


def main(argv):
    token, repo = os.environ.get("GH_TOKEN"), os.environ.get("REPO")
    if not token or not repo:
        print("briefing_watch: GH_TOKEN or REPO not set"); return 0
    base = f"https://api.github.com/repos/{repo}/actions/workflows/{WORKFLOW}"
    if "--wait" in argv:
        return wait_and_kick(repo, token, base, "--dry-run" in argv)
    now = datetime.now(timezone.utc)
    runs = _runs(base, token, now)
    go, why = decide(now, runs)
    print(f"briefing_watch: {why}")
    if go and "--dry-run" not in argv:
        _api("POST", f"{base}/dispatches", token, {"ref": "main"})
        print("briefing_watch: deploy dispatched")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
