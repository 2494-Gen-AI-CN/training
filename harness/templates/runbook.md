# {{id}} runbook — {{title}}

Week {{week}} · Day {{day}} · {{dateLabel}} · {{theme}}
Notes page: [{{rel}}.html]({{siteUrl}}weeks/{{rel}}.html) · Walkthroughs: [../demos/](../demos/) · Brief: [research/{{rel}}.md]({{repoUrl}}/blob/main/harness/research/{{rel}}.md)

## Day at a glance

| Block | Minutes | Artifact |
|---|---|---|
| Setup check | 10 | — |
| Recap / framing | 15 | notes page lede |
| Facilitation 1: <concept subtopic> | 30 | this runbook |
| Walkthrough 01-<slug>.md | 105 | ../demos/01-<slug>.md (break inside it after Step n) |
| Lunch | 60 | — |
| Walkthrough 02-<slug>.md | 75 | ../demos/02-<slug>.md |
| Break | 10 | — |
| Notes page handoff | 10 | docs/weeks/… |
| Sprint / project work | 80 | trainee's learner repo, `<week-dir>/hackathon/` |
| Wrap-up / questions | 20 | — |
| **Total** | **360** | |

The walkthroughs (what the trainer performs, step by step, one per demo block) live in the week folder `../demos/` with the series README (D-0055). Their answer key is the demo repo at each block's commit on the week's prep branch; nothing about them is on the learner site.

## Objectives

By the end of today trainees can:
- ...

<!-- D-0063, from exitCriteria.fromWeek (week 3): the section ENDS with this table, copied from the prompt's EXIT CRITERIA rows, Required rows first; omit it when the prompt carries no rows.
Exit criteria mapped to today

| ID | Tier | Criterion | Where |
|---|---|---|---|
| qc2.sql.R07 | Required | <criterion text as the source lists it> | 01-<slug> (or facilitation / notes-only) |
-->

## Setup check (10 min)

- Python {{python}} present: `python --version`
- The demo repo clone on `main` in the state the previous block left (the week README's Run prerequisites say what else)
- Env keys (if any): copy `.env.example` → `.env`
- Trainees have pulled the repo; the trainer's scratch folder for today is empty and the terminal font is readable from the back row

## Facilitation 1: <concept subtopic> (30 min)

**Goal:** what the room can do after this block (one sentence).
**Sequence:**
1. (5 min) Board plan: ...
2. (10 min) Ask the room: "...?" → steer toward: ...
3. (10 min) Pairs: ... ; debrief: ...
4. (5 min) What they write down: ...
**Ask the room:** ≥2 questions with the answer you are steering toward.
**Misconception to surface:** from the brief, and how you surface it.

## Demo: 01-<slug>.md

**Walkthrough:** ../demos/01-<slug>.md · **Time:** 105 min (AM block) · **Commit:** `<the block's commit message>` on the prep branch
**Room state before:** the commit of <previous block NN-<slug>> (or cold): what is on screen and in the repo when the block starts
**Stop point if long:** after Step n (the plan's Stop points row); the rest resumes at ...
**Checkpoint questions for the room:**
- ...
**Pitfall from the brief:** ...

## Demo: 02-<slug>.md

(same structure; the talk track lives in the walkthrough, not here)

## Notes page handoff

- Open docs/weeks/{{rel}}.html; show the table of contents and the "Check yourself" step at the end. The page is tonight's study material (30–45 minutes of reading, D-0040), not a recap of the day: name the 2–3 sections that go beyond what the demos built.
- Trainees read it after class and do the 6-question check (unlocks tomorrow's page).

## Sprint / project work

- What to work on: the current sprint or official project spec on the site's Projects page, named in one sentence (D-0068).
- Where trainees hand in: `<week-dir>/hackathon/` (the week dir of `{{rel}}`) in their own public `<FirstnameLastname>` repository (D-0051), committed and pushed to `main`.
- Where trainees get stuck: ≥2 likely points, each with the nudge you give.
- How you circulate: ...

## Common questions

- Q: ... A: ...

## If running long / short

- Long: drop ... ; Short: add ...

{{#if feedback}}
## Feedback form

- Last 10 minutes: open {{feedbackFormUrl}}; trainees submit before leaving.
{{/if}}

{{#if review}}
## Review agenda

- Cumulative quiz, mini-project walkthrough, Q&A ...
{{/if}}

<!-- "## Delivery record (<date>)" is appended by harness/close_day.py after the day (D-0050, D-0055); authors never write it. -->
