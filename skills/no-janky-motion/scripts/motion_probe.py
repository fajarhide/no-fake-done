#!/usr/bin/env python3
"""Record the motion a page actually runs, in four browsers: normal, reduced
motion, JavaScript off, and CPU slowed 4x.

usage: motion_probe.py OUT_DIR URL [--action click:SEL|hover:SEL|focus:SEL|scroll]
                       [--label before] [--cookie name=value]
Prints JSON. Every animation and finding names a selector, so a reader can check it.
Needs Playwright: pip install playwright && playwright install chromium
"""
import json
import os
import re
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1280, "height": 800}
SAMPLE_MS = 1500
LAYOUT_PROPS = re.compile(r"^(width|height|top|left|right|bottom|inset|margin.*|padding.*|max-.*|min-.*)$")

# Installed before any page script. Polls getAnimations() every frame, because
# a 150 ms transition is over long before a single check after the action.
RECORDER = r"""
(() => {
  const seen = new WeakSet(), list = [], gaps = [];
  let last = 0;
  const sel = (el) => {
    if (!el || !el.tagName) return '?';
    if (el.id) return `${el.tagName.toLowerCase()}#${el.id}`;
    const cls = [...el.classList].slice(0, 2).map((c) => '.' + c).join('');
    return el.tagName.toLowerCase() + cls;
  };
  const grab = () => {
    for (const a of document.getAnimations({ subtree: true })) {
      if (seen.has(a) || !a.effect) continue;
      seen.add(a);
      const kf = a.effect.getKeyframes(), t = a.effect.getComputedTiming(), el = a.effect.target;
      const props = new Set();
      kf.forEach((k) => Object.keys(k).forEach((p) => {
        if (!['offset', 'computedOffset', 'easing', 'composite'].includes(p)) props.add(p);
      }));
      if (a.transitionProperty) props.add(a.transitionProperty);
      const timingEase = a.effect.getTiming().easing;
      list.push({
        selector: sel(el), el,
        kind: a.constructor.name, name: a.animationName || a.transitionProperty || a.id || '',
        properties: [...props], duration: Number(t.duration) || 0, delay: t.delay || 0,
        iterations: t.iterations === Infinity ? 'Infinity' : t.iterations,
        easing: timingEase !== 'linear' ? timingEase : ((kf[0] && kf[0].easing) || 'linear'),
        firstTransform: (kf[0] && kf[0].transform) || '',
        transitionAll: !!el && (() => {
          // The default is `all 0s`, so only a non-zero duration paired with `all` counts.
          const s = getComputedStyle(el), props = s.transitionProperty.split(','), durs = s.transitionDuration.split(',');
          return props.some((p, i) => p.trim() === 'all' && parseFloat(durs[i % durs.length]) > 0);
        })(),
        anim: a,
      });
    }
  };
  const tick = (now) => { if (last) gaps.push(now - last); last = now; grab(); requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
  let shift = 0; const longFrames = [];
  try { new PerformanceObserver((l) => l.getEntries().forEach((e) => { if (!e.hadRecentInput) shift += e.value; }))
    .observe({ type: 'layout-shift', buffered: true }); } catch (e) {}
  try { new PerformanceObserver((l) => l.getEntries().forEach((e) => longFrames.push(Math.round(e.duration))))
    .observe({ type: 'long-animation-frame', buffered: true }); } catch (e) {}
  const offscreen = new Set();
  window.__mr = {
    reset() { gaps.length = 0; last = 0; },
    offscreen() {
      grab();
      list.filter((x) => x.iterations === 'Infinity' && x.anim.playState === 'running' && x.el && (() => {
        const r = x.el.getBoundingClientRect(); return r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth;
      })()).forEach((x) => offscreen.add(x.selector));
    },
    report() {
      this.offscreen();
      return { animations: list.map(({ el, anim, ...rest }) => rest), gaps: gaps.map(Math.round),
               layoutShift: Math.round(shift * 1000) / 1000, longFrames, loopsOffscreen: [...offscreen] };
    },
  };
})();
"""

# JavaScript off: text an intro script was meant to reveal stays invisible.
HIDDEN_AT_REST = r"""
() => [...document.body.querySelectorAll('*')].filter((el) => {
  const s = getComputedStyle(el);
  return (s.opacity === '0' || s.visibility === 'hidden') && el.innerText && el.innerText.trim().length > 2
    && ![...el.children].some((c) => c.innerText === el.innerText);
}).slice(0, 10).map((el) => (el.id ? '#' + el.id : el.tagName.toLowerCase() + [...el.classList].slice(0, 2).map((c) => '.' + c).join('')))
"""


def launch(p):
    """Same order as no-broken-ui: default browser, then an installed Chrome or Edge."""
    error = None
    for options in ({}, {"channel": "chrome"}, {"channel": "msedge"}):
        try:
            return p.chromium.launch(**options)
        except Exception as exc:  # the next candidate may exist
            error = exc
    raise SystemExit(f"No browser found. Run: playwright install chromium\n{error}")


def act(page, action):
    if not action:
        return
    verb, _, target = action.partition(":")
    if verb == "scroll":
        page.mouse.wheel(0, 2400)
    elif verb in ("click", "hover", "focus"):
        getattr(page.locator(target).first, verb)(timeout=5000)
    else:
        raise SystemExit(f"unknown action {action}")


