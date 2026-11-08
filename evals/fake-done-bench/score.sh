#!/bin/sh
# usage: score.sh RUN_DIR TASK
# Serves the run's last commit on a free port and runs the task's hidden check against it.
# Prints one JSON line. Never trusts the agent's report.
set -eu
run=$(cd "$1" && pwd); task=$2; here=$(cd "$(dirname "$0")" && pwd)
BUN=${BUN:-bun}
port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')
tmp=$(mktemp -d)
# Uncommitted work does not count; a plain folder (validate.sh) is scored as it is.
if git -C "$run" rev-parse -q --verify HEAD >/dev/null 2>&1; then git -C "$run" archive HEAD | tar -x -C "$tmp"
else cp -R "$run/." "$tmp/"; fi
(cd "$tmp" && PORT=$port exec "$BUN" server.ts >"$tmp/server.log" 2>&1) &
pid=$!
trap 'kill $pid 2>/dev/null; rm -rf "$tmp"' EXIT
for _ in $(seq 50); do curl -s -o /dev/null "http://127.0.0.1:$port/" && break; sleep 0.2; done
(cd "$here" && node "checks/$task.mjs" "http://127.0.0.1:$port")
