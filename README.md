# 2494 · Gen-AI Python Developer Training

Welcome. This repo holds everything you need for the 11-week program: the code we type together in class, the notes site, and the sprint and project specs.

**This repo:** https://github.com/2494-Gen-AI-CN/training
**Notes site:** https://2494-gen-ai-cn.github.io/training/
**Weekly feedback form (last day of each week):** [Microsoft Forms](https://forms.cloud.microsoft/pages/responsepage.aspx?id=iuJja_motUeqQJfiMSFRZMU3bOO2vNdAiSFsti9sgKVUQkhYWEhIRzJSWjNOVVM5REFOU0tWT0JXQyQlQCN0PWcu&route=shorturl)

## Dates

Training runs **Tue 2026-10-13 → Thu 2026-12-24**, Monday to Friday, Eastern time (America/Toronto). No class on:

| Date | Holiday |
|---|---|
| Mon 2026-10-12 | Thanksgiving (Canada) |
| Thu 2026-11-26 | Thanksgiving (US) |
| Fri 2026-11-27 | Day after Thanksgiving (US) |
| Fri 2026-12-25 | Christmas Day |

So week 1 is Tue–Fri, week 7 (Nov 23–27) is Mon–Wed, and week 11 (Dec 21–24) is Mon–Thu. The [notes site](https://2494-gen-ai-cn.github.io/training/) calendar shows the date on every day and highlights today.

## How each day works

1. **Code-along demos** — the trainer types the day's examples live, step by step; you type along. After the session the finished files (the answer key) are published to `demos/<week>/<day>/` with a README that lists them in order, so you can replay anything you missed. On a day the trainer improvised, the folder holds the files typed in class, as committed to the public demo repo `2494-Gen-AI-CN/demos`.
2. **Notes page** — on the site, one page per day: the ideas behind the demo, a live diagram, and a 6-question self-check. Finishing the check unlocks the next day's page.
3. **Practice and projects** — the notes pages carry practice tasks you run right in the page, and the [Projects page](https://2494-gen-ai-cn.github.io/training/projects/) holds the sprints and Project 0. The last part of most days is sprint or project work in your own learner repository.

## Setup (once)

You need Python 3.15 and Git.

```
git clone https://github.com/2494-Gen-AI-CN/training.git
cd training
py -3.15 -m venv .venv          # Windows: the py launcher picks 3.15 even when another Python is on PATH
# python3.15 -m venv .venv      # macOS / Linux
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements-dev.txt
```

Each morning: `git pull` to get the day's material.

Some weeks need extra packages or an API key. The demo folder for that day has a `requirements.txt` and/or `.env.example` with instructions.

## Replaying a demo (after class)

```
cd demos/week-01/day-3-python-basics
python 01_<name>.py
```

The README in each demo folder lists the files in run order and what each one shows. A `.md` file there is the transcript of a terminal demo: replay its `$` commands in a scratch folder. The folder appears after the day has been taught.

## Sprints and projects

Each spec on the [Projects page](https://2494-gen-ai-cn.github.io/training/projects/) says what to build, when it is due and how it is presented. Your work goes in your own public learner repository, `https://github.com/2494-Gen-AI-CN/<FirstnameLastname>`, in `<week-dir>/hackathon/` (for example `week-03/hackathon/`) unless the spec names another folder. Commit as you go and push to `main` there; nothing is pushed to this repo.

## Where things are

```
docs/        the notes site (served by GitHub Pages)
demos/       code-along files, one folder per day
projects/    sprint and project specs (shown on the site's Projects page)
Curricula/   the official topic grid for all 11 weeks
```

Folders are named `week-01/day-2-orientation-agile-and-git`, so the path tells you the week, the day and the topic.

## The 11 weeks

| Weeks | Theme |
|---|---|
| 1–2 | Agile, Git, Python fundamentals and advanced Python |
| 3–4 | SQL with MySQL; cloud, big data, warehousing, ETL |
| 5 | Gen AI introduction and prompt engineering |
| 6–7 | ML fundamentals, deep learning, TensorFlow |
| 8 | Feature engineering, model evaluation, vector databases |
| 9–10 | LangChain, LangGraph and agentic AI |
| 11 | AWS SageMaker and MLOps |

Projects: Project 0 (weeks 1–5), Project 1 (weeks 6–8), Project 2 (weeks 9–11).

## Stuck?

Ask in class. Trainees are welcome to self-organize on Discord for study groups and peer help. If something in the materials is wrong or confusing, say so in the weekly feedback form (last day of each week) — it gets read.

---

*Maintainers: the content pipeline lives in `harness/` (see `harness/README.md` and `AGENTS.md`). Contract tests: `python -m unittest discover -s tests -v`.*
