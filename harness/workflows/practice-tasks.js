// practice-tasks.js — practice tasks for notes pages, as a stage of its own AFTER a week's days are authored (D-0047).
//
// Two runs with the trainer's answer between them. A script cannot ask a question, so the answer lives on disk:
//
//   1. Suitability   python harness/args_for.py <week> [day...] --practice --today YYYY-MM-DD   -> paste as args
//                    One assessor per authored page: for every teaching step, does a task fit the runtime and the
//                    page, and which one. Writes harness/practice/<rel>.json (proposals only; the page is not touched).
//   2. The trainer   python harness/practice_tasks.py show <week>      the session puts this in front of the trainer
//                    python harness/practice_tasks.py approve <week> <day> t1 t3 | --all | --none
//   3. Build         python harness/args_for.py <week> [day...] --practice-build --today YYYY-MM-DD   -> paste as args
//                    (refused while a proposed task has no answer). Per day, in parallel: an author fills q, starter
//                    and tests for the approved tasks, writes trainer/<rel>/solutions/practice.py and
//                    practice_cases.py and runs practice_tasks.py insert; a DIFFERENT critic agent judges it against
//                    harness/critics/practice.md; up to 3 passes, then the day is flagged (never blocks the others).
//   Workflow({ scriptPath: "harness/workflows/practice-tasks.js", args: <that JSON> })
//
// Both runs end with Record (run log + work tracker, D-0035) and Verify (contract tests). The browser pass
// (harness/practice_browser.py, AGENTS.md) is NOT in here: the session drives it with its browser tools after a
// build, and the stage is not done until it reports ok: true for every built day.
// Agents: suitability = days + 2; build = 2 to 6 per day + 2.
//
// Model tiers (D-0026, D-0047): `practice-suitability`, `practice`, `critic`, `wire`, `verify` from config.json
// models via args_for.py; tier() is copied from day-fanout.js. Every agent() call spreads a tier.
// Scripts cannot touch the filesystem or Date(); everything comes in through args.

export const meta = {
  name: 'practice-tasks',
  description: 'Practice tasks for authored notes pages: a suitability pass that proposes tasks per day, or, once the trainer has approved them, the build of the tasks, model answers and cases (critic-gated)',
  phases: [
    { title: 'Suitability' },
    { title: 'Build' },
    { title: 'Record' },
    { title: 'Verify' },
  ],
}

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
if (!A.root || !A.today || !A.week || !Array.isArray(A.days) || !A.days.length || !A.critic || !['suitability', 'build'].includes(A.mode)) throw new Error('args must come from `python harness/args_for.py <week> --practice` or `--practice-build` (root, today, week, days[], critic, mode required)')
if (!A.models || !A.models.stages || !A.models.stages['practice-suitability'] || !A.models.stages['practice']) throw new Error('args.models.stages must carry practice-suitability and practice (D-0047); regenerate args with args_for.py')
const BUILD = A.mode === 'build'
if (BUILD && A.days.some(d => !Array.isArray(d.tasks) || !d.tasks.length)) throw new Error('a build day needs its approved tasks; regenerate args with args_for.py --practice-build')
const ROOT = A.root
const H = `${ROOT}/harness`
const M = (A.metrics || {}).practice || {}
const CFG = A.config || {}
const RT = A.runtime || {}
const EX = A.exemplar
const DAYS = A.days
const TIERS = A.models || {}
// Every agent call spreads tier() exactly once, so counting the calls counts the agents (run record, D-0035).
let AGENTS = 0
function tier(stage, pass, quiet) {
  if (!quiet) AGENTS++
  const st = (TIERS.stages || {})[stage] || {}
  const esc = (pass && TIERS.escalateOn && pass >= TIERS.escalateOn && TIERS.escalate) ? TIERS.escalate : null
  const t = esc || st
  const o = {}
  if (t.model) o.model = t.model
  if (t.effort) o.effort = t.effort
  return o
}
const tierLabel = (s) => { const t = tier(s, 0, true); return `${s}=${t.model || 'inherit'}/${t.effort || 'inherit'}` }
const TIER_LABELS = (BUILD ? ['practice', 'critic', 'wire', 'verify'] : ['practice-suitability', 'wire', 'verify']).map(tierLabel).join(' · ')
const J = (x) => JSON.stringify(x, null, 1)
const MAX_PASSES = 3

