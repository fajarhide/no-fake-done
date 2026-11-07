# The README examples

Each skill section in the root README opens with one before and after image from `assets/compare/`. This folder holds what went into them, so a reader can check each one. They are examples, one run or one demo each, not measured rounds. The measured rounds are in each skill's README.

| Image | Where it came from |
| --- | --- |
| `no-fake-done-swap.png`, `no-fake-done-locked.png` | The screenshots in `assets/no-fake-done/`, from the one brief built twice that `skills/no-fake-done/README.md` describes. |
| `no-broken-ui-double-pay.png` | `assets/no-broken-ui/checkout-double-*.png`: a test page with synthetic data, audited with the skill and then fixed by hand following its findings. |
| `no-template-ui-coffee.png` | `kopi-lereng/`: one agent built the brief below without a skill, another with `no-template-ui`. Both pages are here as the agents left them. The seat states and prices on the second page are sample data the agent made up and said so. |
| `no-janky-motion-menu.png` | `menu-motion/before.html` was written with the menu problems on purpose; `after.html` is the same page fixed by hand following `motion_probe.py`. The image lists what the probe reported on each, including the two findings it still reports after. |
| `no-leaky-app-harden.png` | The round 1 fixture from `evals/no-leaky-app/`, one agent without the skill and one with it, scored with `score_round1.py` on the running app. Without: 6 of 7 gaps closed, Permissions-Policy missing, and the public maps key the page needs deleted. With: 7 of 7, nothing broken. |

The brief for the coffee site: "Build a one-page website for Kopi Lereng, a small coffee roastery on the slopes of Mount Merapi. They sell roasted beans online, roast twice a week, and run a cupping session every Saturday morning for ten people. Plain HTML and CSS in index.html and style.css, no build step, no external images."

`compare/` renders the images: `compare.html` lays out two screenshots or two checklists side by side, `configs.json` holds each image's captions and the boxes it draws, in the screenshot's own pixels, and `render.mjs` screenshots them with Playwright. Copy the screenshots it names next to it and run `bun render.mjs` after changing `dir` to that folder.
