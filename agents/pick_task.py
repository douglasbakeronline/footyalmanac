"""Office agents: pick today's development task from the live scoreboard.

Reads the same numbers the Footyalmanac HQ office reports on, finds the most
important objective that is behind, and writes a prompt for the agent that owns
it. Writes GitHub Actions outputs: skip, key, owner, title, prompt.
"""
import argparse, json, os, subprocess, sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS = {
    "chief": ("Luke", "Chief of Staff"), "scout": ("Ava", "Fixture Scout"), "quality": ("Cory", "Data Quality"),
    "source": ("Raj", "Source Manager"), "ratings": ("Ben", "Ratings Modeller"), "experiment": ("Mia", "Experiment Lead"),
    "sports": ("Theo", "New Sports Researcher"), "auditor": ("Susie", "Results Auditor"),
    "calib": ("Andrew", "Calibration & Market Analyst"), "curator": ("Nina", "Picks Curator"), "engineer": ("Allan", "Engineer"),
}
PROTECTED = ["record.json", "predictions/", "predictions-sports/", "predictions-tennis/", "current/", "history/",
             "history-sports/", "dashboard.html", "adjustments.json", "calibration.json", "tuning-report.json",
             "sports-record.json", "sports-record.js", "tennis-record.json", "tennis-record.js", ".github/"]
MAX_OPEN = 2
COOLDOWN_DAYS = 7

def load(path, default=None):
    try:
        with open(os.path.join(ROOT, path)) as f: return json.load(f)
    except Exception: return default

def gh(args):
    try:
        out = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=60)
        return json.loads(out.stdout) if out.stdout.strip() else []
    except Exception: return []

def pct(x): return f"{x*100:.0f}%" if x is not None else "n/a"

def latest(d):
    p = os.path.join(ROOT, d)
    if not os.path.isdir(p): return None, []
    names = sorted(n for n in os.listdir(p) if n.endswith(".json"))
    return (names[-1][:-5], load(f"{d}/{names[-1]}", [])) if names else (None, [])

def backlog():
    """Issues labelled office-backlog (from Douglas, Julius or Perplexity) come before the agents' own picks."""
    out = []
    for i in gh(["issue", "list", "--label", "office-backlog", "--state", "open", "-L", "20", "--json", "number,title,body,labels"]):
        owner = next((l["name"][6:] for l in i.get("labels", []) if l["name"].startswith("agent:") and l["name"][6:] in AGENTS), "experiment")
        brief = (i.get("body") or "").strip()[:4000]
        out.append((f"issue-{i['number']}", owner, i["title"][:80],
                    f"Backlog issue #{i['number']}: {i['title']}\n\n{brief}\n\nWork on exactly this. If the evidence says it is not worth doing, explain why in the report."))
    return sorted(out, key=lambda c: int(c[0][6:]))

