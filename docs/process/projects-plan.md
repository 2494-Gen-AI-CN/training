# Projects section: spec sheets decoupled from the notes pipeline (D-0065, O-26)

Companion to `codify-plan.md` and `sql-in-page-plan.md`. Same shape: each stage's exit criteria are the next
stage's entry conditions, then the stage block below. S0 and S1 land together in one Workflow run (the trainer
opted in on 2026-10-21); S2 is a later content-only session. Written 2026-10-21, the day the room got its first
sprint, the Data analysis and visualisation mini-sprint (pairs, a public dataset of their choice, pandas and
Matplotlib, due Mon 2026-10-26).

## The decision in one paragraph

Learners get a public Projects section on the site: one spec sheet per official project (P0 weeks 1–5, P1
weeks 6–8, P2 weeks 9–11, already registered in `harness/curriculum.json` `projects`) and one per sprint, opened
from the index calendar. The trainer writes every spec by hand in the markdown drop zone `projects/`
(`official/P<n>-<slug>.md` with seven fixed sections and a `draft | published | closed` lifecycle;
`sprints/YYYY-MM-DD-<slug>.md`, loose, for 1–4 day sprints) and `harness/build_projects.py` renders them into
`docs/projects/`. A sprint is the week's hackathon: learners hand in under `<week-dir>/hackathon/` in their own
repo (`config.json` `learnerRepo.layout.hackathon`), a second sprint in the same week under
`<week-dir>/hackathon/<slug>/`, so `learnerRepo` does not change. The calendar shows a 🏁 pill on each sprint
due day and each official checkpoint day, plus one span bar per sprint. The section is deliberately decoupled
from the day pipeline: no prompt, critic, `plan_check.py` rule or `args_for.py` field reads `projects/`, day
pages never link project pages and project pages never link day or exit-criteria pages, so a spec written on
short notice can never stop a day from being authored, closed or released. Specs never name a trainee;
pairings stay in the private Trainer-Notes.

## Facts established on 2026-10-21 (do not re-derive)

| Fact | Source |
|---|---|
| `markdown` and PyYAML are not installed on `py` 3.15; `requirements-dev.txt` (`pytest>=8.0`, `nbformat>=5.10`) is the only dependency file | `py -c "import markdown"`; AGENTS.md Commands |
| `args_for.py`, `release_week.py` and `close_day.py` import `build_index`, so `build_projects` imports `markdown` lazily inside the page renderer and the harness stays stdlib everywhere else | the imports in those three scripts |
| `build_exit_pages.py` holds `load_config`, `esc`, `version()` / `js_version()` (read `?v=` from `docs/index.html`, fallback `"1"`) and a `_shell()` that hard-wires its nav hrefs relative to `exit-criteria/` and leaves `</body></html>` to the caller; `expected` / `check` / `build` are generic except the literal `docs/exit-criteria` | `harness/build_exit_pages.py` |
| `build_index.py --check` runs `build_exit_pages.check()`; the build, `release_week.py` and `close_day.py` rebuild the exit pages; `tests/test_exit_site.py` greps those hook lines as source text | `harness/build_index.py`, `tests/test_exit_site.py` |
| `drift_check.py` scans `MD_SCAN_DIRS = ("docs", "harness", "trainer")` plus root `*.md` for the drift marker words; its only generated-file check is `check_tracker`; untracked files are HARD in `check_git` | `harness/drift_check.py` |
| `docs/index.html` already emits `window.PROJECTS`, used only for the `.proj-band`; the tokens `--accent-soft`, `--accent-line` and `--accent-ink` exist, so the sprint bar needs page-local CSS and no `bump-css.sh` | `docs/index.html`, `docs/assets/css/style.css` |
| The topnav is hard-coded in `docs/index.html`, the exit-page shell and `harness/templates/day.exemplar.html`; `tests/test_pages.py` asserts exactly one "Demos" and one "Exit criteria" topnav per day page, so day pages stay untouched | `tests/test_pages.py` `_structure_checks` |
| `tests/test_exit_site._common_checks` is the page template to reuse: `theme.js` the only script, `?v=` matches the index, no ISO date in page text, relative links resolve, external links go to github.com only | `tests/test_exit_site.py` |
| `date_label(d, year=True)` prints "Tue Oct 13, 2026", the human date the no-ISO rule needs; `expand_week` gives each slot its `date`, `kind` and `day` | `harness/build_index.py` |
| The course runs 2026-10-13 to 2026-12-24; P0 is weeks 1–5, so its showcase checkpoint is W5D5, Fri 2026-11-13 | `harness/curriculum.json` |
| A week goes `live` at its Friday release (D-0052), so week 5 is live from Fri 2026-11-06 | `harness/release_week.py`, STATUS.md Log |
| W2D5's rubric "mini-project" is an exercise (`exerciseKind: rubric`), not a project; the hackathon mentions in `config.json`, `day-fanout.js`, AGENTS.md and the W1D5 trainer files stay as they are | `harness/curriculum.json`, grep for "hackathon" |
| The next decision id is D-0065 and the next open item O-26 | `decisions/`, STATUS.md |

