#!/usr/bin/env python3
"""Check the receipts table in a spec or PR body before anyone calls the work done.

usage: receipts.py FILE [FILE ...] [--root DIR] [--strict]

Reads every Markdown table with a Receipt column. A row fails when its receipt is
empty or filler ("looks fine", "TODO", "passed"), when a file it names in backticks
does not exist under --root (default: the current directory), or when it says Not
verified while the file's "Not verified:" line says none. Not verified rows pass
unless --strict. Exit 1 on any failure. Standard library only, so any agent, git
hook or CI job can run it.
"""
import os
import re
import sys

FILLER = re.compile(r"^(-+|n/?a|none|tbd|todo|later|ok|done|pass(ed)?|works|yes|verified|checked|"
                    r"looks (fine|good|ok)|manual( check)?|see above)?\.?$", re.I)
EXT = re.compile(r"\.(png|jpe?g|webp|gif|mp4|webm|tsx?|jsx?|py|go|rs|rb|java|kt|swift|md|json|ya?ml|txt|log|"
                 r"html?|css|sql|sh|toml)$", re.I)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def named_files(receipt):
    for span in re.findall(r"`([^`]+)`", receipt):
        for token in span.split():
            token = re.sub(r"(:\d+)+$", "", token.strip(",;:()"))
            if token.startswith(("-", "http://", "https://", "$")) or "*" in token or "<" in token:
                continue
            if "/" in token or EXT.search(token):
                yield token


def check(path, root):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    nv_line = next((m.group(1) for m in (re.match(r"^\s*Not verified:\s*(.*)", l, re.I) for l in lines) if m), None)
    rows, col = [], None
    for line in lines:
        if not line.strip().startswith("|"):
            col = None
            continue
        row = cells(line)
        if col is None:
            col = next((i for i, c in enumerate(row) if c.lower() == "receipt"), None)
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in row if c):
            continue
        rows.append((row[0] or "?", row[col] if col < len(row) else ""))

    if not rows:
        return [f"FAIL {path}: no receipts table (a Markdown table with a Receipt column)"], 1, 0
    report, failed, unverified = [], 0, 0
    for num, receipt in rows:
        problem = None
        if receipt.lower().startswith("not verified"):
            unverified += 1
            if not nv_line or re.match(r"^none\b", nv_line, re.I):
                problem = "says Not verified, but the Not verified line says none or is missing"
        elif FILLER.match(receipt):
            problem = f"has no receipt ({receipt or 'empty'!r})"
        else:
            missing = [f for f in named_files(receipt) if not os.path.exists(os.path.join(root, f))]
            if missing:
                problem = "names files that do not exist: " + ", ".join(missing)
        if problem:
            failed += 1
            report.append(f"FAIL {path} row {num}: {problem}")
        elif receipt.lower().startswith("not verified"):
            report.append(f"NOT VERIFIED {path} row {num}: {receipt}")
    report.append(f"{path}: {len(rows)} rows, {failed} failing, {unverified} not verified")
    return report, failed, unverified


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    root = "."
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i : i + 2]
    if not args:
        raise SystemExit(__doc__)
    failed = unverified = 0
    for path in args:
        report, f, u = check(path, root)
        print("\n".join(report))
        failed, unverified = failed + f, unverified + u
    sys.exit(1 if failed or (strict and unverified) else 0)


if __name__ == "__main__":
    main()
