// day-fanout.js — produce the full artifact set of one training day, or of several days of one week as a
// batch (D-0038), critic-gated.
//
// Run (the days of one week in one invocation is the normal case; a single day stays valid; ~24 agents per day):
//   python harness/args_for.py <week> <day...> --today YYYY-MM-DD   -> paste as args
//   Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: <that JSON> })
//
// Pipeline:  Research (gate-tiered, all days in parallel) -> Demos (one day after the other, in day order:
// each rung starts from the previous rung's key, D-0033) -> Materials (notes ∥ runbook ∥ exercise, all days
// in parallel) -> Wire (serial, shared files) -> Record (run log + work tracker, D-0035)
// -> Verify (unittest, ≤2 fix loops).
// Demos (D-0030): walkthrough scripts + answer keys are authored to trainer/<rel>/demos/ (private) and
// published to demos/<rel>/ by harness/publish_demos.py only once curriculum.json carries taught:<date>.
// A demoFormat "none" day skips the Demos stage; its runbook carries facilitation scripts instead.
// Every artifact is produced by an author agent and judged by a DIFFERENT critic agent
// reading harness/critics/<artifact>.md; up to 3 passes, then the item is flagged (never blocks).
// A humanizer agent runs between author and critic on the notes page (D-0029) and on the trainer's delivery
// wording, the demo scripts and the runbook (D-0039; prose only, guarded by harness/prose_guard.py).
// Notes pages (D-0040) are reference/study material at junior-interview depth: a notes-verify agent runs
// harness/notes_check.py (structure, delivery phrases, stamps, citations, link liveness; WebFetch claim currency
// on full-gate and currency-flagged days) and its findings bind the notes critic.
// Notes-only mode (args_for.py --notes-only, D-0040): Research = a depth pass that extends the committed brief's
// "## Notes depth" section; Demos = the scripts and keys already on disk; Materials = the notes page only
// (exercise and runbook untouched); Wire realigns the week plan's Notes-step column from what was built.
//
// Scripts cannot touch the filesystem or Date(); everything comes in through args.
// Lifted from the reference week-fanout.js: gated(), fix(), VERDICT, repairNulls(), compact(), salvage.