def candidates():
    rec = load("record.json", {}) or {}
    trec = load("tennis-record.json", {}) or {}
    day, preds = latest("predictions")
    out = []
    runs = gh(["run", "list", "--workflow", "deploy.yml", "-L", "5", "--json", "conclusion,createdAt,url"])
    if runs and runs[0].get("conclusion") == "failure":
        out.append(("build-failure", "engineer", "Fix the failing daily build",
            f"The latest 'Rebuild and publish' run failed ({runs[0]['url']}). Find the cause from the code and the "
            "workflow, fix it in the smallest safe way, and explain the root cause. Remember a failing upstream keeps "
            "yesterday's site (Rule 9): do not weaken that safety."))
    unrated = [p for p in preds if p.get("unrated")]
    if unrated:
        sample = "; ".join(f"{p['home']} v {p['away']} ({p['league']})" for p in unrated[:8])
        out.append(("unrated-fixtures", "quality", f"Rate {len(unrated)} unrated fixtures",
            f"{len(unrated)} fixtures on {day} are unrated. Examples: {sample}. Follow Rule 6: find which are spellings, "
            "fix the matcher or add LIVE_NAMES entries, extend nametest.py, and never force a doubtful match."))
    weak = sorted([(v["accuracy"], k, v) for k, v in (rec.get("byLeague") or {}).items() if v.get("n", 0) >= 30])
    if weak and weak[0][0] < 0.45:
        acc, lk, v = weak[0]
        out.append((f"weak-league-{lk}", "experiment", f"Lift accuracy in {v['name']}",
            f"{v['name']} ({lk}) is the weakest league with 30+ graded games: {pct(acc)} over {v['n']} games "
            f"(home rate {pct(v.get('homeRate'))}, drawn out {v.get('drawnOut')}). Investigate why using history only "
            "(never record.json, Rule 1). Propose ONE change (e.g. league-specific home advantage or draw handling), "
            "test it paired and bootstrapped (Rule 2), fit on the last completed season and confirm on the current one "
            "(Rule 3 gates). If it passes, ship it with evidence. If it fails, ship only a dated claude/ note recording "
            "the rejected test so nobody repeats it."))
    bands = rec.get("bands") or []
    if bands:
        g = max(bands, key=lambda b: abs(b["hit"] - b["expected"]))
        if abs(g["hit"] - g["expected"]) > 0.05:
            out.append(("calibration-gap", "calib", f"Close the {pct(g['from'])}-{pct(g['to'])} calibration gap",
                f"Picks predicted at {pct(g['from'])}-{pct(g['to'])} won {pct(g['hit'])} vs {pct(g['expected'])} expected "
                f"over {g['n']} games. Work out whether this is noise (bootstrap it) or a real miscalibration, using "
                "history not record.json. calibration.json only changes through tune.py's gates (Rule 5); you may "
                "improve the method, but do not hand-edit calibration.json. If nothing passes, write the finding up."))
    tiers = {t["name"]: t for t in rec.get("tiers") or []}
    st = tiers.get("Strong")
    if st and st["hit"] < st["expected"] - 0.01:
        out.append(("strong-tier", "ratings", "Strong tier is below its expected hit rate",
            f"Strong picks won {pct(st['hit'])} vs {pct(st['expected'])} expected over {st['n']} games "
            f"({st.get('drawnOut')} drawn out). Look for a pattern in the Strong misses in history (league, draw risk, "
            "Celtic's Law) and test one fix under the gates. Report honestly if it is noise."))
    tov = trec.get("overall") or {}
    if tov and tov.get("accuracy") is not None and tov["accuracy"] < tov.get("expected", 0) - 0.01:
        out.append(("tennis-gap", "sports", "Tennis is below its expected hit rate",
            f"Tennis hit {pct(tov['accuracy'])} vs {pct(tov.get('expected'))} expected over {tov.get('n')} matches. "
            "Check by tour and surface; test one improvement (e.g. surface weighting) with tune_tennis.py style evidence. "
            "Football must never depend on tennis code."))
    out.append(("coverage", "scout", "Add a free data source for an uncovered league",
        "Read claude/coverage-expansion.md and claude/data-expansion-plan.md. Pick the most valuable league that is "
        "not yet covered and has a free, automatable source. Add it with a name-matching test, keeping the Daily List "
        "rules (new leagues stay off the list until replayed above the bar)."))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--task", default=""); a = ap.parse_args()
    prs = gh(["pr", "list", "--label", "office-agent", "--state", "all", "-L", "60", "--json", "number,state,labels,createdAt"])
    open_prs = [p for p in prs if p["state"] == "OPEN"]
    recent = set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=COOLDOWN_DAYS)
    for p in prs:
        made = datetime.fromisoformat(p["createdAt"].replace("Z", "+00:00"))
        for l in p.get("labels", []):
            if l["name"].startswith("objective:") and (p["state"] == "OPEN" or made > cutoff):
                recent.add(l["name"][10:])
    out = os.environ.get("GITHUB_OUTPUT", "/dev/stdout")
    def emit(**kw):
        with open(out, "a") as f:
            for k, v in kw.items():
                if "\n" in str(v): f.write(f"{k}<<__EOF__\n{v}\n__EOF__\n")
                else: f.write(f"{k}={v}\n")
    if len(open_prs) >= MAX_OPEN and not a.task:
        print(f"{len(open_prs)} agent pull requests already open; waiting for them to merge."); emit(skip="1"); return
    cands = backlog() + candidates()
    pick = next((c for c in cands if c[0] == a.task), None) if a.task else next((c for c in cands if c[0] not in recent), None)
    if not pick:
        print("Nothing new to work on today."); emit(skip="1"); return
    key, owner, title, brief = pick
    name, role = AGENTS[owner]
    prompt = f"""You are {name}, the {role} at Footyalmanac HQ, an AI engineering team improving this sports prediction project. You are working unattended in GitHub Actions; nobody will answer questions, so make careful decisions and explain them.

Before anything else, read CLAUDE.md and AGENTS.md in full and follow every rule in them, especially Rules 1 to 10 and the owner's standing decisions. Honesty over confidence: a well-documented rejected test is a good outcome.

TODAY'S TASK: {title}
{brief}

How to work:
- Do not run git commit, git push, git tag or open pull requests: leave your changes in the working tree. The workflow verifies and opens the pull request for you.
- Never edit these paths (the workflow discards changes to them): {", ".join(PROTECTED)}
- Keep the change small and focused on this one task. No visual or layout changes unless the task needs them.
- Verify: python3 nametest.py, and python3 build.py --days 2 --no-topup --no-odds if you touched the football pipeline. Restore bot-written files the build overwrote.
- Add an entry at the top of RELEASES.md in the existing style, marked "(tag pending)", with What changed / Evidence / Files / Not changed / Roll back. For a significant finding add a dated note in claude/ in the style of the existing ones.

When finished, write two files:
1. /tmp/office-agent/report.md: the pull request description (what and why, evidence with the actual numbers, files, what was not changed, how to roll back).
2. /tmp/office-agent/meta.json: {{"type": "model|data|code|docs|ui", "gates": "passed|failed|n/a", "automerge": true or false, "summary": "one sentence for the office stand-up"}}
Set automerge to false for any visual change, any change to model numbers that did not pass every gate, or anything you are not confident is safe to ship unattended."""
    print(f"Task: {key} -> {name} ({role}): {title}")
    emit(skip="0", key=key, owner=owner, title=title, prompt=prompt)

if __name__ == "__main__":
    main()
