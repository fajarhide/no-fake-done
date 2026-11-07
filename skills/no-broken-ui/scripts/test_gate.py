#!/usr/bin/env python3
"""Run with: python scripts/test_gate.py. Standard library only."""
import json
import os
import subprocess
import sys
import tempfile

GATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate.py")
STATE = tempfile.mkdtemp()


def hook(event, session="s1", **extra):
    payload = {"hook_event_name": event, "session_id": session, "cwd": "/tmp/app", **extra}
    out = subprocess.run([sys.executable, GATE], input=json.dumps(payload), capture_output=True, text=True,
                         env={**os.environ, "NO_BROKEN_UI_GATE_DIR": STATE})
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout) if out.stdout.strip() else {}


def edit(path, session="s1"):
    return hook("PostToolUse", session, tool_name="Edit", tool_input={"file_path": path})


def bash(command, session="s1"):
    return hook("PostToolUse", session, tool_name="Bash", tool_input={"command": command})


def stop(session="s1", active=False):
    return hook("Stop", session, stop_hook_active=active)


# 1. Nothing edited: stop is allowed.
assert stop("clean") == {}

# 2. A UI edit with no probe after it: blocked once, naming the file.
edit("/tmp/app/src/App.tsx", "s2")
blocked = stop("s2")
assert blocked.get("decision") == "block" and "App.tsx" in blocked["reason"], blocked

# 4. The second stop goes through, by flag or by the same state.
assert stop("s2", active=True) == {}
assert stop("s2") == {}

# 3. Probe after the edit: allowed. An edit after the probe makes it dirty again.
edit("/tmp/app/styles/site.css", "s3")
bash("python ~/.claude/skills/no-broken-ui/scripts/probe.py out http://localhost:5173/", "s3")
assert stop("s3") == {}
edit("/tmp/app/index.html", "s3")
assert stop("s3").get("decision") == "block"

# 5. Server code alone is not a UI change.
edit("/tmp/app/server.ts", "s5")
assert stop("s5") == {}

# 6. Sessions do not share state.
edit("/tmp/app/page.vue", "s6a")
assert stop("s6b") == {}
assert stop("s6a").get("decision") == "block"

# Garbage on stdin never breaks the session.
out = subprocess.run([sys.executable, GATE], input="not json", capture_output=True, text=True,
                     env={**os.environ, "NO_BROKEN_UI_GATE_DIR": STATE})
assert out.returncode == 0 and out.stdout == "", out
print("ok")