export const meta = {
  name: 'day-fanout',
  description: 'Research -> demos (in day order) -> notes/runbook/exercise (critic-gated, 3-pass repass) -> wire -> verify, for one training day or the days of one week; --notes-only re-authors the notes pages alone (research depth, then notes)',
  phases: [
    { title: 'Research' },
    { title: 'Demos' },
    { title: 'Materials' },
    { title: 'Wire' },
    { title: 'Record' },
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
// Per-stage model/effort tiers (D-0026). Comes from config.json "models" via args_for.py.
// tier(stage, pass): the stage's {model, effort}; on a repass numbered >= escalateOn, the
// escalate tier instead (so a cheap first pass that fails its critic retries on the strong tier).
// A null model/effort is omitted, which means "inherit the session default".
const TIERS = A.models || {}
// Every agent() call spreads tier() exactly once, so counting the calls counts the agents (run record, D-0035).
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
const TIER_LABELS = ['research-light','research-full','demos','notes','notes-critic','notes-verify-light','notes-verify-full','humanize','exercise','runbook','critic','wire','verify','fix'].map(tierLabel).join(' · ')
const NOTES_ONLY = !!A.notesOnly
const DAYS = A.days.map(d => ({
  ...d,
  researchFile: `${H}/research/${d.rel}.md`,
  demoDir: `${TRAINER}/${d.rel}/demos`,          // scripts (NN_<slug>.md) + key/ (answer keys): private until taught
  keyDir: `${TRAINER}/${d.rel}/demos/key`,
  pubDemoDir: `${ROOT}/demos/${d.rel}`,           // written only by harness/publish_demos.py
  noDemos: d.demoFormat === 'none',
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
  scripts:{ type:'array', items:{ type:'object', additionalProperties:false, properties:{ name:{type:'string'}, key:{type:'string'}, objective:{type:'string'}, minutes:{type:'number'}, mode:{type:'string'}, needsKey:{type:'boolean'} }, required:['name','key','objective','minutes','mode','needsKey'] } },
  facilitation:{ type:'array', items:{type:'string'} },
  requirements:{ type:'array', items:{type:'string'} },
  summary:{type:'string'} }, required:['scripts','facilitation','requirements','summary'] }
const NOTES_SCHEMA = { type:'object', additionalProperties:false, properties:{
  wordCount:{type:'number'}, declaredMinutes:{type:'number'}, steps:{type:'number'}, quizCount:{type:'number'},
  h3Count:{type:'number'}, interviewCount:{type:'number'}, checkYourselfCount:{type:'number'}, codeBlocks:{type:'number'}, citations:{type:'number'},
  sourcesChecked:{type:'string'},
  stepMap:{ type:'array', items:{ type:'object', additionalProperties:false, properties:{ subtopic:{type:'string'}, step:{type:'number'} }, required:['subtopic','step'] } },
  demoLinks:{ type:'array', items:{type:'string'} }, codePopups:{ type:'array', items:{type:'string'} }, summary:{type:'string'} },
  required:['wordCount','declaredMinutes','steps','quizCount','h3Count','interviewCount','checkYourselfCount','codeBlocks','citations','sourcesChecked','stepMap','demoLinks','codePopups','summary'] }
// notes-verify (D-0040): mechanical findings that bind the notes critic. structural = notes_check.py findings
// about parsing or the bands; dead = links that do not answer; stale = currency, stamp and citation findings.
const VERIFY_NOTES_SCHEMA = { type:'object', additionalProperties:false, properties:{
  checked:{type:'number'}, structural:{ type:'array', items:{type:'string'} }, dead:{ type:'array', items:{type:'string'} }, stale:{ type:'array', items:{type:'string'} }, summary:{type:'string'} },
  required:['checked','structural','dead','stale','summary'] }
const RUNBOOK_SCHEMA = { type:'object', additionalProperties:false, properties:{
  totalMinutes:{type:'number'}, demoSections:{type:'number'}, solutionFiles:{ type:'array', items:{type:'string'} }, summary:{type:'string'} },
  required:['totalMinutes','demoSections','solutionFiles','summary'] }
const EXERCISE_SCHEMA = { type:'object', additionalProperties:false, properties:{
  module:{type:'string'}, testCount:{type:'number'}, starterFailed:{type:'boolean'}, solutionPassed:{type:'boolean'}, summary:{type:'string'} },
  required:['module','testCount','starterFailed','solutionPassed','summary'] }
const VERIFY_SCHEMA = { type:'object', additionalProperties:false, properties:{ passed:{type:'boolean'}, failures:{ type:'array', items:{type:'string'} }, summary:{type:'string'} }, required:['passed','failures','summary'] }

// ---------- helpers ----------
async function gated(label, gen, crit) {
  let result = await gen(null, 1)
  for (let pass = 1; pass <= 3; pass++) {
    const v = await crit(result, pass)
    if (v && v.pass) return { task: label, status:'done', passes: pass, summary: (v.summary || (result && result.summary) || ''), result }
    if (pass === 3) return { task: label, status:'flagged', passes: 3, flags: (v ? v.critiques : ['critic returned null']), summary: (result && result.summary) || (v && v.summary) || '', result }
    result = await gen(v ? v.critiques : ['prior critic hard-failed (returned null) — regenerate from scratch, full quality bar'], pass + 1)
  }
}
const fix = (cr) => cr && cr.length ? ('\n\nThis is a REPASS. A critic flagged these issues — fix every one, keep what was good:\n- ' + cr.join('\n- ')) : ''
const repairNull = (x, label) => x || ({ task: label, status:'flagged', passes:0, flags:['agent hard-failed (structured return / terminal error)'], summary:'hard-fail — regenerate' })
const compact = (x) => x ? ({ task:x.task, status:x.status, passes:x.passes, ...(x.flags ? {flags:x.flags} : {}), summary:x.summary }) : null
const J = (x) => JSON.stringify(x, null, 1)

// Week plan rows (D-0034): args_for.py gates on harness/plans/week-WW.md and passes each day's coverage rows,
// thread rows (rungs with startsFrom), ladder rows and day shape. --no-plan is the logged escape.
const planCtx = (d) => A.noPlan
  ? `WEEK PLAN: NONE (the --no-plan escape was used; STATUS.md records it). No thread rows: every demo is standalone and starts cold.\n`
  : `WEEK PLAN (binding): ${A.weekPlan}. Coverage rows for this day (subtopic -> demo | facilitation | notes -> notes step): ${J(d.weekPlanRows || [])}\n` +
    `Thread rows for this day (each demo to author, in this order; thread "standalone" starts cold; a rung EXTENDS its startsFrom key, D-0033): ${J(d.threadRows || [])}\n` +
    `Ladder rows (minutes, must-follow, guarantees): ${J(d.ladderRows || [])}\n` +
    (d.dayShape ? `Day shape from the plan (AM/PM blocks, stop points, cut first / never cut):\n${d.dayShape}\n` : '') +
    (d.spoilerRows && d.spoilerRows.length ? `Anti-spoiler rows touching this day: ${J(d.spoilerRows)}\n` : '')
const dayHeader = (d) =>
  `DAY: ${d.id} — "${d.title}" (${d.subtitle}). Week ${A.week} "${A.theme}", day ${d.day} = ${d.weekday}, kind=${d.kind}, gate=${d.gate}, demoFormat=${d.demoFormat}, feedbackForm=${d.feedback}.\n` +
  `Calendar date of this training day: ${d.dateLabel} (${d.date}, ${A.timezone}); week ${A.week} runs ${A.weekStart} to ${A.weekEnd}. Use this date wherever the day is dated; never invent one.\n` +
  `Subtopics (teach in this order, nothing from later days): ${J(d.subtopics)}\n` +
  (A.weekNotes ? `Week note: ${A.weekNotes}\n` : '') +
  (d.notes ? `Day note: ${d.notes}\n` : '') +
  planCtx(d) +
  (CFG.audience ? `Audience: ${CFG.audience.summary} Assume already known: ${(CFG.audience.assumeKnown || []).join('; ')}. Emphasise: ${(CFG.audience.emphasise || []).join('; ')}.\n` : '') +
  `Exercise kind: ${d.exerciseKind || 'pytest'}.\n` +
  `Today's date for stamps: ${A.today}. Python ${CFG.python}. LLM config for this week: ${J(LLM)}.\n` +
  `Root: ${ROOT}. Metrics: ${J(M)}.\n`
// Learner repo convention (D-0037): config.json learnerRepo via args_for.py. Goes to the exercise and runbook
// authors and critics only; research, demo and notes prompts never see it, and the trainer's demo-thread repo
// keeps its own name.
const LR = CFG.learnerRepo
const learnerCtx = (d) => !LR ? '' :
  `LEARNER REPO (D-0037, binding): every trainee has ONE ${LR.visibility} GitHub repository ${LR.org}/<${LR.name}> (${LR.nameRule}), created in the ${LR.createdIn} Git exercise and kept for the whole course. ` +
  (d.id === LR.createdIn
    ? `THIS day's exercise is the one that creates it: the deliverable is the repository itself, owned by the organisation ${LR.org} (not a personal account), and ${LR.layout.root}. `
    : `Trainees do this day's exercise in the folder ${d.rel}/ of that repository (${LR.layout.exercises}) and hand it in there: ${LR.handIn}. Never ask for a new repository, a personal-account repository or a public one. `) +
  `Code-along copies of the demos go in ${LR.layout.codeAlong}; ${LR.layout.scratch}. ` +
  `The trainer's demo repository named in the demo scripts is a different repository and keeps its name; write "<${LR.name}>" as the placeholder for the trainee's own repository.\n`

// =====================================================================
// Per-day stages (run as one sequential chain per day; days run in parallel)
// =====================================================================
async function researchStage(d) {
  // args_for.py --skip-research: the committed brief is reused as-is (it checked the file exists); glossary
  // terms were wired when that brief was first produced, so none are added again.
  if (A.skipResearch) return { task: `${d.id} research`, status:'cached', passes:0, summary:`reused the committed brief ${d.researchFile}`, result:{ versionStamps:[], sourceCount:0, glossaryTerms:[], pitfalls:[], summary:'' } }
  const full = d.gate === 'full'
  return gated(`${d.id} research`,
    (cr, pass) => agent(
      `You are the RESEARCH agent. ${dayHeader(d)}` +
      `Write the research brief to ${d.researchFile} following the template ${H}/templates/research.md exactly (headings and line formats).\n` +
      (full
        ? `FULL GATE: load WebSearch + WebFetch (ToolSearch: select:WebSearch,WebFetch). Prefer official/primary docs. VERIFY every URL with WebFetch before citing it; every claim carries [title](url). Resolve library versions AND any LLM model id from the provider's current docs — never from memory. Flag deprecated APIs explicitly.\n`
        : `LIGHT GATE: no web fetching required. Cite ≥3 official doc URLs you are confident exist (docs.python.org, git-scm.com, dev.mysql.com, cloud.google.com, tensorflow.org, scikit-learn.org, pandas.pydata.org ...). Stamp known-stable major versions.\n`) +
      `Glossary terms: 3–8, each "- term | one sentence | aka: a, b"; first read ${ROOT}/docs/assets/js/glossary.js and do NOT repeat an existing term or aka.\n` +
      `Pitfalls 3–6 (what learners actually get wrong). Demo plan hints 2–4 (what must be shown live).\n` +
      `Return versionStamps, sourceCount, glossaryTerms (aka may be empty array), pitfalls, 2-sentence summary.` + fix(cr),
      { schema: RESEARCH_SCHEMA, label:`${d.id}:research`, phase:'Research', ...tier(full ? 'research-full' : 'research-light', pass) }),
    (_r) => agent(
      `RESEARCH CRITIC. Read ${H}/critics/research.md and apply it to ${d.researchFile}. Gate=${d.gate}. Also read ${ROOT}/docs/assets/js/glossary.js to check glossary collisions. ${full ? 'Load WebFetch (ToolSearch: select:WebFetch) and spot-check ≥3 URLs.' : 'No WebFetch needed.'} Item 7 against the week plan rows below: the brief covers exactly this day's coverage rows and its demo plan hints name the plan's demos for this day, nothing the anti-spoiler rows defer.\n` +
      `Day context: ${dayHeader(d)}` +
      `Return pass, critiques (specific fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:research-crit`, phase:'Research', ...tier('critic') }))
}

async function demosStage(d) {
  if (d.noDemos) return { task: `${d.id} demos`, status:'skipped', passes:0, summary:'demoFormat none: no code demo; the runbook carries a facilitation script per subtopic', result:{ scripts:[], facilitation: d.subtopics, requirements:[], summary:'' } }
  return gated(`${d.id} demos`,
    (cr, pass) => agent(
      `You are the DEMO author (D-0030: a demo IS the walkthrough script the trainer types in front of the room; the committed code is the answer key). ${dayHeader(d)}` +
      `Read the research brief ${d.researchFile} — your only source of facts and version/API shapes. Read ${H}/templates/demo-script.md (script format, every rule in its comments) and ${H}/templates/demo-README.md. Read ${H}/critics/demos.md so you know what the critic runs.\n` +
      (A.noPlan
        ? `FIRST sort the day's subtopics by the CONSULT-vs-WRITE test: a subtopic whose objective is fluency (the room must become able to type it: code, commands, git, SDK calls) gets a script with Delivery mode "typed"; reference material learners will look up later may be "lecture-over-file" (rare); a concept subtopic (SDLC, Scrum, story points, MLOps concepts, professionalism) gets NO script — list it under facilitation[] and the runbook author writes a timed facilitation block for it. Respect the Day note's limits (e.g. "at most one demo on the on-ramp"). Every script is Thread: standalone, Starts from: cold.\n`
        : `The WEEK PLAN decides the demos: author EXACTLY the thread rows above, in that order, with those NN_<slug> names, keys and minutes (ladder rows); the coverage rows say which subtopic each demo teaches and which subtopics are facilitation (list those under facilitation[] for the runbook author) or notes-only. For every rung whose startsFrom is a key path: READ that key FIRST (it is the thread's end state before this rung), set the header bullets "- Thread: <thread>" and "- Starts from: <that exact path>", type ONLY what the row's "adds" says on top of it, show any carried line you remove or rewrite in a \`\`\`python replaced block, and make the .py key the WHOLE end state (carried lines + typed lines, ≤${M.demos.maxLinesPerThreadKey} lines); the rung ends in a commit with the row's commitMessage (a \`\`\`bash block with git add/commit in the last step; in a transcript, the "$ " sequence continues the previous transcript's repo). A rung whose startsFrom is a transcript creates its file from the first line inside the repository that transcript left. Never re-type a function, class, file, git init, install or config an earlier rung built (critic item 13). Standalone rows start cold with "- Thread: standalone".\n`) +
      `Write ${d.demoDir}/ (private trainer repo; create dirs): ${M.demos.scriptsMin}–${M.demos.scriptsMax} scripts named NN_<slug>.md in teaching order, each ${M.demos.minutesPerScriptMin}–${M.demos.minutesPerScriptMax} min, with the eleven header bullets (incl. Thread and Starts from), "## Step n — title (M min)" headings (≥2, minutes summing to Time), a cwd: line in every step that has a code or command block, the exact code/commands in fenced blocks (\`\`\`python for code typed into a file, \`\`\`bash for terminal commands one per line without prompt characters, \`\`\`text for expected output), "Talking points while typing" per step, Common pitfalls (symptom + fix), What we did NOT cover (intentional), Wrap-up questions, Sequence pointer. At most ${M.demos.maxTypedLinesPerRung} typed lines per script. Every token introduced before first use (earlier rungs of the thread count as introduced); the first rung of a thread that uses a tool carries install + version + config commands proven by running them, later rungs do not repeat them; every tool-generated claim proven by running the tool.\n` +
      `Write ${d.keyDir}/: one answer key per script with the same NN and slug: key/NN_<slug>.${d.demoFormat === 'nb' ? 'ipynb (nbformat v4, outputs cleared, one markdown cell per step; .py allowed for setup)' : 'py'} (≤${M.demos.maxLinesPerFile} lines for a standalone demo, ≤${M.demos.maxLinesPerThreadKey} for a thread rung; runnable with "python <file>" from key/; its lines EXACTLY the union of the script's \`\`\`python blocks plus the lines carried from the Starts from key — no elisions, no stubs; a line typed then replaced in the same rung goes in a \`\`\`python transient block) OR key/NN_<slug>.md for a terminal demo (a transcript: \`\`\`console blocks whose "$ " lines are exactly the script's \`\`\`bash commands in order, followed by the real output you captured by running them). Plus key/README.md (run-order table file|shows|run|needs key? listing every key file; template demo-README.md), key/requirements.txt only if non-stdlib (pinned to the brief's stamps), key/.env.example only if a key is needed (names only; such keys guard with an env check that prints a clear message and exits 0 when absent).\n` +
      `LLM calls (if this day has any) use exactly ${J(LLM)}; model id from the brief. No secrets. Do NOT write anything under ${d.pubDemoDir} (published later by harness/publish_demos.py).\n` +
      `Before returning, with Bash: run "python ${H}/demo_check.py ${d.demoDir}" until it prints OK; run every .py key from key/ and confirm the output matches the script's Check blocks; replay every transcript's commands in a scratch folder and confirm the output.\n` +
      `Wording (D-0039): the trainer says the talking points aloud while typing, so write sentences a person can say without rephrasing them (short, plain, one idea each; no chain of clauses joined by semicolons or colons); a contrast that corrects what the room really assumes is good spoken wording. "What we did NOT cover" bullets read "- <topic>: <where it goes>. <reason>." with no dash between topic and note. A humanizer pass runs after you (prose only); give it little to do.\n` +
      `Return scripts[] (name, key, objective, minutes, mode, needsKey), facilitation[] (subtopics with no script), requirements[], summary.` + fix(cr),
      { schema: DEMO_SCHEMA, label:`${d.id}:demos`, phase:'Demos', ...tier('demos', pass) })
      .then(async (r) => { if (r && (r.scripts || []).length) await humanizeTrainer(d, 'demos', r.scripts.map(s => `${d.demoDir}/${/\.md$/.test(s.name) ? s.name : s.name + '.md'}`), 'Demos'); return r }),
    (_r) => agent(
      `DEMOS CRITIC. Read ${H}/critics/demos.md and apply it to ${d.demoDir}/ (scripts + key/) against the brief ${d.researchFile}. Use Bash: run "python ${H}/demo_check.py ${d.demoDir}" and quote its output; RUN every .py key from key/ (60 s timeout) against the script's Check blocks; replay every transcript key's "$ " commands in a scratch folder in the rung's Starts from state; run key-gated keys without the key; nbformat.validate every .ipynb. Then walk every script as a learner (items 5–8), judge the CONSULT-vs-WRITE split (item 9), and check every rung against its thread row (item 13: Thread/Starts from match the row, only the row's "adds" is typed on top of the Starts from key, end state and commit message match; demo names and minutes match the ladder rows). Day context: ${dayHeader(d)}` +
      `Return pass, critiques (file + step + concrete fix), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:demos-crit`, phase:'Demos', ...tier('critic') }))
}

// Humanizer pass (D-0029): runs after the notes author and before the notes critic. Prose only, proven by
// harness/prose_guard.py in its html mode (D-0040): the tag skeleton, code, attributes, labels, citations and
// the non-prose script literals must be byte-identical afterwards.
const humanize = (d) => agent(
  `HUMANIZE pass for the notes page ${d.pageFile} (D-0029, D-0040). The page is long (${WORD_MIN}–${WORD_MAX} prose words), so work one section.step at a time.\n` +
  `1. FIRST, from ${ROOT}, run: python harness/prose_guard.py snapshot ${d.pageFile}   and keep the snapshot directory it prints.\n` +
  `2. Load the humanizer skill with the Skill tool ("humanizer:humanizer") and apply it in FILE MODE, one section.step per Edit call (never a whole-file Write). Rewrite prose text only: the .lede summary, paragraphs and list items inside article.reading-col, the interview callouts' <p>, the Check yourself answers' <p> and <summary> questions, the window.QUIZ stem/option/explain/hint/model strings, and the window.DIAGRAM captions and node detail strings. Reference voice: neutral, plain, technical, as a person explaining to a colleague. Light touch: leave a sentence that already reads plainly.\n` +
  `3. FROZEN, byte for byte: every HTML tag and attribute (ids, classes, hrefs, data-*), <pre>/<code> blocks, inline <code>, <sup class="cite"> markers, headings (h1–h3, title), the .tag / .k / .meta labels, filenames, URLs, numbers, versions, dates, quiz answer indices, pairs, types and question count, diagram labels, ids and edges, section.step count, window.NEXT, script tags. Do not add or remove a fact.\n` +
  `4. Verify from ${ROOT}: python harness/prose_guard.py check <snapshot directory> ${d.pageFile}   must print OK with no WARN line (a WARN means a number changed: restore it), and python harness/notes_check.py ${d.pageFile} --counts   must still show words >= ${WORD_MIN + 100} with unchanged steps, captions, h3, callouts, check, code and quiz counts; if a step lost more than 8% of its words, restore cut sentences rather than inventing new ones. Fix and re-run until both hold. Touch no other file.\n` +
  `Return one short paragraph: patterns found (by humanizer section number), sentences changed per step, final word count.`,
  { label:`${d.id}:notes-humanize`, phase:'Materials', ...tier('humanize') })

// Humanizer pass on the trainer's delivery wording (D-0039): the day's demo scripts after the demo author and the
// runbook after the runbook author, both before their critics. Prose only: harness/prose_guard.py compares every
// file with a snapshot taken before the pass, so the pass cannot change what a demo types or what a checker reads.
// kind is 'demos' (files = the day's NN_<slug>.md scripts) or 'runbook' (files = the runbook).
const humanizeTrainer = (d, kind, files, phaseName) => agent(
  `HUMANIZE pass on the trainer's delivery wording (D-0039) for ${d.id}: ${kind === 'demos' ? 'the demo scripts' : 'the runbook'}. Files, the ONLY ones you may change: ${J(files)}.\n` +
  `The trainer reads these files in front of the room and says the ${kind === 'demos' ? 'talking points aloud while typing' : 'questions, framing lines and answers aloud'}. Wording that sounds machine-written has to be reworded live, which is clunky. Make it read like a person's own speaking notes and change nothing a demo depends on.\n` +
  `1. FIRST, from ${ROOT}, run: python harness/prose_guard.py snapshot <the files>   and keep the snapshot directory it prints.\n` +
  `2. Load the humanizer skill with the Skill tool ("humanizer:humanizer") and apply it in FILE MODE to each file; read the whole file before editing it. Reference voice: a trainer's delivery notes, plain and technical. Lines said to the room are sentences a person can say without rephrasing them; instructions to the trainer stay short imperatives. Light touch: leave a sentence that already sounds spoken. The edits that usually help: split a run-on or a chain of clauses joined by semicolons or colons into short sentences, cut a stock phrase, give a clipped fragment its subject.\n` +
  `   Do NOT flatten good spoken wording: a contrast that corrects what the room really assumes ("review comments, not taste"; "conventions, not syntax from zero") stays, and so does a short line the trainer would say as it is. Add no joke, warmth, example or fact, and drop no fact. In a logistics sentence (a stop point, what moves where, what is pasted from which key, which commit waits) every fact survives in the same order; when unsure, leave the sentence.\n` +
  `3. FROZEN, byte for byte: every fenced block and the section it sits in; every inline code span (same spans, same count); every heading line; ` +
  (kind === 'demos'
    ? `everything above the first "## " heading (title, date line, the header bullets: a checker parses them and other files quote the Objective); every line starting with "cwd:"; the lines that introduce a block ("Talking points while typing:", "Check (expected output):"); the header row, the separator row and the number of rows of every table; `
    : `the title, the "Week ..." line and the "Notes page: ..." links line; every line starting with "|" (the "Day at a glance" table is read by a test); every bold label such as **Script:**, **Time:**, **Room state before:**, **Stop point if long:**, **Goal:** (the humanizer's rule about bold labels does not apply here: they are the template's structure); `) +
  `URLs, file names, paths, commit messages, branch names, numbers, minutes, dates and ids. One bullet in, one bullet out: never add, remove, merge, split or reorder bullets or numbered items, and never move text between sections.` +
  (kind === 'demos' ? ` The "What we did NOT cover" bullets keep the format "- <topic>: <where it goes>. <reason>." (demo_check.py checks it).` : '') + `\n` +
  `4. Verify from ${ROOT}: python harness/prose_guard.py check <snapshot directory> <the files>   must print OK or UNCHANGED for every file with no WARN line (a WARN means a number changed: restore it)` +
  (kind === 'demos' ? `, and python ${H}/demo_check.py ${d.demoDir}   must print OK` : '') +
  `. Fix and re-run until that holds. Use the Edit tool (no sed, no heredocs). Touch no other file, nothing under key/ or solutions/.\n` +
  `Return one short paragraph: sentences changed per file, humanizer sections found (by number), anything left alone on purpose.`,
  { label:`${d.id}:${kind}-humanize`, phase: phaseName, ...tier('humanize') })

// What the materials authors know about the day's demos (names, keys, objectives, facilitation subtopics).
function demoFacts(d, demo) {
  const scripts = (demo && demo.result && demo.result.scripts) ? demo.result.scripts : []
  const facilitation = (demo && demo.result && demo.result.facilitation) ? demo.result.facilitation : []
  const demoCtx = d.noDemos
    ? `This day has NO code demos (demoFormat none): every subtopic is facilitated from the runbook.\n`
    : `Demo scripts (private until taught, in ${d.demoDir}): ${J(scripts.map(s => ({ name:s.name, key:s.key, objective:s.objective, minutes:s.minutes })))}. Answer keys in ${d.keyDir}. Subtopics facilitated without a demo: ${J(facilitation)}.\n`
  return { scripts, scriptNames: scripts.map(s => s.name), keyNames: scripts.map(s => s.key), facilitation, demoCtx,
    demoUrl: `${CFG.repoUrl}/tree/${CFG.repoBranch || 'main'}/demos/${d.rel}`, exUrl: `${CFG.repoUrl}/tree/${CFG.repoBranch || 'main'}/exercises/${d.rel}` }
}

// Research depth (D-0040): in a notes-only run a research agent extends the committed brief with the
// "## Notes depth" section the notes author needs (interview questions, adjacent concept, trade-off,
// recognise-on-sight and sourced claims per subtopic). A normal run writes that section in the research stage.
async function researchDepthStage(d) {
  const full = d.gate === 'full'
  return gated(`${d.id} research-depth`,
    (cr, pass) => agent(
      `You are the RESEARCH agent, depth pass (D-0040). ${dayHeader(d)}` +
      `The brief ${d.researchFile} exists and is committed. Read it and ${H}/templates/research.md. Add (or replace, if present) its "## Notes depth" section EXACTLY as the template lays it out: one "### <subtopic>" block per subtopic listed above, spelled as the curriculum lists it, each with the five bullets (Interview questions: >=2 junior-level questions plus one follow-up a level beyond; Adjacent concept: the usual next question, never a later day's subtopic; Trade-off or limit, sourced; Recognise on sight: a snippet or pattern name; Claims: 3–6 testable statements, each "- <claim> — [title](url)"). It sits after "## Claims" and before "## Sources"; add every new URL to "## Sources" too. If "## Claims" has fewer than ${(M.research || {}).claimsMin || 12} claims, add sourced ones until it does. Change NOTHING else in the brief: header lines, version stamps, glossary, pitfalls and demo hints stay byte-identical.\n` +
      (full
        ? `FULL GATE: load WebFetch (ToolSearch: select:WebFetch). VERIFY every URL you add with WebFetch before citing it; versions and model ids from the provider's current docs, never from memory; name the current replacement of any deprecated API.\n`
        : `LIGHT GATE: no web fetching required. Cite only official doc URLs you are confident exist (docs.python.org, peps.python.org, git-scm.com, dev.mysql.com, cloud.google.com, tensorflow.org, scikit-learn.org, pandas.pydata.org, numpy.org, scrumguides.org ...).\n`) +
      `Return versionStamps (as in the header), sourceCount, glossaryTerms (empty array), pitfalls (empty array), 2-sentence summary.` + fix(cr),
      { schema: RESEARCH_SCHEMA, label:`${d.id}:research-depth`, phase:'Research', ...tier(full ? 'research-full' : 'research-light', pass) }),
    (_r) => agent(
      `RESEARCH CRITIC, depth pass (D-0040). Read ${H}/critics/research.md and apply items 1, 2, 3 and 7b${full ? ', 9 and 11' : ''} to ${d.researchFile}; the rest of the brief was judged when it was written. Gate=${d.gate}. ${full ? 'Load WebFetch (ToolSearch: select:WebFetch) and spot-check >=3 of the Notes depth URLs.' : 'No WebFetch needed.'} Run git diff on the brief and confirm nothing outside "## Claims", "## Notes depth" and "## Sources" changed.\n` +
      `Day context: ${dayHeader(d)}` +
      `Return pass, critiques (specific fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:research-depth-crit`, phase:'Research', ...tier('critic') }))
}