## Recommended order and sizing

| Order | Stage | When | Size |
|---|---|---|---|
| 1 | S0 Shell lift, drop zone, generator, first sprint spec | landed with S1 on Wed 2026-10-21 | one Workflow run (parallel lanes in worktrees, opus/high), no index change yet |
| 2 | S1 Calendar marks, index wiring, drift hook, records | Wed 2026-10-21, same run as S0 | the run's integrate and review phases on main; D-0065 is recorded at integrate |
| 3 | S2 Publish P0 | when P0's requirements exist, before Fri 2026-11-06 | half a session, content only, no agents |

The first sprint's spec ships in S0, so it is on the site well before Mon 2026-10-26. Nothing here gates the day
pipeline: if S1 slips, only the calendar marks wait; `close_day.py` and `release_week.py` run as they do today.
S2 has a hard edge: the validator refuses a `draft` official spec whose checkpoint day is already `live`, so the
week-5 release on Fri 2026-11-06 fails `--check` until P0 is published or its checkpoint moved.

---

## Stage S0 — Shell lift, drop zone, generator (nothing on the index yet)

```
STAGE S0 — Lift the page shell, write the drop zone and the generator, ship the first sprint spec.
Read first: docs/process/projects-plan.md, harness/build_exit_pages.py, harness/build_index.py (date_label,
expand_week), tests/test_exit_site.py, tests/helpers.py (ParsedPage, FORBIDDEN_RE).
1. harness/site_pages.py (stdlib): SECTIONS = [("exit", "Exit criteria", "exit-criteria"), ("projects",
   "Projects", "projects")]; load_config, esc, version, js_version move here from build_exit_pages.py, which
   re-exports them; shell(title, body, cfg, v, *, active, extra_css, main_class, article_class) draws Home,
   Demos, Exercises, then one topnav per SECTIONS entry (href "index.html" on the active one,
   "../<dir>/index.html" on the other) and leaves </body></html> to the caller; check_dir(want, out_dir, root,
   rebuild_cmd) and build_dir(want, out_dir, root, quiet). build_exit_pages._shell becomes one call
   (active="exit"), its check() and build() delegate, its public API is unchanged. py harness/build_exit_pages.py
   regenerates the three pages; git diff --stat docs/exit-criteria shows one new Projects nav line per page.
2. projects/README.md: the process, the frontmatter grammar, both templates, "specs never name a trainee", and
   a pointer to the drift marker words in harness/drift_check.py that spec prose must avoid.
   Grammar: a leading --- ... --- fence, one "key: value" per line (key = a letter, then letters or digits);
   only "checkpoints:" with an empty value may be followed by "- w05d5 Showcase" lines (day id, then label).
   No quoting, no nesting. An unknown or duplicate key, a list line anywhere else or a missing fence is an
   error carrying file:line.
3. Official spec, projects/official/P<n>-<slug>.md (the filename prefix equals project): kind official,
   project (a key of curriculum.json projects), title, status draft|published|closed, handIn (non-empty, for
   example projects/P0/), checkpoints (one or more). Body: ## Goal, ## Scope, ## Requirements, ## Deliverable,
   ## Checkpoints, ## Rubric, ## Presentation, each exactly once and in that order (extra ## sections allowed
   after them); Requirements carries "- R-01 ..." bullets numbered from R-01 with no gap.
4. Sprint spec, projects/sprints/YYYY-MM-DD-<slug>.md (the date prefix equals assigned; the page slug is the
   stem without the date): kind sprint, title, assigned, due (ISO dates), mode pairs|solo|teams, handIn
   week-NN/hackathon/ or week-NN/hackathon/<slug>/, status open|closed, optional tools (comma list). Free body.
5. harness/build_projects.py (stdlib; `import markdown` lazily inside render_page only): parse_frontmatter,
   validate(root, cur) returning "projects/<rel>: <msg>" lines, load_specs(root, cur, strict) (strict raises
   SpecError; strict=False skips a broken file with a warning on stderr), calendar_marks(specs, cur),
   render_page, render_index, expected, check (validate + site_pages.check_dir), build, main (--check |
   --validate | build). Validation: unknown project id; unknown day id or a holiday slot; a section missing,
   duplicated or out of order; Requirements not numbered R-01..; a date outside the course; assigned or due
   not a teaching day; due before assigned; a slug used twice across folders; filename and frontmatter
   disagree; bad kind, status, mode or ISO date; unknown key; a draft official whose checkpoint day is
   already live (publish it or move the checkpoint).
   Rendering: the body splits on "## " into <section class="step" id="<section-slug>"> blocks with an <h2>,
   each through markdown.markdown(text, extensions=["tables", "fenced_code"]); the text before the first
   "## " is the lede. Dates only as date_label(d, year=True), never ISO in page text; a checkpoint reads
   "Week 5 · Day 5 — Fri Nov 13, 2026 — Showcase" and is never linked to the day page. visible = status is
   not draft: drafts get a page but no index card and no calendar mark (hidden like authored days, D-0052);
   closed cards get pj-closed. An empty index says "No projects published yet."
6. First sprint, projects/sprints/2026-10-21-data-analysis-mini-sprint.md: kind sprint, title "Data analysis
   and visualisation mini-sprint", assigned 2026-10-21, due 2026-10-26, mode pairs, handIn
   week-02/hackathon/, tools pandas, Matplotlib, status open. Body: the trainer's brief as given (pairs, a
   public dataset of their choice, analysed with pandas and charted with Matplotlib), with no placeholder
   text. Page slug data-analysis-mini-sprint.
7. projects/official/P0-ticket-desk.md (renamed P0-dataset-to-warehouse.md, D-0072): status draft, checkpoints "- w05d5 Showcase", all seven sections with
   real short text.
8. requirements-dev.txt gains markdown>=3.11; py -m pip install -r requirements-dev.txt;
   py harness/build_projects.py generates docs/projects/ (the index and two pages).
9. tests/test_projects.py: ParserTests (temp-dir fixtures over a copy of the real curriculum, one per
   validation message, strict=False skips and warns); SyncTests (check() == [], expected() matches
   docs/projects/*.html, markdown in requirements-dev.txt); PageTests (the test_exit_site common checks, one
   Projects topnav at index.html and one Exit criteria topnav at ../exit-criteria/index.html, cards for
   visible specs only, seven section.step ids on official pages, mode, hand-in and both human dates on sprint
   pages, no drift marker words, every page parses with ParsedPage so unclosed raw HTML in a spec fails);
   DecouplingTests in both directions (no article link from docs/projects/ to ../weeks/ or ../exit-criteria/,
   no spec mentions weeks/ or exit-criteria/; no "projects/" in docs/weeks/**, the day template, the
   workflows, the critics, plan_check.py or args_for.py; exit pages link projects/ once, in the topnav).
   tests/test_exit_site.py gains the Projects topnav assertion.
Exit: py -m pytest -q green; py harness/build_projects.py --check OK; the exit pages differ only by the nav
line.
```

