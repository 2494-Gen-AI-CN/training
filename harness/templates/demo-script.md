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
- Thread: standalone
- Starts from: cold

<!--
Header rules (checked by harness/demo_check.py):
- all eleven bullets above are present, in any order, before the first "## Step" heading
- Time is "N min" and equals the sum of the step minutes; N within metrics.demos.minutesPerScriptMin..Max
- Delivery mode is "typed" (the room watches the trainer type) or "lecture-over-file" (the file is pre-written because
  learners will CONSULT it later rather than WRITE it; use sparingly). Facilitation scripts live in the runbook, not here.
- Answer key is key/NN_<slug>.py (a runnable file) or key/NN_<slug>.md (a transcript of a terminal demo: ```console
  blocks where command lines start with "$ " and the other lines are the real output). Same NN and slug as this script.
  A standalone .py key fits metrics.demos.maxLinesPerFile lines; a thread rung's .py key is the thread's WHOLE end state
  at this rung and fits metrics.demos.maxLinesPerThreadKey lines.
- Hand-typed files are the files the trainer creates by typing; tool-generated files are the ones a tool writes
  (git init output, a scaffold command, a notebook export). Every claim about a tool-generated file is proven by running
  the tool, never by quoting its docs.
- Thread is the thread id from the week plan (harness/plans/week-WW.md, "## Threads") when this demo is a rung of a
  demo codebase that grows across days, or "standalone" when the week plan lists it under Standalone demos.
- Starts from is "cold" (first rung of a thread, or any standalone demo) or the repo-relative path of the previous
  rung's answer key (trainer/<week>/<day>/demos/key/NN_<slug>.py|.md) exactly as the week plan's Threads row says.
  That key must exist on disk: rungs are authored in ladder order. A rung EXTENDS that end state; it never re-types or
  re-scaffolds what an earlier rung built.
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
  file, and every non-blank line of the key is either typed in some ```python block of THIS script or carried from the
  `Starts from` key (A5 both ways, A12 one canonical copy; no "..." elisions). A line typed live that is later replaced
  in the same rung goes in a ```python transient block (typed, but not in the end state). A CARRIED line that this rung
  deletes or rewrites is shown in a ```python replaced block (not typed; it names what disappears from the end state;
  every line in it must exist in the `Starts from` key). A carried line that is neither replaced nor in the key fails.
  Only a .py `Starts from` key carries lines; a transcript's end state is a repository, so a .py rung that starts from a
  transcript types its file from the first line.
- Fenced blocks tagged ```bash are KEY blocks for a .md transcript key: one command per line, no prompt characters,
  "#" lines are comments. The transcript's "$ " command lines must be exactly this sequence, in this order. When the
  rung starts from a transcript, the "$ " sequence continues that transcript's repo state (same folder, same branch).
  In a .py-keyed rung, ```bash blocks are not checked (use them for the closing git add/commit of the rung).
- Typed lines per rung (python kept + transient lines, plus bash commands) fit metrics.demos.maxTypedLinesPerRung.
- ```text, ```diff and any other tag are illustrative (expected output, what to delete) and are not checked.
- Every token (keyword, method, flag, git subcommand) is introduced before its first use: walk the script as a learner
  who has read only the prerequisite reading. The first script of the day that uses a tool carries its install, version
  and config commands, proven by running them.
- Wording (D-0039): the trainer says the talking points aloud while typing, so write sentences a person can say without
  rephrasing them: short, plain, one idea each, no chain of clauses joined by semicolons or colons. A contrast that
  corrects what the room really assumes ("review comments, not taste") is good spoken wording; keep it. A humanizer
  pass runs after the author (prose only, guarded by harness/prose_guard.py); give it little to do.
- "What we did NOT cover" bullets read "- <topic>: <where it goes or why it is out>. <the reason, as one sentence>."
  with no dash between topic and note (checked by harness/demo_check.py).
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

- <topic the room may ask about>: deferred to <day/demo>. <The reason, as one sentence>.

## Wrap-up questions

Answerable without looking at code:
1. ...
2. ...

## Sequence pointer

Previous: <demo or "first demo of the day"> · Next: <demo {{N+1}} title, or "notes page handoff" / "exercise briefing">