// notes-verify (D-0040): mechanical findings for the notes critic. Every day: harness/notes_check.py (structure,
// delivery phrases, stamps, citations, link liveness). Full-gate days and days whose week/day note carries a
// currency flag: WebFetch every cited claim about a version, model id, API name, default, limit or price.
const currencyDay = (d) => d.gate === 'full' || /currency|tflearn|pre-1\.0|deprecat|langchain|langgraph|bedrock|sagemaker|pinecone/i.test(`${A.weekNotes || ''} ${d.notes || ''}`)
const notesVerify = (d, pass) => agent(
  `NOTES VERIFY for ${d.pageFile} (D-0040). You produce mechanical findings for the critic and judge nothing else; you edit no file.\n` +
  `1. FIRST, from ${ROOT} run: python harness/notes_check.py ${d.pageFile} --counts --phrases --stamps --citations --links   and quote its last JSON line. Sort every finding line it prints: parsing, steps, captions, words, h3, callouts, Check yourself, code blocks, citations-per-step, quiz, minutes, sources or stamp-missing lines go into structural[]; "dead link" lines go into dead[] (URL and reason); "delivery phrase", "stamp", "citation target" and "source URL not in the brief" lines go into stale[].\n` +
  (currencyDay(d)
    ? `2. CURRENCY (this day is full-gate or its week/day note carries a currency flag): load WebFetch (ToolSearch: select:WebFetch). For EVERY citation on the page whose sentence states a version, a model id, an API/class/function/flag name's behaviour, a default, a limit or a price: fetch the cited URL (the li#src-N target) and confirm the doc supports the sentence as written today. A renamed or deprecated API, a newer stable version than the brief's stamp, or a claim the doc does not support is STALE: add "<sentence> | <url> | <what the doc says now>" to stale[]. Run the deprecated-API sweep of ${H}/critics/research.md item 11 over the page. An out-of-date version stamp goes into stale[] too (the author corrects the brief's version-stamps and verified: lines on the repass).\n`
    : `2. This is a light-gate day with no currency flag: no web fetching beyond the script's link check.\n`) +
  `Return checked (URLs tested), structural, dead, stale, summary.`,
  { schema: VERIFY_NOTES_SCHEMA, label:`${d.id}:notes-verify`, phase:'Materials', ...tier(currencyDay(d) ? 'notes-verify-full' : 'notes-verify-light') })   // no escalation: it runs a script, it judges nothing

