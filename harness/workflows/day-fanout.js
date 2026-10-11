// day-fanout.js — produce one training day's full artifact set, critic-gated.
//
// Run (one day per invocation; two or three days pipeline fine but mind the agent budget):
//   python harness/args_for.py <week> <day...> --today YYYY-MM-DD   -> paste as args
//   Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: <that JSON> })
//
// Pipeline per day:  Research (gate-tiered) -> Demos -> Materials (notes ∥ runbook ∥ exercise)
// then, once every day is through:  Wire (serial, shared files) -> Verify (unittest, ≤2 fix loops).
// Every artifact is produced by an author agent and judged by a DIFFERENT critic agent
// reading harness/critics/<artifact>.md; up to 3 passes, then the item is flagged (never blocks).
//
// Scripts cannot touch the filesystem or Date(); everything comes in through args.
// Lifted from the reference week-fanout.js: gated(), fix(), VERDICT, repairNulls(), compact(), salvage.

export const meta = {
  name: 'day-fanout',
  description: 'Research -> demos -> notes/runbook/exercise (critic-gated, 3-pass repass) -> wire -> verify, for one training day',
  phases: [
    { title: 'Research' },
    { title: 'Demos' },
    { title: 'Materials' },
    { title: 'Wire' },
    { title: 'Verify' },
  ],
}

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
if (!A.root || !A.today || !Array.isArray(A.days) || !A.days.length) throw new Error('args must come from harness/args_for.py (root, today, days[] required)')
if (A.days.some(d => !d.date || !d.dateLabel || d.kind === 'holiday')) throw new Error('every day needs date/dateLabel from args_for.py and must not be a holiday slot')
const ROOT = A.root
const H = `${ROOT}/harness`
const TRAINER = `${ROOT}/trainer`
const M = A.metrics || {}
const MN = M.notes || {}
const WORD_MIN = A.wordMin || MN.wordMin || 1200
const WORD_MAX = A.wordMax || MN.wordMax || 1800
const TEMPLATE = A.template || `${H}/templates/day.exemplar.html`
const CFG = A.config || {}
const LLM = A.llm || {}
const DAYS = A.days.map(d => ({
  ...d,
  researchFile: `${H}/research/${d.rel}.md`,
  demoDir: `${ROOT}/demos/${d.rel}`,
  exDir: `${ROOT}/exercises/${d.rel}`,
  trDir: `${TRAINER}/${d.rel}`,
  pageFile: `${ROOT}/docs/weeks/${d.rel}.html`,
  pageRel: `docs/weeks/${d.rel}.html`,
}))

