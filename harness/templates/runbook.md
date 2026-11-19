# {{id}} runbook — {{title}}

Week {{week}} · Day {{day}} · {{dateLabel}} · {{theme}}
Notes page: [{{rel}}.html]({{siteUrl}}weeks/{{rel}}.html) · Walkthroughs: [../demos/](../demos/) · Brief: [research/{{rel}}.md]({{repoUrl}}/blob/main/harness/research/{{rel}}.md) · Crib sheet: [crib-sheet.md](crib-sheet.md)

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

<!-- D-0096, PRESENTATION ORDER. After Objectives, the file has one `##` section per row of this table, in the
same order, so reading down the file is reading the day. A Break or Lunch row gets a short section of its own
(`## Break (10 min)`, `## Lunch (60 min)`: two or three lines on what to check or reset before the room leaves).
Only `## Common questions` and `## If running long / short` sit outside the timeline, last, as reference. The
sections below are in a typical order; move them to match the table. -->

**How this runbook is laid out.** Every section below is one row of the table above, in the same order, top to bottom. Read down the file and you are reading the day. Breaks and lunch have their own short sections so the place is never lost. Only the last two sections, Common questions and If running long / short, are reference and sit outside the timeline.

Each teaching block opens with notes, not a script: what the block covers, then each idea or term with what it is, how it works and the numbers that go with it. Teach from them in your own words. After the notes come the things you do with the room (On screen, Ask, Predict before running, Try changing), then `Trap`, `If asked` (the likely hard questions with their answers) and `Heads-up` (where the notes page differs from the demo). The longer background is in [crib-sheet.md](crib-sheet.md), in the same order as this file.

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

<!-- D-0096: plain instructions throughout the file. No `Say:` line and no quoted line for the trainer to recite;
the only quoted sentences are the Ask and Predict questions and the If asked questions. -->