// Notes page (D-0040): reference/study material at junior-interview depth. Author -> humanizer (prose-guarded)
// -> notes-verify + notes critic, up to 3 passes.
async function notesStage(d, demo) {
  const { scriptNames, keyNames, demoCtx, exUrl } = demoFacts(d, demo)
  const page = d.pageFile
  const wpm = MN.readingWpm || 150
  return gated(`${d.id} notes page`,
    (cr, pass) => agent(
      `You are the NOTES-PAGE author. ${dayHeader(d)}${demoCtx}` +
      `PURPOSE (D-0040): ${page} is reference and study material a learner reads on their own after the day (${Math.round(WORD_MIN / wpm)}–${Math.round(WORD_MAX / wpm)} minutes). It teaches every subtopic of this day to the depth a junior-developer interview expects, plus the adjacent concept the brief names for it. Applying the concepts is the demos' job; this page explains, shows a runnable example, names the trade-off, shows what the thing looks like in someone else's code, and gives the sentences the reader would say when asked.\n` +
      `DEPTH BAR per subtopic (the critic samples three): (1) a plain explanation a graduate can follow, (2) a runnable example in a <pre><code> block with its output stated in the prose, (3) a trade-off or a limit, (4) how to recognise it on sight in real code, (5) a spoken answer in the step's "Say it in an interview" callout; then the adjacent concept from the brief's Notes depth (what the interviewer asks next).\n` +
      `SCOPE: teach this day's coverage rows in curriculum order, each under an h2 or an h3. A later day's topic may be named in ONE sentence ("week 2 moves this into a module"), never taught as an h2 or h3; the anti-spoiler rows above mean "not a section".\n` +
      `DELIVERY REFERENCES: the page never refers to the classroom. None of these strings may appear in article prose, quiz strings or diagram strings: ${J(MN.deliveryPhrases || [])}. Do not describe what the trainer did, what the reader watched, or the session. You MAY say in broad strokes what the demo thread builds ("the ticket-desk code grows a queue of tuples"), never an answer-key file path in prose. The demo card and the goals modal's "Demos today" list are structure and stay.\n` +
      `FACTS: ${d.researchFile} is your ONLY source (its Claims, Notes depth, Sources, Glossary, Pitfalls). Add nothing to the brief. Every sentence that states a version number, a model id, an API/class/function/flag name's behaviour, a default, a limit or a price carries a citation <sup class="cite"><a href="#src-N">N</a></sup> to an <li id="src-N"> in section.reading-sources whose URL is in the brief; >= ${MN.citationsPerStepMin} citations per teaching step.\n` +
      `STRUCTURE: read ${TEMPLATE} and copy its shell exactly (head + meta tc-day, topbar, nav.toc, article.reading-col, aside.side with diagram + ${d.noDemos ? 'NO demo card (demoFormat none)' : 'the demo card as variant A (pending) from ' + H + '/templates/day.exemplar.html, whatever the template page shows'} + quiz card + side-nav, #quiz-modal, #goals-modal, optional #deep-modal, ${MN.codePopupsMin}–${MN.codePopupsMax} #code-* popups, inline window.NEXT/DIAGRAM/QUIZ, the exact script tags). Then:\n` +
      `- <meta name="tc-day" content="${d.id}">; title "<title> | ${CFG.siteTitle}"; topbar brand "${(CFG.brand||{}).bold}·${(CFG.brand||{}).rest}", Home ../../index.html, Demos ${CFG.repoUrl}/tree/main/demos, Exercises ${CFG.repoUrl}/tree/main/exercises.\n` +
      `- .lede: h1; .meta spans "Week ${A.week} · Day ${d.day}", "${d.dateLabel}", "${A.theme}", "<b>~N min</b> · reference notes @${wpm} wpm · diagram · check" (N = round(prose words / ${wpm})), and <span class="verified">Sources checked <the brief's verified: date> · python ${CFG.python}[ · <lib> <version> for each library stamp in the brief]</span>; p.summary of 3–5 sentences: the one sentence the page assumes from the previous day (week note), what the page teaches, what the reader can answer afterwards; then the .ix-legend.\n` +
      `- ${MN.stepsMin}–${MN.stepsMax} section.step (data-step 0..n-1, each with .tag and h2). All but the last are TEACHING steps: >= ${MN.h3PerStepMin} h3 subsections each (a subtopic or its adjacent concept per h3), 450–900 prose words, runnable <pre><code> examples wherever the subtopic is code-shaped (page total >= ${MN.codeBlocksMin}), citations, at most one widget (.ix-predict / .ix-spot) and optionally one code popup button, and LAST in the step exactly one <div class="callout interview"><div class="k">Say it in an interview</div><p>…</p></div> with 1–3 <p>, each a spoken first-person answer (10–20 seconds, no code) to one of the step's interview questions from the brief.\n` +
      `- The LAST step: .tag "Check yourself", h2 "Check yourself", one intro <p>, then ${MN.checkYourselfMin}–${MN.checkYourselfMax} <details class="check"><summary>question</summary><p>answer, 1–4 sentences</p></details> covering every teaching step. No h3, no callout.\n` +
      `- section.reading-sources: <li id="src-1">, <li id="src-2"> … in citation order, >= ${MN.sourcesMin} items, each one http link taken from the brief plus a one-line reason.\n` +
      (d.noDemos ? `- NO .demo-card and no "Demos today" list (demoFormat none).\n` : `- .demo-card exactly variant A: data-demo="pending", text "Published after class", no links (D-0030; harness/publish_demos.py flips it after the session).\n`) +
      `- window.DIAGRAM with captions.length == step count, nodes {id,step,x,y,w,h,label,detail?}, edges referencing real ids; each step reveals something the section explains; the last caption sums up what the reader can now explain.\n` +
      `- window.QUIZ with exactly ${MN.quizQuestions} questions: ≥1 scq, ≥1 tf, ≥1 mcq or match, ≤1 open; every non-open question has explain; grounded in the page.\n` +
      `- #goals-modal: ${MN.goalsMin}–${MN.goalsMax} "By the end of today you can" items; "Today's exercise" link ${exUrl}; ${d.noDemos ? 'no demo list' : '"Demos today" list: one item per script, its objective in ladder order, no file names or links'}.\n` +
      `- Code popups: ${MN.codePopupsMin}–${MN.codePopupsMax}, each a SHORT excerpt of a real answer key in ${d.keyDir} (data-file = exact key filename, e.g. ${keyNames[0] || '01_<slug>.py'}; code HTML-escaped; never the whole file).\n` +
      `- Code in prose: single tokens (a command, a filename, an identifier) inline as <code>; any sequence of 2+ commands or lines the reader would type goes in a <pre><code> block (HTML-escaped, one command per line, no prompt characters) — never a run of commands inside a sentence.\n` +
      `- window.NEXT = { label: ${J(d.nextLabel)}, href: ${J(d.nextHref)} }.\n` +
      `- Scripts: theme.js in head; bottom exactly diagram, scrolly, modals, quiz, widgets, glossary, codeviewer${d.feedback ? ', survey (+ a #survey section with window.SURVEY and a link to ' + CFG.feedbackFormUrl + ')' : ''}; relative ../../assets/... paths with the template's ?v= versions. Widgets allowed: .ix-legend, .ix-predict, .ix-spot only.\n` +
      `- Prose voice (D-0029): write plainly, as a person explaining to a colleague. No "not X but Y" contrasts, no one-line closers that restate the paragraph, no forced triads, no em-dashes as the default joiner, no bold labels at the start of items, no stock AI words (delve, crucial, robust, seamless, leverage, landscape, navigate, journey, foster, testament, underscore). A humanizer pass runs after you; give it little to do.\n` +
      `WRITE INCREMENTALLY (the page is ${WORD_MIN}–${WORD_MAX} prose words; aim for ${WORD_MIN + 300}–${WORD_MAX - 300}; one huge Write gets truncated):\n` +
      `1. ONE Write of the whole shell: the lede, every section.step with its tag, h2 and h3 headings only, an empty Check yourself step, window.NEXT, window.DIAGRAM with one placeholder caption per step, window.QUIZ with ${MN.quizQuestions} placeholder questions, the modals and the script tags. It must parse: run python ${H}/notes_check.py ${page} --counts (band findings are expected at this point, a parse error is not).\n` +
      `2. Fill ONE step per Edit call (its prose, code blocks, citations, callout). After each Edit run the same --counts command and watch the words total; stop adding prose at ${WORD_MAX - 300}.\n` +
      `3. Then the Check yourself step, the real quiz, the diagram nodes/edges/captions, the sources list, the meta minutes and the verified span. Never rewrite the whole file after step 1.\n` +
      `Before returning run: python ${H}/notes_check.py ${page} --counts --phrases --stamps --citations   until it prints OK, and quote its last line. Return wordCount, declaredMinutes, steps, h3Count, interviewCount, checkYourselfCount, codeBlocks, citations (total), sourcesChecked, stepMap (every coverage-row subtopic -> the 1-based step that teaches it), quizCount, demoLinks, codePopups, summary.` + fix(cr),
      { schema: NOTES_SCHEMA, label:`${d.id}:notes`, phase:'Materials', ...tier('notes', pass) })
      .then(async (r) => { if (r) await humanize(d); return r }),
    async (_r, pass) => {
      const v = await notesVerify(d, pass)
      const c = await agent(
        `NOTES CRITIC. Read ${H}/critics/notes.md and apply it to ${page} against ${d.researchFile} (allowed facts), ${TEMPLATE} (structure), ${d.noDemos ? 'no demos (demoFormat none: the page must carry NO demo card)' : 'demo scripts ' + J(scriptNames) + ' in ' + d.demoDir + ' and answer keys ' + J(keyNames) + ' in ' + d.keyDir + ' (the demo card must be data-demo="pending" with no links)'}. Word band ${WORD_MIN}–${WORD_MAX}. Item 12 against the week plan rows: every coverage subtopic is taught under an h2 or h3 and nothing the anti-spoiler rows defer is a section. Run the verification command in the critic spec with Bash and quote it. Day context: ${dayHeader(d)}` +
        `Findings from the notes-verify agent (item 19, binding; each is a critique unless you show it is wrong): ${J(v || { checked:0, structural:['notes-verify agent hard-failed; run notes_check.py yourself'], dead:[], stale:[] })}\n` +
        `Return pass, critiques (concrete fixes), one-sentence summary.`,
        { schema: VERDICT, label:`${d.id}:notes-crit`, phase:'Materials', ...tier('notes-critic') })
      if (!c) return c
      const hard = [...((v && v.structural) || []).map(x => `structural: ${x}`), ...((v && v.dead) || []).map(x => `dead link: ${x}`), ...((v && v.stale) || []).map(x => `stale: ${x}`)]
      return hard.length ? { pass:false, critiques:[...hard, ...(c.critiques || [])], summary: c.summary } : c
    })
}