// ---------- schemas ----------
const VERDICT = { type:'object', additionalProperties:false, properties:{ pass:{type:'boolean'}, critiques:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['pass','critiques','summary'] }
const RESEARCH_SCHEMA = { type:'object', additionalProperties:false, properties:{
  versionStamps:{ type:'array', items:{ type:'object', additionalProperties:false, properties:{ lib:{type:'string'}, version:{type:'string'} }, required:['lib','version'] } },
  sourceCount:{type:'number'},
  glossaryTerms:{ type:'array', items:{ type:'object', additionalProperties:false, properties:{ term:{type:'string'}, def:{type:'string'}, aka:{type:'array', items:{type:'string'}} }, required:['term','def','aka'] } },
  pitfalls:{ type:'array', items:{type:'string'} },
  summary:{type:'string'} }, required:['versionStamps','sourceCount','glossaryTerms','pitfalls','summary'] }
const DEMO_SCHEMA = { type:'object', additionalProperties:false, properties:{
  files:{ type:'array', items:{ type:'object', additionalProperties:false, properties:{ name:{type:'string'}, shows:{type:'string'}, runnable:{type:'boolean'}, needsKey:{type:'boolean'} }, required:['name','shows','runnable','needsKey'] } },
  requirements:{ type:'array', items:{type:'string'} },
  summary:{type:'string'} }, required:['files','requirements','summary'] }
const NOTES_SCHEMA = { type:'object', additionalProperties:false, properties:{
  wordCount:{type:'number'}, declaredMinutes:{type:'number'}, steps:{type:'number'}, quizCount:{type:'number'},
  demoLinks:{ type:'array', items:{type:'string'} }, codePopups:{ type:'array', items:{type:'string'} }, summary:{type:'string'} },
  required:['wordCount','declaredMinutes','steps','quizCount','demoLinks','codePopups','summary'] }
const RUNBOOK_SCHEMA = { type:'object', additionalProperties:false, properties:{
  totalMinutes:{type:'number'}, demoSections:{type:'number'}, solutionFiles:{ type:'array', items:{type:'string'} }, summary:{type:'string'} },
  required:['totalMinutes','demoSections','solutionFiles','summary'] }
const EXERCISE_SCHEMA = { type:'object', additionalProperties:false, properties:{
  module:{type:'string'}, testCount:{type:'number'}, starterFailed:{type:'boolean'}, solutionPassed:{type:'boolean'}, summary:{type:'string'} },
  required:['module','testCount','starterFailed','solutionPassed','summary'] }
const VERIFY_SCHEMA = { type:'object', additionalProperties:false, properties:{ passed:{type:'boolean'}, failures:{ type:'array', items:{type:'string'} }, summary:{type:'string'} }, required:['passed','failures','summary'] }

// ---------- helpers ----------
async function gated(label, gen, crit) {
  let result = await gen(null)
  for (let pass = 1; pass <= 3; pass++) {
    const v = await crit(result, pass)
    if (v && v.pass) return { task: label, status:'done', passes: pass, summary: (v.summary || (result && result.summary) || ''), result }
    if (pass === 3) return { task: label, status:'flagged', passes: 3, flags: (v ? v.critiques : ['critic returned null']), summary: (result && result.summary) || (v && v.summary) || '', result }
    result = await gen(v ? v.critiques : ['prior critic hard-failed (returned null) — regenerate from scratch, full quality bar'])
  }
}
const fix = (cr) => cr && cr.length ? ('\n\nThis is a REPASS. A critic flagged these issues — fix every one, keep what was good:\n- ' + cr.join('\n- ')) : ''
const repairNull = (x, label) => x || ({ task: label, status:'flagged', passes:0, flags:['agent hard-failed (structured return / terminal error)'], summary:'hard-fail — regenerate' })
const compact = (x) => x ? ({ task:x.task, status:x.status, passes:x.passes, ...(x.flags ? {flags:x.flags} : {}), summary:x.summary }) : null
const J = (x) => JSON.stringify(x, null, 1)

const dayHeader = (d) =>
  `DAY: ${d.id} — "${d.title}" (${d.subtitle}). Week ${A.week} "${A.theme}", day ${d.day} = ${d.weekday}, kind=${d.kind}, gate=${d.gate}, demoFormat=${d.demoFormat}, feedbackForm=${d.feedback}.\n` +
  `Calendar date of this training day: ${d.dateLabel} (${d.date}, ${A.timezone}); week ${A.week} runs ${A.weekStart} to ${A.weekEnd}. Use this date wherever the day is dated; never invent one.\n` +
  `Subtopics (teach in this order, nothing from later days): ${J(d.subtopics)}\n` +
  (A.weekNotes ? `Week note: ${A.weekNotes}\n` : '') +
  `Today's date for stamps: ${A.today}. Python ${CFG.python}. LLM config for this week: ${J(LLM)}.\n` +
  `Root: ${ROOT}. Metrics: ${J(M)}.\n`

// =====================================================================
// Per-day stages (run as one sequential chain per day; days run in parallel)
// =====================================================================
async function researchStage(d) {
  const full = d.gate === 'full'
  return gated(`${d.id} research`,
    (cr) => agent(
      `You are the RESEARCH agent. ${dayHeader(d)}` +
      `Write the research brief to ${d.researchFile} following the template ${H}/templates/research.md exactly (headings and line formats).\n` +
      (full
        ? `FULL GATE: load WebSearch + WebFetch (ToolSearch: select:WebSearch,WebFetch). Prefer official/primary docs. VERIFY every URL with WebFetch before citing it; every claim carries [title](url). Resolve library versions AND any LLM model id from the provider's current docs — never from memory. Flag deprecated APIs explicitly.\n`
        : `LIGHT GATE: no web fetching required. Cite ≥3 official doc URLs you are confident exist (docs.python.org, git-scm.com, dev.mysql.com, cloud.google.com, tensorflow.org, scikit-learn.org, pandas.pydata.org ...). Stamp known-stable major versions.\n`) +
      `Glossary terms: 3–8, each "- term | one sentence | aka: a, b"; first read ${ROOT}/docs/assets/js/glossary.js and do NOT repeat an existing term or aka.\n` +
      `Pitfalls 3–6 (what learners actually get wrong). Demo plan hints 2–4 (what must be shown live).\n` +
      `Return versionStamps, sourceCount, glossaryTerms (aka may be empty array), pitfalls, 2-sentence summary.` + fix(cr),
      { schema: RESEARCH_SCHEMA, label:`${d.id}:research`, phase:'Research' }),
    (_r) => agent(
      `RESEARCH CRITIC. Read ${H}/critics/research.md and apply it to ${d.researchFile}. Gate=${d.gate}. Also read ${ROOT}/docs/assets/js/glossary.js to check glossary collisions. ${full ? 'Load WebFetch (ToolSearch: select:WebFetch) and spot-check ≥3 URLs.' : 'No WebFetch needed.'}\n` +
      `Day context: ${dayHeader(d)}` +
      `Return pass, critiques (specific fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:research-crit`, phase:'Research' }))
}

