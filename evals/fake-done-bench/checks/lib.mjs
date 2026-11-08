import { chromium } from "playwright";

// One page per staff member and width, with page errors collected.
export async function open(base, { staff = 1, width = 1280, path = "/" } = {}) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height: 844 }, acceptDownloads: true });
  await ctx.addCookies([{ name: "staff", value: String(staff), url: base }]);
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
  page.on("dialog", (d) => d.accept());
  await page.goto(base + path, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);
  return { browser, ctx, page, errors };
}

export function report(task, checks) {
  const pass = checks.every((c) => c.ok);
  console.log(JSON.stringify({ task, pass, checks }));
  process.exit(0);
}
