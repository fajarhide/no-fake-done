#!/bin/sh
# "clinic-bills": held-out app for no-leaky-app. Seven gaps round 1 did not have, three decoys.
# Every secret is an obvious fake. The answer key lives outside the fixture.
set -e
ROOT="$1"
F="$ROOT/template"
rm -rf "$ROOT" && mkdir -p "$F/web" "$F/lib" && cd "$F"

cat > README.md <<'EOF'
# clinic-bills

Pet owners see and pay their vet bills. Bun, no build step. Security headers were added last
sprint through `lib/headers.ts`.

    bun main.ts        # PORT=3000 by default
EOF

cat > package.json <<'EOF'
{ "name": "clinic-bills", "private": true, "scripts": { "start": "bun main.ts" } }
EOF

cat > lib/headers.ts <<'EOF'
// Applied to every successful response.
export const SECURITY_HEADERS: Record<string, string> = {
  "Content-Security-Policy-Report-Only":
    "default-src 'self'; script-src 'self' data:; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "unsafe-url",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Strict-Transport-Security": "max-age=300",
  "Server": "clinic-bills/2.3.1 (bun)",
};

export function secure(res: Response): Response {
  const headers = new Headers(res.headers);
  for (const [k, v] of Object.entries(SECURITY_HEADERS)) headers.set(k, v);
  return new Response(res.body, { status: res.status, headers });
}
EOF

cat > lib/routes.ts <<'EOF'
import { randomUUID } from "crypto";

const sessions = new Map<string, string>();

export async function route(req: Request): Promise<Response> {
  const url = new URL(req.url);
  if (url.pathname === "/") return new Response(Bun.file("web/index.html"), { headers: { "Content-Type": "text/html" } });
  if (url.pathname === "/web/bills.js") return new Response(Bun.file("web/bills.js"));

  // Clinic status for the public board; fine to cache.
  if (url.pathname === "/api/status") {
    return Response.json({ open: true, queue: 3 }, { headers: { "Cache-Control": "public, max-age=60" } });
  }

  if (url.pathname === "/login" && req.method === "POST") {
    const id = randomUUID();
    sessions.set(id, "owner-17");
    return new Response("ok", { headers: { "Set-Cookie": `bill_sid=${id}; Path=/; HttpOnly; Secure; SameSite=Lax` } });
  }

  const sid = (req.headers.get("cookie") ?? "").match(/(?:^|;\s*)bill_sid=([\w-]+)/)?.[1] ?? "";
  const owner = sessions.get(sid);

  if (url.pathname === "/api/me") {
    if (!owner) return Response.json({ error: "login first" }, { status: 401 });
    return Response.json({ owner }, { headers: { "Cache-Control": "no-store" } });
  }

  // Short-lived token the payment widget uses.
  if (url.pathname === "/api/pay-token") {
    if (!owner) return Response.json({ error: "login first" }, { status: 401 });
    return Response.json({ token: `FAKE-pay-token-${owner}` });
  }

  if (url.pathname === "/api/bills") {
    if (!owner) return Response.json({ error: "login first" }, { status: 401 });
    throw new Error("billing service unavailable");
  }

  return new Response("<!doctype html><title>Not found</title><p>Not found</p>", { status: 404, headers: { "Content-Type": "text/html" } });
}
EOF

cat > main.ts <<'EOF'
import { secure } from "./lib/headers";
import { route } from "./lib/routes";

Bun.serve({
  port: Number(process.env.PORT ?? 3000),
  async fetch(req) {
    try {
      return secure(await route(req));
    } catch {
      return new Response("<!doctype html><title>Error</title><p>Something went wrong.</p>", {
        status: 500,
        headers: { "Content-Type": "text/html" },
      });
    }
  },
});
EOF

cat > web/index.html <<'EOF'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Clinic bills</title>
<style>body{font-family:system-ui;margin:2rem}</style></head>
<body><h1>Your bills</h1><div id="out"></div><script src="/web/bills.js"></script></body></html>
EOF

cat > web/bills.js <<'EOF'
// Browser key for the clinic map; restricted to the clinic's domain in the maps console.
const PUBLIC_MAPS_KEY = "maps-browser-key-restricted-to-clinic-domain";
fetch("/api/me", { credentials: "include" }).then((r) => r.json()).then((d) => {
  document.getElementById("out").textContent = JSON.stringify(d);
});
EOF

git init -q && git add -A && git commit -qm "clinic-bills"
cd "$ROOT"
for n in base1 base2 base3 skill1 skill2 skill3; do cp -R template "$n"; done
ls "$ROOT"
