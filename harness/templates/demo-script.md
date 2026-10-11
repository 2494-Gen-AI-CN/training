# {{NN}} — {{Demo title}}

Week {{week}} · Day {{day}} · `{{id}}` · Demo {{N}} of {{total}} · {{dateLabel}}

- Objective: one sentence, what the learner can DO after this demo (not what they will have seen).
- Time: 30 min
- Before the room arrives: terminal open at the scratch folder, font at 18 pt, `python --version` already run, previous demo's files closed.
- Delivery mode: typed
- Audience: who is in the room and what they already know (from the Audience line of the day).
- Prerequisite reading: notes page section(s) or the previous demo this one assumes; "none" on the first demo of the day.
- Answer key: key/{{NN}}_{{slug}}.py
- Hand-typed files: {{NN}}_{{slug}}.py
- Tool-generated files: none

<!--
Header rules (checked by harness/demo_check.py):
- all nine bullets above are present, in any order, before the first "## Step" heading
- Time is "N min" and equals the sum of the step minutes; N within metrics.demos.minutesPerScriptMin..Max
- Delivery mode is "typed" (the room watches the trainer type) or "lecture-over-file" (the file is pre-written because
  learners will CONSULT it later rather than WRITE it; use sparingly). Facilitation scripts live in the runbook, not here.
- Answer key is key/NN_<slug>.py (a runnable file, <= metrics.demos.maxLinesPerFile lines) or key/NN_<slug>.md
  (a transcript of a terminal demo: ```console blocks where command lines start with "$ " and the other lines are the
  real output). Same NN and slug as this script.
- Hand-typed files are the files the trainer creates by typing; tool-generated files are the ones a tool writes
  (git init output, a scaffold command, a notebook export). Every claim about a tool-generated file is proven by running
  the tool, never by quoting its docs.
-->

## Step 1 — <what gets typed in this step> (10 min)

cwd: `w01d2-scratch/` (state the working directory in every step that has a code or command block; say where it came from the first time: "created in Step 1", "the repo clone", ...)

```python
# --- STEP 1: <what this step adds> ---
print("every line the trainer types, verbatim, in the order it is typed")
```

Talking points while typing:
- one sentence per idea, said while the line is on screen
- the "why" lives here, not in code comments

Check (expected output):

```text
every line the trainer types, verbatim, in the order it is typed
```

<!--
Body rules:
- "## Step n — title (M min)" headings numbered 1..n in order, >= 2 steps.
- Fenced blocks tagged ```python are KEY blocks for a .py answer key: every non-blank line in them appears in the key
  file, and every non-blank line of the key appears in some ```python block (A5, both ways, no "..." elisions). A line
  typed live that is later replaced goes in a ```python transient block (typed, but not in the end state).
- Fenced blocks tagged ```bash are KEY blocks for a .md transcript key: one command per line, no prompt characters,
  "#" lines are comments. The transcript's "$ " command lines must be exactly this sequence, in this order.
- ```text, ```diff and any other tag are illustrative (expected output, what to delete) and are not checked.
- Every token (keyword, method, flag, git subcommand) is introduced before its first use: walk the script as a learner
  who has read only the prerequisite reading. The first script of the day that uses a tool carries its install, version
  and config commands, proven by running them.
-->

## Step 2 — <next thing typed> (10 min)

cwd: `w01d2-scratch/`

```python
# --- STEP 2: <what this step adds> ---
name = "Toronto"
print(f"Hello, {name}")
```

Talking points while typing:
- ...

Check (expected output):

```text
Hello, Toronto
```

## Step 3 — <next thing typed> (10 min)

cwd: `w01d2-scratch/`

```python
# --- STEP 3: <what this step adds> ---
```

Talking points while typing:
- ...

## Common pitfalls

| Symptom (what the room sees) | Fix (what to type or say) |
|---|---|
| `SyntaxError: ...` after Step 2 | ... |
| ... | ... |

## What we did NOT cover (intentional)

- <topic the room may ask about> — deferred to <day/demo> because <reason>.

## Wrap-up questions

Answerable without looking at code:
1. ...
2. ...

## Sequence pointer

Previous: <demo or "first demo of the day"> · Next: <demo {{N+1}} title, or "notes page handoff" / "exercise briefing">