def pct(values, q):
    if not values:
        return 0
    values = sorted(values)
    return values[min(len(values) - 1, int(len(values) * q))]


def findings(runs):
    out = []
    normal = runs["normal"]
    for a in normal.get("animations", []):
        where = f"{a['selector']} ({a['kind']} {a['name']})".strip()
        layout = [p for p in a["properties"] if LAYOUT_PROPS.match(p)]
        if layout:
            out.append({"rule": "layout-property", "where": where, "measured": layout})
        if a["transitionAll"]:
            out.append({"rule": "transition-all", "where": where, "measured": "transition-property: all"})
        total = a["duration"] + a["delay"]
        if a["iterations"] != "Infinity" and total > 500:
            out.append({"rule": "slow", "where": where, "measured": f"{round(total)} ms"})
        elif a["iterations"] != "Infinity" and total > 300:
            out.append({"rule": "slow-for-small-ui", "where": where, "measured": f"{round(total)} ms", "lead": True})
        if a["easing"].startswith("ease-in") and not a["easing"].startswith("ease-in-out"):
            out.append({"rule": "ease-in", "where": where, "measured": a["easing"], "lead": True})
        scale = re.search(r"scale\(\s*([\d.]+)", a["firstTransform"])
        if scale and float(scale.group(1)) < 0.5:
            out.append({"rule": "grows-from-nothing", "where": where, "measured": a["firstTransform"]})
    for sel in normal.get("loopsOffscreen", []):
        out.append({"rule": "loop-offscreen", "where": sel, "measured": "infinite, running, outside the viewport"})
    for a in runs["reduced"].get("animations", []):
        moving = any(p in ("transform", "translate", "scale", "rotate") for p in a["properties"])
        if a["iterations"] == "Infinity" or moving:
            out.append({"rule": "ignores-reduced-motion", "where": a["selector"],
                        "measured": f"{a['properties']} iterations={a['iterations']}"})
    for sel in runs["nojs"].get("hiddenAtRest", []):
        out.append({"rule": "hidden-without-js", "where": sel, "measured": "opacity 0 or hidden with JavaScript off"})
    if normal.get("layoutShift", 0) > 0.1:
        out.append({"rule": "layout-shift", "where": "page", "measured": normal["layoutShift"]})
    slow = runs["cpu4x"]
    if slow.get("frames", {}).get("over50", 0):
        out.append({"rule": "long-frames-cpu4x", "where": "page", "measured": slow["frames"], "lead": True})
    return out


def run(browser, name, url, action, out_dir, label, cookies):
    options = {"viewport": VIEWPORT}
    if name == "reduced":
        options["reduced_motion"] = "reduce"
    if name == "nojs":
        options["java_script_enabled"] = False
    context = browser.new_context(**options)
    host = urlparse(url).hostname
    for cookie in cookies:
        key, value = cookie.split("=", 1)
        context.add_cookies([{"name": key, "value": value, "domain": host, "path": "/"}])
    context.add_init_script(RECORDER)
    page = context.new_page()
    if name == "cpu4x":
        context.new_cdp_session(page).send("Emulation.setCPUThrottlingRate", {"rate": 4})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)[:200]))
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except Exception as exc:  # slow pages still get measured
        errors.append(f"navigation: {str(exc)[:160]}")
    result = {"errors": errors}
    if name == "nojs":
        # Init scripts do not run without JavaScript, but evaluate still does.
        result["hiddenAtRest"] = page.evaluate(HIDDEN_AT_REST)
        page.screenshot(path=os.path.join(out_dir, f"{label}nojs.png"))
        context.close()
        return result
    page.evaluate("__mr.reset()")
    act(page, action)
    if name == "normal":
        page.wait_for_timeout(60)
        page.screenshot(path=os.path.join(out_dir, f"{label}motion-start.png"))
    page.wait_for_timeout(SAMPLE_MS)
    if name == "normal":
        page.screenshot(path=os.path.join(out_dir, f"{label}motion-settled.png"))
        page.evaluate("__mr.offscreen()")  # loops below the first screen
        page.mouse.wheel(0, 100000)  # then loops near the top
        page.wait_for_timeout(300)
    data = page.evaluate("__mr.report()")
    gaps = data.pop("gaps")
    data["frames"] = {"count": len(gaps), "p50": pct(gaps, 0.5), "p95": pct(gaps, 0.95),
                      "max": max(gaps or [0]), "over50": sum(g > 50 for g in gaps)}
    result.update(data)
    context.close()
    return result


def main():
    args = sys.argv[1:]
    opts = {"--action": "", "--label": ""}
    cookies = []
    while "--cookie" in args:
        i = args.index("--cookie")
        cookies.append(args[i + 1])
        del args[i : i + 2]
    for flag in opts:
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1]
            del args[i : i + 2]
    if len(args) != 2:
        raise SystemExit(__doc__)
    out_dir, url = args
    label = opts["--label"] + "-" if opts["--label"] else ""
    os.makedirs(out_dir, exist_ok=True)
    with sync_playwright() as p:
        browser = launch(p)
        runs = {name: run(browser, name, url, opts["--action"], out_dir, label, cookies)
                for name in ("normal", "reduced", "nojs", "cpu4x")}
        browser.close()
    print(json.dumps({"url": url, "action": opts["--action"], "findings": findings(runs), "runs": runs}, indent=1))


if __name__ == "__main__":
    main()