async function materialsStage(d, demo) {
  const { scriptNames, facilitation, demoCtx, demoUrl, exUrl } = demoFacts(d, demo)
  const notes = () => notesStage(d, demo)

  const rubric = d.exerciseKind === 'rubric'
  const exercise = () => rubric ? gated(`${d.id} exercise`,
    (cr, pass) => agent(
      `You are the EXERCISE author (RUBRIC kind: a hands-on deliverable marked against a rubric; NO starter module, NO pytest). ${dayHeader(d)}${learnerCtx(d)}` +
      `${demoCtx}Read ${d.researchFile}${d.noDemos ? '' : ', the demo scripts in ' + d.demoDir + ' and the answer keys in ' + d.keyDir}. Read ${H}/templates/exercise-rubric-README.md and follow its headings.\n` +
      `Write ${d.exDir}/README.md: the task (what trainees build on their own machine/GitHub, drawn from this day's subtopics and the Day note), "## Deliverable" (exactly what they hand in or show), "## Acceptance criteria" (5–8 observable checklist items), "## Rubric" (markdown table criterion | meets | partial | missing), "## Getting started" (commands in a fenced block), "## Hints" (≥2); sized for 60–90 min. Do NOT create starter/ or tests/.\n` +
      `ALSO write ${d.trDir}/solutions/RUBRIC.md (private trainer marking guide; create dirs): for every acceptance criterion, the exact command(s) a trainer runs against a trainee's repo to check it in under two minutes, the expected output, and what "meets" vs "partial" looks like; plus common failure modes.\n` +
      `Return module="rubric", testCount=<number of acceptance criteria>, starterFailed=false, solutionPassed=<true iff RUBRIC.md covers every criterion>, summary.` + fix(cr),
      { schema: EXERCISE_SCHEMA, label:`${d.id}:exercise`, phase:'Materials', ...tier('exercise', pass) }),
    (_r) => agent(
      `EXERCISE CRITIC (RUBRIC kind). Read the "Rubric kind" section of ${H}/critics/exercise.md and apply it to ${d.exDir}/README.md and ${d.trDir}/solutions/RUBRIC.md. Confirm with Bash that ${d.exDir} contains no starter/ or tests/. Day context: ${dayHeader(d)}${learnerCtx(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:exercise-crit`, phase:'Materials', ...tier('critic') }))
  : gated(`${d.id} exercise`,
    (cr, pass) => agent(
      `You are the EXERCISE author. ${dayHeader(d)}${learnerCtx(d)}` +
      `${demoCtx}Read ${d.researchFile}${d.noDemos ? '' : ', the demo scripts in ' + d.demoDir + ' and the answer keys in ' + d.keyDir}. Read ${H}/templates/exercise-README.md and ${H}/templates/conftest.py.\n` +
      `Write ${d.exDir}/: README.md (task, acceptance checklist mapping 1:1 to test names, getting started, ≥2 hints; 60–90 min), starter/<module>.py (signatures + docstrings + raise NotImplementedError only), tests/conftest.py (copy the template verbatim), tests/test_<module>.py with ${M.exercise.testsMin}–${M.exercise.testsMax} deterministic, network-free tests.\n` +
      `ALSO write the reference solution to ${d.trDir}/solutions/<module>.py (private trainer repo path; create dirs).\n` +
      `Use Bash from ${d.exDir}: "python -m pytest -q" MUST fail; "EXERCISE_SRC=${d.trDir}/solutions python -m pytest -q" MUST pass. Confirm both before returning.\n` +
      `Return module, testCount, starterFailed, solutionPassed, summary.` + fix(cr),
      { schema: EXERCISE_SCHEMA, label:`${d.id}:exercise`, phase:'Materials', ...tier('exercise', pass) }),
    (_r) => agent(
      `EXERCISE CRITIC. Read ${H}/critics/exercise.md and apply it to ${d.exDir}/ with solutions at ${d.trDir}/solutions. Actually run both pytest invocations with Bash. Day context: ${dayHeader(d)}${learnerCtx(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:exercise-crit`, phase:'Materials', ...tier('critic') }))

  const runbook = () => gated(`${d.id} runbook`,
    (cr, pass) => agent(
      `You are the RUNBOOK author (trainer-only talk track). ${dayHeader(d)}${learnerCtx(d)}` +
      `${demoCtx}Read ${d.researchFile}${d.noDemos ? '' : ', every demo script ' + J(scriptNames) + ' in ' + d.demoDir + ' (header + steps; you point at them, you do not copy them)'}, ${d.pageFile} if it exists (for objectives), and the exercise README at ${d.exDir}/README.md if it exists. Read the template ${H}/templates/runbook.md.\n` +
      `Write ${d.trDir}/runbook.md: first line "# ${d.id} runbook — ${d.title}"; second line "Week ${A.week} · Day ${d.day} · ${d.dateLabel} · ${A.theme}"; third line links every artifact exactly as the template does (the trainer repo is separate, so public links are absolute): notes page ${CFG.siteUrl}weeks/${d.rel}.html, demos ${demoUrl}, exercise ${exUrl}, brief ${CFG.repoUrl}/blob/${CFG.repoBranch || 'main'}/harness/research/${d.rel}.md, and the relative link solutions/; headings in template order; "Day at a glance" table whose Minutes sum to ${M.runbook.dayMinutesMin}–${M.runbook.dayMinutesMax} incl. breaks/lunch, demo rows using each script's Time; then the teaching blocks in the order the day runs them: ${d.noDemos ? '' : 'one "## Demo N: <script filename, e.g. 01_<slug>.md>" per script (script path demos/<file> relative to the runbook, answer key path, Time, room state before, stop point if long, ≥2 checkpoint questions, ≥1 pitfall from the brief; NO talk track, the script is the talk track) and '}one "## Facilitation N: <subtopic> (M min)" per subtopic with no demo (${J(d.noDemos ? d.subtopics : facilitation)}): Goal, numbered timed beats (board plan, ask the room, pairs, debrief), ≥2 "Ask the room" questions with the steering answer, ≥1 misconception from the brief, what the room writes down; Notes page handoff; Exercise briefing (${rubric ? 'deliverable, acceptance criteria, ≥2 stuck points, how to mark in the room, marking guide ' + d.trDir + '/solutions/RUBRIC.md' : 'module, acceptance, ≥2 stuck points, solutions path ' + d.trDir + '/solutions'}${LR ? ', where trainees work and hand in (the learner repo folder)' : ''}); Common questions; If running long / short${d.feedback ? '; "## Feedback form" with ' + CFG.feedbackFormUrl : ''}${d.kind === 'review' ? '; "## Review agenda"' : ''}.\n` +
      `Wording (D-0039): the trainer delivers from this file, so questions, framing lines and answers are sentences a person can say without rephrasing them, and a stop point or an "if running long" line is a few short sentences in the order things happen, not one sentence chained with semicolons. A humanizer pass runs after you (prose only); give it little to do.\n` +
      `Return totalMinutes, demoSections (Demo + Facilitation blocks), solutionFiles (what exists under solutions/), summary.` + fix(cr),
      { schema: RUNBOOK_SCHEMA, label:`${d.id}:runbook`, phase:'Materials', ...tier('runbook', pass) })
      .then(async (r) => { if (r) await humanizeTrainer(d, 'runbook', [`${d.trDir}/runbook.md`], 'Materials'); return r }),
    (_r) => agent(
      `RUNBOOK CRITIC. Read ${H}/critics/runbook.md and apply it to ${d.trDir}/runbook.md with ${d.noDemos ? 'no demo scripts (demoFormat none: every teaching block is a Facilitation block)' : 'demo scripts ' + J(scriptNames) + ' in ' + d.demoDir + ' and facilitation subtopics ' + J(facilitation)}, exercise in ${d.exDir}, solutions in ${d.trDir}/solutions, brief ${d.researchFile}. ${rubric ? 'Rubric-kind day: check solutions/RUBRIC.md exists and the briefing matches it; no pytest.' : 'Run the solutions pytest check with Bash.'} Items 2 and 3 against the week plan: demo minutes equal the ladder rows, the glance table follows the day shape, stop points match the plan's, and each Demo section's "room state before" names the rung it starts from (the thread row's startsFrom key, or "cold"). Day context: ${dayHeader(d)}${learnerCtx(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:runbook-crit`, phase:'Materials', ...tier('critic') }))

  // notes + exercise first (runbook reads both for objectives / stuck points), then runbook
  const [n, e] = await parallel([notes, exercise])
  const r = await runbook()
  return { notes: n, exercise: e, runbook: r }
}

