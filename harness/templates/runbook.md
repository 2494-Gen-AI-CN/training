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
| Sprint / project work | 80 | trainee's learner repo: `<week-dir>/hackathon/` for a sprint, the spec's hand-in folder for an official project |
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

<!-- D-0089: this block is the presenter's LECTURE NOTES for the subtopic, not an activity plan. A trainer who has
not opened the brief or the notes page can teach the subtopic from this section alone. Every fact comes from the
brief or the notes page. Never name an activity without its content ("draw the timeline and fill it as you talk",
"discuss the history", "ask the first two questions below"): write the content itself. -->

**Goal:** what the room can do after this block (one sentence).
**Topics introduced, in order:** the 2–6 ideas or terms that are new to the room here, a few words each; one `### Topic` below per item.

### Topic 1: <idea or term> (8 min)

- **Teach:** 3–6 points, each a sentence or two the trainer can say as written. In this order: the term defined in one plain sentence; the problem it solves or why it exists; how it works; one concrete example, number or date from the brief.
- **On screen:** the literal text, table rows or code typed or pasted on the shared screen, in order, written so it can be pasted (D-0090: delivery is remote; there is no board, so no drawing. The Setup check names the scratch text cell or file it goes in).
- **Ask:** "...?" → steer toward: ... → if the room says <the likely wrong answer>: ...
- **Bridge:** one sentence that leads into the next topic.

### Topic 2: <idea or term> (7 min)

(same four labels)

### Activity: <what the room does> (10 min)

At most one per block, placed after the topic it practises. Remote, and lecture is lecture (D-0090, D-0093): solo work, answers typed in the chat and sent together on the trainer's word; no pairs, no breakout room. The task as the trainer says it, the materials written out in full (every line, card or row), the answer key, and one debrief line per answer.

**Misconception to surface:** from the brief, and how you surface it.
**What the room writes down:** the lines themselves, not a description of them.

Topic and Activity minutes sum to the heading's minutes.

## Demo: 01-<slug>.md

**Walkthrough:** ../demos/01-<slug>.md · **Time:** 105 min (AM block) · **Commit:** `<the block's commit message>` on the prep branch
**Room state before:** the commit of <previous block NN-<slug>> (or cold): what is on screen and in the repo when the block starts
**Stop point if long:** after Step n (the plan's Stop points row); the rest resumes at ...
**Checkpoint questions for the room:**
- ...
**Pitfall from the brief:** ...

## Demo: 02-<slug>.md

(same structure; the talk track lives in the walkthrough, not here)

<!-- D-0085, demoFormat notebook days ONLY (instead of every "## Demo:" section; Facilitation blocks stay for the
subtopics the notebook does not cover). The glance table carries "Notebook: <file> §1–§3 | 105 | demo repo notebooks/week-WW/<file>"
rows whose minutes sum to the timed sections below. While the notebook is not written yet, time the sections the
subtopics imply and say so in one line under the heading.

## Notebook: NN_<weekday>_<slug>.ipynb

**Notebook:** `notebooks/week-WW/NN_<weekday>_<slug>.ipynb` on `main` of the demo repo · **Runtime:** Google Colab (File > Open notebook > GitHub); run the setup cell first
**Stop point if long:** after section n; the rest is picked up ...

### 1. <section heading as the notebook has it> (25 min)

- Teach: the idea this section introduces, in 2–4 sentences (D-0089): the term defined plainly, why it works, what the room should be able to say after the cells.
- Say: 2–4 lines.
- Predict before running: "...?" → answer: ...
- Try changing: `<parameter>` to ...; the room should see ...
- Trap: the mistake the room or the trainer is likely to make here, and how it shows (D-0092).
- If asked: "<the likeliest hard question>" → the answer in one to three sentences, from the brief or the notes page. One or two of these; the full list is in `crib-sheet.md`.

### Recap and Quick check (10 min)

- Ask aloud: Quick check questions n, m.
-->

## Notes page handoff

- Open docs/weeks/{{rel}}.html; show the table of contents and the "Check yourself" step at the end. The page is tonight's study material (30–45 minutes of reading, D-0040), not a recap of the day: name the 2–3 sections that go beyond what the demos built.
- Trainees read it after class and do the 6-question check (unlocks tomorrow's page).

## Sprint / project work

- What to work on: the current sprint or official project spec on the site's Projects page, named in one sentence (D-0068).
- Where trainees hand in: for a sprint, `<week-dir>/hackathon/` (the week dir of `{{rel}}`); for an official project, the hand-in folder its spec names (D-0094), never the week's hackathon folder. Either way in their own public `<FirstnameLastname>` repository (D-0051), committed and pushed to `main`.
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
