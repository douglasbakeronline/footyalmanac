"""Google Tag Manager on every published page (16 Nov 2026).

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
TAG = f"""<!-- Google Tag Manager (16 Nov 2026, Douglas). On every page: tools/tag_pages.py adds it on deploy if missing. -->
<script async src="https://www.googletagmanager.com/gtm.js?id={GTM_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
</script>
"""
HEAD = re.compile(r"<head[^>]*>\s*(<meta\s+charset=[^>]*>\s*)?", re.I)


def has_tag(html):
    return f"gtm.js?id={GTM_ID}" in html


def add_tag(html):
    """The page with the tag after <head> (and its charset line); unchanged if
    it already has it or has no <head>."""
    if has_tag(html):
        return html
    m = HEAD.search(html)
    if not m:
        return html
    return html[:m.end()] + TAG + html[m.end():]


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
