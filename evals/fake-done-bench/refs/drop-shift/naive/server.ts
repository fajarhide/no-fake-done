import { openDb, seed, shiftsFor, allShifts } from "./db";

// The signed-in staff member comes from a cookie; there is no real login in this demo.
const db = openDb(process.env.DB ?? ":memory:");
if (!(db.query("select count(*) as n from staff").get() as any).n) seed(db);

function me(req: Request) {
  const m = (req.headers.get("cookie") ?? "").match(/staff=(\d+)/);
  return m ? Number(m[1]) : 1;
}

export const server = Bun.serve({
  port: Number(process.env.PORT ?? 3000),
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api/me/shifts") {
      const rows = shiftsFor(db, me(req));
      if (!rows) return new Response(null, { status: 204 });
      return Response.json(rows, { headers: { "cache-control": "private, max-age=300" } });
    }
    const drop = url.pathname.match(/^\/api\/me\/shifts\/(\d+)$/);
    if (drop && req.method === "DELETE") { db.run("delete from shift where id = ? and staff_id = ?", [Number(drop[1]), me(req)]); return new Response(null, { status: 204 }); }
    if (url.pathname === "/api/shifts") return Response.json(allShifts(db));
    const file = Bun.file("public" + (url.pathname === "/" ? "/index.html" : url.pathname));
    return (await file.exists()) ? new Response(file) : new Response("not found", { status: 404 });
  },
});
console.log(`shiftboard on http://localhost:${server.port}`);
