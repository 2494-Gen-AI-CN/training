# 2494 · Gen-AI Python Developer Training

Prep repo for an 11-week Python / Gen-AI developer training. Two things ship per training day:

1. **Live code-along demos** (`demos/`) the trainer types in front of the room.
2. **A GitHub Pages site** (`docs/`) with notes, a live diagram, a 6-question self-check and an exercise with pytest checks.

Trainer runbooks and exercise solutions live in a separate private repo cloned at `trainer/`.

## Layout

```
docs/                  GitHub Pages root (zero build): index.html, weeks/<week>/<day>.html, assets/
demos/<week>/<day>/    code-along scripts or notebooks + README (run order)
exercises/<week>/<day>/  README, starter/, tests/   (python -m pytest)
trainer/<week>/<day>/  runbook.md, solutions/       (private repo, gitignored)
harness/               curriculum.json (source of truth), metrics, config, workflow, templates, critics, research briefs
tests/                 contract tests: python -m unittest discover -s tests -v
Curricula/             official topic grid (input)
```

Day folders are named `week-01/day-1-orientation-agile-and-git` — see `harness/curriculum.json`.

## Producing a day

```
python harness/args_for.py 1 1 > /tmp/args.json      # week 1, day 1
# then in Claude Code:
Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: <contents of args.json> })
python -m unittest discover -s tests -v
```

The workflow runs research → demos → (notes ∥ runbook ∥ exercise) → wire → verify, each artifact gated by an independent critic with up to three repair passes. See `harness/README.md`.

## Site

Pages serves `docs/` from `main`. After editing CSS/JS run `docs/bump-css.sh --all` so browsers pick up the change. Preview locally with `cd docs && python -m http.server 8000`.
