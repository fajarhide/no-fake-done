#!/usr/bin/env python3
"""Run with: python scripts/test_probe.py. Needs what probe.py needs."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = """<!doctype html><html><head><title>t</title></head><body style="margin:0;color:#111111;background:#ffffff;font-family:Arial">
<h1 style="width:200px;font-size:40px;line-height:40px">A headline long enough to wrap</h1>
<a href="#x" style="position:absolute;left:-999px;color:#111111">skip</a><p style="color:#ff0000;margin-left:50px">off token</p>
<div style="height:3000px"></div><p>end</p></body></html>"""
DESIGN = '---\ncolors:\n  ink: "#111111"\n  ground: "#FFFFFF"\ntypography:\n  body: { fontFamily: Arial, fontSize: 16px }\n---\n'

with tempfile.TemporaryDirectory() as tmp:
    page, design = os.path.join(tmp, "p.html"), os.path.join(tmp, "DESIGN.md")
    open(page, "w").write(PAGE)
    open(design, "w").write(DESIGN)
    out = subprocess.run(
        [sys.executable, os.path.join(HERE, "probe.py"), tmp, f"file://{page}", "--design", design],
        capture_output=True, text=True, check=True,
    ).stdout
    desktop = json.loads(out)[1]["design"]

assert [c["color"] for c in desktop["offTokenColors"]] == ["#ff0000"], desktop
assert desktop["offTokenFonts"] == [], desktop
assert desktop["textLeftEdges"] == 2, desktop
assert desktop["headlines"][0]["lines"] > 1, desktop
assert desktop["margins"]["left"] == 0, desktop
assert desktop["emptyScreens"] >= 2, desktop
print("ok")