- Python {{python}} present: `python --version`
- The demo repo clone on `main` in the state the previous block left (the week README's Run prerequisites say what else)
- Env keys (if any): copy `.env.example` → `.env`
- Trainees have pulled the repo; the trainer's scratch folder for today is empty and the terminal font is readable on the shared screen

## Recap / framing (15 min)

What this block covers, in order:
1. Where today sits in the week, and the two or three questions the day answers. Content, not a line to recite.

## Facilitation 1: <concept subtopic> (30 min)

<!-- D-0089, D-0096: this block is the presenter's LECTURE NOTES for the subtopic, not an activity plan and not a
script. A substitute trainer who has not opened the brief or the notes page can teach the subtopic from this
section alone. Every fact comes from the
brief or the notes page. Never name an activity without its content ("draw the timeline and fill it as you talk",
"discuss the history", "ask the first two questions below"): write the content itself. -->

**Goal:** what the room can do after this block (one sentence).
**Topics introduced, in order:** the 2–6 ideas or terms that are new to the room here, a few words each; one `### Topic` below per item.

### Topic 1: <idea or term> (8 min)

- **Notes:**
  - 4–8 sub-bullets, one per idea. Content notes, not lines to recite: each new **term** in bold and defined in one plain sentence; the problem it solves or why it exists; how it works; the concrete example, number or date from the brief.
  - Where the brief is thin, the notes are thin and say so, and point to the crib sheet section.
- **On screen:** the literal text, table rows or code typed or pasted on the shared screen, in order, written so it can be pasted (D-0090: delivery is remote; there is no board, so no drawing. The Setup check names the scratch text cell or file it goes in).
- **Ask:** "...?" → steer toward: ... → if the room says <the likely wrong answer>: ...

### Topic 2: <idea or term> (7 min)

(same three labels)

### Activity: <what the room does> (10 min)

At most one per block, placed after the topic it practises. Remote, and lecture is lecture (D-0090, D-0093): solo work, answers typed in the chat and sent together on the trainer's word; no pairs, no breakout room. The task as a plain instruction, the materials written out in full (every line or row), the answer key, and one debrief line per answer.

**If asked:**
- "<a likely hard question>" → the answer in one to three sentences, from the brief or the notes page. About three per block.

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

## Lunch (60 min)

- What to check or reset before the room leaves, and what is open on screen when it comes back.

## Break (10 min)

- Same, in a line or two. One section per Break row of the glance table, placed where the break falls.

<!-- D-0085, D-0096, demoFormat notebook days ONLY (instead of every "## Demo:" section; Facilitation blocks stay for the
subtopics the notebook does not cover). The glance table carries one "Notebook: <file> §1–§3 | 55 | demo repo notebooks/week-WW/<file>"
row per part of the pass; a break, lunch or Facilitation block between two parts is its own row. The "## Notebook: <file>"
section is a short overview, directly above part 1. Each row then gets a "## Notebook part k: §a–§b (M min)" section,
placed where it runs in the day, whose timed "###" sections sum to the row's minutes. While the notebook is not
written yet, time the sections the subtopics imply and say so in one line under the overview heading.
D-0097: the direct Colab link to the notebook (https://colab.research.google.com/github/<org>/<repo>/blob/main/notebooks/week-WW/NN_<weekday>_<slug>.ipynb,
org / repo / branch from config.json demoRepo) appears three times: on line 3 as " · Colab: [<file>.ipynb](<link>)" just before the
Crib sheet link, in the Setup check step where learners open the notebook ("Paste the direct link into the chat for anyone who
gets lost: <link>"), and in the Runtime field below.

## Notebook: NN_<weekday>_<slug>.ipynb

**Notebook:** `notebooks/week-WW/NN_<weekday>_<slug>.ipynb` on `main` of the demo repo · **Runtime:** Google Colab (File > Open notebook > GitHub, or the direct link https://colab.research.google.com/github/<org>/<repo>/blob/main/notebooks/week-WW/NN_<weekday>_<slug>.ipynb); run the setup cell first
**Time:** the total minutes, and the parts it is split into · **Stop point if long:** after section n; the rest is picked up ...

## Notebook part 1: §1–§3 (55 min)

### 1. <section heading as the notebook has it> (25 min)

**Covering:** the ideas and terms this section introduces, as a list.

- **<Term or idea>.** What it is in one plain sentence, how it works, and the values the cells print for it. One bullet per item of the Covering line. Content notes, not lines to recite.

**With the room:**

- The cells in run order, one bullet each where something needs pointing out.
- Predict before running: "...?" → answer: ...
- Try changing: `<parameter>` to ...; the room should see ...
- Trap: the mistake the room or the trainer is likely to make here, and how it shows (D-0092).
- If asked: "<a likely hard question>" → the answer in one to three sentences, from the brief or the notes page. Three to five of these; the full list is in `crib-sheet.md`.
- Heads-up: only where the notes page and the notebook differ (a variable name, a number, a print format): what differs and what to tell a learner who notices.

## Notebook part 2: §4–Recap (50 min)

(same structure; it sits after the break, lunch or Facilitation block that comes before it in the glance table)

### Recap and Quick check (10 min)

- Ask aloud: Quick check questions n, m.
-->

## Notes page handoff (10 min)

- Open docs/weeks/{{rel}}.html; show the table of contents and the "Check yourself" step at the end. The page is tonight's study material (30–45 minutes of reading, D-0040), not a recap of the day: name the 2–3 sections that go beyond what the demos built.
- Trainees read it after class and do the 6-question check (unlocks tomorrow's page).

## Sprint / project work (80 min)

- What to work on: the current sprint or official project spec on the site's Projects page, named in one sentence (D-0068).
- Where trainees hand in: for a sprint, `<week-dir>/hackathon/` (the week dir of `{{rel}}`); for an official project, the hand-in folder its spec names (D-0094), never the week's hackathon folder. Either way in their own public `<FirstnameLastname>` repository (D-0051), committed and pushed to `main`.
- Where trainees get stuck: ≥2 likely points, each with the nudge you give.
- How you circulate: ...

## Wrap-up / questions (20 min)

- What to ask or show to close the day, as plain instructions.

{{#if feedback}}
## Feedback form

- Last 10 minutes: open {{feedbackFormUrl}}; trainees submit before leaving.
{{/if}}

{{#if review}}
## Review agenda

- Cumulative quiz, mini-project walkthrough, Q&A ...
{{/if}}

<!-- Reference, outside the timeline (D-0096): these two sections are always last. -->

## Common questions

- Q: ... A: ...

## If running long / short

- Long: drop ... ; Short: add ...

<!-- "## Delivery record (<date>)" is appended by harness/close_day.py after the day (D-0050, D-0055); authors never write it. -->
