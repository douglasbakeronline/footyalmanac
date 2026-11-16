"""Google Tag Manager and Google Analytics on every published page (16 Nov 2026).

Douglas, 16 Nov 2026: "Please add this to every page and make sure it gets
added to all future pages". The tag sits in the source of each page
(`index.html`, `analysis.html`); this script is the backstop. deploy.yml runs
it over `_site/` before the upload, so a page added later without the tag gets
it inserted on publish, straight after `<head>`, and the build log names it.
`tests/test_tag_pages.py` fails CI when a page in the repo lacks it.

    python3 tools/tag_pages.py _site            # add the tag where missing
    python3 tools/tag_pages.py --check _site    # list pages without it, exit 1

Standard library only.
"""
import argparse, glob, os, re, sys

GTM_ID = "GTM-WP7C2F6B"
# 16 Nov 2026: Google Analytics 4 straight from the page (Douglas's stream "Sports Almanac", measurement
# ID from GA Admin -> Data streams), as the GTM container held no Google tag and GA showed "No data
# received". Don't also add a Google tag for this ID inside GTM: every view would count twice.
GA_ID = "G-35788M25WE"
TAG = f"""<!-- Google Tag Manager (16 Nov 2026, Douglas). On every page: tools/tag_pages.py adds it on deploy if missing. -->
<script async src="https://www.googletagmanager.com/gtm.js?id={GTM_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
</script>
"""
GA_TAG = f"""<!-- Google Analytics 4, direct (16 Nov 2026). Tabs are sent as tab_view events from index.html. -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>gtag('config', '{GA_ID}');</script>
"""
HEAD = re.compile(r"<head[^>]*>\s*(<meta\s+charset=[^>]*>\s*)?", re.I)


def has_gtm(html):
    return f"gtm.js?id={GTM_ID}" in html


def has_ga(html):
    return f"gtag/js?id={GA_ID}" in html


def has_tag(html):
    return has_gtm(html) and has_ga(html)


def add_tag(html):
    """The page with the tags after <head> (and its charset line): Tag Manager
    first (it defines gtag), then Analytics. Each is added only if missing;
    unchanged if the page has no <head>."""
    if has_tag(html):
        return html
    if not has_gtm(html):
        m = HEAD.search(html)
        if not m:
            return html
        html = html[:m.end()] + TAG + html[m.end():]
    if not has_ga(html):
        i = html.index("gtag('js', new Date());")
        i = html.index("</script>", i) + len("</script>\n")
        html = html[:i] + GA_TAG + html[i:]
    return html


def pages(root):
    return sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="_site")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    missing, added = [], []
    for p in pages(a.root):
        with open(p, encoding="utf-8") as f:
            html = f.read()
        if has_tag(html):
            continue
        if a.check:
            missing.append(p); continue
        new = add_tag(html)
        if new == html:
            missing.append(p); continue
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        added.append(p)
    for p in added:
        print(f"::warning::{p} had no Google Tag Manager tag; added on publish (add it to the page's source)")
    for p in missing:
        print(f"{'missing' if a.check else 'no <head>, not tagged'}: {p}", file=sys.stderr)
    print(f"tag_pages: {len(pages(a.root))} page(s), {len(added)} tagged now, {len(missing)} without the tag")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
