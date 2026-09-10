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
A single slab-serif A, white on the masthead's red, inside the black keyline
the cover uses. One letter is all that survives at 60 points, which is the size
iOS actually renders a home-screen icon: the wordmark, the star band and the
year band all turn to mush well before that. The A is set in Bevan, the same
face as FOOTBALL on the cover, so the icon is a crop of the identity rather
than a separate mark that happens to sit near it.

Two things that catch people out on iOS, both handled here:

  - The corners are masked to a superellipse, not a rounded rectangle, and it
    cuts further in than people expect. Everything is drawn inside a safe area
    of 80%, so the letter keeps its feet.
  - Transparency is composited against black. Every icon is opaque RGB.

The font is vendored under fonts/ with its OFL licence so this regenerates
anywhere, including on a runner with no fonts installed.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "Bevan-Regular.ttf")

RED = (200, 16, 46)        # the masthead's red
INK = (16, 14, 12)
WHITE = (255, 255, 255)

DRAW_AT = 1024             # drawn large, downsampled: cleaner edges than
                           # drawing small, and one source for every size
SAFE = 0.80                # iOS masks the corners harder than it looks
KEYLINE = 0.050
OFFSET = 0.026             # the hard shadow the cover uses, in em


def _letter(size=DRAW_AT):
    # Ink is the ground and the red sits inside it, rather than a red ground
    # with an ink rectangle drawn on top. The mask is a superellipse and a
    # rectangle's corners fall outside it, so drawing the keyline as a shape
    # leaves four slivers of red at the corners where the mask cuts through it.
    # This way the outermost pixel is black whichever way the mask falls.
    im = Image.new("RGB", (size, size), INK)
    d = ImageDraw.Draw(im)
    k = size * KEYLINE
    d.rectangle([k, k, size - k, size - k], fill=RED)

    # Fit the A to the safe area rather than the square, measuring rather than
    # guessing: the same letter at the same point size is a different height in
    # every face, and this has to be right in one shot.
    fs = int(size * SAFE)
    while fs > 8:
        font = ImageFont.truetype(FONT, fs)
        b = d.textbbox((0, 0), "A", font=font)
        if (b[2] - b[0]) <= size * SAFE and (b[3] - b[1]) <= size * SAFE:
            break
        fs = int(fs * 0.97)

    w, h = b[2] - b[0], b[3] - b[1]
    x = (size - w) / 2 - b[0]
    # Optically centred, not mathematically: the hard shadow falls down and to
    # the right, so the letter is nudged up and left to compensate.
    y = (size - h) / 2 - b[1] - size * OFFSET * 0.45
    off = size * OFFSET
    d.text((x + off, y + off), "A", font=font, fill=INK)
    d.text((x - size * OFFSET * 0.15, y), "A", font=font, fill=WHITE)

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

    # The favicon goes into the page as a data URI, so print it ready to paste
    # if the icon is ever redrawn.
    import base64
    with open(os.path.join(HERE, "icon-64.png"), "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    print(f"\nfavicon data URI is {len(b64)} chars; the <link rel=icon> in "
          f"index.html carries a copy of it")


if __name__ == "__main__":
    main()
