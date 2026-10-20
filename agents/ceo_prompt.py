"""Elena, the CEO: turn Douglas's brief (an issue labelled `ceo`) into a prompt for Claude.

Run by .github/workflows/ceo.yml. Reads the issue and its thread with the
workflow's token, keeps only Douglas's words and Elena's own earlier replies,
and writes GitHub Actions outputs: skip, issue, prompt.

Elena can do three things, and says which in her reply:
  answer    any question about the project, its numbers, its code or its plans
  ship      make a change herself; it goes through open_pr.sh and the merge gate
            exactly like an office agent's, so it ships only if every check passes
  delegate  queue work for named agents as office-backlog issues, which the
            next sprint picks up before anything else
"""
import argparse, json, os, subprocess, sys

OWNER = "douglasbakeronline"
BOT_MARK = "<!-- elena -->"          # first line of every reply Elena posts, so she knows her own words
OUT = "/tmp/office-agent"
AGENTS = {
    "chief": "Luke, Chief of Staff", "scout": "Ava, Fixture Scout", "quality": "Cory, Data Quality",
    "source": "Raj, Source Manager", "ratings": "Ben, Ratings Modeller", "experiment": "Mia, Experiment Lead",
    "sports": "Theo, New Sports Researcher", "auditor": "Susie, Results Auditor",
    "calib": "Andrew, Calibration & Market Analyst", "curator": "Nina, Picks Curator", "engineer": "Allan, Engineer",
    "champ": "Priya, England Championship Specialist", "odds": "Oscar, Odds Analyst (Groups & Odds Desk)",
    "accas": "Jade, Accumulator Strategist (Groups & Odds Desk)", "value": "Kofi, Value Analyst (Groups & Odds Desk)",
    "legs": "Hannah, Leg Selector (Groups & Odds Desk)",
}


def gh(args):
    try:
        out = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=60)
        return json.loads(out.stdout) if out.stdout.strip() else None
    except Exception:
        return None


def thread(repo, n):
    issue = gh(["api", f"repos/{repo}/issues/{n}"]) or {}
    comments = gh(["api", f"repos/{repo}/issues/{n}/comments?per_page=100"]) or []
    turns = []
    if (issue.get("user") or {}).get("login") == OWNER:
        turns.append(("Douglas", f"{issue.get('title', '')}\n\n{issue.get('body') or ''}".strip()))
    for c in comments:
        who, body = (c.get("user") or {}).get("login"), c.get("body") or ""
        if who == OWNER: turns.append(("Douglas", body))
        elif body.startswith(BOT_MARK): turns.append(("Elena", body[len(BOT_MARK):].strip()))
        # anyone else's words are ignored: the repository is public
    return issue, turns


