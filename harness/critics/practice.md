# Practice tasks — suitability bar and build PASS criteria

Practice tasks are added to a notes page AFTER the day's other content is authored (D-0047), in three steps: a suitability pass proposes tasks, the trainer approves or declines each one, a build writes the approved ones. `harness/practice/<week>/<day>.json` is the one source of a page's tasks; the page's `section.practice` is generated from it by `python harness/practice_tasks.py insert <week> <day>` and never edited by hand. Numbers live in `harness/metrics.json` `practice`.

A task is ungraded practice on one teaching step: the reader types a short solution in the page, runs it, and the page reports each check as passed or failed. It is answerable from the page alone.

## The runtime (binding for both parts)

Read `docs/assets/js/pyworker.js`; it is the whole contract.

- The code runs in Pyodide (CPython on WebAssembly) in the reader's browser. The version is in your prompt; it can trail the course Python.
- Standard library only. The worker loads no package: nothing from PyPI, and none of the standard-library modules Pyodide ships separately or leaves out (`sqlite3`, `ssl`, `lzma`, `tkinter`, `curses`, `venv` among them). No `pip`, no `pytest`, no `numpy`, `pandas` or `matplotlib`.
- No terminal. `input()` meets end-of-file. No subprocess, no threads or processes, no sockets, no network, no API key, no database server.
- Files exist only in an in-memory file system that lasts as long as the worker. A task that reads or writes files takes the path as an argument, and its checks create what they need under `tempfile.mkdtemp()` in their own setup lines.
- A check sees the namespace the reader's code left behind: names, functions, classes and what calling them returns or raises. It does not see what was printed.
- One file. A task cannot span modules.
- Output is cut at 200 lines; nothing should loop or wait. A model answer runs in well under a second.

When you are not sure a standard-library module is present in Pyodide, say so in the step's reason (suitability) or avoid it (build). The browser pass is the proof, and it runs after the build.

## Suitability (the proposal)

The assessor reads the authored page and decides, for EVERY teaching step (each `section.step` but the last), whether one task fits. The trainer reads the result and decides what gets built, so a reason must stand on its own.

A step fits when ALL of these hold:

1. What it teaches shows up as behaviour: a function's return value, an object's state, a name's value, an exception raised. A step that teaches a convention, a tool or a concept (PEP 8 layout, comments, pip, pylint, Git, Scrum) does not fit; say so in one sentence.
2. The task runs inside the runtime above with nothing faked. A step whose point is typed input, an installed package, several files, a network call or a server does not fit, even when a neighbouring idea would.
3. The page alone is enough to solve it: every name, method and idiom the model answer needs is taught on this page or listed as known in the audience line. Nothing the week plan's anti-spoiler rows defer from this day to a later one.
4. It is small: a model answer of at most `modelLinesMax` lines, one function, class or short script.
5. Each proposed check proves ONE behaviour, and a mistake the page names (its pitfalls, its "recognise on sight" lines, the brief's Pitfalls) fails it. A task whose only wrong answer is "did not write it" is not worth a slot.
6. It does not hand over the day's exercise: read `exercises/<rel>/README.md` and stay off its functions and its acceptance criteria. The same holds for the day's demo rungs: the task is a sibling in the same domain, never the rung itself.

Shape of a proposal: at most ONE task per teaching step, ids `t1`, `t2`, ... in step order, `title` the short name of the section it practises (as the exemplar does), `idea` in two or three sentences (what the reader writes, the signature, one example of input and result), `checks` a list of `checksPerTaskMin`..`checksPerTaskMax` plain sentences, each the behaviour one check will prove. Keep to the demo thread's domain where the page does (the exemplar's tasks are all about tickets). `q`, `starter` and `tests` stay empty and `approved` stays null: the trainer has not answered.

Verdict: `full` when every teaching step carries a task, `partial` when some do, `none` when none does. `none` and `partial` are honest outcomes, not failures. `summary` says in one sentence what the day lends itself to and what it does not.

Mechanical check: `python harness/practice_tasks.py validate <week> <day>` prints OK.

## Build (PASS criteria for the critic)

You are judging the built tasks of one day. You are NOT the author. Read the day's file under `harness/practice/`, the page, `trainer/<rel>/solutions/practice.py` and `practice_cases.py`, and the exemplar named in your prompt (the accepted shape, D-0046). Run the commands and quote their output; return `pass=false` with specific critiques if ANY item fails.

1. `python harness/practice_tasks.py verify <week> <day>` prints OK: the file is valid, the page's section is what the file renders, every starter fails, every model answer passes, every other right answer passes, every wrong answer is caught by the check named for it, and every check is failed by at least one wrong answer.
2. Exactly the approved tasks were built, with the ids, titles and steps of the proposal. A declined task has no `q`, `starter` or `tests`. Nothing else in the file moved: the steps, the reasons, the ideas and the trainer's answers are as they were.
3. `q` (the task text) names the function, class or names to write with the exact signature, says what comes back (returned, never "printed", unless the task is a script), and gives one example. It is solvable from the page alone and uses nothing a later day teaches. Markup is `<code>` only. No reference to the classroom or the trainer (`metrics.notes.deliveryPhrases`). It reads like a person wrote it (the wording rules of `harness/critics/notes.md` item 18).
4. `starter` is the signature with `...` for a body, or for a fix-it task the broken script as the reader meets it. At most `starterLinesMax` lines. It gives away no part of the answer.
5. `tests`: `checksPerTaskMin`..`checksPerTaskMax` top-level asserts, each with a message that names the behaviour in words a reader can act on without being told the answer ("leaves the caller's list as it was"). Prefer `left == right`, so the page can show expected and got. Lines that are not asserts are setup. `raises(ExcType, fn, *args)` is available for a check that expects an exception. Deterministic: no clock, no randomness, no reliance on set or dict order beyond what Python guarantees. No check depends on printed output.
6. The checks hold the task text and nothing more: every sentence of `q` that states a requirement has a check, and no check asks for something `q` does not say.
7. `practice.py` holds one model answer per built task, in page order, under a comment naming the task, in one file whose names do not collide. Each answer is at most `modelLinesMax` lines and uses only what the page teaches.
8. `practice_cases.py` has an entry per built task and no other: `accept` with at least `acceptMin` right answers written a different way from the model (a different idiom, not a renamed variable), `reject` with (code, label) pairs where each wrong answer is a mistake a learner of this page would plausibly make, most of them the pitfalls the page names. A `None` label marks code that stops with an error before the checks. No case, right or wrong, recurses without end: under CPython that is a RecursionError the check catches, but in the browser it overflows the stack and kills Pyodide, so the page restarts it and the case behaves differently from CPython (a `__repr__` that formats a bound method, as in `f"{self.load}"`, is the usual way in).
9. The page changed only inside `section.practice`: `git diff --stat -- <page>` and the diff itself show no other hunk, and `python harness/notes_check.py <page> --counts` passes as it did before.
10. Runtime: every import is standard library present in Pyodide, nothing reads `input()`, file tasks work on a path they are given, nothing sleeps or loops without end.

Not yours to judge: whether the day should have tasks at all (the trainer decided), and the browser pass (the session runs `harness/practice_browser.py` after the build; the stage is not done until it reports `ok: true`).

Return a one-sentence summary plus critiques as concrete fixes, each naming the task id.
