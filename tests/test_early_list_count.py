"""The masthead's list count runs listShown while index.html is still loading,
before lbKey and the other consts further down exist. On 27 Nov 2026 listShown
called pickPrice (which reads lbKey), the script stopped with "Cannot access
'lbKey' before initialization", and the Daily List and the tab bar went dead.
listShown and itemPrice must call only function declarations that are safe
that early."""
import re
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
UNSAFE = ("lbKey", "pickPrice", "hillPrice", "itemHill", "collegeTier(", "GL_KEEP")


def body(name):
    m = re.search(r"function %s\(" % name, HTML)
    assert m, name
    i, depth = HTML.index("{", m.end()), 0
    for j in range(i, len(HTML)):
        depth += {"{": 1, "}": -1}.get(HTML[j], 0)
        if depth == 0:
            return HTML[i:j + 1]


class EarlyListCount(unittest.TestCase):
    def test_item_price_is_load_safe(self):
        b = body("itemPrice")
        for u in UNSAFE:
            self.assertNotIn(u, b, f"itemPrice calls {u}, which may not exist yet when the masthead counts")

    def test_list_shown_calls_only_load_safe_helpers(self):
        b = body("listShown")
        for u in ("lbKey", "pickPrice", "hillPrice", "itemHill", "GL_KEEP"):
            self.assertNotIn(u, b)

    def test_masthead_count_still_comes_before_lbkey(self):
        # if this ever flips, the guard above can be relaxed
        self.assertLess(HTML.index("listShown(g)).length + _tennis"), HTML.index("const lbKey ="))


if __name__ == "__main__":
    unittest.main()
