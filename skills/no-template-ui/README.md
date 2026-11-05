# no-template-ui

You ask for a coffee roaster's site. You get cream, terracotta, a serif headline and three icon cards, the page an agent hands almost everyone who asks. Swap the logo and it could sell anything.

`no-template-ui` makes the agent build from what only this subject has, so the page could not belong to anyone else.

A skill for AI coding agents that gives a new web page a look of its own. It makes the agent list what only this subject has, name the worlds its audience knows by heart, roll a die instead of picking the safest one, and check the rendered page.

In our tests, pages built without a skill were marked as generic AI output in 6 of 8 judgments on the two standalone rounds, and pages built with this one in 0 of 8.

```sh
npx skills add fajarhide/skills --skill no-template-ui -g
pip install playwright && playwright install chromium
```

Then ask your agent to build or restyle a page, or to write a `DESIGN.md`.

## What the agent does

For a page people read and act on, it writes down the mechanism and the page this category always ships, lists seven worlds the audience knows, rolls for one, and tests the idea against the nearest competitor. It saves the decision in a `DESIGN.md`, builds, then runs:

```sh
python scripts/probe.py OUT_DIR URL --design DESIGN.md
```

That saves phone and desktop screenshots and reports contrast, tap targets, overflow, font sizes, text edges, margins and any colours or fonts outside the `DESIGN.md`.

For a screen people work in, it skips the worlds. The first line names what needs doing now, with a button. Sample data opens on the hard cases, and the phone gets a layout built around the next task.

## How it was measured

Each round used briefs written for that round, with no brand or photographs. One mid-tier model built each page. Two judges per brief, using a stronger model, scored screenshots with the builds anonymous and shuffled per judge. The rubric weighted job 30%, craft 30%, belonging to the subject 25% and honesty 15%.

Final round, a boat workshop site and a lab sample tracker:

| Mean over 4 judgments | This skill | A popular design skill | No skill |
| --- | --- | --- | --- |
| Overall score, of 10 | **8.32** | 7.55 | 5.60 |
| Ranked first | **4 of 4** | 0 of 4 | 0 of 4 |
| Marked as generic AI output | **0 of 4** | **0 of 4** | 4 of 4 |
| Tokens per build | 93k | 132k | **70k** |

Round before it, a tailor site and a laundry dispatch board:

| Mean over 4 judgments | This skill | A shorter version, no dice | No skill |
| --- | --- | --- | --- |
| Overall score, of 10 | **7.85** | 6.65 | 6.83 |
| Ranked first | **4 of 4** | 0 of 4 | 0 of 4 |
| Marked as generic AI output | **0 of 4** | 1 of 4 | 2 of 4 |
| Tokens per build | 79k | 83k | **68k** |

Read these with the following in mind:

- **Nearly the same text lost once.** Placed inside our audit skill, it scored 6.50 on a letterpress site and a repair queue, behind the same popular skill at 7.62 and no skill at 7.28. We moved it into its own skill and it won both rounds above. We cannot say whether the packaging or the briefs explain the swing, so expect some pages to miss.
- **The sample is small.** Four briefs and eight judgments, with no-skill scores from 5.60 to 6.83 between rounds. Compare within a round only.
- **The other skill ran with a handicap.** It could not ask questions or start the helper agents it uses to review its work, so its full process may do better.
- **The author wrote the briefs, the rubric and this skill.** The judges are models, not people, and they saw screenshots only, so these scores do not test whether forms work.

## The copy recipe

Added on 2026-11-05, after the rounds above. Each headline, button, error and empty state is written to a set shape, and every sentence is read aloud and rewritten if it sounds like an ad or an assistant. A small check: one brief (a booking page for a bicycle repair shop), one model, three runs with the recipe and three without.

| | Without | With the recipe |
| --- | --- | --- |
| Error says what was kept | 1 of 3 | 3 of 3 |
| Error opens with "Sorry" | 2 of 3 | 0 of 3 |
| Button names the specific thing ("Book Sat 7 Nov, 10:00") | 0 of 3 | 3 of 3 |
| Made-up claim or closing flourish left unmarked ("Book it in 30 seconds") | 3 of 3 | 0 of 3 |
| Dashes | 0 | 0 |

The fourth row favours the recipe, since only those runs were asked to list what they made up. Dashes and a repeated verb in the toast were already right without it. Six short runs on one brief are a lead to test on more briefs before anyone quotes them.

## What it will not do

- It does not make the page right for your business. Whether it looks better is your call, so it shows you the screenshots.
- It does not replace an audit. Use [no-broken-ui](../no-broken-ui) to try to break the result.
- An existing `DESIGN.md` or brand decides. The skill then follows it and skips the choice of world.

## License

Apache 2.0
