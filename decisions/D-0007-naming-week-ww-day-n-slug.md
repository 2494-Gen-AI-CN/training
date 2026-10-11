# D-0007 — Directory naming is week-WW/day-N-slug everywhere; the short id (w01d1) is only for meta tags, localStorage keys and test keys

- Date: 2026-10-11
- Status: accepted
- Decision: Directory naming is week-WW/day-N-slug everywhere; the short id (w01d1) is only for meta tags, localStorage keys and test keys
- Why: One naming rule across demos/, exercises/, trainer/, docs/weeks/ and harness/research/ lets every path derive from curriculum.json.
- Affects: harness/curriculum.json slugs, harness/build_index.py day_paths, all per-day directories
- Supersedes: —
- Superseded-by: —

## Notes

Walkthrough section 1 (Dir naming). day N is the weekday slot (1=Mon .. 5=Fri).
