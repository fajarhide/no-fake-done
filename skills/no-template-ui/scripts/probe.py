#!/usr/bin/env python3
"""Measure rendered pages and save a screenshot per page and viewport.

usage: probe.py OUT_DIR URL [URL ...] [--cookie name=value] [--label before] [--design DESIGN.md]
Prints JSON. Each finding names a selector, so a reader can check it by hand.
Needs Playwright: pip install playwright && playwright install chromium
"""
import glob
import json
import os
import re
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

VIEWPORTS = {"mobile": (390, 844), "desktop": (1280, 800)}

# Runs in the page. Colours go through a canvas so oklch() and color-mix() come
# back as real pixels, and a background that cannot be resolved to one colour
# (image, gradient) is reported as unknown, never guessed.
MEASURE = r"""
() => {
  const ctx = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
  const rgba = (c) => {
    ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1);
    const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data; return [r, g, b, a / 255];
  };
  const over = (f, b) => [0, 1, 2].map((i) => f[i] * f[3] + b[i] * (1 - f[3])).concat(1);
  const lum = (c) => {
    const [r, g, b] = c.slice(0, 3).map((v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
    return .2126 * r + .7152 * g + .0722 * b;
  };
  const ratio = (a, b) => { const [h, l] = [lum(a), lum(b)].sort((x, y) => y - x); return (h + .05) / (l + .05); };
  const seen = (el) => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0 && r.width > 0 && r.height > 0;
  };
  const sel = (el) => {
    if (el.id) return '#' + el.id;
    const cls = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    const p = el.parentElement;
    const nth = p ? `:nth-of-type(${[...p.children].filter((c) => c.tagName === el.tagName).indexOf(el) + 1})` : '';
    return (p && p !== document.body ? sel(p) + ' > ' : '') + el.tagName.toLowerCase() + cls + nth;
  };
  const text = (el) => (el.innerText || el.value || '').trim().replace(/\s+/g, ' ').slice(0, 60);
  const bgOf = (el) => {
    let c = [255, 255, 255, 0];
    for (let n = el; n; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.backgroundImage !== 'none') return null;
      c = c[3] === 1 ? c : over(c, rgba(s.backgroundColor).map((v, i) => i === 3 ? v : v)).slice(0, 3).concat(Math.min(1, c[3] + rgba(s.backgroundColor)[3] * (1 - c[3])));
      if (c[3] >= 1) return c;
    }
    return over(c, [255, 255, 255, 1]);
  };
  const out = { contrast: [], unknownContrast: 0, tapTargets: [], unnamed: [], unlabeled: [], images: [], deadLinks: [], clipped: [], overflow: null, leakedText: [] };
  const hidden = (el) => el.closest('[aria-hidden="true"]');
  const seenText = new Set();

  for (const el of document.querySelectorAll('body *')) {
    if (!seen(el) || hidden(el) || el.closest('[disabled],[aria-disabled="true"]')) continue;
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own) continue;
    const s = getComputedStyle(el), bg = bgOf(el);
    if (!bg) { out.unknownContrast++; continue; }
    const size = parseFloat(s.fontSize), large = size >= 24 || (size >= 18.66 && +s.fontWeight >= 700);
    const r = ratio(over(rgba(s.color), bg), bg), need = large ? 3 : 4.5;
    const key = s.color + bg + size;
    if (r < need && !seenText.has(key)) {
      seenText.add(key);
      out.contrast.push({ selector: sel(el), text: text(el), ratio: +r.toFixed(2), need });
    }
    if (el.scrollWidth > el.clientWidth + 1 && s.overflowX === 'hidden' && s.textOverflow !== 'ellipsis' && !el.title) {
      out.clipped.push({ selector: sel(el), text: text(el) });
    }
  }

  const controls = 'a[href],button,input:not([type=hidden]),select,textarea,[role=button],[role=link],[tabindex]:not([tabindex="-1"])';
  for (const el of document.querySelectorAll(controls)) {
    if (!seen(el) || hidden(el)) continue;
    const r = el.getBoundingClientRect();
    const isText = el.tagName === 'A' && el.closest('p,li') && el.closest('p,li').innerText.length > el.innerText.length;
    if ((r.width < 24 || r.height < 24) && !isText && !el.disabled) {
      out.tapTargets.push({ selector: sel(el), text: text(el), size: `${Math.round(r.width)}x${Math.round(r.height)}` });
    }
    const name = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.title || text(el) || el.querySelector?.('img[alt]:not([alt=""])');
    if (el.matches('input,select,textarea')) {
      const labelled = (el.labels && el.labels.length) || el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.title;
      if (!labelled && !['submit', 'button', 'reset'].includes(el.type)) {
        out.unlabeled.push({ selector: sel(el), placeholder: el.placeholder || null });
      }
    } else if (!name) {
      out.unnamed.push({ selector: sel(el) });
    }
    if (el.tagName === 'A') {
      const h = el.getAttribute('href');
      if (h === '#' || h === '' || /^javascript:/i.test(h)) out.deadLinks.push({ selector: sel(el), text: text(el) });
    }
  }

  for (const img of document.images) {
    if (!seen(img) && img.complete && img.naturalWidth) continue;
    const broken = img.complete && !img.naturalWidth, noAlt = !img.hasAttribute('alt');
    if (broken || noAlt) out.images.push({ src: img.getAttribute('src'), broken, noAlt });
  }

  const doc = document.documentElement, vw = doc.clientWidth;
  if (doc.scrollWidth > vw + 1) {
    const wide = [...document.querySelectorAll('body *')].filter((el) => {
      if (!seen(el) || el.getBoundingClientRect().right <= vw + 1) return false;
      for (let p = el.parentElement; p; p = p.parentElement) if (/auto|scroll|hidden/.test(getComputedStyle(p).overflowX) && p !== doc && p !== document.body) return false;
      return true;
    });
    out.overflow = { pageWidth: doc.scrollWidth, viewport: vw, widest: wide.slice(0, 3).map(sel) };
  }

  const body = document.body.innerText;
  const leaks = /\b(undefined|NaN|null)\b|\[object Object\]|\{\{.*?\}\}|lorem ipsum|TODO|FIXME/gi;
  for (const line of body.split('\n')) {
    const m = line.match(leaks);
    if (m) out.leakedText.push({ match: m[0], line: line.trim().slice(0, 100) });
  }
  return out;
}
"""

