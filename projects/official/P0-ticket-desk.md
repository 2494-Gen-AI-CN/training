---
kind: official
project: P0
title: Project 0: the ticket desk
status: draft
handIn: projects/P0/
checkpoints:
- w05d5 Showcase
---

Project 0 is the support-ticket desk you build up over the first five weeks: one small codebase that gains a piece with each new topic, from plain Python classes to files, tests, data analysis, a database and a language model.

## Goal

Build a working support-ticket desk for a small software team in your own learner repository, and show that you can carry one codebase from plain Python all the way to a feature that calls a language model, keeping it runnable and tested at every step.

## Scope

In scope: tickets with a title, priority, status and history; customers who file tickets and agents who triage them; a service-level target (SLA) in hours for each priority; and the storage, tests, statistics and charts the desk needs.

Out of scope: a web front end, user accounts and passwords, and deployment to a server. The desk runs from the command line or a notebook.

## Requirements

- R-01 Model a ticket as a Python class with a title, priority, status and a history of changes, and let an agent move a ticket from open to in progress to resolved with every change recorded in its history.
- R-02 Save the desk to a JSON file and load it back, handling a missing or malformed file with a clear message instead of a crash.
- R-03 Flag every ticket that has broken its SLA (open longer than the target hours for its priority), with pytest tests for the SLA rule, the status changes of R-01 and the file handling of R-02.
- R-04 Report resolution hours with NumPy (mean, median and worst case per priority), load the tickets into a pandas DataFrame that answers at least three questions about the desk, and save one Matplotlib chart as an image file.
- R-05 Keep tickets, customers and agents in SQL tables, and add one feature that sends a ticket to a language model (a triage suggestion, a summary or a draft reply), reading the API key from the environment and never committing it.

## Deliverable

A folder `projects/P0/` in your learner repository holding the code, the tests, the saved chart and a README that explains how to install, run and test the desk and which file covers each requirement.

## Checkpoints

The showcase is the one checkpoint: the desk is complete and you present it. Each topic adds the piece the next requirement needs, so keep the desk working as you go instead of building it all in the last week.

## Rubric

| Area | What a complete project shows |
| --- | --- |
| Working code | The desk runs from a fresh clone by following the README. |
| Requirements | R-01 to R-05 are each met and easy to find. |
| Tests | `pytest` passes and covers the SLA rule and the file errors. |
| Code quality | Small functions, clear names, no secrets in the repository. |
| Presentation | A clear walk-through, with questions answered from the code. |

## Presentation

About ten minutes each at the showcase: run the desk live, walk through the code of one requirement, show the chart and the language model feature, then take questions.
