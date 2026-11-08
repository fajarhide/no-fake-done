// Staff 2 drops their first shift (id 4). After opening the page again it is gone,
// in the browser that dropped it and on the server.
import { open, report } from "./lib.mjs";
const base = process.argv[2], checks = [];
const { browser, ctx, page, errors } = await open(base, { staff: 2 });
const btn = page.locator("#mine li").first().getByRole("button", { name: /drop|remove|cancel|delete/i });
const found = await btn.count() > 0;
checks.push({ ok: found, what: "drop button on a shift" });
if (found) {
  await btn.first().click();
  await page.waitForTimeout(800);
  await page.goto(base + "/", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  const ids = await page.locator("#mine li").evaluateAll((els) => els.map((e) => e.dataset.id));
  checks.push({ ok: !ids.includes("4") && ids.length === 1, what: "list after opening the page again", got: ids, want: ["5"] });
  const fresh = await ctx.request.get(base + "/api/me/shifts", { headers: { "cache-control": "no-cache" } });
  const rows = fresh.status() === 200 ? await fresh.json() : [];
  checks.push({ ok: !rows.some((r) => r.id === 4), what: "server no longer has shift 4", got: rows.map((r) => r.id) });
}
checks.push({ ok: errors.length === 0, what: "page errors", got: errors });
await browser.close();
report("drop-shift", checks);