const VERDICT = { type:'object', additionalProperties:false, properties:{ pass:{type:'boolean'}, critiques:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['pass','critiques','summary'] }
const SUIT_SCHEMA = { type:'object', additionalProperties:false, properties:{
  verdict:{ type:'string', enum:['full','partial','none'] }, teachingSteps:{type:'number'}, tasksProposed:{type:'number'},
  validated:{type:'boolean'}, summary:{type:'string'} },
  required:['verdict','teachingSteps','tasksProposed','validated','summary'] }
const BUILD_SCHEMA = { type:'object', additionalProperties:false, properties:{
  tasksBuilt:{type:'number'}, checks:{type:'number'}, rightAnswers:{type:'number'}, wrongAnswers:{type:'number'},
  verifyOutput:{type:'string'}, summary:{type:'string'} },
  required:['tasksBuilt','checks','rightAnswers','wrongAnswers','verifyOutput','summary'] }
const VERIFY_SCHEMA = { type:'object', additionalProperties:false, properties:{ passed:{type:'boolean'}, failures:{type:'array', items:{type:'string'}} }, required:['passed','failures'] }

const fix = (cr) => cr && cr.length ? ('\n\nThis is a REPASS. The critic flagged these issues — fix every one, keep what was good:\n- ' + cr.join('\n- ')) : ''

const context = (d) =>
  `DAY ${d.id} "${d.title}" (week ${A.week} "${A.theme}", ${d.dateLabel}); subtopics: ${(d.subtopics || []).join('; ')}.\n` +
  (CFG.audience ? `Audience: ${CFG.audience.summary} Assume already known: ${(CFG.audience.assumeKnown || []).join('; ')}.\n` : '') +
  `Notes page (already authored, the reader's only material): ${d.pageFile}\n` +
  `Practice file (the one source of this page's tasks): ${d.practiceFile}\n` +
  `Research brief (Pitfalls and Notes depth name the mistakes worth catching): ${d.researchBrief || 'none'}\n` +
  `Exercise README (a task never hands this over): ${d.exerciseReadme || 'none'}\n` +
  `Week-plan anti-spoiler rows that mention this day (a task uses nothing a row defers from this day to a later one): ${J(d.spoilerRows || [])}\n` +
  `Demo threads in scope (keep to the domain where the page does): ${J(A.threads || {})}\n` +
  `Runtime: Pyodide ${RT.pyodide || '(see the worker)'} in the reader's browser, standard library only, no input(), no packages; the contract is ${ROOT}/${RT.worker || 'docs/assets/js/pyworker.js'}. Course Python is ${CFG.python}.\n` +
  `Bars (metrics.json practice): ${J(M)}.\n` +
  (EX ? `Exemplar, the accepted shape (D-0046), from ${EX.day}: file ${EX.file}; its page ${ROOT}/${EX.page}; model answers ${ROOT}/${EX.answers}; cases ${ROOT}/${EX.cases}.\n` : 'No exemplar on disk yet: the shapes are described in AGENTS.md and harness/practice_tasks.py.\n') +
  `Root: ${ROOT}. Today: ${A.today}.\n`

async function gated(gen, crit) {
  let result = await gen(null, 1)
  for (let pass = 1; pass <= MAX_PASSES; pass++) {
    const v = await crit(result, pass)
    if (v && v.pass) return { status:'done', passes: pass, summary: (v.summary || (result && result.summary) || ''), result }
    if (pass === MAX_PASSES) return { status:'flagged', passes: pass, flags: (v ? v.critiques : ['critic returned null']), summary: (result && result.summary) || (v && v.summary) || '', result }
    result = await gen(v ? v.critiques : ['prior critic hard-failed (returned null) — redo the build from the proposal, full quality bar'], pass + 1)
  }
}

log(`Mode ${A.mode}: ${DAYS.map(d => d.id).join(', ')}. Model tiers: ${TIER_LABELS}; escalate on pass ≥ ${TIERS.escalateOn || '—'}`)

// ---------- SUITABILITY: one assessor per authored page; the trainer is the judge, so there is no critic ----------
const assess = (d) => agent(
  `You are the PRACTICE SUITABILITY assessor (D-0047). You propose; the trainer decides; a later run builds. ${context(d)}` +
  `Read, in this order: (1) ${A.critic} — "The runtime" and "Suitability" are your bar; (2) ${ROOT}/${RT.worker || 'docs/assets/js/pyworker.js'} — what a check can see; (3) the notes page, every teaching step (each section.step but the last, Check yourself); (4) the research brief's Pitfalls and Notes depth; (5) the exercise README; (6) the exemplar file and its page section, for the size and voice of a task.\n` +
  `Write ${d.practiceFile} with the Write tool (never echo or a heredoc; it is JSON with quotes in it), with exactly these keys:\n` +
  `- "day": "${d.id}", "page": "${d.pageRel}", "assessed": "${A.today}", "verdict", "summary";\n` +
  `- "steps": one object per teaching step in page order: "step" (the section's data-step number), "title" (its h2 text, exactly), "suitable" (true or false), "reason" (one or two sentences the trainer can act on: what in this step shows up as behaviour a check can see, or which rule of the bar rules a task out), "task" (the task id, or null);\n` +
  `- "tasks": at most one per suitable step, in step order: "id" (t1, t2, ...), "title", "step", "idea", "checks" (${M.checksPerTaskMin || 2} to ${M.checksPerTaskMax || 4} sentences, one behaviour each, each failed by a mistake the page names), "approved": null, "q": "", "starter": "", "tests": "".\n` +
  `Judge every step on its own. "partial" and "none" are honest verdicts; do not stretch a step that teaches a convention, a tool or typed input into a task. Do NOT write task text, starters or asserts, do NOT touch the page, the trainer repo or any other file.\n` +
  `Write plainly (D-0029): present tense, concrete names, no filler, no "not X but Y", no stock AI words.\n` +
  `Before returning, with Bash from ${ROOT}: run "python harness/practice_tasks.py validate ${A.week} ${d.day}" until it prints OK (fix the file, never the checker).\n` +
  `Return verdict, teachingSteps, tasksProposed, validated (true only if the command printed OK), summary (one sentence: what the day lends itself to and what it does not).`,
  { schema: SUIT_SCHEMA, label:`${d.id}:suitability`, phase:'Suitability', ...tier('practice-suitability') })

// ---------- BUILD: author + critic per day; days run side by side (each touches only its own files) ----------
const build = (d) => gated(
  (cr, pass) => agent(
    `You are the PRACTICE TASK author (D-0047), pass ${pass}. The trainer approved these tasks of this day; build exactly these and no other: ${J(d.tasks)}\n${context(d)}` +
    `Read: (1) ${A.critic} — "The runtime" and "Build" are what the critic checks; (2) ${ROOT}/${RT.worker || 'docs/assets/js/pyworker.js'} — the runner: how a check is tried, what raises() does; (3) the notes page, above all the steps these tasks practise; (4) the practice file as it stands; (5) the exemplar: its file (q, starter, tests), its model answers and its cases — copy those three shapes exactly; (6) the research brief's Pitfalls and the exercise README.\n` +
    `Then, with the Write and Edit tools only (never echo or a heredoc: these files carry quotes, backslashes and newlines):\n` +
    `1. In ${d.practiceFile}, for each approved task fill "q" (the task text, HTML with <code> only), "starter" and "tests" (top-level asserts, each with a message that is the label the reader sees). Change nothing else in the file: steps, reasons, ideas, the trainer's answers and every declined task stay as they are.\n` +
    `2. Write ${ROOT}/${d.solutionsDir}/practice.py: one model answer per built task in page order, each under a comment naming the task, in one file whose names do not collide.\n` +
    `3. Write ${ROOT}/${d.solutionsDir}/practice_cases.py: CASES = { "<task id>": { "accept": [other right answers], "reject": [(wrong answer, label of the check that must catch it)] } } with an entry per built task and no other. Every check needs a wrong answer that fails it; make the wrong answers the mistakes this page warns about.\n` +
    `4. From ${ROOT}: python harness/practice_tasks.py insert ${A.week} ${d.day}   — it writes section.practice into the page from the file. NEVER edit that section, or anything else on the page, by hand.\n` +
    `5. From ${ROOT}: python harness/practice_tasks.py verify ${A.week} ${d.day}   until it prints OK (after every change to the file, run insert again first). Fix the tasks, the answers or the cases; never the checker, ${RT.worker || 'pyworker.js'} or ${RT.widgets || 'widgets.js'}.\n` +
    `6. From ${ROOT}: python harness/notes_check.py ${d.pageRel} --counts   must still pass, and "git diff --stat -- ${d.pageRel}" must show the practice section as the page's only change.\n` +
    `Other days are being built beside you: touch only this day's practice file, its page (through insert) and its two files under ${d.solutionsDir}. Do not run the whole test suite; step 5 is this day's share of it.\n` +
    `Write the task text plainly (D-0029). Return tasksBuilt, checks (asserts across the tasks), rightAnswers and wrongAnswers (entries in practice_cases.py), verifyOutput (the last lines step 5 printed, verbatim), summary (2 sentences).` + fix(cr),
    { schema: BUILD_SCHEMA, label:`${d.id}:practice`, phase:'Build', ...tier('practice', pass) }),
  (_r, pass) => agent(
    `PRACTICE TASK CRITIC (pass ${pass}). Read ${A.critic} and apply every "Build" item to day ${d.id}. The approved tasks were: ${J(d.tasks.map(t => ({ id: t.id, title: t.title, step: t.step, idea: t.idea })))}\n${context(d)}` +
    `With Bash from ${ROOT}, run and quote verbatim: "python harness/practice_tasks.py verify ${A.week} ${d.day}", "python harness/notes_check.py ${d.pageRel} --counts" and "git diff --stat -- ${d.pageRel}". Read ${d.practiceFile}, the page's section.practice and the steps it practises, ${ROOT}/${d.solutionsDir}/practice.py and practice_cases.py. Solve each task yourself from the task text alone before you read its model answer: if you needed something the page does not teach, or the text left a requirement to guesswork, that is a critique. Change no file.\n` +
    `Return pass, critiques (task id + what is wrong + the concrete fix), one-sentence summary.`,
    { schema: VERDICT, label:`${d.id}:practice-crit`, phase:'Build', ...tier('critic') }))

phase(BUILD ? 'Build' : 'Suitability')
const results = await parallel(DAYS.map(d => () => BUILD ? build(d) : assess(d)))
const report = DAYS.map((d, i) => {
  const r = results[i]
  if (BUILD) return { day: d.id, status: r ? r.status : 'flagged', passes: r ? r.passes : 0, flags: r ? (r.flags || []) : ['author or critic hard-failed'], summary: r ? r.summary : '', built: r && r.result ? r.result.tasksBuilt : 0 }
  const ok = !!(r && r.validated)
  return { day: d.id, status: ok ? 'done' : 'flagged', passes: r ? 1 : 0, flags: ok ? [] : [r ? 'the proposal does not pass practice_tasks.py validate' : 'assessor hard-failed'], summary: r ? r.summary : '', verdict: r ? r.verdict : null, proposed: r ? r.tasksProposed : 0 }
})
const flagged = report.filter(r => r.status === 'flagged')

// ---------- RECORD (work tracker, D-0035) ----------
// Written before Verify so the run-log contract test sees it; Verify amends the test result. Run id, tokens and
// minutes are invisible to a script: the session adds them with `python harness/log_run.py amend --last ...`.
phase('Record')
const DAY_IDS = DAYS.map(d => d.id).join(',')
const runRecord = {
  kind: 'practice', date: A.today, week: A.week, days: DAYS.map(d => d.id), runId: null, agents: AGENTS + 2, minutes: null, tokens: null,
  tiers: { labels: TIER_LABELS, verified: null },
  artifacts: report.map(r => ({ day: r.day, name: BUILD ? 'practice' : 'practice-proposal', status: r.status, passes: r.passes })),
  flagged: flagged.length,
  flags: flagged.map(f => ({ day: f.day, artifact: BUILD ? 'practice' : 'practice-proposal', flags: (f.flags || []).slice(0, 6).map(x => String(x).slice(0, 300)) })),
  tests: null, resolved: false,
  note: BUILD ? 'practice build (D-0047): approved tasks written; the browser pass is owed per built day' : 'practice suitability pass (D-0047): proposals only, the trainer answers next',
}
const recorded = await agent(
  `RECORD step (work tracker, D-0035).\n` +
  `1. With the Write tool (not echo, not a heredoc) create ${H}/run-report.tmp.json containing EXACTLY this JSON:\n${JSON.stringify(runRecord)}\n` +
  `2. From ${ROOT} run: python harness/log_run.py add harness/run-report.tmp.json\n` +
  `   It validates the record, appends it to harness/runs.jsonl, deletes the temp file and rebuilds tracker.html. If it rejects the record, fix only what its message names in the temp file and retry. Never edit harness/runs.jsonl or tracker.html by hand.\n` +
  `3. Run: python harness/build_tracker.py --check   and return its one-line output.`,
  { label:'record', phase:'Record', ...tier('wire') })

// ---------- VERIFY ----------
// No fix loop: a failure here is either a flagged day (already reported) or one day's files against another's,
// and the session that reads this result is the one that runs the browser pass next.
phase('Verify')
const verify = await agent(
  `VERIFY step. From ${ROOT}: run python harness/build_tracker.py, then python harness/practice_tasks.py check, then python -m unittest discover -s tests -v. Report passed=true only if all of it passes. List each failure as "<test or command>: <one-line cause>". Change no file other than what build_tracker.py writes.\n` +
  (recorded
    ? `Then record the result: python harness/log_run.py amend --last --match-days ${DAY_IDS} --tests pass   (use --tests fail when anything failed). If it refuses because the last record is not this run's, skip it and say so.`
    : `The Record step did not complete; do not amend the run log.`),
  { schema: VERIFY_SCHEMA, label:'verify', phase:'Verify', ...tier('verify') })

const next = BUILD
  ? `Browser pass per built day (AGENTS.md): python harness/practice_browser.py ${A.week} <day> for ${report.filter(r => r.status === 'done').map(r => r.day).join(', ') || 'no day (all flagged)'}; then the STATUS.md log.`
  : `Put the proposals in front of the trainer: python harness/practice_tasks.py show ${A.week}; record each day's answer with practice_tasks.py approve; then python harness/args_for.py ${A.week} --practice-build.`
log(`Practice ${A.mode} complete: ${DAYS.length} day(s), ${flagged.length} flagged, tests ${verify && verify.passed ? 'PASS' : 'FAIL'}; run log ${recorded ? 'recorded' : 'NOT recorded'} (add the run id with: python harness/log_run.py amend --last --run-id <wf_...>). Next: ${next}`)
return { mode: A.mode, week: A.week, days: DAYS.map(d => d.id), flaggedCount: flagged.length, flagged, report, verify, recorded, next }
