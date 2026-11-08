#!/bin/sh
# Checks the scorer both ways before any real run: the untouched app and the naive
# solution (the one that walks into the trap) must fail, the good solution must pass.
set -u
here=$(cd "$(dirname "$0")" && pwd); work=$(mktemp -d); bad=0
for task in $(ls "$here/refs"); do
  for v in fixture naive good; do
    d="$work/$task-$v"; cp -R "$here/clinic" "$d"
    [ "$v" = fixture ] || cp -R "$here/refs/$task/$v/." "$d/"
    out=$("$here/score.sh" "$d" "$task" 2>&1 | tail -1)
    pass=$(printf '%s' "$out" | grep -o '"pass":[a-z]*' | cut -d: -f2)
    want=false; [ "$v" = good ] && want=true
    if [ "$pass" = "$want" ]; then ok=ok; else ok=WRONG; bad=1; fi
    printf '%-12s %-8s pass=%-6s %s\n' "$task" "$v" "$pass" "$ok"
    [ "$ok" = ok ] || printf '  %s\n' "$out"
  done
done
rm -rf "$work"; exit $bad
