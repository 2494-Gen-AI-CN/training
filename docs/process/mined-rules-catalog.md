# Catalog: reusable process rules mined from the TRNG-2442 (.NET Test Automation) prep repo

Immutable dated record (mined 2026-10-11, D-0028). Corrections go in a new dated file, not here.
Nothing in this catalog is codified in this repo yet; see STATUS.md O-10 for what to codify first.

Source root: `C:\Users\JonathanDeLaCruz\Documents\Revature\TRNG-2442-NET-Test-Automation\Prep\`
Files mined: CLAUDE.md, RULES.md (R-001..R-027), README.md, NET-Test-Auto-Delivery-Model.md (DM),
content-agents/{weekly-playbook,pedagogy-reviewer,engineering-reviewer,review-guide-agent}.md,
tools/drift-check.ps1, weeklytechrepo/ (structure + series README + walkthrough header), qc-criteria/,
docs/history/* (audit prompts, cohort decisions, compression plan), docs/status/* (process audits,
demo audit, note-depth audit, drift audit, CMA logs, producer-consumer analysis), STATE.md (head + headings).

Tags: reuse = lift as-is; adapt = lift with changes; avoid = documented failure, do the opposite; have = 2494 harness already has an equivalent.

Old-repo vocabulary: thread = one demo repo growing over days; rung = one `NN-topic` commit; ladder = the chain;
series README = index of a week's demo scripts; Log = weekly plan/verify file; OVERRIDE = logged one-off rule break;
QC rubric = assessment with Must / Should / Nice tiers.

---

## A. Demo / code-along authoring (the part that answers "what is a demo for")

| # | Rule | Source | Tag | 2494 relevance |
|---|---|---|---|---|
| A1 | "Demos are live-coded, not demoed." The deliverable is the SCRIPT the trainer types in front of the room; the committed code is the end-state answer key, "never a substitute for performing it". | RULES R-004 L58-61 | reuse | Inverts current contract: today the .py file is the deliverable and the critic runs it. Script-first would make 02/03 (print slideware) impossible and 04/05 (subprocess runners) unnecessary. |
| A2 | Script contents: timed steps, "talking points while typing", no-code framing beat, pitfalls (symptom + fix), "What we did NOT cover (intentional)", wrap-up questions answerable without code, pointer to next demo. | R-004 L58-60; playbook L110-117 | reuse | Our runbook has most of this per demo; the demo README has none. Merge: runbook demo sections ARE the script. |
| A3 | CONSULT-vs-WRITE test: lecture over a pre-written file only for material learners will look up later; "if the objective is fluency, the typing IS the lesson". | R-004(f) L69-73 | reuse | Single best heuristic for deciding script vs reference artefact per subtopic. Git commands = WRITE. Scrum events list = CONSULT. |
| A4 | Lecture-mode file allowed only if: mode declared in header and per step; full text in script with placement; listed as seed in series README; runs clean at every rung; product code still live-coded. | R-004(a-e) L62-69 | adapt | Governs Python reference/cheat-sheet files. |
| A5 | Script equals commit in BOTH directions: rebuild from script, diff against the rung. Every added line incl. comments appears verbatim in the script with placement; no "answer key" elisions, no `{ ... }` stubs; edits shown as fenced changed lines at the point of edit. | R-005 L85-94 | reuse | Mechanical check a critic can run. Replaces "run the script and compare to docstring". |
| A6 | Exemptions declared in script: tool-generated files (show generating command), seed files, lines typed-then-replaced on screen. | R-005 L95-99 | adapt | e.g. `uv.lock`, generated stubs. |
| A7 | One repo per thread; one commit per topic (`NN-topic` = commit message); extend, never re-scaffold; runnable at EVERY commit; if prior state missing, request it. | R-005 L81-84 | reuse | Maps to a code-along repo that grows Wed-Fri (Python) and later weeks. |
| A8 | Boilerplate ships as seed files on `main`; `*-start` branches retired. Load-bearing lessons always typed live: "bug-then-fix moments, assertion bodies, ... anything where the typing is the point". Day-1/first-contact demos fully from scratch. | R-006 L106-109 | reuse | |
| A9 | Tool installs the room lacks are numbered LIVE steps with idempotency note + verify line; never "install before arrival" except SDK/standing infra. | R-006 L113-115; CONTEXT-BRIEF L197-198 | adapt | pip/uv/venv/API keys. Contradicts our runbook "Setup check" that assumes pre-installed. |
| A10 | One demo domain per thread (Library); learners mirror in THEIR OWN domain. | R-007 L117-118; CONTEXT-BRIEF L123-124 | adapt | Pick a Gen-AI demo domain; exercises domain-neutral. |
| A11 | No teaching future-day concepts in depth; deferrals listed under "What we did NOT cover". | R-008 L121-123 | have | dayHeader already says "nothing from later days"; add the explicit deferral list. |
| A12 | Exactly one canonical copy of each thread's code, named in STATE; classroom copies are derived and reconciled at the gate. | R-018 L128-131 | reuse | Relevant if trainer types live into a classroom folder and publishes after. |
| A13 | Authoring unit = thread-week BATCH, never one-off scripts. Order: series README skeleton first (full ladder, dependency graph, per-demo minute budgets, stop points), then scripts+commits in ladder order. Batch incl. review PASS done BEFORE the week's first delivery day. | R-020 L133-141; playbook L80-103 | reuse | Direct answer to "how do we plan the week so it flows": week-level README before any day is authored. Our pipeline authors days in isolation (D-0024 week note was a patch). |
| A14 | Dual-lens review of the WHOLE series; final rung must realize the Weekly Epic; max 2 fix passes then escalate; AUTHORED only on dual PASS. | R-020 L141-146 | reuse | We have per-artifact critics with 3 passes; no series-level review, no epic. |
| A15 | Once taught, a commit is FROZEN; defects fixed forward with a maintenance commit + Log line; delivered defects corrected live bug-then-fix, never silently patched. | R-020 L147-150; demo audit L221-224 | reuse | |
| A16 | Series README carries "Real-world framing" + deliberate-deviation ledger (Deviation / Workplace reality / Pedagogical reason). Unledgered "nobody builds this" shape fails review. | R-021 L154-161 | reuse | Very relevant to Gen-AI demos (toy RAG, fake vector DB, bare repo standing in for GitHub). |
| A17 | Pre-flight R-026: (1) every URL/port matches the binding; (2) every syntax token introduced before first use, checked by walking as a learner; (3) assume NO tooling installed, first script carries install+version+config, proven by running; (4) every session starts COLD: startup command for every service, stated cwd per command; (5) tool-generated claims proven by running the tool at the captured version, never by reading docs. | R-026 L180-208 | reuse | Most transferable demo rule. (5) matters for fast-moving AI SDKs. |
| A18 | First-contact teach: a concept's first appearance is TAUGHT with a no-code/whiteboard beat, "never merely named before use". Notes provide depth, not first contact. | R-014 T1 L329-332 | reuse | |
| A19 | Production patterns beyond the day's scope are a pedagogy concern, not rigor; code unsafe at any level fails even if simpler. | R-014 T2 L339-341; eng-reviewer L46-50 | reuse | |
| A20 | Demo task is done only with BOTH script path and commit id ("two-part gate"). | R-011 L255-256 | reuse | |
| A21 | Demo block: "LIVE — trainer builds + pushes cumulative demo (commit per topic)". Code reaches trainees by pushing DURING the block. | DM L17 | reuse | Answers the visibility question: publish-as-you-go, not pre-published. |
| A22 | Non-code topics (SDLC/Agile) ship as a note + pre-watch, NOT a demo repo; awareness topics are lectures outside project scope. | DM L39, L171, L130-131 | reuse | Directly retires 02/03 as code. |
| A23 | Intro topics that fit no thread become standalone AM demos with their own deliverable. | DM L53-54, L326-330 | reuse | |
| A24 | "Build what you demo": the demo thread mirrors the learner project; project stays buildable from tech already taught; Floor (MVP) fully taught before the build. | cohort-decisions L36-41; DM L115-118 | reuse | Central lesson of the old cohort. We have P0/P1/P2 weeks with no demo-mirrors-project rule. |
| A25 | Dependency guarantees list (which rung precedes which) in the series README. | DM L144-147 | adapt | |
| A26 | Day budgets were optimistic (scripts ~85 min, delivery took a day). Track minutes per demo against the block. | demo audit T1-6 L231-233 | reuse | Our runbook already sums minutes; add per-demo actuals after delivery. |
| A27 | Series README template sections: Threads; ordered demo table with minutes; dependency graph (mermaid); stop points if splitting; squeeze priorities ("Cut first" / "Never cut"); anti-spoiler ledger; real-world framing + deviation ledger; run prerequisites; seed-file manifest. | weeklytechrepo/Test-Automation/demo/walkthroughs/README.md | reuse | Best runbook/series skeleton found. |
| A28 | Walkthrough script header: Objective / Time / "Before the room arrives" / Delivery mode / Audience / Prerequisite reading / Target thread / Hand-typed vs Tool-generated file lists; body: cheat-sheet table, timed steps, pitfalls, not-covered, wrap-up Qs, sequence pointer; appended dated Delivery record. | weeklytechrepo/.../03-cypress-fundamentals.md | reuse | |
| A29 | Delivered-code defects shown in class had never been run (broken sort, unsound search). | demo audit T2-2, T1-3 | avoid | Our demos critic runs every script: keep that even if the artifact becomes a script. |
| A30 | Gap: no step-marker syntax, no numeric size cap, no explicit rehearsal rule in the old repo. | rulebook sweep | — | Our `# --- STEP n ---` + ≤90 lines + critic run are additions worth keeping. |

