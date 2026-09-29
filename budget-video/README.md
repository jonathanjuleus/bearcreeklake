# Weekly budget video frames

Run `python3 generate_frames.py` from this folder to regenerate the full set of
transparent 1080x1920 PNG frames for the "What it actually costs" CapCut series.

Each week: open `generate_frames.py`, update the numbers at the top
(SIGNUPS, REVENUE, SECTIONS, BREAKEVEN_COUNT), run it, then pull the new
PNGs from `output/` into CapCut in filename order.

See the big docstring at the top of the script for the full breakdown of
what each config field controls and the design notes (colors, fonts, why
"Remaining Cash" flips orange, why the breakeven box sits low in frame).
