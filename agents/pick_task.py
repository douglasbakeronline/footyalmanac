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
    "champ": ("Priya", "England Championship Specialist"), "odds": ("Oscar", "Odds Analyst"), "accas": ("Jade", "Accumulator Strategist"),
}
# Sprint order: the people who keep the pipeline healthy first, then the modellers, then the write-ups.
SPRINT = ["engineer", "quality", "source", "scout", "ratings", "experiment", "champ", "calib", "sports",
          "curator", "odds", "accas", "auditor", "chief"]
GATES = ("test it paired and bootstrapped (Rule 2), fit on the last completed season and confirm on the current one "
         "(Rule 3 gates). If it passes, ship it with evidence. If it fails, ship only a dated claude/ note recording "
         "the rejected test so nobody repeats it.")
# Each agent's standing job, used when the live scoreboard gives them nothing more urgent.
STANDING = {
    "engineer": ("tests-gap", "Add tests for the least-tested module",
        "Find the Python module in this repo with the most logic and the fewest tests (tests/ and nametest.py). Add focused "
        "stdlib unittest tests for its riskiest functions under tests/, fix any real bug the tests expose in the smallest "
        "safe way, and make sure python3 -m unittest discover -s tests passes."),
    "quality": ("fixture-integrity", "Check today's fixtures for duplicates, wrong dates and doubtful name matches",
        "Read the latest file in predictions/ and the matching code. Look for duplicate fixtures, fixtures on the wrong UK date, "
        "and doubtful team-name matches (Rule 6). Fix the matcher or LIVE_NAMES for anything real, extend nametest.py, and "
        "never force a doubtful match. If everything is clean, write up what you checked in claude/data-integrity.md."),
    "source": ("source-resilience", "Make one data source fail more gracefully",
        "Read sources.py and the build. Find the data source whose failure would cost the most (no retry, no fallback, or a "
        "silent empty result) and make it fail safely: a retry with backoff, a clear warning, or a fallback to the last good "
        "copy, keeping Rule 9 (a failing upstream keeps yesterday's site). Add a test with a fake failing source."),
    "scout": ("coverage", "Add a free data source for an uncovered league",
        "Read claude/coverage-expansion.md and claude/data-expansion-plan.md. Pick the most valuable league that is "
        "not yet covered and has a free, automatable source. Add it with a name-matching test, keeping the Daily List "
        "rules (new leagues stay off the list until replayed above the bar). If none is feasible today, update the plan "
        "with what you checked and why."),
    "ratings": ("ratings-idea", "Test one ratings improvement",
        "Read engine.py and claude/tuning-evidence.md. Pick ONE ratings idea not already tested there (for example a "
        "different rating decay between seasons or a promoted-team prior) and " + GATES),
    "experiment": ("draw-handling", "Test one draw-handling improvement across all leagues",
        "Draws cost the most picks. Read engine.py and claude/tuning-evidence.md, pick ONE draw-handling idea not already "
        "tested and " + GATES),
    "champ": ("championship-deep-dive", "Find why the Championship misses",
        "England Championship (en.2) is our weakest league and Mia has already rejected league-specific home advantage and "
        "rho (claude/championship-test-2026-10-04.md). Using history only, break the Championship misses down: promoted and "
        "relegated teams, early season, big rating gaps, draws. Pick ONE idea not yet tested and " + GATES),
    "calib": ("calibration-check", "Check calibration by sport and confidence band",
        "Using history (not record.json), measure calibration by confidence band for football, and by sport for the "
        "other sports where there is enough data. Bootstrap the gaps. calibration.json only changes through tune.py's gates "
        "(Rule 5); you may improve the method, but never hand-edit calibration.json. Write the finding up in claude/."),
    "sports": ("other-sports", "Lift the weakest of the other sports",
        "Read the tennis and multi-sport code and records (claude/multi-sport.md, claude/tennis-record.md). Find the sport or "
        "tour that is furthest below its expected hit rate with enough matches, test ONE improvement with the existing tuning "
        "evidence style, and ship it only if it passes. Football must never depend on other-sport code."),
    "curator": ("list-bar", "Test the Daily List bar",
        "Read claude/daily-list.md. Replay the Daily List selection rules on history: would a slightly higher or lower bar, "
        "or a per-league bar, raise the list's hit rate without losing too many picks? Bootstrap it. Change the rule only if "
        "it clearly passes; otherwise write up the replay in claude/daily-list.md."),
    "odds": ("odds-coverage", "Price more of the Odds tab legs",
        "Read groupings.py. About a third of football legs and all tennis and rugby legs have no bookmaker price and fall back "
        "to the model's fair price. Find a free, automatable price source (or a better API-Football match: date, team-name "
        "normalisation) that prices more legs, add it with a test in tests/test_groupings.py, and keep the rule that prices "
        "never feed any model. Measure before and after on today's pool."),
    "accas": ("group-rules", "Backtest the Odds tab group rules",
        "Read groupings.py and groupings-record.json. Using history, replay the group rules (the 65%/30 tested-rate bar, the "
        "spread rules, the bands) on past days and measure how often each band's groups would have won against their stated "
        "chance. If one rule change clearly improves the hit rate at the same odds, ship it with tests; otherwise write the "
        "backtest up in claude/odds-groupings.md."),
    "auditor": ("grading-audit", "Audit the grading of recent results",
        "Take a sample of at least 50 recently graded games across football, tennis and other sports. Check each result in the "
        "graded files against an independent free source where possible, and check score.py's handling of postponed, "
        "abandoned, walkover and retired matches. Fix any grading bug in the code (never hand-edit record files) with a test, "
        "and write up the audit in claude/results-review-board.md."),
    "chief": ("office-review", "Write the office review and next week's priorities",
        "Read RELEASES.md for the last 14 days, the claude/ notes and the record summaries. Write claude/office-review-<today>.md: "
        "what the office shipped, what it learned (including rejected tests), where accuracy and data quality stand, and the "
        "three most valuable tasks for next week with an owner each from: " + ", ".join(f"{v[0]} ({k})" for k, v in AGENTS.items())
        + ". Keep it short and evidence-led."),
}
PROTECTED = ["record.json", "predictions/", "predictions-sports/", "predictions-tennis/", "current/", "history/",
             "history-sports/", "dashboard.html", "adjustments.json", "calibration.json", "tuning-report.json",
             "sports-record.json", "sports-record.js", "tennis-record.json", "tennis-record.js", ".github/",
             "agents/", "CLAUDE.md", "AGENTS.md"]