## B. Notes / lecture material

| # | Rule | Source | Tag | 2494 relevance |
|---|---|---|---|---|
| B1 | Notes are a training-independent per-technology library. PORTABILITY (hard): never mention classroom, demos, commits, cohort project, calendar, or exams; examples self-contained. Portability grep at review. | R-022 L264-272; note-depth audit L57-65, L82-84 | adapt | Our pages are deliberately day-bound (date, demo links, NEXT). Decide: portable notes vs day pages. Could split: day page (bound) wraps portable sections. |
| B2 | Interview-pass depth per objective: prose, runnable code, cost/trade-off, recognize-on-sight, spoken-form answer. | R-022 L273-276 | reuse | Concrete depth bar for notes critic. |
| B3 | Mandatory sections: "Say it in an interview" (1-3 sentences/objective) and "Check yourself" (3-5 retrieval Qs with answers), before Resources. Adjacent-question rule: cover the usual follow-up one level beyond. | R-022 L277-281 | reuse | Our quiz ≈ Check yourself; "Say it in an interview" is missing and fits the persona (job-bound grads). |
| B4 | Notes may teach ahead; R-008 sequences demos only. | R-022 L281-283 | reuse | Resolves our "nothing from later days" tension for notes. |
| B5 | 10-20 min reading per note. | R-022 L284; DM L25 | have | Ours: 1200-1800 words ≈ 8-12 min. |
| B6 | Every external URL tested with an HTTP request at authoring time; dead at gate = gate defect; repo-relative links must resolve. | R-023 L287-293 | have (partial) | We have `test_links_external` behind CHECK_EXTERNAL=1 and light-gate "no fetch". Make link liveness mandatory regardless of gate. |
| B7 | Traceability lives outside notes: week `content/README.md` coverage map (curriculum bullet → note → demo rung). | R-022 L270-271; weeklytechrepo/.../content/README.md | adapt | We have no coverage map; curriculum.json subtopics → page step → demo would be the equivalent. |
| B8 | Material from a skipped demo goes to concept notes, not crammed into class. | note-depth audit L15-31 | reuse | |
| B9 | Note skeleton: Title & Objective → Why it matters → Core concept → Code examples → Say it in an interview → Check yourself → Summary → 2-3 external resources. | playbook L57-59 | adapt | |

