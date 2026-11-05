# dev-receipts

Runs a change from a one-line request to a PR, and makes every claim on the way carry a receipt: a test, a command and its output, a screenshot, a step someone can repeat. When the change touches a screen, it hands the look to `ui-direction` and the check to `ui-receipts`.

```sh
npx skills add fajarhide/skills --skill dev-receipts -g
```

Install all three skills to get the screen steps. Without the other two, the agent still writes the spec and the PR table, and it marks the screen rows Not verified.

## What it changes

We gave agents the same two prompts with and without the skill, first to see where they go wrong on their own. These agents already had strict global instructions about verifying work, so the baseline is stronger than a fresh install.

| Failure seen without the skill | Runs | What the skill puts in its place |
| --- | --- | --- |
| The plan stays in the agent's head, with no acceptance criteria anyone can check | 2 of 2 | A spec file on disk, where every acceptance row names its receipt |
| A request and accept flow, a new table and a migration, chosen silently for "I need it today" | 2 of 2 | Both designs in one line each, the smaller one built, the other listed under Not doing |
| Empty, failure, phone and keyboard states never specified | 4 of 4 | A screen states table filled in before any code |
| An unrequested refactor shipped in the same PR | 2 of 2 | Every changed line traces to an acceptance row, anything else is split out |
| "Done" said about a button nobody had seen in a browser | 1 of 2 | A screen that changed is walked in a real browser, or the row is Not verified |

## A real repo, seven runs

Seven agents got the same small Bun and SQLite app, the same request ("add a way for two staff to swap a shift with each other. I need it today, keep it moving.") and the same browser on a remote machine. Four read this skill first. Afterwards we ran every final commit ourselves, loaded the page and counted what it showed.

| | Without the skill (3 runs) | With the skill (4 runs) |
| --- | --- | --- |
| Spec on disk with a receipt per row | 0 | 4 |
| PR body with a receipts table, Not verified and Not doing | 0 | 4 |
| Agent walked the flow in a browser | 0 | 3 |
| Tests at the end | 5, 5, 7 | 11, 16, 11, 12 |
| Page renders when we load it | 3 | 3 |
| Rewrote the existing render function nobody asked about | 0 | 2 |
| Minutes | 1.6 to 2.3 | 2.1 to 9.5 |

The skill lost on two rows. Two runs rewrote the list renderer while adding swap buttons, and one committed an empty `index.html`, so its page was blank. That run had said plainly that it never opened the page. After this round the skill gained three lines: extend code before replacing it, fetch each changed page over HTTP when no browser can run, and on a shared machine stop only your own processes. Those lines have not been tested yet.

Our setup had its own fault. The ports we handed to four of the seven runs were already taken on the shared test machine, so three of them could not open a browser (one with the skill worked around it). We reran one run per side on free ports. Every run chose a request and accept flow over a direct swap, with the reason that a direct swap moves a shift its owner never agreed to.

## One brief, built twice

The brief: "Our vet clinic schedules staff shifts in a web app. Build the screen where a staff member swaps one of their shifts with a colleague. I need it today, keep it moving." Both agents got the same brief, the same fake server (600 ms, rejects a locked shift) and the same access to a browser. One of them also had the three skills. The same script took every screenshot below.

### Picking the shift to take

The agent without the skill lists every colleague shift and leaves the locked one selectable. With the skill, the screen says what you are giving away, and each option that would not work says why: you already work that day, or it is the same shift.

| Without the skill | With the three skills |
| --- | --- |
| <img src="../../assets/dev-receipts/before-desktop-swap.png" width="440" alt="Dialog listing six colleague shifts, one marked Locked but still selectable"> | <img src="../../assets/dev-receipts/after-desktop-swap.png" width="440" alt="Two columns, unworkable shifts greyed out with the reason under each"> |

### When the server says no

Both screens show the error. The second one says what happened, that nothing changed, what it kept and what to do next.

| Without the skill | With the three skills |
| --- | --- |
| <img src="../../assets/dev-receipts/before-desktop-fail.png" width="440" alt="Red box: the shift is locked and cannot be swapped"> | <img src="../../assets/dev-receipts/after-desktop-fail.png" width="440" alt="Banner: locked by the rota manager after the page loaded, nothing changed, your shift is still selected"> |

### On a phone

The first line of the second screen counts what can still be done and offers the next swap as one button.

| Without the skill | With the three skills |
| --- | --- |
| <img src="../../assets/dev-receipts/before-mobile.png" width="300" alt="Five shift cards, each with a Swap button"> | <img src="../../assets/dev-receipts/after-mobile.png" width="300" alt="3 of your 5 shifts can still be swapped, with a button for the next one"> |

### What each agent checked

| | Without the skill | With the three skills |
| --- | --- | --- |
| Opened it in a browser | No | Yes, phone and desktop |
| Forced cases | None | Double-click confirm, server refusal, 390 px width, Tab order |
| Said what it did not test | Yes, everything | Reduced motion, 200% zoom, 320 px, JavaScript off, slow network, reload |
| Time and tokens | 35 s, 50k | 6 min, 78k |

## Limits

This is one build per side, and nobody judged the screenshots blind. It shows what the skill makes an agent do. It does not show by how much the skill wins. The look did not get bolder, because a screen people work in should get clearer, and `ui-direction` says so. The skill costs time: six minutes against thirty-five seconds here, most of it spent checking.
