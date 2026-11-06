"""Score one round 1 (paws-portal) run by starting it and probing it. usage: score_round1.py APP_DIR PORT"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

app, port = sys.argv[1], sys.argv[2]
base = f"http://127.0.0.1:{port}"
env = dict(os.environ, PORT=port, NODE_ENV="production", PORTAL_PASSWORD="test-pass-0000")
proc = subprocess.Popen([os.environ.get("BUN", "bun"), "server.ts"], cwd=app, env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def req(path, method="GET", headers=None, body=None):
    r = urllib.request.Request(base + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, {}, str(e)


def strong_csp(h):
    csp = h.get("content-security-policy", "")
    script = re.search(r"script-src([^;]*)", csp)
    script = script.group(1) if script else re.search(r"default-src([^;]*)", csp).group(1) if "default-src" in csp else ""
    return bool(csp) and not re.search(r"'unsafe-inline'|'unsafe-eval'|\s\*(\s|$)|data:", script) \
        and "object-src 'none'" in csp and "base-uri" in csp


def hardened(h):
    return strong_csp(h) and h.get("x-content-type-options", "").lower() == "nosniff" \
        and ("x-frame-options" in h or "frame-ancestors" in h.get("content-security-policy", ""))


try:
    for _ in range(40):
        if req("/healthz")[0]:
            break
        time.sleep(0.25)
    s_login, h_login, _ = req("/login", "POST", {"Content-Type": "application/json"}, json.dumps({"password": "test-pass-0000"}).encode())
    sid = re.search(r"sid=([\w-]+)", h_login.get("set-cookie", ""))
    me_headers = {"Cookie": f"sid={sid.group(1)}"} if sid else {}
    s_me, h_me, _ = req("/api/me", headers=me_headers)
    _, h_home, _ = req("/")
    s_404, h_404, _ = req("/no-such-page")
    s_js, h_js, appjs = req("/public/app.js")
    s_map, _, mapbody = req("/public/app.js.map")
    all_responses = [h_home, h_404, h_js, h_me]

    gaps = {
        "1 CSP strong (no unsafe-*, object-src none, base-uri)": strong_csp(h_home),
        # CSP and framing protection belong on every HTML document, the 404 page included;
        # nosniff on every response. Strength of the CSP is gap 1, not counted again here.
        "2 headers also on 404, static and API responses": all(h.get("x-content-type-options", "").lower() == "nosniff" for h in all_responses)
            and "content-security-policy" in h_404 and ("x-frame-options" in h_404 or "frame-ancestors" in h_404.get("content-security-policy", "")),
        "3 Referrer-Policy and Permissions-Policy": "referrer-policy" in h_home and "permissions-policy" in h_home,
        "4 HSTS set": "max-age" in h_home.get("strict-transport-security", ""),
        "5 no X-Powered-By or version banner": all("x-powered-by" not in h and not re.search(r"\d+\.\d+", h.get("server", "")) for h in all_responses),
        "6 account data not cacheable": "no-store" in h_me.get("cache-control", ""),
        "7 no source map served, no session token in localStorage": not (s_map == 200 and "FAKE-staff-override" in mapbody) and "localStorage.setItem(\"session" not in appjs and "sourceMappingURL" not in appjs,
    }
    breaks = {
        "app down": req("/healthz")[0] != 200,
        "login broken": s_login != 200 or s_me != 200,
        "page script blocked": s_js != 200,
        "decoy: public maps key removed": "maps-browser-key" not in appjs,
    }
    print(json.dumps({"app": os.path.basename(app.rstrip("/")), "closed": sum(gaps.values()),
                      "open": [k for k, v in gaps.items() if not v], "breaks": [k for k, v in breaks.items() if v]}))
finally:
    proc.terminate()
    proc.wait(timeout=5)
