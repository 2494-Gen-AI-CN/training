# {{id}} runbook — {{title}}

Week {{week}} · Day {{day}} · {{theme}}
Notes page: docs/weeks/{{rel}}.html · Demos: demos/{{rel}}/ · Exercise: exercises/{{rel}}/

## Day at a glance

| Block | Minutes | Artifact |
|---|---|---|
| Setup check | 10 | — |
| Recap / framing | 15 | notes page lede |
| Demo 1: 01_<slug>.py | 40 | demos/… |
| Break | 10 | — |
| Demo 2: 02_<slug>.py | 40 | demos/… |
| Lunch | 60 | — |
| Demo 3: 03_<slug>.py | 40 | demos/… |
| Notes page walkthrough + quiz | 25 | docs/weeks/… |
| Exercise briefing | 10 | exercises/… |
| Exercise (trainees work) | 90 | exercises/… |
| Wrap-up / questions | 20 | — |
| **Total** | **360** | |

## Objectives

By the end of today trainees can:
- ...

## Setup check (10 min)

- Python {{python}} present: `python --version`
- Packages: `pip install -r demos/{{rel}}/requirements.txt` (if present)
- Env keys (if any): copy `.env.example` → `.env`
- Trainees have pulled the repo and can run `python demos/{{rel}}/01_*.py`

## Demo 1: 01_<slug>.py

**Goal:** ...
**Type live / paste:** STEP 1–2 live, STEP 3 paste.
**Talk track:**
1. ...
**Checkpoint questions for the room:**
- ...
**Expected output:** ...
**Pitfalls:** ...

## Demo 2: 02_<slug>.py

(same structure)

## Notes page handoff

- Open docs/weeks/{{rel}}.html; scroll the diagram with the room; call out the 2–3 sections that deepen what the demo showed.
- Trainees do the 6-question check (unlocks tomorrow's page).

## Exercise briefing

- Task in one sentence: ...
- Acceptance: all tests in `exercises/{{rel}}/tests/` pass.
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
