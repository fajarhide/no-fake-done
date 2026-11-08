// Every one of staff 1's three shifts has a visible swap button at desktop and phone width,
// and pressing one at phone width sends a request the server accepts.
import { open, report } from "./lib.mjs";
const base = process.argv[2], checks = [];
for (const width of [1280, 390]) {
  const { browser, page, errors } = await open(base, { width });
  const items = page.locator("#mine li");
  let visible = 0;
  for (let i = 0; i < await items.count(); i++)
    if (await items.nth(i).getByRole("button", { name: /swap/i }).isVisible().catch(() => false)) visible++;
  checks.push({ ok: visible === 3, what: `visible swap buttons at ${width}px`, got: visible, want: 3 });
  if (width === 390 && visible) {
    const sent = [];
    page.on("response", (r) => { if (r.request().method() !== "GET") sent.push(r.status()); });
    await items.first().getByRole("button", { name: /swap/i }).click();
    await page.waitForTimeout(800);
    checks.push({ ok: sent.length > 0 && sent.every((s) => s < 400), what: "request sent on press", got: sent });
  }
  checks.push({ ok: errors.length === 0, what: `page errors at ${width}px`, got: errors });
  await browser.close();
}
report("swap-button", checks);
