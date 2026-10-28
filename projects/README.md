# Projects: the spec drop zone (D-0065)

This folder holds the learner-facing spec sheets for the course projects and the short sprints. Each spec
is a markdown file written by hand. `harness/build_projects.py` turns them into the pages under
`docs/projects/` (one page per spec plus an index) and hands the due days and checkpoints to the course
calendar on the site home page. Never hand-edit the generated pages.

The projects are deliberately kept apart from the day pipeline: no week plan, prompt, critic or day page
reads these files, and a spec never links a day page or an exit-criteria page. A spec says what to build,
how to hand it in and when; it does not point at the notes.

## Two kinds of spec

| Kind | File | Lifecycle | Body |
| --- | --- | --- | --- |
| Official project (P0, P1, P2) | `official/P<n>-<slug>.md` | `draft`, then `published`, then `closed` | free-form (D-0073) |
| Sprint (one to four days) | `sprints/YYYY-MM-DD-<slug>.md` | `open`, then `closed` | free-form |

### Official projects

The projects come from `harness/curriculum.json` `projects` (P0 weeks 1 to 5, P1 weeks 6 to 8, P2 weeks 9
to 11). The process:

1. Start the spec as `status: draft`. A draft gets a page but no card on the projects index and no mark on
   the calendar, so it can be written in the open without being announced.
2. Write the body in the shape of a sprint page: a lead paragraph, then short `##` sections of one-line
   bullets (Dataset, Build, Rules, Presentation, Hand-in, What we look for is the shape P0 uses). If a spec
   has a `## Requirements` section, its bullets are numbered `R-01`, `R-02`, ... in order with no gaps, and a
   requirement keeps its number once the spec is published, so new ones go at the end.
3. Set `status: published` before the first checkpoint day goes live. A draft whose checkpoint day is
   already live is an error: publish the spec or move the checkpoint.
4. Set `status: closed` after the last checkpoint. A closed spec keeps its page and its card (shown faded).

The filename prefix must equal `project` (`P0-ticket-desk.md` for `project: P0`). The page is named after
the file: `P0-ticket-desk.html`.

No section is required (D-0073 withdrew the seven-section rule of D-0065). The checkpoint days from the
frontmatter render in the page's At a glance table, so the body never repeats them.

### Sprints

A sprint is the week's hackathon. It hands in under the hackathon folder of the learner repository
(`learnerRepo.layout.hackathon` in `harness/config.json`): `week-NN/hackathon/` for the week the sprint is
assigned in. A second sprint assigned in the same week hands in under `week-NN/hackathon/<slug>/`, so two
sprints never share a folder.

The filename date must equal `assigned`; the page is named after the rest of the filename
(`2026-10-21-data-analysis-mini-sprint.md` becomes `data-analysis-mini-sprint.html`). `assigned` and `due`
must both be teaching days of the course, and `due` cannot come before `assigned`. Set `status: closed`
once the sprint has been presented.

## Frontmatter grammar

Every spec opens with a frontmatter block between two `---` lines:

- one `key: value` per line; keys are letters and digits, starting with a letter;
- no quoting and no nesting: the value is the rest of the line, trimmed;
- only `checkpoints:` takes a list, written as `- wNNdN Label` lines under it (a day id from
  `harness/curriculum.json`, then a short label);
- an unknown key, a duplicate key, a list line anywhere else or a missing `---` is an error.

| Key | Official | Sprint | Values |
| --- | --- | --- | --- |
| `kind` | required | required | `official` or `sprint` |
| `title` | required | required | the page title |
| `status` | required | required | official: `draft`, `published`, `closed`; sprint: `open`, `closed` |
| `handIn` | required | required | official: a folder such as `projects/P0/`; sprint: `week-NN/hackathon/` or `week-NN/hackathon/<slug>/` |
| `project` | required | | a key of `curriculum.json` `projects` |
| `checkpoints` | required | | one or more `- wNNdN Label` lines, inside the project's weeks |
| `assigned` | | required | an ISO date, a teaching day |
| `due` | | required | an ISO date, a teaching day, not before `assigned` |
| `mode` | | required | `pairs`, `solo` or `teams` |
| `tools` | | optional | a comma-separated list |

Dates appear in the frontmatter only. In the body, write a date the way a reader says it ("Monday 26
October 2026"): the generated pages never show an ISO date.

## Writing rules

- Never name a trainee. Pairs and teams are assigned in class and recorded in the private Trainer-Notes.
- Do not link or name day pages or exit-criteria pages; the spec stands on its own.
- Do not leave marker words in the prose: `TBD`, `OWED`, `pending`, `blocked until`. Every spec ships
  complete; a section that is not ready means the spec stays a draft.
- Plain markdown only (paragraphs, lists, tables, fenced code). Raw HTML must close every tag it opens.

## Commands

```
py harness/build_projects.py           # rebuild docs/projects/ after any change here
py harness/build_projects.py --check   # specs valid and pages in sync (also run by the tests and drift_check)
```

`--validate` checks the grammar, sections and dates only, without comparing the pages. The renderer needs
the `markdown` package from `requirements-dev.txt`. A broken spec is skipped (with a warning) when the
calendar is rebuilt, and is a hard failure in `--check`, the tests and `harness/drift_check.py`.

## Template: official project

```
---
kind: official
project: P1
title: Project 1: <name>
status: draft
handIn: projects/P1/
checkpoints:
- w08d5 Showcase
---

One paragraph that says what the project is.

## Goal

What the learner can show at the end.

## Scope

What is in and what is out.

## Requirements

- R-01 The first thing the project must do.
- R-02 The second thing.

## Deliverable

What is handed in, and where.

## Checkpoints

What each checkpoint expects.

## Rubric

| Area | What a complete project shows |
| --- | --- |
| Working code | It runs from a fresh clone. |

## Presentation

How long, who speaks, what to show.
```

## Template: sprint

```
---
kind: sprint
title: <name of the sprint>
assigned: 2026-10-21
due: 2026-10-26
mode: pairs
handIn: week-02/hackathon/
status: open
tools: Python, pandas
---

One paragraph that says what the sprint asks for.

## Rules

- What is allowed and what is not.

## Presentation

- When, how long, what to show.

## Hand-in

What to push, and to which folder.
```
