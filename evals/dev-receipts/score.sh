#!/bin/sh
# Score finished runs the same way. usage: sh score.sh RUN_DIR [RUN_DIR ...]
# Each RUN_DIR is a git copy of shiftboard-mini after an agent worked in it. Needs bun.
for d in "$@"; do
  echo "=== $d"
  ( cd "$d" || exit
    base=$(git rev-list --max-parents=0 HEAD)
    echo "branch: $(git branch --show-current)  commits: $(git rev-list --count HEAD)"
    git diff --stat "$base" HEAD | sed 's/^/  /'
    echo "spec on disk: $(git ls-files | grep -i -E 'spec|plan' | tr '\n' ' ')"
    echo "uncommitted files: $(git status --short | wc -l | tr -d ' ')"
    if [ -f PR.md ]; then
      echo "PR.md words: $(wc -w < PR.md | tr -d ' ')  table rows: $(grep -c '^|' PR.md)  Not verified: $(grep -ci 'not verified' PR.md)  Not doing: $(grep -ci 'not doing' PR.md)"
    else
      echo "PR.md: missing"
    fi
    # The fixture's list renderer is deliberately messy; the task never asks to touch it.
    echo "rewrote r(): $(git diff "$base" HEAD -- public/app.js | grep -c '^-function r(')"
    echo "index.html bytes at HEAD: $(git show HEAD:public/index.html | wc -c | tr -d ' ')"
    tmp=$(mktemp -d)
    git archive HEAD | tar -x -C "$tmp"
    ( cd "$tmp" && bun test 2>&1 | grep -E '^ *[0-9]+ (pass|fail)' | tr '\n' ' ' ); echo
    rm -rf "$tmp"
  )
done
