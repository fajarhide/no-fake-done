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


def serve(extra_headers):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            for k, v in extra_headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(PAGE)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def missing_for(extra_headers):
    server = serve(extra_headers)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            out = subprocess.run(
                [sys.executable, os.path.join(HERE, "probe.py"), tmp, f"http://127.0.0.1:{server.server_port}/"],
                capture_output=True, text=True, check=True,
            ).stdout
        return json.loads(out)[0]["missingSecurityHeaders"]
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
print("ok")