## Stage S1 — Calendar marks, index wiring, drift hook, records

```
STAGE S1 — Show the specs on the index calendar, fail drift on a broken spec, write the records.
Lands in the same run as S0.
1. harness/build_index.py render(): late import of build_projects (circular, as for build_exit_pages);
   specs = load_specs(cur=cur, strict=False); marks = calendar_marks(specs, cur); emit window.SPRINTS right
   after window.PROJECTS (always, [] when there is none); a day entry gains "due" and "cp" lists only when
   non-empty. main(): --check also runs build_projects.check(); the build runs build_projects.build(quiet=True)
   before the tracker. A broken spec is skipped with a warning here and never stops close_day.py or
   release_week.py; the hard failure lives in --check, the tests and drift.
2. docs/index.html: a Projects topnav after Exit criteria; a "🏁 Projects" rail button; a legend entry
   "🏁 Sprint due / project checkpoint"; a 🏁 pill linking projects/<slug>.html per day.due (title
   "Sprint due: <title>") and per day.cp (title "Checkpoint: <label> — <title>"); after each week's five
   cells, one sprint-row per sprint overlapping the week, holding a sprint-bar that spans its days (columns
   clamped to 1..5, UTC date math like dowOf). Page-local CSS only (.sprint-row, .sprint-bar,
   .cal-cell .mk.flag), so no bump-css.sh. py harness/build_index.py regenerates the block; commit the
   generated pages with the index change (every index href must resolve).
3. tests/test_projects_calendar.py: render() carries window.SPRINTS; "due" on the entry whose date is the due
   date; "cp" on each checkpoint day; a draft fixture yields no mark; a broken fixture is skipped, not raised.
4. harness/drift_check.py: check_projects(root) returns [] when projects/ is absent, else validate() and
   check() as HARD lines ("run: python harness/build_projects.py"); it runs after check_curriculum, with a
   --no-projects flag and a docstring line; MD_SCAN_DIRS gains "projects" so the marker words are caught in
   spec prose. tests/test_drift.py: FLAGS and the cli call gain --no-projects; a temp root with a broken
   projects/sprints/x.md yields HARD projects. tests/test_decisions.py: CITATION_SCOPES gains ROOT/"projects".
5. Records: py decisions/new.py records D-0065 (the decision paragraph above; --affects lists every path this
   plan touches); this file; AGENTS.md gains a Rules bullet after Exit criteria and a Commands bullet after
   the index sync check; STATUS.md gains O-26, a Log line and a Phase step; py harness/build_tracker.py.
Exit: py -m pytest -q green; py harness/build_index.py --check in sync (index, exit pages, projects);
git add -A, then py harness/drift_check.py with 0 hard; headless-Chrome screenshots of index.html,
projects/index.html and projects/data-analysis-mini-sprint.html, light and --force-dark-mode, read back
(🏁 on Mon Oct 26, a bar from Wed to Fri of week 2 and on Mon of week 3, the legend, the topnav); D-0065 in
the commit subject. Push.
```

