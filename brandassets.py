#!/usr/bin/env python3
"""
Draw the home-screen and browser icons.

    python3 brandassets.py

Why these exist as files
-----------------------
iOS fetches the touch icon when someone adds the page to their home screen, so
it has to sit at a real URL. It cannot be a data URI and it cannot be an SVG.
The browser favicon is inlined into the page instead, because dashboard.html is
meant to survive being emailed or opened off a disk.

The icon
--------
A single slab-serif A, white on the masthead's red, inside a yellow keyline in
the year band's yellow. One letter is all that survives at 60 points, which is
the size iOS actually renders a home-screen icon. The A is set in Bevan, the
same face as FOOTBALL on the cover, so the icon is a crop of the identity
rather than a separate mark that happens to sit near it.

Why the keyline is curved
-------------------------
iOS masks every home-screen icon to a superellipse with its own rounded
corners. The previous icon drew a square black border, and the mask cut
straight through its corners: square ink on the straight edges, clipped
slivers at the corners, a frame that visibly did not belong to its own shape.

So the keyline is not drawn as a border at all. The whole square is filled
yellow and the red field is a superellipse set inside it. iOS then trims the
outside to its mask, and what is left is a yellow band of even width that
follows the mask all the way round, corners included. Nothing in the PNG is
rounded or transparent, which is what iOS wants: it does the rounding itself,
and transparency is composited against black.

Other things that catch people out on iOS:

  - The mask cuts further in than people expect. The letter is sized to a safe
    area well inside the red field, so it keeps its feet.
  - Every icon is opaque RGB.

The font is vendored under fonts/ with its OFL licence so this regenerates
anywhere, including on a runner with no fonts installed.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "Bevan-Regular.ttf")

RED = (200, 16, 46)        # the masthead's red, #c8102e
RED_DEEP = (122, 8, 26)    # the same red in shadow, for the letter's offset
YELLOW = (244, 210, 28)    # the year band, #f4d21c
WHITE = (255, 255, 255)

DRAW_AT = 1024             # drawn large, downsampled: cleaner edges than
                           # drawing small, and one source for every size
KEYLINE = 0.058            # yellow band, as a share of the icon's width
SUPER_N = 5.0              # superellipse exponent that tracks the iOS mask
LETTER = 0.60              # the A's largest dimension, as a share of the icon
OFFSET = 0.022             # the hard shadow the cover uses, in icon widths


def _superellipse(size, inset, n=SUPER_N, steps=720):
    """Points round a superellipse filling the square less `inset` each side."""
    import math
    c = size / 2
    r = size / 2 - inset
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        ct, st = math.cos(t), math.sin(t)
        x = c + r * (abs(ct) ** (2 / n)) * (1 if ct >= 0 else -1)
        y = c + r * (abs(st) ** (2 / n)) * (1 if st >= 0 else -1)
        pts.append((x, y))
    return pts


def _letter(size=DRAW_AT):
    im = Image.new("RGB", (size, size), YELLOW)
    d = ImageDraw.Draw(im)
    d.polygon(_superellipse(size, size * KEYLINE), fill=RED)

    # Fit the A by measuring rather than guessing: the same letter at the same
    # point size is a different height in every face.
    target = size * LETTER
    fs = int(size * 0.9)
    while fs > 8:
        font = ImageFont.truetype(FONT, fs)
        b = d.textbbox((0, 0), "A", font=font)
        if max(b[2] - b[0], b[3] - b[1]) <= target:
            break
        fs = int(fs * 0.98)

    w, h = b[2] - b[0], b[3] - b[1]
    off = size * OFFSET
    # Optically centred, not mathematically: the shadow falls down and to the
    # right, so the letter is nudged up and left by half of it.
    x = (size - w) / 2 - b[0] - off / 2
    y = (size - h) / 2 - b[1] - off / 2
    d.text((x + off, y + off), "A", font=font, fill=RED_DEEP)
    d.text((x, y), "A", font=font, fill=WHITE)
    return im


# 180 is the iPhone touch icon. The rest cover iPad, older devices, and the
# favicon, all downsampled from the same drawing so nothing drifts.
SIZES = [180, 167, 152, 120, 64, 32]


def main():
    if not os.path.exists(FONT):
        raise SystemExit(f"missing {FONT} — the icon is set in it")
    master = _letter()
    for s in SIZES:
        out = os.path.join(HERE, f"icon-{s}.png")
        master.resize((s, s), Image.LANCZOS).save(out, optimize=True)
        print(f"wrote {os.path.basename(out)}")

    # The favicon goes into the page as a data URI, so the page is kept in
    # step here rather than by someone remembering to paste it.
    import base64, re
    with open(os.path.join(HERE, "icon-64.png"), "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    page = os.path.join(HERE, "index.html")
    if os.path.exists(page):
        html = open(page, encoding="utf-8").read()
        new, n = re.subn(r'(<link rel="icon" type="image/png" sizes="64x64" href="data:image/png;base64,)[^"]*(")',
                         lambda m: m.group(1) + b64 + m.group(2), html, count=1)
        if n:
            open(page, "w", encoding="utf-8").write(new)
            print("updated the favicon in index.html")


if __name__ == "__main__":
    main()
