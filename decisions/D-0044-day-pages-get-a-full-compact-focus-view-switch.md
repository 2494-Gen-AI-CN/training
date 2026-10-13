# D-0044 — Day pages get a Full / Compact / Focus view switch in the top bar, remembered in the browser (localStorage tc_view)

- Date: 2026-10-13
- Status: accepted
- Decision: Day pages get a Full / Compact / Focus view switch in the top bar, remembered in the browser (localStorage tc_view)
- Why: Trainer feedback 2026-10-13: the day pages are dense. The right rail takes at least 520px, so at 1280px the notes column is about 480px wide, and a learner had no way to quiet the page. Compact keeps the page menu (top-level entries only) and turns the rail into a slim button strip with the diagram opened on demand; Focus shows the notes alone, with the quiz and the gated Next link as one row under them, and switches off the progress bar and the glossary underlines. Both give the notes their full 860px measure.
- Affects: docs/assets/js/theme.js, glossary.js; docs/assets/css/style.css; docs/bump-css.sh; tests/test_view_modes.py; AGENTS.md; STATUS.md
- Supersedes: —
- Superseded-by: —

## Notes

No page, template or critic markup changes: theme.js sets html[data-view] before first paint and injects the switch into .topbar-right, the same way it injects the theme toggle, so every current and future day page gets it. A reader who has not picked a view gets Compact (trainer decision the same day, after seeing it); Full leaves the layout as it was, and any choice is remembered. All view rules sit inside @media screen, so print is unchanged. The diagram is hidden by clipping, never display:none, because diagram.js measures path lengths on every render. Alt+Shift+F cycles the views. Not covered: docs/index.html (no page menu there) and O-7 (phone-width overflow).
