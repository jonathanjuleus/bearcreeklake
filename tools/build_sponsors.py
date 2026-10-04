#!/usr/bin/env python3
"""
Sponsor page + tracked-link generator
=====================================
Single source of truth: tools/sponsors.json  (slug, name, url)

Run from the repo root after editing it:
    python3 tools/build_sponsors.py

It rewrites two generated regions (between the START/END markers):
  1. the sponsor cards in sponsors.html
  2. the sponsor lookup table in sponsor-redirect.html (powers /go/<slug>)

Tracking you get for every sponsor with a url:
  - Mixpanel event "Sponsor Click" {sponsor, slug, via, ...}
      via = "sponsors_page"  -> clicked the logo on the website
      via = "redirect"       -> used a /go/<slug> link (email, Instagram, QR, cards)
  - UTM tags on the outbound link so the sponsor sees you in THEIR analytics:
      utm_source=bearcreekbackyardultra  utm_medium=<channel>  utm_campaign=11th_hour_backyard_ultra

A sponsor with url=null still gets a card (logo only), just no link/tracking yet.
Logo files go in images/sponsors/<slug>.png (see tools/process_logos.py).
"""
import json, re, sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

SOURCE = "bearcreekbackyardultra"
CAMPAIGN = "11th_hour_backyard_ultra"


def with_utm(url, medium, content):
    p = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not k.startswith("utm_")]
    q += [("utm_source", SOURCE), ("utm_medium", medium), ("utm_campaign", CAMPAIGN), ("utm_content", content)]
    return urlunsplit((p.scheme, p.netloc, p.path or "/", urlencode(q), p.fragment))


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def card(s):
    name, slug, url = s["name"], s["slug"], s["url"]
    img = f'<img src="images/sponsors/{slug}.png" alt="{esc(name)}">'
    if url:
        href = esc(with_utm(url, "sponsor_page", "logo"))
        return (f'      <a class="sponsor-card" data-sponsor="{esc(name)}" data-slug="{slug}" href="{href}" '
                f'target="_blank" rel="noopener sponsored" aria-label="{esc(name)}">\n        {img}\n      </a>\n')
    return f'      <div class="sponsor-card" data-sponsor="{esc(name)}" data-slug="{slug}">\n        {img}\n      </div>\n'


def replace_between(text, start, end, new):
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        sys.exit(f"marker not found: {start}")
    return pat.sub(lambda m: start + "\n" + new + end, text, count=1)


def main():
    sponsors = json.load(open("tools/sponsors.json"))
    slugs = [s["slug"] for s in sponsors]
    assert len(slugs) == len(set(slugs)), "duplicate slug in sponsors.json"
    for s in sponsors:
        if s["url"] and not s["url"].startswith("https://"):
            sys.exit(f'{s["name"]}: url must start with https://')

    page = open("sponsors.html").read()
    cards = "".join(card(s) for s in sponsors)
    page = replace_between(page, "<!-- SPONSORS:START -->", "      <!-- SPONSORS:END -->", cards)
    open("sponsors.html", "w").write(page)

    table = ",\n".join(
        f'      {json.dumps(s["slug"])}: {{name: {json.dumps(s["name"])}, url: {json.dumps(s["url"])}}}'
        for s in sponsors if s["url"]
    ) + "\n"
    red = open("sponsor-redirect.html").read()
    red = replace_between(red, "/* SPONSORS:START */", "      /* SPONSORS:END */", table)
    open("sponsor-redirect.html", "w").write(red)

    linked = [s for s in sponsors if s["url"]]
    print(f"{len(sponsors)} sponsors, {len(linked)} with tracked links")
    for s in sponsors:
        print(f'  {s["name"]:<20} {"/go/" + s["slug"] if s["url"] else "(no link yet)"}')


if __name__ == "__main__":
    main()
