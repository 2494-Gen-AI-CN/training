# Demo: {{Title}} (`{{thread-id}}` -> `{{NN}}-{{slug}}`)

> **Objective:** One paragraph: what the room can DO after this block, the shape of the code it leaves behind, and the end state in one sentence ("End-state: ...").
>
> **Time:** 90 min ({{AM|PM}} block)
> **Audience:** Who is in the room and what they hold: the previous block's end state by name, what they have and have not written yet.
> **Prerequisite reading:** notes page section(s) this block assumes, or "none" for the first block of the week.
> **Thread:** `{{thread-id}}` — commit `{{commit message}}` on top of `{{previous block NN-slug}}`

This **extends an existing thread** (or: is **first-contact, built from scratch**). One short paragraph on what is hand-typed and why the typing is the lesson. Nothing pre-provided unless the Stub manifest says so.

### Hand-typed during demo
- `ticket-desk/<file>.py` — what this block adds to it
- `ticket-desk/<new file>.py` — new file, what it holds

### Stub manifest
- None.

<!--
Header rules (checked by harness/demo_check.py):
- Title line: "# Demo: <title> (`<thread-id>` -> `NN-<slug>`)"; NN-<slug> is the file name without .md.
- Five blockquote fields, each on its own "> **Label:** value" line, in any order, above the first "## " heading:
  Objective, Time, Audience, Prerequisite reading, Thread. A field may continue on following "> " lines.
- Time reads "N min" first (anything after it, such as "(AM block)", is free text); N within
  metrics.demos.minutesPerBlockMin..Max and equal to the sum of the step minutes.
- Thread reads one of:
    `<thread-id>` — commit `<message>` on top of `<NN-slug of the previous block>`
    `<thread-id>` — commit `<message>`, starts cold
    standalone — starts cold
  The thread id, commit message and previous block come from the week plan's Threads table row for this block
  (harness/plans/week-WW.md). A block EXTENDS the previous block's commit on the prep branch of the demo repo
  (config.json demoRepo.prepBranch); it never re-types or re-scaffolds what an earlier block built.
- "### Hand-typed during demo" and "### Stub manifest" are optional but recommended; they sit above the first "## ".
- A "> **DELIVERY RECORD (YYYY-MM-DD)**" blockquote is appended by harness/close_day.py after the day is taught;
  the author never writes one.
-->

---

## Presenter cheat-sheet

| # | Step | File touched |
|---|------|--------------|
| 1 | Frame: why this block, on the whiteboard | Whiteboard |
| 2 | <what gets typed> | `ticket-desk/<file>.py` |
| 3 | <what gets typed> | `ticket-desk/<file>.py` |
| 4 | Run; commit `{{commit message}}` | Terminal |
| 5 | Wrap-up questions | Discussion |

<!--
Cheat-sheet rules: one row per "## Step" heading, numbered 1..n in the same order; the Step cell is a short label of
the step, the File cell names the file, "Terminal", "Whiteboard" or "Discussion".
-->

---

## Step 1 — Frame: <the idea in six words> (5 min, no code)

*"The sentence the trainer opens with, in quotes, said aloud."*

Whiteboard:

```text
<the picture the room sees before any code: a table, a before/after, an arrow diagram>
```

- One bullet per idea the picture carries.
- *"A spoken line that lands the idea."*

<!--
Body rules (checked by harness/demo_check.py unless marked "critic"):
- "## Step n — title (M min)" headings numbered 1..n in order; steps within metrics.demos.stepsPerBlockMin..Max;
  "(M min, no code)" marks a whiteboard or discussion step. Minutes sum to the header Time.
- Every step that has a ```python or ```bash fence states its working directory on a "cwd:" line; the first time a
  directory appears the line says where it came from ("created in Step 2", "the demo repo clone", ...).
- Fenced ```python / ```bash blocks are exactly what the trainer types, in order, no "..." elisions. Lines typed and
  then replaced inside the same block are shown as typed; the end state is the block's prep commit, not the script.
  Typed lines per block (non-blank python lines plus bash commands) fit metrics.demos.maxTypedLinesPerBlock.
- "### Talking points while typing" follows each typed block: one idea per bullet, said while the line is on screen;
  the why lives here, never in code comments. Bold the term being taught; italics for a line said verbatim.
- "> **Pre-empt — "<question the room asks>"** <answer>" after a talking point that provokes the question (critic:
  at least one per block, answering a real question, never a rhetorical one).
- "Check (expected output):" with a ```text fence after each run; a prose "Check:" when the state is visible in the
  editor rather than the terminal.
- Every token (keyword, method, flag, git subcommand) is introduced before its first use, counting the Prerequisite
  reading and every earlier block of the thread. The first block that uses a tool carries its install, version and
  config commands, proven by running them.
- Wording (D-0039): the trainer says the talking points aloud while typing, so write sentences a person can say without
  rephrasing: short, plain, one idea each. A humanizer pass runs after the author (prose only, guarded by
  harness/prose_guard.py); give it little to do.
- The last step of a thread block ends with the block's commit: a ```bash fence holding git add and
  git commit -m "<the Thread line's commit message>" (checked).
-->

---

## Step 2 — <what gets typed> (35 min)

cwd: `ticket-desk/` (the demo repo clone, on the branch the previous block left)

Create `ticket-desk/<file>.py`. Start with the shape, then the behaviour:

```python
# every line the trainer types, verbatim, in the order it is typed
```

### Talking points while typing

- **The term being taught** — what it is, in one sentence.
- *"The line said aloud that makes it land."*
- Why this and not the obvious alternative.

> **Pre-empt — "Why not just ...?"** The answer, two sentences, said before anyone asks.

Check (expected output):

```text
<what the terminal shows, exactly>
```

---

## Step 3 — <what gets typed> (35 min)

cwd: `ticket-desk/`

```python
```

### Talking points while typing

- ...

Check (expected output):

```text
```

---

## Step 4 — Run; commit (10 min)

cwd: `ticket-desk/`

Run the whole thing once more, then commit the block:

```bash
python ticket_desk.py
git add .
git commit -m "{{commit message}}"
```

### Talking points while running

- *"Second commit on the thread, still runs end to end. `{{previous block}}` -> `{{NN}}-{{slug}}`."*
- What the next block extends from here.

---

## Step 5 — Wrap-up questions (5 min, no code)

See "End-of-demo wrap-up" below; ask them with the screen off.

---

## Common pitfalls (call these out proactively)

1. **<Symptom the room sees, in their words>.** Cause: <one sentence>. Fix: <what to type or say>.
2. **<Symptom>.** Cause: ... Fix: ...

## What we did NOT cover (intentional)

- <topic the room may ask about>: deferred to <block or day>. <The reason, as one sentence>.

<!--
"What we did NOT cover" bullets read "- <topic>: <where it goes or why it is out>. <the reason, as one sentence>."
with no dash between topic and note (checked by harness/demo_check.py, D-0039).
-->

## End-of-demo wrap-up

Without looking at the screen:

1. <question answerable from the mental model, not the code>
2. ...
3. ...

If question 2 stumps them, restate: <the one-sentence model>. It is the hinge for <the next block>.

## Sequence pointer

Previous: **`{{previous block}}`** (<day, slot>). Next: **`{{next block}}`** (<day, slot>) — <one sentence on what it extends from this block's commit>. Never restart.