# Only with --design. Reports what the page really uses, so a look can be compared to its tokens.
DESIGN = r"""
() => {
  const ctx = document.createElement('canvas').getContext('2d');
  const hex = (c) => {
    ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1);
    const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
    return a === 0 ? null : '#' + [r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('');
  };
  const seen = (el) => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0 && r.width > 0 && r.height > 0;
  };
  const colors = {}, sizes = new Set(), fonts = new Set(), edges = new Set(), boxes = [];
  const add = (c) => { const h = c && hex(c); if (h) colors[h] = (colors[h] || 0) + 1; };
  let gradients = 0, shadows = 0, blurs = 0, left = Infinity, right = -Infinity;
  const vw = document.documentElement.clientWidth, sy = scrollY;
  for (const el of document.querySelectorAll('body *')) {
    if (!seen(el) || el.closest('[aria-hidden="true"]')) continue;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    add(s.backgroundColor);
    if (parseFloat(s.borderTopWidth) > 0) add(s.borderTopColor);
    if (s.backgroundImage.includes('gradient')) gradients++;
    if (s.boxShadow !== 'none') shadows++;
    if (s.backdropFilter && s.backdropFilter !== 'none') blurs++;
    if (el.matches('img,svg,video,canvas')) boxes.push([r.top + sy, r.bottom + sy]);
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    add(s.color); sizes.add(parseFloat(s.fontSize)); fonts.add(s.fontFamily.split(',')[0].replace(/["']/g, '').trim());
    boxes.push([r.top + sy, r.bottom + sy]);
    if (!s.display.startsWith('inline') && r.width > 2 && r.right > 0 && r.left < vw) edges.add(Math.round(r.left));
    // Skip links and visually hidden text sit off screen or in a 1px box, and are not the page's frame.
    if (r.width > 2 && r.right > 0 && r.left < vw) { left = Math.min(left, r.left); right = Math.max(right, r.right); }
  }
  const headlines = [...document.querySelectorAll('h1,h2,h3')].filter(seen).map((h) => {
    const s = getComputedStyle(h), line = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.2;
    return { tag: h.tagName.toLowerCase(), text: h.innerText.trim().slice(0, 60), lines: Math.round(h.getBoundingClientRect().height / line), px: parseFloat(s.fontSize) };
  });
  // A screen with nothing on it, measured in steps of one viewport down the page.
  let emptyScreens = 0;
  for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight) {
    const end = Math.min(y + innerHeight, document.documentElement.scrollHeight);
    if (end - y > innerHeight / 2 && !boxes.some(([a, b]) => a < end && b > y)) emptyScreens++;
  }
  return {
    colors, fontSizes: [...sizes].sort((a, b) => a - b), fonts: [...fonts], textLeftEdges: edges.size,
    margins: { left: Math.round(left), right: Math.round(vw - right) }, headlines, gradients, shadows, blurs, emptyScreens,
  };
}
"""


