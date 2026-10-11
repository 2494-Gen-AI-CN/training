"""02 - SDLC: the same project delivered waterfall, then Agile.

PURPOSE
  Name the six SDLC phases every piece of software passes through, then
  schedule one small backlog two ways: waterfall (each phase signed off before
  the next, software at the very end) and Agile (two-week Sprints that each run
  every phase and ship an Increment). A requirement change arrives in week 6
  and the two models react differently. Ends with the four Manifesto values.

EXPECTED OUTPUT (fully deterministic)
  STEP 1  six numbered phases
  STEP 2  a 10-week waterfall timeline; change in week 6 -> "change request,
          queued until after release"; first working software: week 10
  STEP 3  five Sprints; change in week 6 -> "goes into Sprint 4's backlog";
          first working software: week 2
  STEP 4  the four values, left side over right side
"""

# --- STEP 1: the SDLC phases (every methodology has them) ---
PHASES = ["requirements / planning", "design", "implementation",
          "testing", "deployment", "maintenance"]
print("STEP 1  SDLC phases:")
for n, phase in enumerate(PHASES, 1):
    print(f"        {n}. {phase}")

CHANGE_WEEK = 6
CHANGE = "customer now wants login via GitHub, not email"

# --- STEP 2: waterfall - one pass, phases in order, software at the end ---
print("\nSTEP 2  Waterfall: 10 weeks, each phase signed off before the next")
WATERFALL = [("requirements", 2), ("design", 2), ("implementation", 3),
             ("testing", 2), ("deployment", 1)]
week = 1
for phase, length in WATERFALL:
    span = f"weeks {week}-{week + length - 1}" if length > 1 else f"week {week}"
    print(f"        {span:<12} {phase}")
    if week <= CHANGE_WEEK < week + length:
        print(f"        week {CHANGE_WEEK}       !! {CHANGE}")
        print("                     -> requirements were frozen in week 2:")
        print("                        change request, queued until after release")
    week += length
print(f"        first working software the customer can touch: week {week - 1}")

# --- STEP 3: Agile - short cycles, every phase inside every Sprint ---
print("\nSTEP 3  Agile: five two-week Sprints, an Increment at the end of each")
BACKLOG = ["hello script", "login via email", "profile page",
           "password reset", "admin dashboard"]
for sprint, item in enumerate(BACKLOG, 1):
    start = (sprint - 1) * 2 + 1
    print(f"        Sprint {sprint}  weeks {start}-{start + 1}  all six phases -> "
          f"Increment: {item}")
    if start <= CHANGE_WEEK <= start + 1:
        print(f"        week {CHANGE_WEEK}       !! {CHANGE}")
        print(f"                     -> welcome it: goes into Sprint {sprint + 1}'s"
              " backlog, ahead of 'password reset'")
print("        first working software the customer can touch: week 2")

# --- STEP 4: the Agile Manifesto values (2001) ---
print("\nSTEP 4  We value the left MORE, while the right still matters:")
VALUES = [("individuals and interactions", "processes and tools"),
          ("working software", "comprehensive documentation"),
          ("customer collaboration", "contract negotiation"),
          ("responding to change", "following a plan")]
for left, right in VALUES:
    print(f"        {left:<30} over  {right}")