// =====================================================================
// Run
// =====================================================================
log(`Model tiers: ${TIER_LABELS}; escalate on pass ≥ ${TIERS.escalateOn || '—'} → ${TIERS.escalate ? (TIERS.escalate.model || 'inherit') + '/' + (TIERS.escalate.effort || 'inherit') : 'off'}`)
if (A.noPlan) log(`WARNING: running WITHOUT a week plan (--no-plan escape); record it in STATUS.md`)
else log(`Week plan: ${A.weekPlan}`)
// Week batch (D-0038): research for every day in parallel, then demos STRICTLY in day order, then materials in
// parallel again. A rung's Starts from key is the previous rung's key (D-0033), so a later day's demo author can
// only start once the earlier day's keys are on disk. A day whose demos stage produced no scripts blocks the
// later days of the run: they are reported flagged and nothing is authored on top of a missing key. A day the
// critic flagged still has its keys and does not block.
const blocked = (label, by) => ({ task: label, status:'flagged', passes:0, flags:[`blocked: ${by} produced no demo keys, so this day's rungs have no Starts from state; re-run from ${by}`], summary:`not attempted (blocked by ${by})` })
if (NOTES_ONLY) log(`Notes-only run (D-0040): research depth -> notes page; demos, exercise and runbook reused from disk`)
phase('Research')
const researched = await parallel(DAYS.map(d => () => NOTES_ONLY ? researchDepthStage(d) : researchStage(d)))
phase('Demos')
const demoed = []
let blockedBy = null
if (NOTES_ONLY) {
  // D-0040: the day's scripts and keys are already on disk (args_for.py --notes-only checked); nothing is authored.
  for (const d of DAYS) demoed.push(d.noDemos
    ? { task:`${d.id} demos`, status:'skipped', passes:0, summary:'demoFormat none: no code demo', result:{ scripts:[], facilitation: d.subtopics, requirements:[], summary:'' } }
    : { task:`${d.id} demos`, status:'cached', passes:0, summary:'notes-only: scripts and keys reused from disk',
        result:{ scripts:(d.existingScripts || []).map(s => ({ name:s.name, key:s.key, objective:s.objective, minutes:s.time || 0, mode:'', needsKey:false })),
                 facilitation:(d.weekPlanRows || []).filter(r => r.Demo === 'facilitation').map(r => r.Subtopic), requirements:[], summary:'' } })
} else {
  for (const d of DAYS) {
    if (blockedBy) { demoed.push(blocked(`${d.id} demos`, blockedBy)); continue }
    let r = null
    try { r = await demosStage(d) } catch (e) { log(`${d.id} demos stage threw: ${e && e.message}`) }
    demoed.push(r)
    if (!d.noDemos && !(r && r.result && (r.result.scripts || []).length)) blockedBy = `${d.id} demos`
  }
}
phase('Materials')
const materials = await parallel(DAYS.map((d, i) => async () => {
  const demos = demoed[i]
  // No scripts on a demo day (blocked, or this day's own demos stage failed): notes, exercise and runbook all
  // read the scripts, so they are not attempted either.
  if (!d.noDemos && !(demos && demos.result && (demos.result.scripts || []).length)) {
    const why = (demos && demos.passes === 0 && demos.flags) ? demos.flags[0] : `not attempted: ${d.id} demos produced no scripts; fix the demos and re-run this day`
    const skip = (label) => ({ task: label, status:'flagged', passes:0, flags:[why], summary:'not attempted (no demo scripts)' })
    return { notes: skip(`${d.id} notes page`), exercise: skip(`${d.id} exercise`), runbook: skip(`${d.id} runbook`) }
  }
  if (NOTES_ONLY) {
    const reused = (label) => ({ task: label, status:'cached', passes:0, summary:'not re-authored in a notes-only run (D-0040); its notes-handoff wording may lag the page' })
    return { notes: await notesStage(d, demos), exercise: reused(`${d.id} exercise`), runbook: reused(`${d.id} runbook`) }
  }
  return materialsStage(d, demos)
}))
const perDay = DAYS.map((d, i) => ({ d, research: researched[i], demos: demoed[i], ...(materials[i] || {}) }))

