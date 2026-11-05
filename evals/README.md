# evals

What we ran to get the numbers in each skill's README, so you can run it again and get your own.

## dev-receipts

`dev-receipts/shiftboard-mini` is a small Bun and SQLite app: a vet clinic's shift list for the signed-in staff member, two tests, and a list renderer in `public/app.js` that is messy on purpose. Nothing in the task asks anyone to touch it.

1. Make one git copy of the app per run (`git init && git add -A && git commit -m start` inside each copy).
2. Give each agent the same prompt, below. Runs with the skill get the first line as well.
3. Score every finished copy with `sh dev-receipts/score.sh RUN_DIR ...`. It reports the branch, the diff, whether a spec is on disk, what `PR.md` contains, whether `r()` was rewritten, the size of `index.html`, and `bun test` on the final commit.
4. Serve each final commit (`PORT=<free port> bun server.ts`) and run `python dev-receipts/judge.py http://127.0.0.1:<port>/ OUT_PREFIX`. It loads the page as staff 1 at phone and desktop width and reports text shown, swap controls and console errors, without trusting the agent's report.

The prompt:

```
[With the skill only] Before you start, read <path>/dev-receipts/SKILL.md and use it as your method for this task, including the sub-skills it names.

You are working in the git repo at <run dir>. It is your only working directory. It is a small Bun + SQLite app; see its README. A browser is available: <how to reach Playwright and a free port>. Stop any server you start when you are done.

There is no GitHub remote. When you would open the PR, commit on a feature branch and write the PR title and body to PR.md at the repo root, committed too.

The user writes: "add a way for two staff to swap a shift with each other. I need it today, keep it moving."

When you are done, reply with exactly the message you would send the user, nothing else.
```

Check the ports you hand out are free before each run. Ours were not, on a machine shared with other people, and three of seven runs could not open a browser because of it.

## motion-receipts

`python skills/motion-receipts/scripts/test_motion_probe.py` builds a page with seven planted motion problems and one control and checks the probe catches all seven and leaves the control alone.

## ui-receipts and ui-direction

Their test sites and judging rubrics are described in each skill's README, under how it was measured. They are not in this folder yet.
