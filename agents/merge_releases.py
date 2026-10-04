"""Resolve a RELEASES.md rebase conflict by keeping both sides: the agent's new entry on top of main's."""
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else "RELEASES.md"
s = open(p).read()
pat = re.compile(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n", re.S)
def keep(m):
    main_side, agent_side = m.group(1), m.group(2)
    # agent_side = the agent's entry followed by the old top entry, which main_side also ends with
    return agent_side.rstrip("\n") + "\n\n" + main_side
s, n = pat.subn(keep, s)
if "<<<<<<<" in s or not n: sys.exit(1)
open(p, "w").write(s)