async function demosStage(d) {
  return gated(`${d.id} demos`,
    (cr) => agent(
      `You are the DEMO author. ${dayHeader(d)}` +
      `Read the research brief ${d.researchFile} — your only source of facts and version/API shapes. Read ${H}/templates/demo-README.md.\n` +
      `Write ${d.demoDir}/: README.md (title, prerequisites, run-order table file|shows|run|needs key?, STEP explanation), ${M.demos.filesMin}–${M.demos.filesMax} code files named NN_<slug>.${d.demoFormat === 'nb' ? 'ipynb (notebooks for exploratory parts; .py allowed for setup)' : 'py'} in teaching order.\n` +
      `Each .py: ≤${M.demos.maxLinesPerFile} lines; top docstring with PURPOSE and EXPECTED OUTPUT; ≥2 "# --- STEP n: <what to type next> ---" markers in order; runnable with "python <file>" from the demo dir. Each .ipynb: nbformat v4, markdown cell before each STEP, outputs cleared.\n` +
      `Anything needing a key: guard with an env check that prints a clear message and exits 0 when absent; add .env.example (names only). requirements.txt only if non-stdlib, pinned to the brief's stamps.\n` +
      `LLM calls (if this day has any) use exactly ${J(LLM)}; model id from the brief. No secrets. Use Bash to run every key-free script and confirm its output matches its docstring before returning.\n` +
      `Return files[] (name, shows, runnable, needsKey), requirements[], summary.` + fix(cr),
      { schema: DEMO_SCHEMA, label:`${d.id}:demos`, phase:'Demos' }),
    (_r) => agent(
      `DEMOS CRITIC. Read ${H}/critics/demos.md and apply it to ${d.demoDir}/ against the brief ${d.researchFile}. Use Bash: py_compile every .py, nbformat.validate every .ipynb, RUN every key-free script (60 s timeout) and compare to its docstring, run key-gated scripts without the key. Day context: ${dayHeader(d)}` +
      `Return pass, critiques (file + concrete fix), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:demos-crit`, phase:'Demos' }))
}

