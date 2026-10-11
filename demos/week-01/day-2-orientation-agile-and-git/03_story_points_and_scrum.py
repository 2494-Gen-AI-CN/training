"""03_story_points_and_scrum.py - planning poker with story points, then the
Scrum accountabilities, events and artifacts with their time-boxes.

PURPOSE
  Run a deterministic planning-poker round on two toy backlog items so the
  "why is yours a 3 and mine an 8?" conversation happens, then print the
  Scrum roles / events / artifacts and scale the Scrum Guide time-boxes
  (quoted for a one-month Sprint) down to our two-week Sprint.

RUN
  python 03_story_points_and_scrum.py

EXPECTED OUTPUT
  Story-point scale (relative effort, NOT hours): [1, 2, 3, 5, 8, 13]

  Planning poker
    add a hello script          votes {'Ana': 1, 'Ben': 2, 'Chen': 1}  -> agreed 2 (one step apart: take the higher)
    set up the shared team repo votes {'Ana': 3, 'Ben': 8, 'Chen': 5}  -> spread 3..8, DISCUSS: Ben explains
    set up the shared team repo re-vote {'Ana': 5, 'Ben': 5, 'Chen': 5} -> agreed 5
  Sprint commitment: 7 points (velocity is only comparable within THIS team)

  Scrum in one screen
    accountabilities: Product Owner, Scrum Master, Developers
    events:           Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective
    artifacts:        Product Backlog, Sprint Backlog, Increment

  Time-boxes (Scrum Guide caps for a 1-month Sprint, scaled to our 2-week Sprint)
    Sprint Planning          8.0 h  ->  4.0 h
    Daily Scrum             15 min  -> 15 min (fixed)
    Sprint Review            4.0 h  ->  2.0 h
    Sprint Retrospective     3.0 h  ->  1.5 h
"""

# --- STEP 1: the scale - Fibonacci-like, relative, unit-less ---
SCALE = [1, 2, 3, 5, 8, 13]
print("Story-point scale (relative effort, NOT hours):", SCALE)


def agree(votes):
    """Return (points, note). Votes one step apart converge; wider spread means talk."""
    lo, hi = min(votes.values()), max(votes.values())
    if lo == hi:
        return hi, "agreed"
    if SCALE.index(hi) - SCALE.index(lo) == 1:
        return hi, "one step apart: take the higher"
    outlier = max(votes, key=votes.get)
    return None, f"spread {lo}..{hi}, DISCUSS: {outlier} explains"


# --- STEP 2: planning poker - everyone votes at once, outliers explain, re-vote ---
print("\nPlanning poker")
rounds = [
    ("add a hello script", {"Ana": 1, "Ben": 2, "Chen": 1}, None),
    ("set up the shared team repo", {"Ana": 3, "Ben": 8, "Chen": 5}, {"Ana": 5, "Ben": 5, "Chen": 5}),
]
committed = 0
for item, votes, revote in rounds:
    points, note = agree(votes)
    if points is None:
        print(f"  {item:<27} votes {votes}  -> {note}")
        points, note = agree(revote)
        print(f"  {item:<27} re-vote {revote} -> {note} {points}")
    else:
        print(f"  {item:<27} votes {votes}  -> agreed {points} ({note})")
    committed += points
print(f"Sprint commitment: {committed} points (velocity is only comparable within THIS team)")

# --- STEP 3: Scrum's three accountabilities, five events, three artifacts ---
print("\nScrum in one screen")
print("  accountabilities: Product Owner, Scrum Master, Developers")
print("  events:           Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective")
print("  artifacts:        Product Backlog, Sprint Backlog, Increment")

# --- STEP 4: time-boxes - Scrum Guide caps are for a one-month Sprint; scale to ours ---
MONTH_WEEKS, OUR_SPRINT_WEEKS = 4, 2
caps_hours = {"Sprint Planning": 8, "Sprint Review": 4, "Sprint Retrospective": 3}
print(f"\nTime-boxes (Scrum Guide caps for a 1-month Sprint, scaled to our {OUR_SPRINT_WEEKS}-week Sprint)")
for event in ["Sprint Planning", "Daily Scrum", "Sprint Review", "Sprint Retrospective"]:
    if event == "Daily Scrum":
        print(f"  {event:<22} 15 min  -> 15 min (fixed)")
        continue
    cap = caps_hours[event]
    ours = cap * OUR_SPRINT_WEEKS / MONTH_WEEKS
    print(f"  {event:<22} {cap:>4.1f} h  -> {ours:>4.1f} h")
