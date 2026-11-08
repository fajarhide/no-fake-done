// Filtering to the ward called Ward shows all five ward shifts, including the one typed "ward ".
import { open, report } from "./lib.mjs";
const base = process.argv[2], checks = [];
const { browser, page, errors } = await open(base, { path: "/all.html" });
let applied = false;
const select = page.locator("select").first();
if (await select.count()) {
  const labels = await select.locator("option").allInnerTexts();
  const label = labels.find((l) => /^\s*ward\s*$/i.test(l));
  if (label !== undefined) { await select.selectOption({ label }); applied = true; }
} else {
  const btn = page.getByRole("button", { name: /^\s*ward\s*$/i }).first();
  if (await btn.count()) { await btn.click(); applied = true; }
}
await page.waitForTimeout(500);
const rows = await page.locator("tbody tr:visible, #all li:visible").count();
checks.push({ ok: applied, what: "a Ward option to pick" });
checks.push({ ok: applied && rows === 5, what: "rows shown for Ward", got: rows, want: 5 });
checks.push({ ok: errors.length === 0, what: "page errors", got: errors });
await browser.close();
report("ward-filter", checks);
