# no-leaky-app

You add a strict Content-Security-Policy to the home page and call the app hardened. The 404 page still has no policy, the API still answers with a version banner, and the policy you added still lets inline scripts run. Nothing in a code review shows it, because each header is right where it was written and missing everywhere it was not.

`no-leaky-app` makes the agent request one of each response your app sends, check every one against a table of headers and delivery rules, fix them in the one place every response passes through, and show the headers before and after.

```sh
npx skills add fajarhide/no-fake-done --skill no-leaky-app -g
```

Use it on an app you own or are allowed to change.

## What it checks

Content-Security-Policy that is enforced and complete (no `'unsafe-inline'`, `'unsafe-eval'`, `*` or `data:` in `script-src`, plus `object-src 'none'` and `base-uri`), framing protection, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS, `no-store` on account data, and no version banners. Each one on the responses where it belongs, 404 and error pages included. Then delivery: source maps, server secrets in the client bundle, session tokens in `localStorage`, credentialed CORS that echoes any origin, debug endpoints, stack traces, and static files outside the public folder.

## How it was measured

Two small Bun apps, each with seven seeded gaps. Agents got the same request ("review it for security hardening problems and fix them before we launch") and the same test host to run the app on. Three ran without the skill and three with it. Afterwards each final commit was started and probed with real requests by `evals/no-leaky-app/score_round*.py`, so a gap counted as closed only when the response changed.

| Round | Without the skill | With it | Broke the app |
| --- | --- | --- | --- |
| 1: the obvious gaps already fixed, header completeness left | 4, 5, 6 of 7 | 7, 7, 7 of 7 | never |
| 2: a different app, headers present but with wrong values | 7, 7, 7 of 7 | 7, 7, 7 of 7 | never |

In round 1, without the skill, no run added `Permissions-Policy`, one in three made the CSP complete with `object-src` and `base-uri`, and two in three put the policy on the 404 page. With the skill all three did all of it. In round 2 every run, with or without the skill, fixed a report-only CSP, `data:` in `script-src`, headers missing from the 500 page, a cacheable token, a `Server` version banner, `Referrer-Policy: unsafe-url` and a five-minute HSTS.

## Limits

The skill wins on completeness, items an agent does not think of on its own, and ties where agents already succeed. Those round 1 items are written in the skill's own table, and the same author wrote the skill, both apps and both scorers, so round 1 shows the checklist is followed, not that it finds problems nobody listed. Six runs per round on one model. Every run also found an unseeded problem (a login that needs no password), which no scorer counted.

Before this, two rounds on a simpler app found nothing for a skill to add: agents without it closed 19 of 21 gaps, verified with curl, and broke nothing. That is why the skill covers what they missed and little else.
