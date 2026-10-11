# D-0018 — Phase palette: Gen AI foundations colour changes from violet #7048e8 to amber #c98500; other four phase colours unchanged

- Date: 2026-10-11
- Status: accepted
- Decision: Phase palette: Gen AI foundations colour changes from violet #7048e8 to amber #c98500; other four phase colours unchanged
- Why: The dataviz palette validator failed the old set: data blue #1c7ed6 and Gen AI violet #7048e8 are adjacent in week order (weeks 4 to 5) and too close (normal-vision dE 14, deutan 5.7); violet also sat at 2.9:1 contrast on the dark surface. Amber passes every check in both modes with no warnings and is the smallest change.
- Affects: harness/curriculum.json phases.genai.c, docs/index.html generated block, every page that reads window.PHASES
- Supersedes: —
- Superseded-by: —

## Notes

Alternatives validated and rejected: magenta end (#ae3ec9), teal/plum (#0b8a7a, #a63fb8), reordering green/violet (dark-mode contrast warning stays), yellow #e8a100/#eda100 (too light on dark), green next to red/magenta (deutan dE 3 to 5). Phase order is py, data, genai, ml, llm; adjacent phases must stay distinct.
