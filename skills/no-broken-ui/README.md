# no-broken-ui

The screenshot looks finished. Then a customer double-clicks Pay and is charged twice, a failed signup wipes everything they typed, and on a phone the table pushes the whole page sideways. None of that shows in a diff, so an agent that only reads code never sees it.

`no-broken-ui` makes the agent use the page the way people do, force what the happy path hides, and report only what it saw happen.

A UI and UX audit skill for AI coding agents. The agent opens your app in a real browser, tries to break it, and reports what it found. Every finding carries a receipt: the action it performed, a number it measured, or a judgment labelled as one.

```sh
npx skills add fajarhide/skills --skill no-broken-ui -g
pip install playwright && playwright install chromium
```

`-g` installs it for your user. Without it, the skill lands inside whichever project you ran the command from.

Then ask your agent, in plain words:

```
Audit the UI and UX of http://localhost:3000
Why does this checkout feel off?
Check this page before I ship it
How would you redesign this flow?
```

## What you get back

Up to ten findings, ranked by what they cost the user. This is the top of a real report from a run on a test shop, with one line trimmed:

```
1. [Blocker] Checkout shows Rp 95.000 as the order total, but the order is
   recorded as "Paid Rp 120.000 (includes Rp 25.000 shipping)".
   Receipt: observed: checkout.html shows `Order total: Rp 95.000`. After Pay,
   the order list reads "Paid Rp 120.000 (includes Rp 25.000 shipping)".
   Fix: show subtotal, shipping and the real total before the Pay button, and
   put the same total on the button ("Pay Rp 120.000").
```

After the findings come what held up and should not be broken, and what could not be tested and why.

The agent also forces what a happy path never shows: double submits, failed requests, empty states, long text, reloads, keyboard use. `scripts/probe.py` measures contrast, tap targets, unlabeled controls, broken images, dead links, clipped text, page overflow and leaked text such as `undefined`, at phone and desktop widths.

## Before and after

Each pair is the same page, viewport and steps. The screens are test pages with synthetic data, audited with this skill and then fixed by hand following its findings. The skill reports and measures. The fixing is up to you or your agent.

### A form that loses your work

Bad email, then submit. The message vanishes, and everything typed is gone.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/signup-failed-before.png" width="340" alt="Empty form with a vague error"> | <img src="../../assets/no-broken-ui/signup-failed-after.png" width="340" alt="Input kept, error beside the field"> |

### A button that looks broken

0.5 seconds after clicking submit. Nothing tells you to wait, so you click again.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/signup-waiting-before.png" width="340" alt="Button unchanged"> | <img src="../../assets/no-broken-ui/signup-waiting-after.png" width="340" alt="Button disabled, saying Creating account"> |

### Charged twice

Double-click on Pay. Also note the total: the before says Rp 95.000 and charges Rp 120.000.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/checkout-double-before.png" width="340" alt="Two paid orders"> | <img src="../../assets/no-broken-ui/checkout-double-after.png" width="340" alt="One paid order, full total shown"> |

### A declined card

The address and phone should survive a problem with the card.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/checkout-declined-before.png" width="340" alt="Form wiped, Payment failed"> | <img src="../../assets/no-broken-ui/checkout-declined-after.png" width="340" alt="Details kept, error says what to do"> |

### A table on a phone

Measured page width: 1000 px on a 390 px screen before, no page overflow after. The clipped customer name now wraps.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/dash-mobile-before.png" width="340" alt="Page overflows sideways"> | <img src="../../assets/no-broken-ui/dash-mobile-after.png" width="340" alt="Table scrolls in its own container"> |

### Filtering to nothing

The before also still says "4 invoices".

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/dash-empty-before.png" width="440" alt="Empty table"> | <img src="../../assets/no-broken-ui/dash-empty-after.png" width="440" alt="Message with a clear filter button"> |

### One click from deleting

Taken right after clicking Delete on the first row. In the before, the row is already gone.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/dash-delete-before.png" width="440" alt="Row removed at once"> | <img src="../../assets/no-broken-ui/dash-delete-after.png" width="440" alt="Confirm naming the invoice"> |

### A dialog off the screen

Measured page width: 668 px on a 390 px screen before, no page overflow after. The dialog now fits, closes with Escape, and has a Cancel.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/settings-dialog-before.png" width="340" alt="Dialog cut off"> | <img src="../../assets/no-broken-ui/settings-dialog-after.png" width="340" alt="Dialog fits"> |

### A call to action you can barely read

