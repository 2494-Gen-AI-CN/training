---
name: weekly-blurb
description: Draft the weekly standup status reply for the 2494 Gen-AI Python training (trainer ratings by color band, status and topics, accomplishments, training goals, shout outs, open issues) from trainer/Trainer-Notes.xlsx. Use when the trainer types /weekly-blurb or asks for "the weekly blurb", "standup blurb" or "status update" for a week.
argument-hint: "[week number]"
---

# Weekly standup blurb

Answers the weekly request (Trainers Rating associate-wise; Current Status & Topics Covered; Key accomplishments; Training Goals 3 to 4; Shout Outs & why; Open Issues; validate attendance in RevPro).

## Privacy (hard rules)

`trainer/Trainer-Notes.xlsx` holds personal assessment data. Read it only for this blurb. The blurb goes to the TERMINAL only, inside one code block, for the trainer to paste into Teams. Never write it to a file, a repo, an artifact, a doc or any external service. Never let its contents touch the harness, the site or anything trainee facing.

## Steps

1. Week = the argument, else the current training week from `harness/curriculum.json` (the week whose days include today). Say which week you used.
2. Run the data script (needs `python`, the 3.12 that has openpyxl; `py` 3.15 does not):
   `python .claude/skills/weekly-blurb/blurb_data.py <week>` (from the repo root)
   It prints the rating line, the band lists, unrated trainees, notes, QC values and the week's days with `taught` dates. Use its counts and lists as given; do not recount by hand.
3. If any trainee is unrated, stop and say who before drafting (the trainer may still be filling the sheet).
4. Status and accomplishments: the days with `taught` dates are done, the rest are "planned" or "Thu-Fri". Add what the room actually did from `STATUS.md` Log entries for that week (blocks pulled forward, self-directed blocks) and the week plan's Weekly Epic (`harness/plans/week-WW.md`) for the project being built. No harness jargon (no block ids, shas, decision ids).
5. Training goals: 3 to 4 lines of what associates can build or implement after the week's topics, plain verbs.
6. Shout outs: from the Notes column and the top band; `Name, Name - why`.
7. Open issues: only things that affect associates (setup needed before next week, blockers); otherwise `None`. Never prep-repo or harness items.
8. Output in the format below, then one line reminding the trainer to validate attendance in RevPro (outside the code block).

## Format (plain text, no markdown inside the block)

```
Trainer Ratings: Technical: 2 - B, 12 - G

Week N (<phase>) underway: <topics done>; <in progress> (as of M/D/YY); <planned>.

<one line: what associates built / key accomplishments>.

Associates will be able to:
<goal>
<goal>
<goal>

Shoutouts:
<Name>, <Name> - <why>

Open Issues:
<issue, or None>

2 Blue below:
1. <Full Name>
2. <Full Name>

12 Green below:
1. <Full Name>
...
```

Band lists run highest band first, one blank line between lists, numbered, full names, no scores (drop the `[score]` the script prints). Dates M/D/YY. Add a `QC: ...` line after the technical line only when the week has numeric QC ratings, counted by the same bands.

## Scale

QC rating scale (`trainer/qc-rating-scale.png`): score out of 5 as a percent, 5 = 100%. Red under 60% (under 3), Yellow 60-69% (3 to under 3.5), Lime 70-79% (3.5 to under 4), Green 80-89% (4 to under 4.5), Blue 90% and up (4.5 and up). Same scale for QC and technical ratings; the workbook's conditional formatting uses it too.
