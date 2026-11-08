---
name: no-fake-done
description: Use when building a feature, fixing a bug or making any change that ends in a commit or PR, from a one-line request to merge, especially under time pressure ("I need it today", "keep it moving", "tell me it's done", "open the PR"), when the change touches a screen people use, or before saying a change is done.
---

# no-fake-done

Every claim about a change carries proof: a test, a command and its output, a screenshot, a step someone can repeat. Done means every acceptance row has one. This runs a change from request to PR in five steps. A step the user has already covered, such as an approved spec, is skipped. Asked only to audit something that already exists, with no change to make, use `no-broken-ui` instead, and come back here when the user asks for the fixes or a before and after.

## 0. Size the change

Take the **small path** when the change fits in an existing screen or endpoint, touches a few files, and adds no new page, table, permission, payment or auth rule. Everything else, and anything the user wants reviewed closely, takes the full path below.

The small path keeps what a reviewer needs and drops the rest:

1. Spec: the Ask line and the Acceptance table only, three to five rows, on disk as below. Skip Screen states, and add one row for the case the data or code makes likely to break (an empty list, a value with a comma, a phone width, a reload).
2. Look: follow the screen's existing styles. Do not load the sub-skills.
3. Build and test as in step 3.
4. Verify: run the project's checks, then open the changed flow once in a real browser at desktop and phone width and try that one likely case. Do not load `no-broken-ui` or force its whole table.
5. Ship exactly as in step 5: the proof table, Not verified, Not doing, commit, then `proof.py`.

If the small path finds a failure you cannot explain, switch to the full path.

## 1. Spec: write down what done means

Before the first line of code, write the spec to disk, where the repo keeps specs or else `docs/specs/YYYY-MM-DD-<slug>.md`. A plan kept in your head is gone after compaction, and the user cannot correct what they never saw.

```
# <change>
Ask: "<the user's words>"
Smallest version: <the one that meets the ask and its deadline>
Assumptions: <each guess that changes what gets built, one per line>
Not doing: <what someone might expect that you are leaving out>

## Acceptance
| # | When | Then | Proof |
| 1 | <action or input> | <observable result> | <test name, command, screenshot or walk step> |

## Screen states (only when a screen changes)
| State | What the person sees, and what they can do next |
| First use or empty | |
| Loading or slow | |
| Failure | |
| Success | |
| Phone | |
| Keyboard only | |
```

- When two designs differ in size, such as a direct swap versus a request and accept flow with a new table, write each in one line, build the smaller one that meets the ask, and put the other under Not doing. Ask the user only when the smaller one would be wrong for them, not merely less complete.
- Every acceptance row names its proof when you write it. "Looks fine" is not proof.
- Include the rules the server has to enforce: who may do it, data that changed since the page loaded, and a repeat or double submit.
- Tell the user the smallest version, the assumptions and Not doing in a few lines, then keep going.

## 2. Look, when a screen changes

- A new page, or one that should have a look of its own: REQUIRED SUB-SKILL `no-template-ui`.
- A screen inside an existing app: use the app's own components and conventions. For a screen people work in, apply the Desk rules from `no-template-ui`: the first line names what needs doing now with a button, each action states its consequence next to it ("accepting gives you Saturday night"), sample data opens on the hard cases, and a phone gets a layout built around the next task.

## 3. Build

- Write the test first for every acceptance row a test can prove.
- Every changed line traces to an acceptance row. A cleanup you want on the way goes in a note for its own PR. If you already made one, revert it or split it out before opening the PR. Extend existing code before replacing it: rewriting a function you only needed to call is a refactor too.
- Reuse what the repo already has before adding anything.

## 4. Verify: collect the proof

Run the project's own checks (tests, typecheck, lint, build) and keep their real output.

If a screen changed, open it in a real browser. Unit tests and a clean build say nothing about a dialog. REQUIRED SUB-SKILL `no-broken-ui`: probe the changed pages, walk the changed flow, and force every row of its table that applies to the change. Each Screen states row ends with a screenshot or a walk step.

When no browser can run, still request each changed page over HTTP and check it returns the content you expect, since an empty or truncated file is the commonest break. A row you cannot check here (no browser, no test account, no database) goes under Not verified with the reason. It is never marked as passing.

Open every file or link you hand over the way its reader will: double-clicked from disk, the published URL, the PR page. A page that passes behind a test server can still arrive unstyled when relative paths no longer resolve.

On a shared machine, use a port you checked is free and stop only the processes you started, by PID.

## 5. Ship

Build your final message, and the PR body when there is a PR, from the acceptance table:

```
<one or two lines: what changed for the person using it>

| # | Acceptance | Proof |
| 1 | Swap updates both shifts | `vitest run lib/swap.test.ts`: 6 passed |
| 5 | Phone layout | screenshot `swap-mobile.png` |

Not verified: <row and reason>, or none.
Not doing: <from the spec>.
```

If any row is under Not verified, the message says the change is not done yet and names those rows first.

A PR is optional. Without one, the spec file is the record: its Proof column is filled in, and every claim of done in your message points to its row there.

Commit the work first. Then, before that message, run `python scripts/proof.py <spec file>` from the repo root, adding the PR body file when there is a PR, and fix every FAIL: proof that is empty or filler, a file it names that does not exist, a Not verified row the Not verified line leaves out, or a change git has not committed. If the user asked you not to commit, pass `--uncommitted-ok` and say in the message that nothing is committed.

## Red flags

| Thought | Reality |
| --- | --- |
| "Tests and build pass, so it's done" | They prove the logic. A screen nobody opened is unverified. |
| "They are in a hurry and trust me" | Cut scope to go faster. A skipped check moves the failure into the demo. |
| "I'll keep the plan in my head" | Write the spec. It takes two minutes and survives compaction. |
| "This refactor is small and related" | It is not in the acceptance table. Split it out. |
| "The old render function is a mess and I am in the file anyway" | Extend it. Rewriting it is a refactor. |
| "Done and committed" | Write it after `proof.py` passes, which reads `git status` for you. Saying it is not doing it. |
| "It is small, so it needs no proof table" | The small path skips process, never proof. The table, Not verified and the commit stay. |
| "I'll fill in the manual check line later" | A placeholder in a spec or PR body reads as a claim. Fill it or move the row to Not verified. |
