"""Google Tag Manager on every page (16 Nov 2026, Douglas: "add this to every
page and make sure it gets added to all future pages")."""
import glob, os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "tools"))
import tag_pages as T

# dashboard.html is build output from index.html (CLAUDE.md: edit index.html, never dashboard.html), so it
# takes the tag from there on the next build; every other page must carry it in its own source.
NOT_PUBLISHED = {"dashboard.html"}


class EveryPage(unittest.TestCase):
    def test_every_html_page_in_the_repo_has_the_tag(self):
        skip = ("julius/", "audit-out/", "node_modules/", "_site/")
        out = subprocess.run(["git", "ls-files", "*.html"], cwd=HERE, capture_output=True, text=True).stdout.split()
        paths = [p for p in out if not p.startswith(skip) and p not in NOT_PUBLISHED] or \
            [os.path.relpath(p, HERE) for p in glob.glob(os.path.join(HERE, "*.html"))]
        self.assertIn("index.html", paths)
        missing = [p for p in paths if not T.has_tag(open(os.path.join(HERE, p), encoding="utf-8").read())]
        self.assertEqual(missing, [], "add tools/tag_pages.TAG to these pages' <head>")

    def test_the_tag_is_the_one_douglas_gave(self):
        self.assertIn('src="https://www.googletagmanager.com/gtm.js?id=GTM-WP7C2F6B"', T.TAG)
        self.assertIn("function gtag(){dataLayer.push(arguments);}", T.TAG)
        self.assertIn("gtag('js', new Date());", T.TAG)


class TabViews(unittest.TestCase):
    def test_every_tab_change_is_sent_to_tag_manager(self):
        # 16 Nov 2026: tabs change without a page load, so the view switch pushes a tab_view event.
        page = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
        switch = page[page.index("/* ---------- view switching ---------- */"):]
        self.assertIn('event: "tab_view"', switch[:switch.index("window.scrollTo({top:0});")])


class AddTag(unittest.TestCase):
    def test_added_after_head_and_charset_once(self):
        page = '<!DOCTYPE html>\n<html><head>\n<meta charset="utf-8">\n<title>x</title></head><body></body></html>'
        out = T.add_tag(page)
        self.assertTrue(out.index("gtm.js") > out.index("charset") and out.index("gtm.js") < out.index("<title>"))
        self.assertEqual(T.add_tag(out), out)

    def test_a_page_without_head_is_left_alone(self):
        self.assertEqual(T.add_tag("<p>hi</p>"), "<p>hi</p>")


if __name__ == "__main__":
    unittest.main()
