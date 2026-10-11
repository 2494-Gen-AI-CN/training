"""03 - Scrum in one screen, then a planning-poker round.

PURPOSE
  List what the 2020 Scrum Guide actually defines (3 accountabilities, 5
  events, 3 artifacts) and its time-boxes, then layer story pointing on top:
  a Fibonacci-like scale, sizing by comparison rather than hours, and a
  planning-poker round where one item converges and one forces the
  "why is yours a 3 and mine an 8?" conversation before a re-vote.

EXPECTED OUTPUT (fully deterministic)
  STEP 1  three short lists
  STEP 2  five events with the Guide's one-month caps and our 2-week budget
  STEP 3  the scale 1 2 3 5 8 13 and the reference item
  STEP 4  item A: votes 1 2 2 1 -> adjacent, tie goes up: 2
          item B: votes 3 8 5 13 -> spread too wide, talk, re-vote 5 5 8 5
          -> majority says 5; points != hours
"""

# --- STEP 1: what Scrum defines (and only this) ---
print("STEP 1  Scrum defines:")
print("        accountabilities  Product Owner, Scrum Master, Developers")
print("        events            Sprint, Sprint Planning, Daily Scrum,")
print("                          Sprint Review, Sprint Retrospective")
print("        artifacts         Product Backlog, Sprint Backlog, Increment")
print("        (story points and hours appear nowhere in the Guide)")

# --- STEP 2: time-boxes - the Guide's caps for a one-month Sprint ---
print("\nSTEP 2  Time-boxes (Guide: 'shorter for shorter Sprints')")
print(f"        {'event':<22}{'one-month cap':<16}our two-week Sprint")
EVENTS = [("Sprint", "<= 1 month", "2 weeks, fixed"),
          ("Sprint Planning", "8 hours", "4 hours, Mon morning"),
          ("Daily Scrum", "15 minutes", "15 minutes, 9:15"),
          ("Sprint Review", "4 hours", "2 hours, second Fri"),
          ("Sprint Retrospective", "3 hours", "90 minutes, after Review")]
for event, cap, ours in EVENTS:
    print(f"        {event:<22}{cap:<16}{ours}")

# --- STEP 3: story points - relative effort, not time ---
SCALE = [1, 2, 3, 5, 8, 13]
print("\nSTEP 3  Scale:", *SCALE, "(gaps widen because big estimates are fuzzier)")
print("        Reference item: 'rename a variable across one file' = 1 point")
print("        Every other item is sized by comparing it with that one.")


def poker(item, votes):
    """One planning-poker round: converge if votes are adjacent on the scale."""
    print(f"\n        {item}")
    print(f"          votes {votes}", end="  ")
    lo, hi = SCALE.index(min(votes)), SCALE.index(max(votes))
    if hi - lo <= 1:
        agreed = max(set(votes), key=lambda v: (votes.count(v), v))  # majority, ties go up
        print(f"-> adjacent on the scale, majority says {agreed}")
        return agreed
    print(f"-> spread {min(votes)}..{max(votes)}: the {min(votes)} and the "
          f"{max(votes)} each explain, then everyone re-votes")
    return None


# --- STEP 4: planning poker on two toy backlog items ---
print("\nSTEP 4  Planning poker, four Developers")
poker("A: add a hello script to the repo", [1, 2, 2, 1])
if poker("B: set up the team's shared repo with branch protection", [3, 8, 5, 13]) is None:
    print("          the 13 feared GitHub permissions; the 3 had done it before")
    poker("B (re-vote)", [5, 5, 8, 5])
print("\n        5 points is NOT 5 hours. Velocity (points done per Sprint) only")
print("        means something inside this team, compared with its own past Sprints.")
