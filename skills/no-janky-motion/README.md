# no-janky-motion

The menu takes 600 ms to open, and people open it forty times a day. On a cheap phone it stutters. With reduced motion switched on, the spinner still spins, and the headline that fades in on load stays invisible when the script fails.

`no-janky-motion` measures the motion the browser runs and tells you which of it to cut.

Checks the motion a page runs in a browser. `scripts/motion_probe.py` loads the page four times (normal, reduced motion, JavaScript off, CPU slowed 4x), performs one action, and records every animation and transition that starts, with its selector, properties, duration, easing and first keyframe, plus frame gaps and layout shift. The skill then has the agent reverse motions halfway, trigger them fast and use the keyboard, and report at most ten findings, each with its receipt.

```sh
npx skills add fajarhide/no-fake-done --skill no-janky-motion -g
pip install playwright && playwright install chromium
```

```
Why does this menu feel slow?
Check the animations on http://localhost:3000 before we ship
Does this page respect reduced motion?
```

## The rules

Interface motion under 300 ms, nothing grows from `scale(0)`, no `ease-in` on entrances, only cheap properties, and reduced motion means less movement while keeping the meaning. Where two reasonable numbers exist, the skill takes the looser one and calls it a lead. Layout shift uses the Core Web Vitals line of 0.1. Taste rules, such as one reveal per page, are left out, because no script can check them and they would push every page towards one style.

## What has been tested

`scripts/test_motion_probe.py` builds a page with seven planted problems and one control that is fine:

| Planted | Caught |
| --- | --- |
| Width animated over 600 ms with `ease-in` | layout property, slow, ease-in |
| A menu popping from `scale(0)` | grows from nothing |
| An infinite spinner below the first screen | loop out of view |
| The same spinner with reduced motion on | ignores reduced motion |
| An intro that shows text only after a script runs | hidden without JavaScript |
| An opacity fade of 150 ms with `ease-out` | not flagged, as it should be |

The first version of the probe failed this test twice: it flagged `transition: all` on every element, because the browser default is `all 0s`, and it missed the spinner because it scrolled before looking. Both are fixed and the test passes.

This skill has not been measured against agents working without it. The fixture was written by the same author as the probe, so it shows that the probe sees what it claims to see, not that the skill finds more real problems.