## Stage S2 — Publish P0 (content only)

```
STAGE S2 — Publish the P0 spec before week 5 goes live.
Entry: the trainer has P0's requirements; target before Fri 2026-11-06, the week-5 release, a week ahead of
the W5D5 showcase (Fri 2026-11-13).
1. projects/official/P0-ticket-desk.md (renamed P0-dataset-to-warehouse.md, D-0072): fill the seven sections from the trainer's requirements (R-01.. in
   Requirements, the rubric rows, the presentation format and time), then status: published.
2. py harness/build_projects.py --validate; py harness/build_projects.py; py harness/build_index.py: the P0
   card on docs/projects/index.html and a 🏁 on W5D5.
3. Decide whether day pages get a Projects topnav. v1 leaves them alone; adding it is a decision entry plus
   a change to harness/templates/day.exemplar.html, the live day pages and tests/test_pages.py.
Exit: suite green; py harness/build_index.py --check in sync; drift 0 hard; STATUS.md O-26 and Log; tracker
rebuilt. Push.
```

## Not in this plan

- Agent-authored specs: no workflow, prompt or critic writes or reads `projects/`; the trainer writes every
  spec by hand.
- Naming trainees: specs say "pairs" or "teams" and nothing more; pairings live in the private Trainer-Notes.
- Links between day pages and project pages in either direction, or from project pages to exit-criteria
  pages; the shared topnav is the only crossing (`tests/test_projects.py` DecouplingTests).
- Grading records: marks, feedback and who handed in what stay in the private Trainer-Notes.
- A Projects topnav on day pages in v1; S2 only decides whether one comes later.

## After every stage

- STATUS.md: O-26 row and a Log line in the same commit; `python harness/build_tracker.py`; finish with
  `python harness/log_run.py tests`.
- D-0065 in the commit subject.
- `git add -A` before `python harness/drift_check.py` (untracked files are HARD); `git status` clean after the
  push.
