import { chromium } from "/root/pw/node_modules/playwright-core/index.mjs";
import { readFileSync } from "fs";
const dir = "/mnt/compare", cfg = JSON.parse(readFileSync(dir + "/configs.json", "utf8"));
const b = await chromium.launch();
const p = await (await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 })).newPage();
for (const [name, c] of Object.entries(cfg)) {
  await p.setViewportSize({ width: c.narrow ? 1200 : 1600, height: 900 });
  await p.goto(`file://${dir}/compare.html?n=${name}#${encodeURIComponent(JSON.stringify(c))}`);
  await p.waitForLoadState("networkidle"); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => i.onload = r))));
  await p.screenshot({ path: `${dir}/${name}.png`, fullPage: true });
  console.log(name, "ok");
}
await b.close();
