#!/usr/bin/env python3
"""Run with: python scripts/test_probe.py. Needs what probe.py needs."""
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = b"<!doctype html><html lang='en'><head><title>t</title></head><body><h1>Hello</h1></body></html>"


def serve(extra_headers, page=PAGE, need_cookie=None):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            ok = need_cookie is None or need_cookie in (self.headers.get("Cookie") or "")
            self.send_response(200 if ok else 401)
            self.send_header("Content-Type", "text/html")
            for k, v in extra_headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def probe(server, *extra):
    with tempfile.TemporaryDirectory() as tmp:
        out = subprocess.run(
            [sys.executable, os.path.join(HERE, "probe.py"), tmp, f"http://127.0.0.1:{server.server_port}/", *extra],
            capture_output=True, text=True, check=True,
        ).stdout
    return json.loads(out)


def missing_for(extra_headers):
    server = serve(extra_headers)
    try:
        return probe(server)[0]["missingSecurityHeaders"]
    finally:
        server.shutdown()


def contrast_of(body):
    server = serve({}, page=b"<!doctype html><html lang='en'><head><title>t</title></head><body>" + body + b"</body></html>")
    try:
        return [hit for row in probe(server) for hit in row["contrast"]]
    finally:
        server.shutdown()


bare = missing_for({})
assert bare == ["content-security-policy", "x-content-type-options: nosniff", "x-frame-options or frame-ancestors"], bare

hardened = missing_for({
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
})
assert hardened == [], hardened

framed_by_header = missing_for({
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
})
assert framed_by_header == [], framed_by_header

# A 60% card inside transparent wrappers stays near white, so mid-grey text on it passes.
nested = contrast_of(b"<div><div style='background:rgb(250 250 250 / .6)'><div><div><button style='background:none;border:0'><span style='color:rgb(99,99,99)'>Readable</span></button></div></div></div></div>")
assert nested == [], nested
faint = contrast_of(b"<div><div style='background:rgb(250 250 250 / .6)'><div><span style='color:rgb(200,200,200)'>Faint</span></div></div></div>")
assert [hit["text"] for hit in faint] == ["Faint", "Faint"], faint  # mobile and desktop

# --storage-state carries every cookie the login set, so a page that needs one loads.
server = serve({}, need_cookie="csrf=abc")
try:
    with tempfile.TemporaryDirectory() as tmp:
        state = os.path.join(tmp, "state.json")
        with open(state, "w") as f:
            json.dump({"cookies": [
                {"name": n, "value": v, "domain": "127.0.0.1", "path": "/", "expires": -1, "httpOnly": False, "secure": False, "sameSite": "Lax"}
                for n, v in (("session", "s1"), ("csrf", "abc"))
            ], "origins": []}, f)
        assert [row["status"] for row in probe(server)] == [401, 401]
        rows = probe(server, "--storage-state", state)
        assert [(row["viewport"], row["status"]) for row in rows] == [("mobile", 200), ("desktop", 200)], rows
finally:
    server.shutdown()
print("ok")