Measured contrast: 2.55 before, against the 4.5 required. The probe reports no failure after.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/contrast-before.png" width="340" alt="Pale green link"> | <img src="../../assets/no-broken-ui/contrast-after.png" width="340" alt="Dark green link"> |

### Docs that fight the phone

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/docs-mobile-before.png" width="340" alt="Sidebar crushes the text"> | <img src="../../assets/no-broken-ui/docs-mobile-after.png" width="340" alt="Sidebar stacks above the text"> |

### A link that hides its own heading

Click "Storing". In the before, the heading lands under the sticky header.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/docs-anchor-before.png" width="440" alt="Heading hidden"> | <img src="../../assets/no-broken-ui/docs-anchor-after.png" width="440" alt="Heading visible"> |

### The generic AI look

The skill asks whether the page could belong to any other product if the logo were swapped. A plain page or a bold brand passes. This one does not, because it never says what the product does. The new copy here is invented for the demo.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/landing-before.png" width="440" alt="Purple gradient, Supercharge your productivity"> | <img src="../../assets/no-broken-ui/landing-after.png" width="440" alt="A concrete promise and an example of the output"> |

### On a real product

An update button in [Nakama](https://github.com/ahmadrosid/nakama), 0.5 seconds after the click. It sat idle for about 3 seconds, and the fix shipped in [a pull request](https://github.com/ahmadrosid/nakama/pull/2221) with these screenshots. This one was found by hand, and the skill was built from that way of working.

| Before | After |
| --- | --- |
| <img src="../../assets/no-broken-ui/real-before.png" width="440" alt="Button unchanged after the click"> | <img src="../../assets/no-broken-ui/real-after.png" width="440" alt="Starting, with a spinner"> |

## More things to ask it

- Check a page before you ship it, and get before and after screenshots with numbers (`probe.py --label before`, then `--label after`).
- Review a landing page: what it is, who for, and whether the main button goes anywhere.
- Review a dashboard: the one decision it serves, and whether the columns help.
- Review a form or a checkout: labels, errors, and whether a failure loses input.
- Review docs: search, anchors, code blocks, phone layout.
- Run it on a page behind a login: `--cookie name=value`.
- Look over production read-only. The agent does not submit, delete or send there, and says which checks that ruled out.
- Ask for a redesign, below.

## Asking for a redesign

Say "how would you redesign this", and after the audit the agent proposes up to three moves that change what the flow is, each with what it costs and what it could break. This came from a run on a one-product coffee shop:

> Today a buyer adds a bag to a cart, then goes to a separate checkout that ignores the cart, instead each bag has a "Buy" button that opens a one-screen order for that bag [...], and the cart only appears once a second bag is added.

These are proposals to test, and nothing about them was measured. It runs as a separate step on purpose: when we mixed it into the audit, defects found fell from a mean of 17 in the first batch to 14.7 and then 12.7, with the same scoring.

## How it was measured

Test site: four pages with 18 seeded defects and 4 decoys, things that look wrong but are fine, such as a low-contrast disabled button. The agent only had the URL. All runs used one mid-tier model. Each report was scored against an answer key by a separate agent, from shuffled file names. The decoys and the key were written by the skill's author, and the report format can give away which run used the skill.

| Mean per run | With the skill (9 runs) | Without (6 runs) |
| --- | --- | --- |
| Defects found, of 18 | **13.9** (range 9 to 17) | 10.3 (range 7 to 13) |
| Decoys reported as defects, of 4 | **0.3** | 3.2 |
| Factual claims the source contradicts | **1.1** | 2.3 |
| Items in the report | **10** | 15.8 |

What this does and does not show:

- **Cleaner reports are the most reliable gain.** A team reading ten ranked findings with no decoys spends less time checking them.
- **Detection improved, and the ranges overlap.** Runs vary a lot: one run with the skill found 9 and another found 17. A single audit will miss things, so run it twice on anything important.
- **Some defects are often missed even with the skill,** such as a dialog overflowing on a phone, which only 2 of the 9 runs caught. Agents do not always force every case in the walkthrough.
- **These are small samples on a synthetic site,** written by the author. The skill was also run once on a real settings page, where it found one-click actions with no confirm, but that run has no answer key.
- **Cost was about the same with and without:** near 90k tokens and 2 to 4 minutes per run.

## What it will not do

- It does not replace testing with real people. It finds what can be seen and measured, not whether anyone wants the product.
- It only sees the web. Native iOS, Android and desktop apps can only be judged from screenshots you provide.
- It needs a running app. Behind a login with no test account, it stops at the login and says so.
- It cannot prove a page looks better. It shows you both screenshots and leaves that call to you.

## License

Apache 2.0
