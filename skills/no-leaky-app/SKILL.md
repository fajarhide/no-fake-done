---
name: no-leaky-app
description: Use when hardening a web app you own before launch, reviewing its security headers, cookies, CORS, caching or error pages, or when asked "is this app secure", "harden this", "security review before launch", "check our headers". Works on the responses the app actually sends.
---

# no-leaky-app

Check the responses your app sends, not the code that is supposed to produce them. A header added in one route handler is missing from the 404 page, and a policy that looks strict can still allow inline scripts. Every claim carries proof: the response, its headers, and what changed. Work only on an app you own or are authorised to change.

## 1. Collect one of each response

Run the app and request one of each: a page, a 404, an error page, a static file, an API response that carries account data, and a redirect if there is one. Save the headers of each (`curl -s -D - -o /dev/null URL`). This is the before proof.

## 2. Check every response against this table

| Header or behaviour | Passes when | Required on |
| --- | --- | --- |
| Content-Security-Policy | enforced (not only `Report-Only`); `script-src` has no `'unsafe-inline'`, `'unsafe-eval'`, `*` or `data:`; has `object-src 'none'` and `base-uri 'self'` or `'none'` | every HTML response, 404 and error pages included |
| Framing protection | `frame-ancestors` in the CSP, or `X-Frame-Options: DENY` | every HTML response |
| `X-Content-Type-Options` | `nosniff` | every response |
| `Referrer-Policy` | `strict-origin-when-cross-origin` or `no-referrer` | every response |
| `Permissions-Policy` | turns off what the app does not use, such as `camera=(), microphone=(), geolocation=()` | every HTML response |
| `Strict-Transport-Security` | `max-age` of at least 15552000 | every response served over HTTPS |
| `Cache-Control` | `no-store` | responses with account data or tokens |
| Version banners | no `X-Powered-By`, no version in `Server` | every response |

Then the delivery checks: no source maps served in production, no server secret in the client bundle, session tokens only in an `HttpOnly; Secure; SameSite` cookie and never in `localStorage`, no CORS response that echoes any origin with credentials, no debug or environment endpoint, error pages without stack traces, and static files served only from the public folder.

## 3. Fix in one place

Set headers in the single wrapper every response passes through, so a new route or a 404 cannot miss them. Keep what is meant to be public, such as a browser maps key restricted by domain. After a CSP change, load the page and confirm its own scripts still run.

## 4. Prove it

Request the same responses again and put their headers next to the before proof. Write REPORT.md:

```
| Response | Before | After |
| / | <headers> | <headers> |
| 404 | ... | ... |

Fixed: <each gap, where, why it mattered>
Not verified: <check and reason>, or none
Not changed: <what you left and why>
```

A check you could not run here, such as HSTS behind a proxy you cannot reach, goes under Not verified, never as passing.
