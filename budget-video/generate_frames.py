#!/usr/bin/env python3
"""
Weekly budget reveal video — frame generator
=============================================
Regenerates the full set of transparent 1080x1920 PNG frames for the
"What it actually costs" CapCut budget video.

HOW TO USE EACH WEEK
---------------------
1. Edit the CONFIG block below:
   - SIGNUPS, REVENUE: this week's numbers
   - SECTIONS: list of (category name, item names, amount) tuples.
     The item names show as one comma-joined line in the orange box.
     Amount is the TOTAL for that whole category (not per item).
   - BREAKEVEN_COUNT: how many more signups are needed to hit net $0
     (compute as: ceil(abs(final remaining) / price_per_signup))

2. Run it:
     python3 generate_frames.py

3. Frames land in ./output/, named so they sort into the right order:
     01a_<category>.png   -> category reveal (bar + orange box)
     01b_transition.png   -> bar only, holds that category's new total
     ...one pair per section...
     99_breakeven.png     -> closing "we need N more signups" card

4. Pull the PNGs into CapCut in numeric filename order. Each category
   pair (Xa then Xb) is one beat: reveal, then hold before the next.

DESIGN NOTES (so future edits stay consistent)
------------------------------------------------
- Brand colors: bg navy #12141C/#1B1F2A, cream text #EDE6D8,
  ember accent #DB6B2C, muted #B9B2A4, line #343B4E. Fraunces for
  headlines/numbers, Public Sans for labels/body.
- Frames are TRANSPARENT (only cards/boxes have solid fill) so they
  can sit directly over video footage in CapCut.
- "Remaining Cash" in the top bar auto-turns ember orange the moment
  it goes negative — that's the emotional beat, don't remove it.
- The breakeven card's top spacer is weighted (flex-grow:2.4 vs a
  fixed 70px bottom gap) to keep the box in the bottom third of the
  frame, clear of a face if this gets overlaid on a talking-head shot.
  Adjust that ratio if a future shot needs the box even lower/higher.
"""

import subprocess, sys, math, os

# ============================== CONFIG ==============================

SIGNUPS = 37
REVENUE = 2220

# (category name, "Item, Item, Item" label, category total spend)
SECTIONS = [
    ("Permits & Fees", "Permit Cost, Entrance Fee, Trail Fee, Hut Fee", 962),
    ("Legal & Insurance", "LLC, Insurance, ATRA Membership", 543),
    ("Medical & Safety", "Misc Supplies, Bones", 404),
    ("Race Supplies", "Flags, Bibs, Misc, Digital Clock, Pickle Juice Shipping, Asana", 476),
    ("Food", "Food", 500),
]

BREAKEVEN_COUNT = 13  # how many more signups needed to reach net $0

OUT_DIR = "output"

# ============================ END CONFIG =============================


def fmt(n):
    neg = n < 0
    n = abs(round(n))
    s = f"${n:,}"
    return f"-{s}" if neg else s


HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0;}
  html,body{background:transparent;}
  body{font-family:'Public Sans',sans-serif;}
  .sh{text-shadow:0 2px 10px rgba(0,0,0,0.85);}
