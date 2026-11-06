#!/bin/sh
# "paws-portal round 1": the obvious gaps are already fixed; seven header and delivery gaps remain.
# Every secret is an obvious fake. The answer key lives outside the fixture.
set -e
ROOT="$1"
F="$ROOT/template"
rm -rf "$ROOT" && mkdir -p "$F/public" && cd "$F"

cat > README.md <<'EOF'
# paws-portal

Pet owners log in to see their pet's appointments. Bun, no build step. Already hardened once
(cookie flags, CORS, no debug endpoint, generic errors); please review before launch.

    bun server.ts      # PORT=3000 by default
EOF

cat > package.json <<'EOF'
{ "name": "paws-portal", "private": true, "scripts": { "start": "bun server.ts" } }
EOF

cat > server.ts <<'EOF'
import { randomUUID } from "crypto";

const sessions = new Map<string, { user: string; pet: string }>();

// Security headers for pages.
const PAGE_HEADERS = {
  "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
};

function withHeaders(res: Response, extra: Record<string, string> = {}) {
  const headers = new Headers(res.headers);
  headers.set("X-Powered-By", "paws-portal/1.4.2 bun");
  for (const [k, v] of Object.entries(extra)) headers.set(k, v);
  return new Response(res.body, { status: res.status, headers });
}

Bun.serve({
  port: Number(process.env.PORT ?? 3000),
  async fetch(req) {
    const url = new URL(req.url);
    try {
      if (url.pathname === "/healthz") return withHeaders(Response.json({ ok: true }));

      if (url.pathname === "/login" && req.method === "POST") {
        const id = randomUUID();
        sessions.set(id, { user: "maya", pet: "Mochi" });
        return withHeaders(new Response("ok", {
          headers: { "Set-Cookie": `sid=${id}; Path=/; HttpOnly; Secure; SameSite=Lax` },
        }));
      }

      if (url.pathname === "/api/me") {
        const sid = (req.headers.get("cookie") ?? "").match(/sid=([\w-]+)/)?.[1] ?? "";
        const s = sessions.get(sid);
        return withHeaders(Response.json(s ?? { error: "login first" }, { status: s ? 200 : 401 }));
      }

      if (url.pathname === "/") {
        return withHeaders(new Response(Bun.file("public/index.html")), PAGE_HEADERS);
      }

      if (url.pathname.startsWith("/public/")) {
        const file = Bun.file("." + url.pathname);
        if (await file.exists()) return withHeaders(new Response(file));
      }
      return withHeaders(new Response("not found", { status: 404 }));
    } catch {
      return withHeaders(new Response("something went wrong", { status: 500 }));
    }
  },
});
EOF

cat > public/index.html <<'EOF'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Paws portal</title></head>
<body><h1>Your pet's appointments</h1><div id="out"></div><script src="/public/app.js"></script></body></html>
EOF

cat > public/app.js <<'EOF'
// Browser key for the clinic map; restricted to the clinic's domain in the maps console.
const PUBLIC_MAPS_KEY = "maps-browser-key-restricted-to-clinic-domain";

async function signIn() {
  const r = await fetch("/login", { method: "POST" });
  // Keep the session handy for the appointment widget.
  localStorage.setItem("session_token", r.headers.get("x-session") ?? "cookie");
}

async function load() {
  const r = await fetch("/api/me", { credentials: "include" });
  document.getElementById("out").textContent = JSON.stringify(await r.json());
}
load();
//# sourceMappingURL=app.js.map
EOF

cat > public/app.js.map <<'EOF'
{"version":3,"file":"app.js","sources":["../src/app.ts"],"sourcesContent":["// internal: staff override code is FAKE-staff-override-0000\nexport async function load() {}\n"],"mappings":"AAAA"}
EOF

git init -q && git add -A && git commit -qm "paws-portal round 1"
cd "$ROOT"
for n in base1 base2 base3 skill1 skill2 skill3; do cp -R template "$n"; done
ls "$ROOT"
