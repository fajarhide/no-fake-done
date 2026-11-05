---
name: no-template-ui
description: Use when building a new web page or giving one a look of its own, when a page reads as templated, generic or AI-made, or when writing a DESIGN.md.
---
# no-template-ui

Use this when building a new page, or when asked to make one look better and the project has no design system that already decides. 

Models reach for the category default: asked for a coffee site, they produce cream, terracotta and a serif. This pass makes each visual decision answer to something true about this subject.

## 1. Name the receipt

Decide what would prove this screen did its job. Judge the surface, not the company: a tool's landing page and its settings screen get different receipts.

| The screen has worked when | Call it | Spend the ambition on |
| --- | --- | --- |
| A stranger takes the main action within five seconds | Pitch | One idea at full scale, one dominant thing per screen |
| Someone finishes the next task without help | Desk | Density, scanability, familiar controls, every state exact |
| A reader finds the answer and leaves | Page | Structure, line length, knowing where they are |
| The visitor remembers the work, not the frame | Show | The work fills the screen and the interface steps back |

Write the receipt in one line before anything else, such as "a nurse covers tonight's gap in two taps". Step 7 checks the page against it.

For a Desk screen, skip steps 3 and 4 and use the work itself as the idea:

- The first line on the screen names what needs doing now, with the count and a button for the next action. "3 shifts have no vet. Fill the next one."
- Sample data puts the hard cases in the first view: gaps, conflicts, overdue items. A screen that opens on "all clear" shows nothing of the job.
- Every item states its consequence next to its action, such as "approving this leaves Monday with no nurse".
- A phone gets its own layout built around the next task, such as one day at a time, and never a squeezed table or one long list.
- Familiar controls and one typeface. Spend the character on the shape of the work.

## 2. Inventory the subject

Write 8 to 12 facts that belong to this subject and to no competitor, from the brief, the repo and the live product: its name and what it means, place, numbers, the constraint it lives with, materials, rituals and hours, the printed things of its world, what it outputs, how the person using it actually works.

Mark what really exists: photographs, screenshots, a logo. Plan only around those. Customers, quotes, logos and statistics that do not exist stay off the page, and sample details get listed for the owner to confirm.

## 3. List seven worlds

Name the mechanism in one sentence: what this does that makes it this product. Write down the page this category always ships and its predictable opposite. Both are out.

Then list seven things the audience already knows by heart, from the inventory and the world around it: artifacts, places, rituals, printed forms, instruments. For each, one line on how it could carry the mechanism and one on how it looks, its ground, type and main shape. A roastery could use a survey map of the farm, a roast log, a bag label. A changelog tool could use a carbon-copy form, a proof sheet, a stamped approval.

Cross out any that are decoration only, or that imply something untrue. At least three must remain, so add more if needed.

## 4. Roll, then commit

You will rank the safest one first, so do not rank them. Number the survivors and roll:

```sh
python -c "import random; print(random.randint(1, N))"
```

Build the world it lands on. Roll again only for a reason you can state: it would mislead, contradict a brand constraint, or cannot hold the real content.

Complete this sentence:

> On this page, **[the world]** becomes **[what the page does with it]**, so **[what the visitor understands at once]**.

Test it. Put the nearest competitor's name in it: if it still works, it is too general, so tie it to an inventory fact. Then ask what someone would remember a day after one look at the first screen. The answer should be that world, shown at full size as the page itself, never as a picture inside a standard hero. Carry its ground, type and shapes into every section, down to the footer.

If a safer choice tempts you, keep the world. Readability, contrast and the order path stay untouched.

## 5. Write DESIGN.md

Put it in the project root. An existing one decides, so skip steps 3 and 4 and follow it. Light or dark comes from where the person uses this.

```md
---
name: <product>
colors:
  ground: "#..."
  ink: "#..."
  accent: "#..."
typography:
  display: { fontFamily: <family>, fontSize: <size> }
  body: { fontFamily: <family>, fontSize: <size> }
rounded: { md: <size> }
spacing: { sm: <size>, md: <size>, lg: <size> }
---

## Overview
Mode. The world and the sentence from step 4. Density, motion and variance, each low, medium or high, with the reason.

## Colors and type
Where each came from in that world. A display face needs character of its own, so load one rather than a system font.

## Do not
Three to five looks this product must avoid, specific to it, with the reason.
```

If `npx` is available, validate it with `npx @google/design.md lint DESIGN.md`.

## 6. Build in this order

1. The words, complete: every section delivers its real content. List each section as a claim with its proof, and delete a section that has no claim. Write each piece to this shape:
   - **Headline:** what this is and who it is for, in the subject's own nouns. If a competitor's name fits in it, rewrite it.
   - **Button:** the verb and its object, such as "Swap Fri 6 Nov". The toast and the confirmation reuse that verb ("Swapped").
   - **Error:** what happened, what was kept, what to do next. "Lina's shift was locked after this page loaded. Your pick is kept. Choose another."
   - **Empty state:** why it is empty and the one action that fills it.
   - **Numbers, quotes and logos:** real ones, or none. Sample content is listed for the owner to confirm.
   - **Sentences:** one idea each, in the words the audience uses at work. Read every line aloud before shipping and rewrite any that sounds like an ad or an assistant: a contrast staged as "not X, but Y", three items where the content has two, a dash used for rhythm, a one-line closer that restates the section, praise words with no fact behind them (seamless, powerful, effortless, revolutionary), and a bold label in front of every line of body copy.
2. Tokens from DESIGN.md, then the first screen at phone and desktop width. It demonstrates the world and the mechanism, and its title says plainly what this is. For a Pitch screen, the headline, one sentence and the primary action fit in 1280 by 800 without scrolling. Theme `::selection`, `caret-color`, the scrollbar and `:focus-visible` from the palette, since browser defaults show through.
3. Each section, carrying the idea through pricing, FAQ and footer. Neighbours differ in layout.
4. Space left by removing ornament goes to scale, content or a real picture, never to another ornament.
5. Motion last, and only where it explains something. The page must work without it and stop under `prefers-reduced-motion`. No `transition: all`, no animating width, height, top or left, interface transitions under 300 ms, and nothing grows from `scale(0)`. Grep the CSS to check.

## 7. Prove it

```sh
python scripts/probe.py OUT_DIR URL --design DESIGN.md
```

Open every screenshot and judge the pictures, not your code:

- **The receipt from step 1:** walk it on the phone screenshot. If it fails, nothing below matters yet.
- **One second:** what did you see? "A website" means there is no focal point.
- **Five seconds:** what is this, who is it for, what do I do next?
- **Cover the name:** could a competitor use this page unchanged?
- **One day later:** what would you remember?
- **Follow the edges:** text left edges should be few and reused.

Fix the worst three things, then probe and look again, two rounds at most. Force the cases below, since a handsome page can still lose the order. Report the idea sentence, the numbers, what is sample content, and both screenshots. Whether it looks better is the owner's call.

## Force what a happy path never shows

On each primary action: double-click submit, bad input, reload after acting, an empty state, a 200 character string, Tab then Escape in any dialog. Say which you did not try.
