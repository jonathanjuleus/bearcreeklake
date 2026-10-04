#!/usr/bin/env python3
"""
Sponsor logo prep
=================
Takes logo screenshots/files you provide and prepares them for the sponsors page.
It NEVER redraws or recolors a logo. It only:
  1. crops the empty margin around it (transparent edge, or a solid-color edge)
  2. shrinks it if it's larger than needed (never enlarges)
  3. saves it as an optimized PNG in images/sponsors/<slug>.png

Usage (run from the repo root):
  python3 tools/process_logos.py ultimate-direction=/path/to/ud.png quinn-snacks=/path/to/quinn.png ...

Slugs used by sponsors.html:
  ultimate-direction  bobs-pickle-pops  salty-britches  red-silo-coffee  quinn-snacks  plain-am

Cards display logos at up to 80px tall on a WHITE tile, so for a sharp result on
phones the source should be at least ~160px tall. The script warns if it's smaller,
and warns if the logo has a non-white background or looks white/light (it would
disappear on the white tile).
"""
import sys, os
from PIL import Image

OUT_DIR = "images/sponsors"
MAX_H, MAX_W = 200, 560
PAD_FRAC = 0.04
THRESH = 28  # how different from the edge color a pixel must be to count as "logo"


def edge_color(im):
    px = im.convert("RGB").load()
    w, h = im.size
    pts = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1],
           px[w // 2, 0], px[w // 2, h - 1], px[0, h // 2], px[w - 1, h // 2]]
    pts.sort()
    return pts[len(pts) // 2]  # median-ish


def crop_to_content(im):
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    a_min, _ = alpha.getextrema()
    note = ""
    if a_min < 250:  # real transparency
        bbox = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
        note = "transparent background"
    else:
        bg = edge_color(im)
        rgb = im.convert("RGB")
        diff = Image.new("L", im.size, 0)
        dpx, spx = diff.load(), rgb.load()
        w, h = im.size
        for y in range(h):
            for x in range(w):
                r, g, b = spx[x, y]
                d = max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2]))
                dpx[x, y] = 255 if d > THRESH else 0
        bbox = diff.getbbox()
        note = f"solid background rgb{bg}"
        if min(bg) < 235:
            note += "  <-- NOT white; it will show as a colored box on the white tile"
    if not bbox:
        return im, note + " (no content found, left uncropped)"
    l, t, r, b = bbox
    pad = int(max(r - l, b - t) * PAD_FRAC)
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(im.width, r + pad), min(im.height, b + pad)
    return im.crop((l, t, r, b)), note


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)
    for arg in sys.argv[1:]:
        slug, _, path = arg.partition("=")
        if not path or not os.path.exists(path):
            print(f"!! {slug}: file not found ({path})"); continue
        im, note = crop_to_content(Image.open(path))
        scale = min(1.0, MAX_H / im.height, MAX_W / im.width)
        if scale < 1.0:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        out = os.path.join(OUT_DIR, f"{slug}.png")
        im.save(out, optimize=True)
        warn = []
        if im.height < 120:
            warn.append(f"low-res ({im.height}px tall) - may look soft on phones; a bigger screenshot would be better")
        # light-logo check: mostly very light visible pixels
        rgb = im.convert("RGBA")
        raw = rgb.tobytes()
        px = [tuple(raw[i:i+4]) for i in range(0, len(raw), 4) if raw[i+3] > 200]
        if px and sum(1 for p in px if min(p[:3]) > 225) / len(px) > 0.9 and "transparent" in note:
            warn.append("logo looks white/light - it will vanish on the white tile")
        print(f"ok  {slug}: {im.width}x{im.height}  [{note}]")
        for w in warn:
            print(f"    WARNING: {w}")


if __name__ == "__main__":
    main()