MAX_OPEN = 6
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
        names = [l["name"] for l in i.get("labels", [])]
        if any(n.startswith("platform:") and n != "platform:office" for n in names):
            continue                      # claimed by another AI platform (AGENTS.md, "Other AI platforms")
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
    for acc, lk, v in [w for w in weak if w[0] < 0.45][:3]:
        out.append((f"weak-league-{lk}", "experiment", f"Lift accuracy in {v['name']}",
            f"{v['name']} ({lk}) is the weakest league with 30+ graded games: {pct(acc)} over {v['n']} games "
            f"(home rate {pct(v.get('homeRate'))}, drawn out {v.get('drawnOut')}). Investigate why using history only "
            "(never record.json, Rule 1). Propose ONE change (e.g. league-specific home advantage or draw handling), "
            + GATES))
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
    ap = argparse.ArgumentParser(); ap.add_argument("--task", default=""); ap.add_argument("--agent", default="")
    ap.add_argument("--list-agents", action="store_true"); a = ap.parse_args()
    if a.list_agents:
        print(json.dumps(SPRINT)); return
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
    if len(open_prs) >= MAX_OPEN and not a.task and not a.agent:
        print(f"{len(open_prs)} agent pull requests already open; waiting for them to merge."); emit(skip="1"); return
    cands = backlog() + candidates()
    if a.task:
        pick = next((c for c in cands if c[0] == a.task), None)
    elif a.agent:
        busy = recent | {l["name"][10:] for p in open_prs for l in p.get("labels", []) if l["name"].startswith("objective:")}
        mine = [c for c in cands if c[1] == a.agent]
        if a.agent in STANDING:
            k, t, b = STANDING[a.agent]; mine.append((k, a.agent, t, b))
        pick = next((c for c in mine if c[0] not in busy), None)
    else:
        pick = next((c for c in cands if c[0] not in recent), None)
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
Nobody reviews your pull request: if the checks pass (python3 nametest.py, python3 -m unittest discover -s tests, the build when you touch the pipeline, and the independent Evaluation, which needs a pass for any model change) it merges straight away. So only change code you are confident is right, never change model numbers unless every gate passed (a model change with gates other than passed is closed, not merged), and when in doubt ship the write-up instead of the change. Set automerge to false only if you believe the change should not ship; it will then be closed with your report kept."""
    print(f"Task: {key} -> {name} ({role}): {title}")
    emit(skip="0", key=key, owner=owner, title=title, prompt=prompt)

if __name__ == "__main__":
    main()