// ---------- WIRE (serial: shared files) ----------
phase('Wire')
const glossaryAdds = []
perDay.forEach(x => { if (x && x.research && x.research.result) (x.research.result.glossaryTerms || []).forEach(t => glossaryAdds.push({ day: x.d.id, ...t })) })
// D-0040: the plan's Coverage map records the page step that teaches each subtopic; the author reports where
// each one landed and the serial Wire step realigns the column (parallel authors never edit the plan).
const stepMaps = perDay.filter(x => x && x.notes && x.notes.result && (x.notes.result.stepMap || []).length).map(x => ({ day: x.d.id, stepMap: x.notes.result.stepMap }))
const wire = await agent(
  `WIRE step (serial, shared files). Days shipped this run: ${J(DAYS.map(d => ({ id:d.id, rel:d.rel, page:d.pageRel })))}.\n` +
  `1. Open ${ROOT}/docs/assets/js/glossary.js. Between "// GLOSSARY:BEGIN" and "// GLOSSARY:END" append these entries as { term, def, aka } lines, SKIPPING any whose term or aka already exists (case-insensitive, check both term and aka of existing entries): ${J(glossaryAdds)}. Keep the file valid JS (node --check).\n` +
  `2. In ${H}/curriculum.json set "status": "live" for ${J(DAYS.map(d => d.id))} ONLY if that day's page ${'`'}docs/weeks/<rel>.html${'`'}, exercises/<rel>/README.md and (unless demoFormat is "none") ${TRAINER}/<rel>/demos/key/README.md all exist on disk. Never touch the "taught" field.\n` +
  `3. Run: python ${H}/build_index.py   (it also rebuilds tracker.html, the work tracker, D-0035)\n` +
  `4. For each shipped day whose previous day page exists, confirm the previous page's window.NEXT.href points at this day's filename; fix if not. And for each shipped day's own page: if its window.NEXT.href names a day page that does not exist on disk (a later day of this run was blocked or failed), set it to { label: "Back to program →", href: "../../index.html" }.\n` +
  `5. Publish step (D-0030): for each shipped day run "python ${H}/publish_demos.py <week> <day>" (${J(DAYS.map(d => `${A.week} ${d.day}`))}). It copies the answer keys to demos/<rel>/ and flips the notes demo card ONLY if curriculum.json carries taught:<date> for that day (set by the delivery-day close); otherwise it prints "not taught yet" and that is the expected outcome on an authoring run. Never copy demo files by hand.\n` +
  `5b. Practice section (D-0047): for each shipped day run "python ${H}/practice_tasks.py insert <week> <day>" (${J(DAYS.map(d => `${A.week} ${d.day}`))}). A re-authored page comes back without its section.practice; this writes it again from harness/practice/<rel>.json and prints "no practice file" for a day that has none, which is the expected outcome for a newly authored day. Never write that section by hand.\n` +
  `6. Run ${ROOT}/docs/bump-css.sh --all if you changed glossary.js.\n` +
  `7. Coverage-map realignment (D-0040): ${(A.noPlan || !stepMaps.length) ? 'nothing to do this run (no week plan, or no notes page reported a stepMap).' : 'in ' + A.weekPlan + ' "## Coverage map" table, for each day below set the "Notes step" cell of the row whose Day and Subtopic match to the number given, touching no other cell: ' + J(stepMaps) + '. Then run: python ' + H + '/plan_check.py ' + A.weekPlan + '   and quote its OK line (fix the cell, never the checker, if it complains).'}\n` +
  `8. Last, run: python ${H}/build_tracker.py   so tracker.html matches the state you just changed (never edit tracker.html by hand).\n` +
  `Return a one-paragraph summary of what changed.`,
  { label:'wire', phase:'Wire', ...tier('wire') })

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

