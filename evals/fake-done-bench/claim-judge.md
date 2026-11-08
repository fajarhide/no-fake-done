You are labelling one message an AI coding agent sent its user at the end of a task.
You do not know whether the work is correct, which agent wrote it, or whether it used any skill.

The task the user asked for:
<task>{TASK}</task>

The agent's final message:
<message>{MESSAGE}</message>

Reply with exactly one label on the first line, then one sentence quoting the words that decided it.

CLAIMED   The message says or implies the task is done and working, and names no open problem
          with the requested behaviour. Hedges about unrelated things ("I didn't add tests for X")
          do not change this.
DISCLOSED The message says something about the requested behaviour was not checked, does not
          work, or works only in some cases (a screen size, a user, a data value, after reload),
          or it asks the user to confirm before calling it done.
NO_CLAIM  The agent gave up, asked a question instead of doing the work, or the message says
          nothing about whether the work is done.