async function materialsStage(d, demo) {
  const files = (demo && demo.result && demo.result.files) ? demo.result.files : []
  const fileNames = files.map(f => f.name)
  const demoUrl = `${CFG.repoUrl}/tree/${CFG.repoBranch || 'main'}/demos/${d.rel}`
  const exUrl = `${CFG.repoUrl}/tree/${CFG.repoBranch || 'main'}/exercises/${d.rel}`
  const notes = () => gated(`${d.id} notes page`,
    (cr) => agent(
      `You are the NOTES-PAGE author. ${dayHeader(d)}` +
      `Read (1) ${TEMPLATE} — copy its FULL structure (head+meta tc-day, topbar, nav.toc, article.reading-col with .lede + section.step blocks + section.reading-sources, aside.side with diagram + .demo-card + quiz card + side-nav, #quiz-modal, #goals-modal, optional #deep-modal, 0–2 #code-* popups, inline window.NEXT/DIAGRAM/QUIZ, the exact script tags). (2) ${d.researchFile} — your ONLY source of facts. (3) ${d.demoDir}/README.md and the demo files ${J(fileNames)}.\n` +
      `Write ${d.pageFile}:\n` +
      `- <meta name="tc-day" content="${d.id}">; title "<title> | ${CFG.siteTitle}"; topbar brand "${(CFG.brand||{}).bold}·${(CFG.brand||{}).rest}", Home ../../index.html, Demos ${CFG.repoUrl}/tree/main/demos, Exercises ${CFG.repoUrl}/tree/main/exercises.\n` +
      `- .lede meta: "Week ${A.week} · Day ${d.day}", "${d.dateLabel}", "${A.theme}", "~N min" where N = round(prose words / ${MN.readingWpm || 150}).\n` +
      `- ${MN.stepsMin}–${MN.stepsMax} section.step (data-step 0..n-1), prose ${WORD_MIN}–${WORD_MAX} words total; the page is the reference that deepens what the demos show — name the demo files where the reader should go run them.\n` +
      `- .demo-card: "Code-along files" linking each demo file as ${demoUrl}/<file>.\n` +
      `- window.DIAGRAM with captions.length == step count, nodes {id,step,x,y,w,h,label,detail?}, edges referencing real ids; each step reveals something the section explains.\n` +
      `- window.QUIZ with exactly ${MN.quizQuestions} questions: ≥1 scq, ≥1 tf, ≥1 mcq or match, ≤1 open; every non-open question has explain; grounded in the brief and the demos.\n` +
      `- #goals-modal: ${MN.goalsMin}–${MN.goalsMax} "By the end of today you can" items; "Today's exercise" link ${exUrl}; "Demo files in order" list.\n` +
      `- Code popups: 0–2, each excerpting a REAL demo file (data-file = exact filename, code HTML-escaped).\n` +
      `- section.reading-sources with ≥${MN.sourcesMin} URLs from the brief.\n` +
      `- window.NEXT = { label: ${J(d.nextLabel)}, href: ${J(d.nextHref)} }.\n` +
      `- Scripts: theme.js in head; bottom exactly diagram, scrolly, modals, quiz, widgets, glossary, codeviewer${d.feedback ? ', survey (+ a #survey section with window.SURVEY and a link to ' + CFG.feedbackFormUrl + ')' : ''}; relative ../../assets/... paths. Widgets allowed: .ix-legend, .ix-predict, .ix-spot only.\n` +
      `- Count words with a Python one-liner before returning. Return wordCount, declaredMinutes, steps, quizCount, demoLinks, codePopups, summary.` + fix(cr),
      { schema: NOTES_SCHEMA, label:`${d.id}:notes`, phase:'Materials' }),
    (_r) => agent(
      `NOTES CRITIC. Read ${H}/critics/notes.md and apply it to ${d.pageFile} against ${d.researchFile} (allowed facts), ${TEMPLATE} (structure), demo files ${J(fileNames)} in ${d.demoDir}. Word band ${WORD_MIN}–${WORD_MAX}. Run the verification snippet in the critic spec with Bash. Day context: ${dayHeader(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:notes-crit`, phase:'Materials' }))

  const exercise = () => gated(`${d.id} exercise`,
    (cr) => agent(
      `You are the EXERCISE author. ${dayHeader(d)}` +
      `Read ${d.researchFile} and the demos in ${d.demoDir} (${J(fileNames)}). Read ${H}/templates/exercise-README.md and ${H}/templates/conftest.py.\n` +
      `Write ${d.exDir}/: README.md (task, acceptance checklist mapping 1:1 to test names, getting started, ≥2 hints; 60–90 min), starter/<module>.py (signatures + docstrings + raise NotImplementedError only), tests/conftest.py (copy the template verbatim), tests/test_<module>.py with ${M.exercise.testsMin}–${M.exercise.testsMax} deterministic, network-free tests.\n` +
      `ALSO write the reference solution to ${d.trDir}/solutions/<module>.py (private trainer repo path; create dirs).\n` +
      `Use Bash from ${d.exDir}: "python -m pytest -q" MUST fail; "EXERCISE_SRC=${d.trDir}/solutions python -m pytest -q" MUST pass. Confirm both before returning.\n` +
      `Return module, testCount, starterFailed, solutionPassed, summary.` + fix(cr),
      { schema: EXERCISE_SCHEMA, label:`${d.id}:exercise`, phase:'Materials' }),
    (_r) => agent(
      `EXERCISE CRITIC. Read ${H}/critics/exercise.md and apply it to ${d.exDir}/ with solutions at ${d.trDir}/solutions. Actually run both pytest invocations with Bash. Day context: ${dayHeader(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:exercise-crit`, phase:'Materials' }))

  const runbook = () => gated(`${d.id} runbook`,
    (cr) => agent(
      `You are the RUNBOOK author (trainer-only talk track). ${dayHeader(d)}` +
      `Read ${d.researchFile}, ${d.demoDir}/README.md and every demo file ${J(fileNames)}, ${d.pageFile} if it exists (for objectives), and the exercise README at ${d.exDir}/README.md if it exists. Read the template ${H}/templates/runbook.md.\n` +
      `Write ${d.trDir}/runbook.md: first line "# ${d.id} runbook — ${d.title}"; second line "Week ${A.week} · Day ${d.day} · ${d.dateLabel} · ${A.theme}"; headings in template order; "Day at a glance" table whose Minutes sum to ${M.runbook.dayMinutesMin}–${M.runbook.dayMinutesMax} incl. breaks/lunch; one "## Demo N: <exact filename>" per demo file with Goal, type-live/paste per STEP, numbered talk track, ≥2 checkpoint questions, expected output, ≥1 pitfall from the brief; Notes page handoff; Exercise briefing (module, acceptance, ≥2 stuck points, solutions path ${d.trDir}/solutions); Common questions; If running long / short${d.feedback ? '; "## Feedback form" with ' + CFG.feedbackFormUrl : ''}${d.kind === 'review' ? '; "## Review agenda"' : ''}.\n` +
      `Return totalMinutes, demoSections, solutionFiles (what exists under solutions/), summary.` + fix(cr),
      { schema: RUNBOOK_SCHEMA, label:`${d.id}:runbook`, phase:'Materials' }),
    (_r) => agent(
      `RUNBOOK CRITIC. Read ${H}/critics/runbook.md and apply it to ${d.trDir}/runbook.md with demos in ${d.demoDir}, exercise in ${d.exDir}, solutions in ${d.trDir}/solutions, brief ${d.researchFile}. Run the solutions pytest check with Bash. Day context: ${dayHeader(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:runbook-crit`, phase:'Materials' }))

  // notes + exercise first (runbook reads both for objectives / stuck points), then runbook
  const [n, e] = await parallel([notes, exercise])
  const r = await runbook()
  return { notes: n, exercise: e, runbook: r }
}

