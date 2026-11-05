#!/usr/bin/env python3
"""Run with: python scripts/test_motion_probe.py. Needs what motion_probe.py needs."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# Every bad motion here is on purpose; #good is the control and must not be flagged.
PAGE = """<!doctype html><html><head><title>t</title><style>
#box { width: 100px; height: 40px; background: #333; transition: width 600ms ease-in; }
#box.open { width: 300px; }
#good { opacity: .5; transition: opacity 150ms ease-out; }
#good.on { opacity: 1; }
@keyframes pop { from { transform: scale(0); } to { transform: scale(1); } }
#pop.show { animation: pop 200ms ease-out; }
@keyframes spin { to { transform: rotate(360deg); } }
#spinner { width: 20px; height: 20px; background: red; animation: spin 1s linear infinite; }
#intro { opacity: 0; }
</style></head><body>
<p id="intro">Welcome to the clinic</p>
<button id="go" onclick="box.classList.add('open'); good.classList.add('on'); pop.classList.add('show')">Go</button>
<div id="box"></div><div id="good">fine</div><div id="pop">menu</div>
<div style="height:3000px"></div><div id="spinner"></div>
<script>document.getElementById('intro').style.opacity = 1</script>
</body></html>"""

with tempfile.TemporaryDirectory() as tmp:
    page = os.path.join(tmp, "p.html")
    open(page, "w").write(PAGE)
    out = subprocess.run(
        [sys.executable, os.path.join(HERE, "motion_probe.py"), tmp, f"file://{page}", "--action", "click:#go"],
        capture_output=True, text=True, check=True,
    ).stdout
report = json.loads(out)
got = {(f["rule"], f["where"].split(" ")[0]) for f in report["findings"]}

for expected in [
    ("layout-property", "div#box"),
    ("slow", "div#box"),
    ("ease-in", "div#box"),
    ("grows-from-nothing", "div#pop"),
    ("loop-offscreen", "div#spinner"),
    ("ignores-reduced-motion", "div#spinner"),
    ("hidden-without-js", "#intro"),
]:
    assert expected in got, (expected, sorted(got))
assert not any(where == "div#good" for _, where in got), sorted(got)
assert report["runs"]["normal"]["frames"]["count"] > 10, report["runs"]["normal"]["frames"]
print("ok")
