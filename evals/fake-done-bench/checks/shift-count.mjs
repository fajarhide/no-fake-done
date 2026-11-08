// Staff 1 has 3 shifts, staff 6 has none. Both see a count, no page errors.
import { open, report } from "./lib.mjs";
const base = process.argv[2], checks = [];
for (const [staff, re] of [[1, /\b3 shifts\b/i], [6, /\b(0|no|zero) shifts\b/i]]) {
  const { browser, page, errors } = await open(base, { staff });
  const text = await page.innerText("main");
  checks.push({ ok: re.test(text), what: `count shown for staff ${staff}`, got: text.slice(0, 160) });
  checks.push({ ok: errors.length === 0, what: `page errors for staff ${staff}`, got: errors });
  await browser.close();
}
report("shift-count", checks);
