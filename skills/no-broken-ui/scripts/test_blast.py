#!/usr/bin/env python3
"""Run with: python scripts/test_blast.py. Standard library only."""
import json
import os
import subprocess
import sys
import tempfile

BLAST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blast.py")

FILES = {
    "src/app/layout.tsx": "import './globals.css'\nexport default function L({children}) { return children }\n",
    "src/app/globals.css": "body { margin: 0 }\n",
    "src/app/page.tsx": "import Hero from '@/components/Hero'\nexport default function P() { return <Hero/> }\n",
    "src/app/pricing/page.tsx": "import { Table } from '../../components/Table'\nexport default function P() { return <Table/> }\n",
    "src/components/Hero.tsx": "import Button from './Button'\nexport default function Hero() { return <Button/> }\n",
    "src/components/Button.tsx": "import { cn } from '../lib/cn'\nexport default function Button() { return null }\n",
    "src/components/Table.tsx": "export function Table() { return null }\n",
    "src/lib/cn.ts": "import { x } from './loop'\nexport const cn = () => x\n",
    "src/lib/loop.ts": "import { cn } from './cn'\nexport const x = 1\n",
    "src/lib/unused.ts": "export const y = 2\n",
    "public/status.html": "<link rel='stylesheet' href='/status.css'><script src='status.js'></script>\n",
    "public/status.css": "h1 { color: red }\n",
}


def run(changed):
    with tempfile.TemporaryDirectory() as root:
        for path, text in FILES.items():
            os.makedirs(os.path.join(root, os.path.dirname(path)), exist_ok=True)
            with open(os.path.join(root, path), "w") as f:
                f.write(text)
        out = subprocess.run([sys.executable, BLAST, "--json", "--files", *changed], cwd=root,
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)


# 1. A component two levels down reaches the home page only; the import cycle in lib/ terminates.
r = run(["src/components/Button.tsx"])
assert [p["route"] for p in r["pages"]] == ["/"], r
assert not r["global"], r

# 5. A file inside the cycle still finds its way up.
assert [p["route"] for p in run(["src/lib/loop.ts"])["pages"]] == ["/"]

# A relative import two folders up resolves.
assert [p["route"] for p in run(["src/components/Table.tsx"])["pages"]] == ["/pricing"]

# 2. The layout, and CSS it imports, reach every page.
for f in ("src/app/layout.tsx", "src/app/globals.css"):
    r = run([f])
    assert r["global"] and {p["route"] for p in r["pages"]} >= {"/", "/pricing"}, (f, r)

# 3. CSS linked from a static page.
assert [p["route"] for p in run(["public/status.css"])["pages"]] == ["/status.html"]

# 4. Nothing imports it.
r = run(["src/lib/unused.ts"])
assert r["pages"] == [] and r["unreached"] == ["src/lib/unused.ts"], r
print("ok")
