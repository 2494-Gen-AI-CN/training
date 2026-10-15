# {{id}} runbook — {{title}}

Week {{week}} · Day {{day}} · {{dateLabel}} · {{theme}}
Notes page: [{{rel}}.html]({{siteUrl}}weeks/{{rel}}.html) · Walkthroughs: [../demos/](../demos/) · Exercise: [exercises/{{rel}}]({{repoUrl}}/tree/main/exercises/{{rel}}) · Brief: [research/{{rel}}.md]({{repoUrl}}/blob/main/harness/research/{{rel}}.md) · Solutions / marking guide: [solutions/](solutions/)

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
| Exercise briefing | 10 | exercises/… |
| Exercise (trainees work) | 70 | exercises/… |
| Wrap-up / questions | 20 | — |
| **Total** | **360** | |

The walkthroughs (what the trainer performs, step by step, one per demo block) live in the week folder `../demos/` with the series README (D-0055). Their answer key is the demo repo at each block's commit on the week's prep branch; nothing about them is on the learner site.

## Objectives

By the end of today trainees can:
- ...

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

## Exercise briefing

- Task in one sentence: ...
- Acceptance: all tests in `exercises/{{rel}}/tests/` pass.
- Where trainees work and hand in: `{{rel}}/` in their own public `<FirstnameLastname>` repository (D-0051), committed and pushed to `main`.
- Where trainees get stuck: ...
- Rubric hints (trainer-only): ...
- Solution: trainer/{{rel}}/solutions/

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