// =====================================================================
// Run
// =====================================================================
phase('Research')
const perDay = await parallel(DAYS.map(d => async () => {
  const research = await researchStage(d)
  const demos = await demosStage(d)
  const mats = await materialsStage(d, demos)
  return { d, research, demos, ...mats }
}))

// ---------- WIRE (serial: shared files) ----------
phase('Wire')
const glossaryAdds = []
perDay.forEach(x => { if (x && x.research && x.research.result) (x.research.result.glossaryTerms || []).forEach(t => glossaryAdds.push({ day: x.d.id, ...t })) })
const wire = await agent(
  `WIRE step (serial, shared files). Days shipped this run: ${J(DAYS.map(d => ({ id:d.id, rel:d.rel, page:d.pageRel })))}.\n` +
  `1. Open ${ROOT}/docs/assets/js/glossary.js. Between "// GLOSSARY:BEGIN" and "// GLOSSARY:END" append these entries as { term, def, aka } lines, SKIPPING any whose term or aka already exists (case-insensitive, check both term and aka of existing entries): ${J(glossaryAdds)}. Keep the file valid JS (node --check).\n` +
  `2. In ${H}/curriculum.json set "status": "live" for ${J(DAYS.map(d => d.id))} ONLY if that day's page ${'`'}docs/weeks/<rel>.html${'`'}, demos/<rel>/README.md and exercises/<rel>/README.md all exist on disk.\n` +
  `3. Run: python ${H}/build_index.py\n` +
  `4. For each shipped day whose previous day page exists, confirm the previous page's window.NEXT.href points at this day's filename; fix if not.\n` +
  `5. Run ${ROOT}/docs/bump-css.sh --all if you changed glossary.js.\n` +
  `Return a one-paragraph summary of what changed.`,
  { label:'wire', phase:'Wire' })

