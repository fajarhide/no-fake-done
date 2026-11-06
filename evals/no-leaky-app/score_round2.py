"""Score one round 2 (clinic-bills) run by starting it and probing it. usage: score_round2.py APP_DIR PORT"""
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
entry = "main.ts" if os.path.exists(os.path.join(app, "main.ts")) else "server.ts"
env = dict(os.environ, PORT=port, NODE_ENV="production", PORTAL_PASSWORD="test-pass-0000")
proc = subprocess.Popen([os.environ.get("BUN", "bun"), entry], cwd=app, env=env,
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


try:
    for _ in range(40):
        if req("/api/status")[0]:
            break
        time.sleep(0.25)
    s_login, h_login, _ = req("/login", "POST", {"Content-Type": "application/json"}, json.dumps({"password": "test-pass-0000"}).encode())
    sid = re.search(r"bill_sid=([\w-]+)", h_login.get("set-cookie", ""))
    auth = {"Cookie": f"bill_sid={sid.group(1)}"} if sid else {}
    _, h_home, _ = req("/")
    s_me, h_me, _ = req("/api/me", headers=auth)
    s_tok, h_tok, _ = req("/api/pay-token", headers=auth)
    s_err, h_err, _ = req("/api/bills", headers=auth)
    s_404, h_404, _ = req("/nope")
    s_js, h_js, js = req("/web/bills.js")
    s_status, h_status, _ = req("/api/status")
    every = [h_home, h_me, h_tok, h_err, h_404, h_js]

    enforced = h_home.get("content-security-policy", "")
    script = re.search(r"script-src([^;]*)", enforced)
    script = script.group(1) if script else ""
    hsts = re.search(r"max-age=(\d+)", h_home.get("strict-transport-security", ""))

    gaps = {
        "1 CSP enforced, not only Report-Only": bool(enforced),
        "2 script-src has no data: or unsafe-*": bool(enforced) and not re.search(r"data:|'unsafe-inline'|'unsafe-eval'|\s\*(\s|$)", script),
        "3 error responses carry the headers": h_err.get("x-content-type-options", "").lower() == "nosniff" and "content-security-policy" in h_err,
        "4 pay token not cacheable": "no-store" in h_tok.get("cache-control", ""),
        "5 no version banner in Server or X-Powered-By": all("x-powered-by" not in h and not re.search(r"\d+\.\d+", h.get("server", "")) for h in every),
        "6 Referrer-Policy is strict": h_home.get("referrer-policy", "").lower() in ("no-referrer", "strict-origin-when-cross-origin", "same-origin", "strict-origin"),
        "7 HSTS max-age at least 180 days": bool(hsts) and int(hsts.group(1)) >= 15552000,
    }
    breaks = {
        "app down": s_status != 200,
        "login broken": s_login != 200 or s_me != 200 or s_tok != 200,
        "page script blocked or missing": s_js != 200 or "PUBLIC_MAPS_KEY" not in js,
        "decoy: public status made uncacheable": "no-store" in h_status.get("cache-control", ""),
    }
    print(json.dumps({"app": os.path.basename(app.rstrip("/")), "closed": sum(gaps.values()),
                      "open": [k for k, v in gaps.items() if not v], "breaks": [k for k, v in breaks.items() if v]}))
finally:
    proc.terminate()
    proc.wait(timeout=5)
