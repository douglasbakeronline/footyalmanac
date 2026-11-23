"""The Analysis page in the same shell as the Almanac (23 Nov 2026, UX release 7).

analysis.html ships as its own self-contained page, so it cannot share a
stylesheet with index.html; it carries copies instead. This test fails CI when
the copies drift:

- every custom property in index.html's first :root block is defined in
  analysis.html's with the same value;
- the tab bar's two rows list the same tabs, in the same order, with the same
  labels (index.html's data-view="<view>" is analysis.html's href="./#<view>",
  and index.html's link to analysis.html is analysis.html's aria-current="page");
- the tab bar's CSS block and the .seg block are word for word the same.

Fix a failure by changing index.html (the source) and copying the named block
into analysis.html, or the other way round if the change was meant for both.
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX, ANALYSIS = "index.html", "analysis.html"

NAV_START = "/* ---------- top-level views ----------"
NAV_END = "/* ---------- end of the shared tab bar (23 Nov 2026, UX release 7) ----------"
SEG_START = "/* ---------- one segmented control (23 Nov 2026, UX release 1) ----------"
SEG_END = ".seg--scroll button{flex:0 0 auto}"
SEG_ON = '.seg button[aria-pressed="true"],.seg button[aria-selected="true"]{'


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


def root_tokens(page):
    """name -> value for every custom property in the page's first :root block."""
    i = page.index(":root{")
    body = page[i + len(":root{"):page.index("\n}", i)]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    out = {}
    for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body):
        out[m.group(1)] = " ".join(m.group(2).split())
    return out


def block(page, start, end):
    """The text from `start` to the end of the line holding `end`, or None."""
    if start not in page:
        return None
    i = page.index(start)
    j = page.find(end, i)
    if j < 0:
        return None
    j = page.find("\n", j)
    return page[i:j if j >= 0 else len(page)]


def nav_rows(page):
    """[(row, [(target, label), ...]), ...] for #views's two rows."""
    nav = page[page.index('<nav class="views almanac" id="views"'):]
    nav = nav[:nav.index("</nav>")]
    rows = []
    for row in ("nav-sections", "nav-sports"):
        part = nav[nav.index('class="%s"' % row):]
        part = part[:part.index("</div>")]
        tabs = []
        for m in re.finditer(r"<(button|a)\b([^>]*)>(.*?)</\1>", part, flags=re.S):
            attrs, label = m.group(2), " ".join(re.sub(r"<[^>]+>", "", m.group(3)).split())
            view = re.search(r'data-view="([^"]+)"', attrs)
            href = re.search(r'href="([^"]+)"', attrs)
            if 'aria-current="page"' in attrs:
                target = "analysis.html"
            elif view:
                target = view.group(1)
            elif href and href.group(1).startswith("./#"):
                target = href.group(1)[3:]
            elif href:
                target = href.group(1)
            else:
                target = None
            tabs.append((target, label))
        rows.append((row, tabs))
    return rows


class ShellSync(unittest.TestCase):
    """index.html and analysis.html carry the same tokens, tab bar and segmented control."""

    def setUp(self):
        self.ix, self.an = read(INDEX), read(ANALYSIS)

    def test_root_tokens_match(self):
        a, b = root_tokens(self.ix), root_tokens(self.an)
        self.assertTrue(a, "no :root custom properties found in index.html")
        missing = sorted(k for k in a if k not in b)
        differ = sorted(k for k in a if k in b and a[k] != b[k])
        msg = []
        if missing:
            msg.append("analysis.html's :root lacks " + ", ".join(missing) + ".")
        for k in differ:
            msg.append("%s is %r in index.html but %r in analysis.html." % (k, a[k], b[k]))
        if msg:
            self.fail("The two pages' tokens have drifted. " + " ".join(msg) +
                      " Fix: copy index.html's :root block over analysis.html's (the first <style>).")

    def test_tab_bar_lists_the_same_tabs(self):
        ix, an = nav_rows(self.ix), nav_rows(self.an)
        for (row, a), (_, b) in zip(ix, an):
            # index.html's own Analysis entry is a link; analysis.html marks itself aria-current
            a = [("analysis.html" if t == "analysis.html" else t, lab) for t, lab in a]
            if a != b:
                self.fail("The tab bar's .%s row differs.\n  index.html:    %s\n  analysis.html: %s\n"
                          "Fix: give analysis.html's row the same tabs in the same order, each "
                          "<a href=\"./#<data-view>\"> with the button's label, and its own "
                          "entry aria-current=\"page\" (the <nav id=\"views\"> near the top of analysis.html)."
                          % (row, a, b))

    def test_analysis_marks_itself_current(self):
        i = self.an.index('<nav class="views almanac"')
        nav = self.an[i:self.an.index("</nav>", i)]
        self.assertEqual(nav.count('aria-current="page"'), 1,
                         "analysis.html's tab bar should mark exactly one tab aria-current=\"page\" (its own)")
        self.assertNotIn("nav-on", nav, "analysis.html's tab bar uses aria-current, not the old span.nav-on")

    def _same_block(self, name, start, end):
        a, b = block(self.ix, start, end), block(self.an, start, end)
        self.assertIsNotNone(a, "index.html has no %s block (from %r to %r)" % (name, start, end))
        self.assertIsNotNone(b, "analysis.html has no %s block: copy it from index.html (from %r to %r)"
                             % (name, start, end))
        if a != b:
            al, bl = a.splitlines(), b.splitlines()
            for n, (x, y) in enumerate(zip(al, bl)):
                if x != y:
                    break
            else:
                n = min(len(al), len(bl))
            x = al[n] if n < len(al) else "(end of block)"
            y = bl[n] if n < len(bl) else "(end of block)"
            self.fail("The %s block differs between the pages, first at line %d of the block:\n"
                      "  index.html:    %s\n  analysis.html: %s\n"
                      "Fix: copy index.html's block (from %r to %r) over analysis.html's." % (name, n + 1, x, y, start, end))

    def test_tab_bar_css_matches(self):
        self._same_block("tab bar", NAV_START, NAV_END)

    def test_seg_block_matches(self):
        self._same_block(".seg", SEG_START, SEG_END)

    def test_seg_selected_state_matches(self):
        rule = lambda p: re.search(re.escape(SEG_ON) + r"[^}]*\}", p)
        a, b = rule(self.ix), rule(self.an)
        self.assertIsNotNone(a, "index.html has no .seg selected-state rule")
        self.assertIsNotNone(b, "analysis.html has no .seg selected-state rule (%s...)" % SEG_ON)
        self.assertEqual(a.group(0), b.group(0), ".seg's selected look differs: copy index.html's rule to analysis.html")

    def test_analysis_bands_are_the_sites(self):
        # the day-by-day control uses the site's bands, not cumulative brackets
        src = lambda p: p[p.index("const BANDS = ["):p.index("];", p.index("const BANDS = ["))]
        norm = lambda s: " ".join(s.split())
        self.assertEqual(norm(src(self.ix)), norm(src(self.an)),
                         "analysis.html's BANDS differs from index.html's: copy index.html's const BANDS")
        self.assertNotIn('data-lo="50" data-hi="100"', self.an, "the cumulative 50%+ ... brackets are back")


class Helpers(unittest.TestCase):
    def test_root_tokens_read_values_and_skip_comments(self):
        page = ":root{\n  --a:#fff;   /* note: --b:1px; */\n  --row:1px 2px  3px;\n}\n"
        self.assertEqual(root_tokens(page), {"--a": "#fff", "--row": "1px 2px 3px"})


if __name__ == "__main__":
    unittest.main()
