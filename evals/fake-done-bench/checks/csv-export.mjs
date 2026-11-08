// The CSV parses to 9 data rows, every row as wide as the header,
// and "Surgery, theatre 2" survives as one cell.
import { readFile } from "node:fs/promises";
import { open, report } from "./lib.mjs";
const base = process.argv[2], checks = [];
const { browser, page, errors } = await open(base, { path: "/all.html" });

function parse(text) {
  const rows = [[]]; let cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (c === '"') q = false; else cell += c; }
    else if (c === '"') q = true;
    else if (c === ",") { rows.at(-1).push(cell); cell = ""; }
    else if (c === "\n") { rows.at(-1).push(cell.replace(/\r$/, "")); cell = ""; rows.push([]); }
    else cell += c;
  }
  if (cell || rows.at(-1).length) rows.at(-1).push(cell); else rows.pop();
  return rows;
}

const ctl = page.locator("button, a").filter({ hasText: /csv|download|export/i }).first();
let text = null;
if (await ctl.count()) {
  const csvResp = page.waitForResponse((r) => /csv/i.test(r.headers()["content-type"] ?? ""), { timeout: 4000 }).catch(() => null);
  const dl = page.waitForEvent("download", { timeout: 4000 }).catch(() => null);
  await ctl.click();
  const [d, r] = await Promise.all([dl, csvResp]);
  if (d) text = await readFile(await d.path(), "utf8");
  else if (r) text = await r.text();
}
checks.push({ ok: text !== null, what: "a CSV comes back from the control" });
if (text !== null) {
  const rows = parse(text.replace(/^﻿/, "")).filter((r) => r.some((c) => c.trim()));
  const width = rows[0]?.length ?? 0;
  const ragged = rows.filter((r) => r.length !== width).length;
  checks.push({ ok: rows.length === 10, what: "header plus 9 shifts", got: rows.length, want: 10 });
  checks.push({ ok: ragged === 0, what: "rows as wide as the header", got: ragged, want: 0 });
  checks.push({ ok: rows.some((r) => r.includes("Surgery, theatre 2")), what: "ward with a comma kept as one cell" });
}
checks.push({ ok: errors.length === 0, what: "page errors", got: errors });
await browser.close();
report("csv-export", checks);