def design_tokens(path):
    """Colours and font families from a DESIGN.md's front matter, or None without the file."""
    if not os.path.exists(path):
        return None
    text = open(path, encoding="utf-8").read()
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    head = match.group(1) if match else text
    return {
        "colors": {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", head)},
        "fonts": {f.strip().lower() for f in re.findall(r"fontFamily:\s*[\"']?([^\"',}\n]+)", head)},
    }


def with_design(measured, tokens):
    """Add what falls outside the tokens, most used first, so drift is the first thing read."""
    if tokens is None:
        return {**measured, "tokens": "no DESIGN.md found"}
    colors = sorted(measured["colors"].items(), key=lambda kv: -kv[1])
    return {
        **measured,
        "offTokenColors": [{"color": c, "uses": n} for c, n in colors if c not in tokens["colors"]],
        "offTokenFonts": [f for f in measured["fonts"] if f.lower() not in tokens["fonts"]],
    }


def launch(p):
    """Default browser, then an installed Chrome or Edge, then any cached build."""
    tries = [{}, {"channel": "chrome"}, {"channel": "msedge"}]
    home = os.path.expanduser("~")
    cached = glob.glob(f"{home}/Library/Caches/ms-playwright/chromium-*/*/*.app/Contents/MacOS/*")
    cached += glob.glob(f"{home}/.cache/ms-playwright/chromium-*/*/chrome")
    tries += [{"executable_path": path} for path in sorted(cached, reverse=True)]
    error = None
    for options in tries:
        try:
            return p.chromium.launch(**options)
        except Exception as exc:  # the next candidate may exist
            error = exc
    raise SystemExit(f"No browser found. Run: playwright install chromium\n{error}")


def main():
    args = sys.argv[1:]
    cookies = []
    while "--cookie" in args:
        i = args.index("--cookie")
        cookies.append(args[i + 1])
        del args[i : i + 2]
    label = ""
    if "--label" in args:
        i = args.index("--label")
        label = args[i + 1] + "-"
        del args[i : i + 2]
    tokens, want_design = None, False
    if "--design" in args:
        i = args.index("--design")
        tokens, want_design = design_tokens(args[i + 1]), True
        del args[i : i + 2]
    if len(args) < 2:
        raise SystemExit(__doc__)
    out_dir, urls = args[0], args[1:]
    os.makedirs(out_dir, exist_ok=True)
    report = []

    with sync_playwright() as p:
        browser = launch(p)
        for url in urls:
            slug = re.sub(r"\W+", "-", urlparse(url).path).strip("-") or "home"
            for name, (width, height) in VIEWPORTS.items():
                context = browser.new_context(viewport={"width": width, "height": height})
                for cookie in cookies:
                    key, value = cookie.split("=", 1)
                    # Scoped to the host, or API calls outside the page's path go out logged out.
                    host = urlparse(url).hostname
                    context.add_cookies([{"name": key, "value": value, "domain": host, "path": "/"}])
                page = context.new_page()
                console, failed = [], []
                # The text of a failed load omits the URL, and favicon misses bypass the response event.
                page.on("console", lambda m: console.append(f"{m.text[:200]} ({m.location.get('url', '')})") if m.type == "error" else None)
                page.on("pageerror", lambda e: console.append(str(e)[:200]))
                page.on("response", lambda r: failed.append(f"{r.status} {r.url}") if r.status >= 400 else None)
                status = None
                try:
                    response = page.goto(url, wait_until="networkidle", timeout=30000)
                    status = response.status if response else None
                except Exception as exc:  # slow pages still get measured
                    console.append(f"navigation: {str(exc)[:160]}")
                shot = os.path.join(out_dir, f"{label}{slug}-{name}.png")
                page.screenshot(path=shot, full_page=True)
                report.append({
                    "url": url, "viewport": name, "status": status, "screenshot": shot,
                    "consoleErrors": console, "failedRequests": failed, **page.evaluate(MEASURE),
                })
                if want_design:
                    report[-1]["design"] = with_design(page.evaluate(DESIGN), tokens)
                context.close()
        browser.close()
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