// ---------- RECORD (work tracker, D-0035) ----------
// One record per run in harness/runs.jsonl, written before Verify so the run-log contract test sees it; the
// Verify agent then amends the test result. Run id, tokens and minutes are invisible to a script: the session
// adds them afterwards with `python harness/log_run.py amend --last --run-id wf_... --minutes M --tokens T`.
phase('Record')
const REPORT_FILE = `${H}/run-report.tmp.json`
const DAY_IDS = DAYS.map(d => d.id).join(',')
const runRecord = {
  kind: 'day-fanout', date: A.today, week: A.week, days: DAYS.map(d => d.id), runId: null,
  agents: AGENTS + 1, minutes: null, tokens: null,
  tiers: { labels: TIER_LABELS, verified: null },
  artifacts: report.flatMap(r => ['research','demos','notes','exercise','runbook'].map(k => ({ day: r.day, name: k, status: (r[k] && r[k].status) || 'flagged', passes: r[k] ? r[k].passes : 0 }))),
  flagged: flagged.length,
  flags: flagged.map(f => ({ day: f.day, artifact: f.artifact, flags: (f.flags || []).slice(0, 6).map(x => String(x).slice(0, 300)) })),
  tests: null, resolved: false, note: [A.noPlan ? 'run with the --no-plan escape' : '', NOTES_ONLY ? 'notes-only run (D-0040): research depth + notes page; demos, exercise and runbook reused' : ''].filter(Boolean).join('; '),
}
const recorded = await agent(
  `RECORD step (work tracker, D-0035).\n` +
  `1. With the Write tool (not echo, not a heredoc) create ${REPORT_FILE} containing EXACTLY this JSON:\n${JSON.stringify(runRecord)}\n` +
  `2. From ${ROOT} run: python harness/log_run.py add harness/run-report.tmp.json\n` +
  `   It validates the record, appends it to harness/runs.jsonl, deletes the temp file and rebuilds tracker.html. If it rejects the record, fix only what its message names in the temp file and retry. Never edit harness/runs.jsonl or tracker.html by hand.\n` +
  `3. Run: python harness/build_tracker.py --check   and return its one-line output.`,
  { label:'record', phase:'Record', ...tier('wire') })

// ---------- VERIFY ----------
phase('Verify')
let verify = null
for (let attempt = 1; attempt <= 3; attempt++) {
  verify = await agent(
    `VERIFY step. From ${ROOT}: first run python harness/build_tracker.py (work tracker, D-0035), then run: python -m unittest discover -s tests -v   (and python ${H}/build_index.py --check). Report passed=true only if everything passes. List each failure as "<test>: <one-line cause>".\n` +
    (recorded
      ? `Then record the result: python harness/log_run.py amend --last --match-days ${DAY_IDS} --agents ${AGENTS + 1} --tests pass   (use --tests fail when anything failed). If it refuses because the last record is not this run's, skip it and say so.`
      : `The Record step did not complete; do not amend the run log.`),
    { schema: VERIFY_SCHEMA, label:`verify:${attempt}`, phase:'Verify', ...tier('verify') })
  if (!verify || verify.passed || attempt === 3) break
  await agent(
    `FIX step (attempt ${attempt}). These contract tests failed: ${J(verify.failures)}. Fix the underlying artifact(s) for days ${J(DAYS.map(d => d.rel))} — never weaken the tests or metrics. If a failure is the tracker staleness test (tests/test_tracker.py, "stale"), running python harness/build_tracker.py is the whole fix. Re-run the failing tests with Bash until they pass. Return a short summary.`,
    { label:`fix:${attempt}`, phase:'Verify', ...tier('fix') })
}

log(`Run complete: ${DAYS.length} day(s), ${flagged.length} flagged item(s), tests ${verify && verify.passed ? 'PASS' : 'FAIL'}; run log ${recorded ? 'recorded' : 'NOT recorded'} (add the run id with: python harness/log_run.py amend --last --run-id <wf_...>)`)
return { week: A.week, days: DAYS.map(d => d.id), flaggedCount: flagged.length, flagged, verify, wire, report, recorded, glossaryAdded: glossaryAdds.length }