def build(n, turns):
    convo = "\n\n".join(f"### {who}\n{text[:6000]}" for who, text in turns[-12:])
    team = "\n".join(f"- `{k}`: {v}" for k, v in AGENTS.items())
    return f"""You are Elena, CEO of the Sports Almanac office: the AI team that develops footyalmanac every day. Douglas,
the owner, has briefed you on issue #{n}. You are working unattended in GitHub Actions on a checkout of the repository.

Read CLAUDE.md and AGENTS.md first and follow every rule in them. Honesty over confidence: never inflate a number,
never claim something works without checking it, and if Douglas is wrong, say so and why.

THE CONVERSATION SO FAR (answer the last message from Douglas):

{convo}

WHAT YOU CAN USE
- The whole repository: code, claude/ notes, RELEASES.md, record files, predictions. Run any script that works offline.
- The office's published data, read with WebFetch: https://raw.githubusercontent.com/douglasbakeronline/footyalmanac-hq/main/docs/data/
  (backlog.json is the ranked list of gaps; latest.json is the last stand-up; org.json is the team).
- Public web pages with WebFetch, for facts about sports or sources.

DECIDE WHAT THIS NEEDS, then do it. You may do more than one.
1. ANSWER. Any question gets a direct, specific answer with real numbers from the files, not from memory.
2. SHIP a change yourself when it is clear, small enough to finish now and safe. Make it in the working tree. Do not
   run git commit, push or open pull requests: the workflow does that, runs nametest.py, the tests and the independent
   Evaluation, and the merge gate ships it only if every check passes. Add a RELEASES.md entry marked "(tag pending)".
   Write /tmp/office-agent/report.md (the pull request description) and /tmp/office-agent/meta.json:
   {{"type": "model|data|code|docs|ui", "gates": "passed|failed|n/a", "automerge": true or false, "summary": "one sentence"}}.
   Model numbers change only with every gate passed (Rules 1 to 5). You cannot change .github/, agents/, CLAUDE.md or
   AGENTS.md: if the brief needs that, say so and say exactly what Douglas should change.
3. DELEGATE work that is bigger, needs research, or belongs to a specialist. Write /tmp/office-agent/delegate.json, a
   list of {{"owner": "<agent key>", "title": "<under 80 characters>", "brief": "<what to do, the evidence, how to
   judge it>"}}. Each becomes an office-backlog issue that the next morning's sprint works before anything else.
   The team:
{team}

ALWAYS write /tmp/office-agent/reply.md: your reply to Douglas, posted on the issue. UK English, no em dashes, direct,
answer first, no preamble. Say what you found, what you shipped (it will be linked) and what you delegated, to whom.
Keep it short enough to read on a phone unless he asked for depth.
"""


def delegate(repo, n, path=f"{OUT}/delegate.json"):
    """Open one office-backlog issue per delegated task. Unknown owners are dropped, at most five a brief."""
    try: tasks = json.load(open(path))
    except Exception: return []
    made = []
    for t in (tasks if isinstance(tasks, list) else [])[:5]:
        owner, title = str(t.get("owner", "")), str(t.get("title", "")).strip()[:80]
        if owner not in AGENTS or not title: continue
        body = (f"{str(t.get('brief', '')).strip()[:4000]}\n\nDelegated by Elena from #{n}. The office sprint works "
                "office-backlog issues before anything else.")
        subprocess.run(["gh", "label", "create", f"agent:{owner}", "--color", "f0b35a", "--force"], capture_output=True)
        subprocess.run(["gh", "label", "create", "from-ceo", "--color", "d4a64a", "--force"], capture_output=True)
        r = subprocess.run(["gh", "issue", "create", "-R", repo, "--title", f"[{owner}] {title}", "--body", body,
                            "--label", "office-backlog", "--label", f"agent:{owner}", "--label", "from-ceo"],
                           capture_output=True, text=True)
        if r.returncode == 0: made.append((owner, title, r.stdout.strip()))
        else: print(f"could not open the issue for {owner}: {r.stderr.strip()}", file=sys.stderr)
    return made


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--issue", required=True)
    ap.add_argument("--delegate", action="store_true", help="open the issues in /tmp/office-agent/delegate.json")
    a = ap.parse_args()
    repo = os.environ.get("GITHUB_REPOSITORY", f"{OWNER}/footyalmanac")
    if a.delegate:
        made = delegate(repo, a.issue)
        with open(f"{OUT}/delegated.md", "w") as f:
            for owner, title, url in made: f.write(f"- {AGENTS[owner].split(',')[0]}: [{title}]({url})\n")
        print(f"{len(made)} task(s) delegated"); return
    issue, turns = thread(repo, a.issue)
    out = os.environ.get("GITHUB_OUTPUT", "/dev/stdout")
    labels = {l["name"] for l in issue.get("labels") or []}
    skip = "ceo" not in labels or not turns or turns[-1][0] != "Douglas"
    os.makedirs(OUT, exist_ok=True)
    with open(out, "a") as f:
        f.write(f"skip={'1' if skip else '0'}\nissue={a.issue}\n")
        if not skip:
            f.write(f"prompt<<__EOF__\n{build(a.issue, turns)}\n__EOF__\n")
    print("skip" if skip else f"Elena briefed on #{a.issue} ({len(turns)} turns)")


if __name__ == "__main__":
    main()