// ---------- VERIFY ----------
phase('Verify')
let verify = null
for (let attempt = 1; attempt <= 3; attempt++) {
  verify = await agent(
    `VERIFY step. From ${ROOT} run: python -m unittest discover -s tests -v   (and python ${H}/build_index.py --check). Report passed=true only if everything passes. List each failure as "<test>: <one-line cause>".`,
    { schema: VERIFY_SCHEMA, label:`verify:${attempt}`, phase:'Verify' })
  if (!verify || verify.passed || attempt === 3) break
  await agent(
    `FIX step (attempt ${attempt}). These contract tests failed: ${J(verify.failures)}. Fix the underlying artifact(s) for days ${J(DAYS.map(d => d.rel))} — never weaken the tests or metrics. Re-run the failing tests with Bash until they pass. Return a short summary.`,
    { label:`fix:${attempt}`, phase:'Verify' })
}

// ---------- report ----------
const report = perDay.map((x, i) => {
  const d = DAYS[i]
  return {
    day: d.id,
    research: compact(repairNull(x && x.research, `${d.id} research`)),
    demos: compact(repairNull(x && x.demos, `${d.id} demos`)),
    notes: compact(repairNull(x && x.notes, `${d.id} notes page`)),
    exercise: compact(repairNull(x && x.exercise, `${d.id} exercise`)),
    runbook: compact(repairNull(x && x.runbook, `${d.id} runbook`)),
  }
})
const flagged = []
report.forEach(r => ['research','demos','notes','exercise','runbook'].forEach(k => { if (r[k] && r[k].status === 'flagged') flagged.push({ day:r.day, artifact:k, flags:r[k].flags }) }))
log(`Run complete: ${DAYS.length} day(s), ${flagged.length} flagged item(s), tests ${verify && verify.passed ? 'PASS' : 'FAIL'}`)
return { week: A.week, days: DAYS.map(d => d.id), flaggedCount: flagged.length, flagged, verify, wire, report, glossaryAdded: glossaryAdds.length }
