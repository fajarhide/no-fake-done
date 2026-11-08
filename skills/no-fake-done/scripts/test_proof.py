#!/usr/bin/env python3
"""Run with: python scripts/test_proof.py. Standard library only."""
import os
import subprocess
import sys
import tempfile

CHECK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proof.py")


def run(body, files=(), *flags):
    with tempfile.TemporaryDirectory() as root:
        for f in files:
            os.makedirs(os.path.dirname(os.path.join(root, f)) or root, exist_ok=True)
            open(os.path.join(root, f), "w").close()
        with open(os.path.join(root, "PR.md"), "w") as f:
            f.write(body)
        out = subprocess.run([sys.executable, CHECK, "PR.md", *flags], cwd=root, capture_output=True, text=True)
        return out.returncode, out.stdout


GOOD = """Swap shifts.

| # | Acceptance | Proof |
| --- | --- | --- |
| 1 | Swap updates both shifts | `bun test lib/swap.test.ts`: 6 passed |
| 2 | Phone layout | screenshot `shots/swap-mobile.png` |

Not verified: none.
"""

code, out = run(GOOD, ["lib/swap.test.ts", "shots/swap-mobile.png"])
assert code == 0 and "2 rows" in out, out

# A proof that names a file the repo does not have.
code, out = run(GOOD, ["lib/swap.test.ts"])
assert code == 1 and "shots/swap-mobile.png" in out, out

# Placeholders are not proof.
for filler in ("", "TODO", "looks fine", "-", "passed", "Manual check"):
    code, out = run(GOOD.replace("screenshot `shots/swap-mobile.png`", filler), ["lib/swap.test.ts"])
    assert code == 1 and "row 2" in out, (filler, out)

# A Not verified row passes by default, fails under --strict, and must be named on the Not verified line.
nv = GOOD.replace("screenshot `shots/swap-mobile.png`", "Not verified: no browser here").replace(
    "Not verified: none.", "Not verified: row 2, no browser here.")
code, out = run(nv, ["lib/swap.test.ts"])
assert code == 0 and "NOT VERIFIED" in out, out
code, out = run(nv, ["lib/swap.test.ts"], "--strict")
assert code == 1, out
code, out = run(nv.replace("Not verified: row 2, no browser here.", "Not verified: none."), ["lib/swap.test.ts"])
assert code == 1 and "none" in out, out

# The spec's four-column table counts too, and a file with no proof table fails.
spec = "| # | When | Then | Proof |\n|---|---|---|---|\n| 1 | open /swap | list shows | `e2e/swap.spec.ts` |\n"
assert run(spec, ["e2e/swap.spec.ts"])[0] == 0
# Tables written before the rename, with a Receipt column, still count.
assert run(spec.replace("Proof", "Receipt"), ["e2e/swap.spec.ts"])[0] == 0
code, out = run("Done, all tests pass.\n")
assert code == 1 and "no proof table" in out, out

# In a git repo, work nobody committed fails, except the proof file itself.
with tempfile.TemporaryDirectory() as root:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
    git = lambda *a: subprocess.run(["git", *a], cwd=root, env=env, check=True, capture_output=True)
    os.makedirs(os.path.join(root, "lib"))
    open(os.path.join(root, "lib/swap.test.ts"), "w").close()
    open(os.path.join(root, "shots-swap-mobile.png"), "w").close()
    git("init", "-q"); git("add", "-A"); git("commit", "-qm", "start")
    with open(os.path.join(root, "PR.md"), "w") as f:
        f.write(GOOD.replace("shots/swap-mobile.png", "shots-swap-mobile.png"))
    check = lambda *flags: subprocess.run([sys.executable, CHECK, "PR.md", *flags], cwd=root, capture_output=True, text=True)
    out = check()
    assert out.returncode == 0, out.stdout
    with open(os.path.join(root, "lib/swap.test.ts"), "w") as f:
        f.write("changed")
    open(os.path.join(root, "lib/new.ts"), "w").close()
    out = check()
    assert out.returncode == 1 and "not committed" in out.stdout and "lib/new.ts" in out.stdout \
        and "lib/swap.test.ts" in out.stdout and "PR.md" not in out.stdout.split("not committed")[1], out.stdout
    assert check("--uncommitted-ok").returncode == 0
    git("add", "-A"); git("commit", "-qm", "work")
    assert check().returncode == 0

# The old script name still runs the check.
out = subprocess.run([sys.executable, CHECK.replace("proof.py", "receipts.py")], capture_output=True, text=True)
assert out.returncode != 0 and "usage: proof.py" in out.stdout + out.stderr, out
print("ok")
