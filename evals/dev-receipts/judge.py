"""Independent check of one run's final commit, served at URL.

usage: judge.py URL OUT_PREFIX
Loads the page as staff 1, measures how much text it shows, counts swap
controls and records console errors at phone and desktop width.
"""
import json
import re
import sys
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("desktop", {"width": 1280, "height": 800}), ("mobile", {"width": 390, "height": 844})):
        ctx = b.new_context(viewport=vp)
        ctx.add_cookies([{"name": "staff", "value": "1", "url": url}])
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        pg.on("console", lambda m: errs.append(m.text[:160]) if m.type == "error" else None)
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_timeout(500)
        swap = pg.locator("button, select, a").filter(has_text=re.compile("swap", re.I))
        res[name] = {
            "bodyTextChars": len(pg.inner_text("body")),
            "swapControls": swap.count(),
            "overflowX": pg.evaluate("document.documentElement.scrollWidth > innerWidth"),
            "errors": errs,
        }
        pg.screenshot(path=f"{out}-{name}.png", full_page=True)
        ctx.close()
    b.close()
print(json.dumps(res))