## C. Exercises / activities / projects

| # | Rule | Source | Tag | 2494 relevance |
|---|---|---|---|---|
| C1 | Specs are domain-neutral, point at the demo commit they mirror, list acceptance criteria; no stubs, no starter scaffold, no solution key. | R-007 L119-120 | adapt | Conflicts with our pytest-kind starter/solution contract; matches our rubric kind (D-0025). Decide per week. |
| C2 | Acceptance checklist = rubric; learner mirrors demo in own repo; submitted as PR; trainer floats. | DM L20, L69 | reuse | |
| C3 | Lab README spec: Objective / The Demos This Mirrors / Use your own domain / `- [ ]` checklist / Build From Scratch / Engineering Definition of Done / Techniques You Must Demonstrate. | weeklytechrepo/SQL/async-lab/sql-training-README.md | adapt | Richer than our exercise-rubric template; lift "Demos this mirrors" and "Definition of Done". |
| C4 | One learner repo (`FirstName-Lastname`), one folder per thread. | DM L31-36 | adapt | We have no learner-repo convention. W1D2 exercise invents `w01d2-team-repo` per day. |
| C5 | MVP → Stretch tiers inside one final spec; no staged deliverables; project buildable from taught tech. | DM L169-170, L117-118 | reuse | For P0/P1/P2 weeks. |
| C6 | Release-arc deliverable across days (v0.1 → v1.0), team builds of 3 with light branch/PR/review. | DM L75-80 | adapt | |
| C7 | Stakeholder blurb + Required Skeleton + coverage contract in project specs. | weeklytechrepo/Test-Automation/project/p3-test-suites.md | adapt | |
| C8 | Drills: model solution + objective pointer; drill prompt domain-neutral; no drills for untaught topics. | review-guide L124-127 | adapt | |

