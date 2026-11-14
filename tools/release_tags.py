"""Tag every release in RELEASES.md that has no tag yet (14 Nov 2026).

Douglas, 14 Nov 2026: "I'm not going to add tags myself so can we find
another way?" Cloud sessions cannot push tags (GitHub drops the connection)
and the API proxy refuses tag writes, so releases merged from them have sat
"(tag pending)" since 11 Nov; only the office's own merges were tagged (by
footyalmanac-hq). `release-tags.yml` runs this on every push to main.

An entry is tagged when its header reads `## YYYY-MM-DD:` or
`## YYYY-MM-DD-N:` (the release id, then a colon). The tag is
`release-<id>`, annotated with the header's title, on the first first-parent
commit of main that added that header line: the merge that shipped it.
Headers with no id of that shape ("## 2026-11-12 (tag pending)") and ids
that appear twice are skipped and listed, never guessed. An existing tag is
never moved. Standard library only.

    python3 tools/release_tags.py            # list what would be tagged
    python3 tools/release_tags.py --apply    # create the tags locally
    python3 tools/release_tags.py --apply --remote origin   # CI: tags read from the remote
"""
import argparse, re, subprocess, sys

HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2}(?:-\d+)?): (.+?)\s*$")
PENDING = re.compile(r"\s*\(tag pending\)\s*$", re.I)


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def entries(text):
    """[(id, title, header line)] for every well-formed header, and the
    headers skipped (no id of the right shape, or an id seen twice)."""
    found, skipped, seen = [], [], {}
    for line in text.splitlines():
        if not line.startswith("## "): continue
        m = HEADER.match(line)
        if not m:
            skipped.append(line); continue
        rid = m.group(1)
        seen[rid] = seen.get(rid, 0) + 1
        found.append((rid, PENDING.sub("", m.group(2)), line))
    dup = {k for k, v in seen.items() if v > 1}
    skipped += [l for r, _, l in found if r in dup]
    return [e for e in found if e[0] not in dup], skipped


def commit_of(line, ref="HEAD"):
    """The first first-parent commit that added this exact header line."""
    out = git("log", ref, "--first-parent", "--reverse", "--format=%H", "-S", line, "--", "RELEASES.md").split()
    return out[0] if out else None


def existing(remote=None):
    """Release tags already made: on the remote when given (a shallow CI
    checkout fetches no tags), else local."""
    if remote:
        out = git("ls-remote", "--tags", "--refs", remote, "refs/tags/release-*")
        return {l.split("refs/tags/", 1)[1] for l in out.splitlines() if "refs/tags/" in l}
    return set(git("tag", "--list", "release-*").split())


def plan(ref="HEAD", remote=None):
    text = git("show", f"{ref}:RELEASES.md")
    have = existing(remote)
    todo, skipped = [], []
    found, bad = entries(text)
    skipped += [f"no id: {l}" for l in bad]
    for rid, title, line in found:
        tag = f"release-{rid}"
        if tag in have: continue
        sha = commit_of(line, ref)
        if not sha:
            skipped.append(f"commit not in history: {line}"); continue
        todo.append((tag, sha, title))
    return todo, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--remote", help="read existing tags from this remote (CI)")
    a = ap.parse_args()
    todo, skipped = plan(a.ref, a.remote)
    for tag, sha, title in todo:
        print(f"{tag} -> {sha[:7]}  {title}")
        if a.apply:
            git("tag", "-a", tag, sha, "-m", title)
    for s in skipped[:10]:
        print(f"skipped: {s}", file=sys.stderr)
    if len(skipped) > 10:
        print(f"skipped: ... and {len(skipped) - 10} more (older headers without an id, or past the history)", file=sys.stderr)
    print(f"{len(todo)} tag(s) {'created' if a.apply else 'to create'}, {len(skipped)} header(s) skipped")


if __name__ == "__main__":
    main()
