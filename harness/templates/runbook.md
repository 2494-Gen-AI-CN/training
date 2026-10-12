# {{id}} runbook — {{title}}

Week {{week}} · Day {{day}} · {{dateLabel}} · {{theme}}
Notes page: [{{rel}}.html]({{siteUrl}}weeks/{{rel}}.html) · Demos: [demos/{{rel}}]({{repoUrl}}/tree/main/demos/{{rel}}) · Exercise: [exercises/{{rel}}]({{repoUrl}}/tree/main/exercises/{{rel}}) · Brief: [research/{{rel}}.md]({{repoUrl}}/blob/main/harness/research/{{rel}}.md) · Solutions / marking guide: [solutions/](solutions/)

## Day at a glance

| Block | Minutes | Artifact |
|---|---|---|
| Setup check | 10 | — |
| Recap / framing | 15 | notes page lede |
| Facilitation 1: <concept subtopic> | 30 | this runbook |
| Demo 1: 01_<slug>.md | 30 | demos/01_<slug>.md (script) |
| Break | 10 | — |
| Demo 2: 02_<slug>.md | 40 | demos/02_<slug>.md (script) |
| Lunch | 60 | — |
| Demo 3: 03_<slug>.md | 40 | demos/03_<slug>.md (script) |
| Notes page walkthrough + quiz | 25 | docs/weeks/… |
| Exercise briefing | 10 | exercises/… |
| Exercise (trainees work) | 70 | exercises/… |
| Wrap-up / questions | 20 | — |
| **Total** | **360** | |

Demo scripts (what the trainer types, step by step) and their answer keys live beside this file in `demos/` (D-0030). The answer keys are published to the public `demos/<week>/<day>/` only after the delivery-day close sets `taught`; until then trainees see "Published after class" on the notes page.

## Objectives

By the end of today trainees can:
- ...

## Setup check (10 min)

- Python {{python}} present: `python --version`
- Packages: `pip install -r demos/{{rel}}/requirements.txt` (if present)
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

## Demo 1: 01_<slug>.md

**Script:** demos/01_<slug>.md · **Answer key:** demos/key/01_<slug>.py · **Time:** 30 min
**Room state before:** (from the script's "Before the room arrives")
**Stop point if long:** after Step n; the rest moves to ...
**Checkpoint questions for the room:**
- ...
**Pitfall from the brief:** ...

## Demo 2: 02_<slug>.md

(same structure; the talk track lives in the script, not here)

## Notes page handoff

- Open docs/weeks/{{rel}}.html; scroll the diagram with the room; call out the 2–3 sections that deepen what the demo showed.
- Trainees do the 6-question check (unlocks tomorrow's page).

## Exercise briefing

- Task in one sentence: ...
- Acceptance: all tests in `exercises/{{rel}}/tests/` pass.
- Where trainees work and hand in: `{{rel}}/` in their own `<FirstnameLastname>` repository (D-0037), committed and pushed to `main`.
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
