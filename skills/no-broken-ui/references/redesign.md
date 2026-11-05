# Redesign pass

Run this only after the audit report is finished, so it never competes with finding defects. Work from the report and the flow you walked.

Fixing every finding can still leave the wrong design. Ask:

- **Should this step exist?** Could a default, an inference or something already known remove the field, the screen or the decision?
- **Where is the anxious moment?** Paying, deleting, publishing. What would make it calm?
- **What does the person know right now that the screen ignores,** and what does it ask that they cannot know yet?
- **What is the job behind the job?** Trace what they were trying to get done when they came here, and the shortest honest path to that.
- **What would you take away?** Teams rarely propose a removal, and it is usually worth more than an addition.

Write up to three moves. A move changes what the flow is, not how well it works. Test each one: imagine every finding already fixed. If the move would no longer change anything, it is a fix, so cut it. One fitting any product gets cut too.

Two examples of the difference, from products unlike most you will see. Use them to calibrate and do not reuse their ideas:

| A fix, cut it | A move |
| --- | --- |
| Show validation errors on the booking form | A returning patient books by replying to a text, and the form is only for first visits |
| Make the report filter persist on reload | Nobody comes to filter: send the three rows that changed, and the page becomes the detail view |

Format:

```
## Bigger moves
1. Today <X>, instead <Y>. Because: <what you observed>. Costs: <effort, and what it could break>.
```

Say why the product's people would want it, and mark each move as a proposal to test, since nothing here was measured. Zero moves is a fine answer when the design is sound.