</style></head><body>"""


def header():
    return f'''<div class="sh" style="font-family:'Public Sans',sans-serif;font-weight:700;font-size:18px;letter-spacing:3px;color:#DB6B2C;text-transform:uppercase;">11th Hour Backyard Ultra</div>
  <div class="sh" style="font-family:'Fraunces',serif;font-weight:600;font-size:64px;line-height:1.05;color:#EDE6D8;margin-top:14px;">What it actually<br>costs</div>
  <div class="sh" style="font-size:20px;color:#B9B2A4;margin-top:10px;">{SIGNUPS} signups so far</div>'''


def bar(remaining, right_label="Remaining Cash"):
    color = "#DB6B2C" if remaining < 0 else "#EDE6D8"
    return f'''<div style="margin-top:40px;background:#1B1F2A;border:1px solid #343B4E;border-radius:14px;padding:32px 36px;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <div style="font-size:14px;font-weight:700;letter-spacing:2px;color:#B9B2A4;text-transform:uppercase;">Total Revenue</div>
      <div style="font-family:'Fraunces',serif;font-weight:700;font-size:60px;color:#EDE6D8;margin-top:6px;">{fmt(REVENUE)}</div>
    </div>
    <div style="width:1px;align-self:stretch;background:#343B4E;margin:0 28px;"></div>
    <div style="text-align:right;">
      <div style="font-size:14px;font-weight:700;letter-spacing:2px;color:#DB6B2C;text-transform:uppercase;">{right_label}</div>
      <div style="font-family:'Fraunces',serif;font-weight:700;font-size:60px;color:{color};margin-top:6px;">{fmt(remaining)}</div>
    </div>
  </div>'''


def category_frame(name, items_label, spend, remaining):
    body = f'''<div style="width:1080px;height:1920px;background:transparent;color:#EDE6D8;position:relative;overflow:hidden;">
<div style="padding:90px 76px 60px;height:100%;display:flex;flex-direction:column;">
  {header()}
  {bar(remaining)}
  <div class="sh" style="font-family:'Fraunces',serif;font-weight:600;font-size:28px;color:#DB6B2C;margin-top:36px;margin-bottom:14px;">{name}</div>
  <div style="background:rgba(219,107,44,0.14);border:1.5px solid #DB6B2C;border-radius:12px;padding:26px 30px;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:16px;font-weight:600;color:#EDE6D8;">{items_label}</div>
    <div style="font-family:'Fraunces',serif;font-weight:700;font-size:44px;color:#DB6B2C;">&minus;{fmt(spend)[1:] if False else '$' + f'{spend:,}'}</div>
  </div>
  <div style="flex-grow:1;"></div>
</div>
</div>'''
    return HEAD + body + "</body></html>"


def transition_frame(remaining):
    body = f'''<div style="width:1080px;height:1920px;background:transparent;color:#EDE6D8;position:relative;overflow:hidden;">
<div style="padding:90px 76px 60px;height:100%;display:flex;flex-direction:column;">
  {header()}
  {bar(remaining)}
  <div style="flex-grow:1;"></div>
</div>
</div>'''
    return HEAD + body + "</body></html>"


def breakeven_frame(final_remaining, breakeven_count):
    body = f'''<div style="width:1080px;height:1920px;background:transparent;color:#EDE6D8;position:relative;overflow:hidden;">
<div style="padding:90px 76px 60px;height:100%;display:flex;flex-direction:column;">
  {header()}
  {bar(final_remaining, right_label="Current Net")}
  <div style="flex-grow:2.4;"></div>
  <div style="text-align:center;background:#DB6B2C;border-radius:16px;padding:52px 32px;">
    <div style="font-size:17px;font-weight:700;letter-spacing:2px;color:#12141C;text-transform:uppercase;">We need</div>
    <div style="font-family:'Fraunces',serif;font-weight:700;font-size:160px;line-height:1;color:#12141C;margin-top:8px;">{breakeven_count}</div>
    <div style="font-family:'Fraunces',serif;font-weight:600;font-size:36px;color:#12141C;margin-top:10px;">more sign-ups<br>to break even</div>
  </div>
  <div style="height:70px;"></div>
</div>
</div>'''
    return HEAD + body + "</body></html>"


def slug(name):
    return name.split(" ")[0].lower()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    html_dir = os.path.join(OUT_DIR, "_html")
    os.makedirs(html_dir, exist_ok=True)

    running = REVENUE
    html_files = []

    for i, (name, items, spend) in enumerate(SECTIONS, start=1):
        running -= spend
        cat_path = os.path.join(html_dir, f"{i:02d}a_{slug(name)}.html")
        with open(cat_path, "w") as f:
            f.write(category_frame(name, items, spend, running))
        html_files.append(cat_path)

        trans_path = os.path.join(html_dir, f"{i:02d}b_transition.html")
        with open(trans_path, "w") as f:
            f.write(transition_frame(running))
        html_files.append(trans_path)

        print(f"{name}: -${spend} -> remaining {fmt(running)}")

    be_path = os.path.join(html_dir, "99_breakeven.html")
    with open(be_path, "w") as f:
        f.write(breakeven_frame(running, BREAKEVEN_COUNT))
    html_files.append(be_path)

    print(f"\nFinal remaining: {fmt(running)}")
    print(f"Breakeven card says: {BREAKEVEN_COUNT} more signups\n")

    # Render every HTML file to a transparent PNG via headless Chromium.
    render_script = f"""
from playwright.sync_api import sync_playwright
files = {html_files!r}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={{'width':1080,'height':1920}})
    for fpath in files:
        import os as _os
        pg.goto('file://' + _os.path.abspath(fpath))
        pg.wait_for_timeout(150)
        out_name = fpath.split('/')[-1].replace('.html', '.png')
        pg.screenshot(path='{OUT_DIR}/' + out_name, omit_background=True)
        print('rendered', out_name)
    b.close()
"""
    subprocess.run([sys.executable, "-c", render_script], check=True)
    print(f"\nAll frames written to ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