## D. Process / governance

| # | Rule | Source | Tag | 2494 relevance |
|---|---|---|---|---|
| D1 | Every rule lives ONCE with a stable ID; other files cite IDs, never restate. Change = edit in place + MODIFY log entry. One-time decisions are not rules; they go to history. | RULES header L3-6; CLAUDE L16-18 | reuse | We have decisions (one-time) but no rule registry; AGENTS.md restates rules in prose. Add RULES with IDs; AGENTS.md cites. |
| D2 | Read order each session: STATE → RULES → week Log → run drift-check; drift-check output is "the copy source — never free-recall counts". | CLAUDE L13-22 | have (partial) | We read STATUS → decisions. Add a mechanical check script. |
| D3 | Two data files: curriculum = WHAT, delivery model = HOW/WHEN; only the planner parses them; delivery model wins calendar disputes. | R-001 L16-19 | adapt | curriculum.json carries both today. A separate delivery model (day shape, hours, budgets, overrides) would hold what metrics.json runbook minutes + startDate/holidays do. |
| D4 | Coverage spine = rubric Must/Should; missing = COVERAGE DEFECT, stop and flag loudly; Nice skip needs user sign-off + log entry. | R-002 L21-26; review-guide L81-85 | adapt | We have no rubric/assessment spine; subtopics from PNGs play that role. "Coverage defect, never buried" pattern transfers. |
| D5 | "Prepare to the rubric, not the name"; QC rubrics are the spine, not the LMS export. | R-003 L51; process audit FIT-03 | reuse | |
| D6 | Task states only `[ ]`, `[x]`+evidence pointer, `[-]`+rationale+log, `[>]`+target; bare `[x]` invalid; header Status = LOWEST task state; every Log has `## Maintenance`. | R-011 L251-262 | reuse | STATUS.md milestones table has Done dates but no evidence pointers. "The single proven drift-catcher in the repo." |
| D7 | Supersession is in-place edit + commit; `*-updated`/`*-v2`/dated sibling files banned. "History answers 'what did it used to say' — files never do." | R-012 L297-300 | reuse | |
| D8 | Cross-repo move: blob-verify before delete; commit deletion same session with log line; status sweep; name what does NOT move. | R-012 L301-307 | reuse | We move things between training/ and trainer/. |
| D9 | Blocking weekly gate (Fri PM): next week's plan may not be authored until this week's pass is recorded. Gate checks: code matches scripts, trees clean, Log truth, STATE current, dual-lens delta review. Recorded in exactly two places. | R-013 L309-320 | reuse | We have milestone 7 "retrospective" but no gate. |
| D10 | Dual-lens review (learner lens + senior-dev lens) at authoring (full series) and gate (delta); reviewers read-only, write PASS/FAIL to the log; "no finding without a pointer". | R-014 L322-343; pedagogy-reviewer L66-67 | have (partial) | Our critics are per-artifact single-lens. Add a series-level pedagogy pass. |
| D11 | Mid-week rule break allowed but logged IMMEDIATELY as OVERRIDE; at gate promoted (MODIFY) or retired (DEPRECATE). "No silent divergence between law and practice." | R-015 L345-349 | reuse | Our decisions log has no override/temporary state. |
| D12 | Governance log: append-only JSONL; fields timestamp, rule_id, action_type (CREATE/MODIFY/DEPRECATE/OVERRIDE/EXECUTE), triggering_event, rationale, affected_artifacts; validated per line (JSON, fields, rule_id resolves, timestamps non-decreasing, enums). Ship-coupling: committing a governed artifact carries a log line same session. | R-016 L351-394 | adapt | Our decisions/*.md + README table is the human-readable equivalent; test_decisions.py validates. Could add action_type/triggering_event. |
| D13 | Every doc has one class: Live / Archive / Immutable record / Prune. Living state belongs only in STATE. | R-017 L396-404 | reuse | |
| D14 | Write/Demo roles are Log-driven: no Log supplied → fail and request, never improvise from data files. | R-019 L406-408 | reuse | Equivalent: authors work only from args/brief. Already true by construction. |
| D15 | Fact correction → repo-wide grep before commit; "sweeping from a remembered doc list is banned"; status claims (owed/pending/blocked-until) propagate the same way; a gate item whose condition closes is struck in the same commit. | R-025 L411-424 | reuse | |
| D16 | Delivery-day close (R-027), blocking: first session after delivery runs the close before other work: log classroom commits, file OVERRIDEs, every untracked file gets a disposition, run drift check, every WARN dispositioned. Catch-up close per missed day; "a no-session gap is not itself drift — an unrun catch-up close at the next session is." Queue-jump needs an OVERRIDE as entry fee. | R-027 L210-241 | adapt | Directly relevant once training starts Tue: post-delivery close = fold what was actually taught back into runbook/demos. |
| D17 | Built-in stops: missing Log, one-off demo request, 2 failed fix passes, coverage defect, missing gate pass, reviewer FAIL. | README L106-110 | reuse | Closed escalation list. |
| D18 | Audit-prompt design: closed check registry with stable IDs, fixed output schema, source-of-truth hierarchy (disk outranks docs), evidence gate, severity taxonomy DEFECT/STALE/OPEN/OVERHEAD, facts phase locked before judgment, bounded anomaly bucket. | PROCESS-AUDIT-PROMPT L41-70, L189-198 | reuse | Strongest reusable template; basis for a retrospective/audit skill. |
| D19 | Demo audit yardsticks: (1) demo mirrors project, every tier taught before needed, with need-by dates; (2) rubric Must/Should coverage. Classroom reality wins: fold classroom deltas back into canonical, never reverse. Repair loop capped at 2. | WK4-5-DEMO-AUDIT-PROMPT L36-44, L62-78, L99-117 | reuse | Basis for milestone 7 week-1 retrospective. |
| D20 | Counts enumerated from the log, never recalled (hand-kept OVERRIDE counts disagreed 7 vs 4 vs 3). | drift audit L43-45, L70 | reuse | |
| D21 | Rules added only for recurring work; one-off procedures stay ad hoc. | process audit 07-10 L67 | reuse | |
| D22 | Only three things are FIXED (blurb, presentation date, one exam); everything else fluid. | CONTEXT-BRIEF L176-195 | adapt | Name our fixed points (start date, holidays, feedback form?). |
| D23 | Producer-consumer trace for a suspect curriculum line: check rubric first; grep everywhere it spread; disposition per file (Removed/Softened/Kept); check auditor's own earlier output; list clean surfaces. | producer-consumer analysis | adapt | Procedure for TFLearn / pre-1.0 LangChain currency lines (D-0012). |

## E. Delivery model / day shape

| # | Rule | Source | Tag | 2494 relevance |
|---|---|---|---|---|
| E1 | 9-17, lunch 12-13; AM live demo 9-12, optional 13:00-13:30 tail, PM 13:30-17 async lab, pre-watch last ~20 min. "No AM-async, no post-lunch ping-pong": one transition per day. | DM L13-25 | adapt | Our W1D2 runbook interleaves 5 demos + hands-on + notes + exercise across the day (10 blocks). Old model: one AM demo block, one PM lab block. |
| E2 | Day shape is a default, not law; overrides legitimate when recorded; "an unrecorded deviation is drift". | R-010 L245-249 | reuse | |
| E3 | Heavy weeks: 3-5h live demo max/day, rest reinforcement drills. | DM L102-103 | adapt | |
| E4 | No-pre-watch weeks: plan as if learners watch nothing; videos optional supplements. | DM L98-100 | reuse | |
| E5 | Lost days get an explicit recovery map; no schedule slips; holiday becomes self-paced buffer. | DM L63-72, L79-80; cohort-decisions L9-19 | have | D-0015..D-0017 did this. |
| E6 | Running long: defer remainder to a named window via OVERRIDE; extra blocks granted and recorded. Running short: re-cut to taught shape; freed minutes returned to project. | DM L159, L300-324 | reuse | Our runbook "If running long / short" is per day; add the override log. |
| E7 | Exam morning moves demo to afternoon; presentation Friday keeps AM demo, shrinks async. | DM L135-140 | adapt | |

## F. Machinery (agents, playbook, scripts, templates)

| # | Item | Path | Tag | What to lift |
|---|---|---|---|---|
| F1 | weekly-playbook.md: 3 roles (PLAN reads data files; WRITE and DEMO are Log-only) + weekly gate; sequence: gate check → coverage check → emit Log → demo batch (series README first) → written content → delivery → gate. | content-agents/weekly-playbook.md | adapt | The week-level planning stage our pipeline lacks. Maps onto a `week-plan` stage before `day-fanout`. |
| F2 | pedagogy-reviewer.md: 8 checks as first-time learner: no future-day depth; coverage; step times sum to budget; first-contact learner simulation (every term introduced before use; wrap-up Qs answerable from taught material); series tells one story / realizes Weekly Epic; learner who has NOT read prerequisites; file+line on every finding. | content-agents/pedagogy-reviewer.md L6-67 | adapt | Series-level critic we do not have. Checks 6-8 transfer verbatim. |
| F3 | engineering-reviewer.md: builds green at every rung; script↔commit both ways; pattern level fits the day; deviation deliberate not industrial; cold-start startup commands with cwd; spot-check tool provenance by RUNNING it; read-only except the log. | content-agents/engineering-reviewer.md L6-79 | adapt | Checks 1,2,6,7,8 transfer; swap dotnet for pytest/ruff. |
| F4 | review-guide-agent.md: produces exam-prep packages (7 files: README, study-guide, self-assessment verbatim checklist, mock-interview with Proves/Source lines, cheat-sheet, drills, out-of-scope register with COVERAGE DEFECTS on top). "Stop and request, don't invent." Every entry traces to a real source file. | content-agents/review-guide-agent.md L15-172 | adapt | Maps to research-brief grounding and to review-day pages (O-2). Mock-interview format fits the persona. |
| F5 | drift-check.ps1: 6 read-only checks (log validity; open OVERRIDEs since last gate; stale markers TBD/OWED/pending in live docs; git tree hygiene incl. unstaged deletions; weekdays without a close; owed prompt files). Exit 1 = hard findings. | tools/drift-check.ps1 | adapt | Port to Python as `harness/drift_check.py`; wire into tests or a pre-commit. |
| F6 | Series README (walkthroughs/README.md) and walkthrough script header/body (see A27, A28). | weeklytechrepo/Test-Automation/demo/walkthroughs/ | reuse | Templates. |
| F7 | Coverage map README: curriculum bullet → note file → demo rung, by day. | weeklytechrepo/Test-Automation/content/README.md | adapt | |
| F8 | QC rubric format: `Criteria Difficulty | Exit Criteria` with Must/Should/Nice tiers. | qc-criteria/QC-6-Test-Automation.md | adapt | We have no assessment spine. |
| F9 | honest-gap-talking-sheet: "what you know cold / the honest boundary / the bridge". | docs/review-guides/QC6-Test-Automation/honest-gap-talking-sheet.md | adapt | For key-gated/awareness topics (weeks 5, 8, 9, 11). |
| F10 | Ad-hoc link check in settings.local.json (`grep -rhoE 'https?://' ... xargs curl -w %{http_code}`). | .claude/settings.local.json | adapt | Make it a real script; our test exists but is opt-in. |

## G. Lessons learned (failure → control)

| Failure | Control | Tag |
|---|---|---|
| Sibling `-updated` files → false "unchanged" claims, calendar skew | Git-only supersession (R-012) | reuse |
| State spread across 6 layers | One STATE file; but it grew to 1,900 lines of addenda and still drifted (15 stale claims) | adapt: keep STATUS.md short, no addendum stack, NEXT as one short list |
| Rules restated in 3-7 places, none enforced | Rule registry by ID; agents cite IDs | reuse |
| `[x]` without evidence; invented states | R-011 state vocabulary + evidence pointer | reuse |
| No verification loop | Blocking weekly gate (R-013) | reuse |
| Demo code had no git history; copies diverged | One canonical copy (R-018) | adapt |
| Too many agents for one trainer; coordination generated drift | Collapsed to one playbook with 3 roles + separate reviewers | reuse (we have ~10 agent roles per day; worth noting) |
| Repo-local memory was the stalest layer | Pruned | reuse |
| Fact corrections from a remembered doc list missed files | R-025 repo-wide grep | reuse |
| Port mismatches 3x, syntax-before-introduction 2x in live beats | R-026 pre-flight | reuse |
| Delivery-day closes ran late; sessions jumped to new authoring | R-027 blocking close + OVERRIDE entry fee + catch-up clause | adapt |
| Hand-kept counts disagreed | Enumerate from the log | reuse |
| Cross-repo move lost a file | Blob-verify before delete | reuse |
| Discipline degraded under delivery pressure | Mechanical drift-check at every close | reuse |
| False reports (claimed non-delivery that had happened; audit contaminated itself) | Disk outranks docs; evidence gate; correction logged as new root cause | reuse |
| Scope creep from LMS export lines | Rubric is the spine | adapt |
| Delivered demo code never run → bugs shown in class | Build/run every rung before delivery | have (critic runs scripts) |
| Demo budgets optimistic (85 min scripted, full day delivered) | Track actuals; squeeze priorities in series README | reuse |

## H. What 2494 already has, mapped

| Old mechanism | 2494 equivalent | Gap |
|---|---|---|
| STATE.md | STATUS.md | fine; keep it short (avoid addendum stack) |
| governance-log.jsonl + RULES.md | decisions/*.md + README table | no rule registry with IDs; no OVERRIDE/temporary state; no action_type |
| CMA weekly Log | none | no week-level plan artifact; days authored in isolation |
| Series README | demos/<day>/README.md (per day) | no week-level ladder, budgets, stop points, deviation ledger |
| Walkthrough script | trainer runbook demo sections | runbook ≈ script already; demo README duplicates |
| Answer-key commit per topic | demos/<day>/NN_*.py | files, not commits; no code-along repo that grows |
| pedagogy/engineering reviewers (series-level, dual lens) | 5 per-artifact critics, single lens | no series-level pass; no learner-simulation check |
| drift-check.ps1 | tests/ (contract tests) | no stale-marker, no close-cadence, no decisions-log enum checks |
| Weekly gate | milestone 7 "retrospective" (one-off) | not blocking, not weekly |
| Delivery-day close | none | needed from Tue 2026-10-13 |
| QC rubric spine | curriculum.json subtopics | no Must/Should/Nice tiers, no coverage defect concept |
| Portable notes (R-022) | day-bound pages | decide portable vs bound |

## I. Candidate skills (later; not committed)

1. `demo-script` — author a live-typed walkthrough script from a brief: A2, A3, A5, A17, A28; critic = F2/F3 subset.
2. `week-plan` — series README first: A13, A16, A25, A27, F1; blocks day-fanout until it exists.
3. `delivery-close` — R-027 post-session close: fold classroom reality back, dispositions, drift check.
4. `drift-check` — F5 ported to Python.
5. `retrospective-audit` — D18 + D19 audit prompt with closed check registry.
6. `notes-portable` — B1-B3 sections and portability grep.

## Provenance

- Every row cites a file under the Prep root; line refs come from the three read-only sweeps on 2026-10-11.
- Mined read-only by three parallel Explore agents; this file is the only artefact produced.
