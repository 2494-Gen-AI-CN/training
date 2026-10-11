"""02_sdlc_waterfall_vs_agile.py - the SDLC phases, run once (waterfall) or
repeated in short cycles (Agile / Scrum Sprints).

PURPOSE
  Make the SDLC concrete as a list of phases, then simulate the same backlog
  delivered waterfall-style (one pass, software at the end) and Agile-style
  (two-week Sprints, a usable Increment every Sprint, a late change absorbed).

RUN
  python 02_sdlc_waterfall_vs_agile.py

EXPECTED OUTPUT
  SDLC phases: plan -> design -> build -> test -> deploy -> maintain

  WATERFALL - every phase once, in order, for the whole backlog
    week  1  plan      ['login', 'search', 'checkout']
    ... design week 3, build week 5, test week 8, deploy week 10 ...
    week 11  maintain  ['login', 'search', 'checkout']
    working software first seen by users: week 10 (deploy)
    'reports' arrived in week 5 -> parked until the next release

  AGILE - every phase inside every two-week Sprint
    Sprint 1 (weeks 1-2): plan design build test deploy -> Increment: ['login']
    Sprint 2 (weeks 3-4): ... -> Increment: ['login', 'search']
    Sprint 3 (weeks 5-6): ... -> Increment: ['login', 'search', 'checkout']
    Sprint 4 (weeks 7-8): ... -> Increment: ['login', 'search', 'checkout', 'reports']
    working software first seen by users: week 2
    'reports' arrived in week 5 -> picked up in Sprint 4

  Agile Manifesto values (left side is valued MORE):
    ...four lines...
"""

# --- STEP 1: the SDLC is a sequence of phases every piece of software passes through ---
PHASES = ["plan", "design", "build", "test", "deploy", "maintain"]
backlog = ["login", "search", "checkout"]
late_change = ("reports", 5)          # a new requirement arrives in week 5
print("SDLC phases:", " -> ".join(PHASES))

# --- STEP 2: waterfall - each phase finishes and is signed off before the next begins ---
WEEKS_PER_PHASE = {"plan": 2, "design": 2, "build": 3, "test": 2, "deploy": 1, "maintain": 1}
print("\nWATERFALL - every phase once, in order, for the whole backlog")
week = 1
first_release = None
for phase in PHASES:
    print(f"  week {week:>2}  {phase:<9} {backlog}")
    if phase == "deploy":
        first_release = week
    week += WEEKS_PER_PHASE[phase]
print(f"  working software first seen by users: week {first_release} (deploy)")
print(f"  '{late_change[0]}' arrived in week {late_change[1]} -> parked until the next release")

# --- STEP 3: Agile - all phases repeat inside every Sprint and each Sprint ships an Increment ---
SPRINT_WEEKS = 2
print("\nAGILE - every phase inside every two-week Sprint")
todo = list(backlog)
increment = []
sprint = 1
while todo:
    start, end = (sprint - 1) * SPRINT_WEEKS + 1, sprint * SPRINT_WEEKS
    if start <= late_change[1] <= end:          # requirement changed mid-way: welcome it
        todo.append(late_change[0])
    increment.append(todo.pop(0))
    ran = " ".join(p for p in PHASES if p != "maintain")
    print(f"  Sprint {sprint} (weeks {start}-{end}): {ran} -> Increment: {increment}")
    sprint += 1
print(f"  working software first seen by users: week {SPRINT_WEEKS}")
print(f"  '{late_change[0]}' arrived in week {late_change[1]} -> picked up in Sprint {sprint - 1}")

# --- STEP 4: why - the four values of the Agile Manifesto (2001) ---
values = [
    ("Individuals and interactions", "processes and tools"),
    ("Working software", "comprehensive documentation"),
    ("Customer collaboration", "contract negotiation"),
    ("Responding to change", "following a plan"),
]
print("\nAgile Manifesto values (left side is valued MORE):")
for more, less in values:
    print(f"  {more:<30} over  {less}")
