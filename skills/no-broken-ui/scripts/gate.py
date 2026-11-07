#!/usr/bin/env python3
"""Claude Code hook: hold "done" once when UI files changed after the last probe run.

PostToolUse records UI edits and probe.py runs; Stop blocks once per unprobed change.
State lives per session under $NO_BROKEN_UI_GATE_DIR or the temp dir. Any failure
lets the agent stop, since a broken hook must never trap a session.
"""
import json
import os
import re
import sys
import tempfile

UI = re.compile(r"\.(html?|css|scss|sass|less|jsx|tsx|vue|svelte|astro|erb|hbs|njk|liquid|jinja2?|twig)$", re.I)


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    session = re.sub(r"[^\w.-]", "_", str(event.get("session_id") or "default"))
    folder = os.environ.get("NO_BROKEN_UI_GATE_DIR") or os.path.join(tempfile.gettempdir(), "no-broken-ui-gate")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, session + ".json")
    try:
        with open(path) as f:
            state = json.load(f)
    except (OSError, ValueError):
        state = {"seq": 0, "changed": [], "dirty": 0, "probed": 0, "blocked": 0}

    name = event.get("hook_event_name")
    tool = event.get("tool_input") or {}
    if name == "PostToolUse":
        state["seq"] += 1
        file = str(tool.get("file_path") or tool.get("notebook_path") or "")
        if UI.search(file):
            state["dirty"] = state["seq"]
            if file not in state["changed"]:
                state["changed"] = (state["changed"] + [file])[-20:]
        elif "probe.py" in str(tool.get("command") or ""):
            state["probed"] = state["seq"]
            state["changed"] = []
    elif name == "Stop":
        unprobed = state["dirty"] > state["probed"]
        if unprobed and not event.get("stop_hook_active") and state["blocked"] < state["dirty"]:
            state["blocked"] = state["dirty"]
            files = ", ".join(os.path.basename(f) for f in state["changed"][-5:])
            print(json.dumps({"decision": "block", "reason": (
                f"no-broken-ui: UI files changed since the last probe run ({files}). Before saying done, "
                "run scripts/probe.py on the pages they render and look at the screenshots, or say in your "
                "reply which pages are Not verified and why.")}))

    with open(path, "w") as f:
        json.dump(state, f)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a hook error must not hold the session
        pass
