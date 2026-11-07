#!/usr/bin/env python3
"""List the pages a change reaches, so an audit probes those and not a guess.

usage: blast.py [--base REF] [--files FILE ...] [--json]

Changed files come from --files, or from `git diff --name-only BASE` plus untracked
files (BASE defaults to the merge base with origin's default branch, else HEAD).
Walks imports backwards (JS/TS import, export from, import(), require(), CSS
@import, HTML script and link tags) until it reaches page files: Next app and
pages routers, SvelteKit, Astro, Nuxt, Remix routes, and plain .html files.
A changed layout or app shell reaches every page under it. Standard library only.
Import parsing is by pattern, so a page reached only through config or a
framework convention it does not know shows up under "no page found".
"""
import json
import os
import re
import subprocess
import sys

SKIP = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".svelte-kit", "out", "coverage", ".turbo"}
EXTS = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro", ".mdx", ".html", ".htm",
        ".css", ".scss", ".sass", ".less")
SPEC = [re.compile(p) for p in (
    r"""(?:import|export)\s[^'";]*?from\s*['"]([^'"]+)['"]""",
    r"""import\s*['"]([^'"]+)['"]""",
    r"""import\(\s*['"]([^'"]+)['"]\s*\)""",
    r"""require\(\s*['"]([^'"]+)['"]\s*\)""",
    r"""@(?:import|use|forward)\s+(?:url\()?['"]?([^'")\s;]+)""",
    r"""<(?:script|img|source)[^>]*\bsrc=['"]([^'"]+)['"]""",
    r"""<link[^>]*\bhref=['"]([^'"]+)['"]""",
)]
LAYOUT = re.compile(r"(^|/)(app/(.*/)?layout|pages/_(app|document)|routes/(.*/)?\+layout|app/root)\.\w+$")


def route_of(rel):
    """URL path for a page file, or None when the file is not a page."""
    m = re.search(r"(?:^|/)app/(.*?)/?page\.(?:tsx|jsx|ts|js|mdx)$", rel)
    if m:
        parts = [s for s in m.group(1).split("/") if s and not s.startswith("(")]
        return "/" + "/".join(parts)
    m = re.search(r"(?:^|/)routes/(.*?)/?\+page\.svelte$", rel)
    if m:
        return "/" + "/".join(s for s in m.group(1).split("/") if s and not s.startswith("("))
    m = re.search(r"(?:^|/)app/routes/(.+)\.(?:tsx|jsx|ts|js)$", rel)
    if m:
        name = m.group(1).replace(".", "/")
        return "/" + re.sub(r"(^|/)_index$", "", name).strip("/")
    m = re.search(r"(?:^|/)pages/(.+)\.(?:tsx|jsx|ts|js|mdx|md|vue|astro)$", rel)
    if m and not m.group(1).startswith(("api/", "_")) and "/_" not in m.group(1):
        return "/" + re.sub(r"(^|/)index$", "", m.group(1)).strip("/")
    if rel.endswith((".html", ".htm")):
        path = re.sub(r"^(public|static|src|www)/", "", rel)
        return "/" + re.sub(r"(^|/)index\.html?$", "", path).strip("/") if "index.htm" in path else "/" + path
    return None


def resolve(spec, src, root, files):
    spec = spec.split("?")[0].split("#")[0]
    if not spec or re.match(r"^(\w+:|//)", spec):
        return None
    if spec.startswith(("@/", "~/")):
        bases = [os.path.join("src", spec[2:]) if os.path.isdir(os.path.join(root, "src")) else spec[2:]]
    elif spec.startswith("/"):
        bases = [os.path.join(d, spec.lstrip("/")) for d in ("", "public", "static", "src")]
    elif spec.startswith("."):
        bases = [os.path.join(os.path.dirname(src), spec)]
    else:
        return None  # a package
    for base in bases:
        base = os.path.normpath(base)
        for cand in [base] + [base + e for e in EXTS] + [os.path.join(base, "index" + e) for e in EXTS]:
            if cand in files:
                return cand
    return None


def scan(root):
    files = set()
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for n in names:
            if n.endswith(EXTS):
                files.add(os.path.relpath(os.path.join(d, n), root))
    importers = {}
    for f in files:
        try:
            text = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pat in SPEC:
            for spec in pat.findall(text):
                target = resolve(spec, f, root, files)
                if target and target != f:
                    importers.setdefault(target, set()).add(f)
    return files, importers


def changed_files(base):
    def git(*a):
        return subprocess.run(["git", *a], capture_output=True, text=True).stdout.split()
    if not base:
        head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        mb = git("merge-base", head[0], "HEAD") if head else []
        base = mb[0] if mb else "HEAD"
    return git("diff", "--name-only", base) + git("ls-files", "--others", "--exclude-standard")


def blast(changed, root="."):
    files, importers = scan(root)
    pages = {f: route_of(f) for f in files if route_of(f) is not None}
    found, everywhere, unreached = {}, False, []
    for start in changed:
        if start not in files:
            continue
        seen, todo, hit = {start}, [start], False
        while todo:
            f = todo.pop()
            if f in pages:
                found.setdefault(f, start)
                hit = True
            if LAYOUT.search(f):
                # A layout wraps every page under its folder; the app shell and a root layout wrap them all.
                scope = os.path.dirname(f)
                shell = "pages/_" in f or f.endswith(tuple("app/root" + e for e in EXTS))
                root_layout = route_of(os.path.join(scope, "page.tsx")) == "/" or route_of(os.path.join(scope, "+page.svelte")) == "/"
                for p in pages:
                    if shell or p.startswith(scope + "/"):
                        found.setdefault(p, start)
                        hit = True
                everywhere = everywhere or shell or root_layout
            for g in importers.get(f, ()):
                if g not in seen:
                    seen.add(g)
                    todo.append(g)
        if not hit:
            unreached.append(start)
    out = sorted(({"route": pages[p], "file": p, "via": v} for p, v in found.items()), key=lambda x: (x["route"], x["file"]))
    return {"changed": [c for c in changed if c in files], "pages": out, "global": everywhere, "unreached": unreached}


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    base = args[args.index("--base") + 1] if "--base" in args else None
    if "--files" in args:
        changed = [a for a in args[args.index("--files") + 1:] if not a.startswith("--")]
    else:
        changed = changed_files(base)
    result = blast(changed)
    if as_json:
        print(json.dumps(result, indent=1))
        return
    if result["global"]:
        print("A layout or app shell changed: every page below is affected.")
    for p in result["pages"]:
        print(f"{p['route']:<30} {p['file']}  (via {p['via']})")
    if result["unreached"]:
        print("No page found for: " + ", ".join(result["unreached"]))
    if not result["changed"]:
        print("No changed source files.")


if __name__ == "__main__":
    main()
