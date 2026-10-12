// day-fanout.js — produce one training day's full artifact set, critic-gated.
//
// Run (one day per invocation; two or three days pipeline fine but mind the agent budget):
//   python harness/args_for.py <week> <day...> --today YYYY-MM-DD   -> paste as args
//   Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: <that JSON> })
//
// Pipeline per day:  Research (gate-tiered) -> Demos -> Materials (notes ∥ runbook ∥ exercise)
// then, once every day is through:  Wire (serial, shared files) -> Record (run log + work tracker, D-0035)
// -> Verify (unittest, ≤2 fix loops).
// Demos (D-0030): walkthrough scripts + answer keys are authored to trainer/<rel>/demos/ (private) and
// published to demos/<rel>/ by harness/publish_demos.py only once curriculum.json carries taught:<date>.
// A demoFormat "none" day skips the Demos stage; its runbook carries facilitation scripts instead.
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
const TIER_LABELS = ['research-light','research-full','demos','notes','humanize','exercise','runbook','critic','wire','verify','fix'].map(tierLabel).join(' · ')
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
      `Return scripts[] (name, key, objective, minutes, mode, needsKey), facilitation[] (subtopics with no script), requirements[], summary.` + fix(cr),
      { schema: DEMO_SCHEMA, label:`${d.id}:demos`, phase:'Demos', ...tier('demos', pass) }),
    (_r) => agent(
      `DEMOS CRITIC. Read ${H}/critics/demos.md and apply it to ${d.demoDir}/ (scripts + key/) against the brief ${d.researchFile}. Use Bash: run "python ${H}/demo_check.py ${d.demoDir}" and quote its output; RUN every .py key from key/ (60 s timeout) against the script's Check blocks; replay every transcript key's "$ " commands in a scratch folder in the rung's Starts from state; run key-gated keys without the key; nbformat.validate every .ipynb. Then walk every script as a learner (items 5–8), judge the CONSULT-vs-WRITE split (item 9), and check every rung against its thread row (item 13: Thread/Starts from match the row, only the row's "adds" is typed on top of the Starts from key, end state and commit message match; demo names and minutes match the ladder rows). Day context: ${dayHeader(d)}` +
      `Return pass, critiques (file + step + concrete fix), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:demos-crit`, phase:'Demos', ...tier('critic') }))
}

// Humanizer pass (D-0029): runs after the notes author and before the notes critic. Prose only.
const humanize = (d) => agent(
  `HUMANIZE pass for ${d.pageFile}. Load the humanizer skill with the Skill tool ("humanizer:humanizer") and apply it in FILE MODE to that page.\n` +
  `Rewrite prose only: text inside article.reading-col (the .lede, paragraphs, list items), the window.QUIZ question/option/explain strings, and window.DIAGRAM captions and node detail strings. Reference voice: neutral, plain, technical.\n` +
  `Leave untouched: every HTML tag and attribute, <pre>/<code> blocks, inline <code>, filenames, URLs, numbers, versions, dates, quiz answer indices and question count, section.step count, window.NEXT, script tags.\n` +
  `Do not add or remove a fact. After writing, run the verification snippet from ${H}/critics/notes.md with Bash and confirm the prose count is still within ${WORD_MIN}–${WORD_MAX} and steps/captions/quiz counts are unchanged; if the rewrite pushed the count under ${WORD_MIN}, restore cut sentences rather than inventing new ones.\n` +
  `Return one short paragraph: patterns found (by humanizer section number), sentences changed, final word count.`,
  { label:`${d.id}:notes-humanize`, phase:'Materials', ...tier('humanize') })

async function materialsStage(d, demo) {
  const scripts = (demo && demo.result && demo.result.scripts) ? demo.result.scripts : []
  const scriptNames = scripts.map(s => s.name)
  const keyNames = scripts.map(s => s.key)
  const facilitation = (demo && demo.result && demo.result.facilitation) ? demo.result.facilitation : []
  const demoUrl = `${CFG.repoUrl}/tree/${CFG.repoBranch || 'main'}/demos/${d.rel}`
  const exUrl = `${CFG.repoUrl}/tree/${CFG.repoBranch || 'main'}/exercises/${d.rel}`
  const demoCtx = d.noDemos
    ? `This day has NO code demos (demoFormat none): every subtopic is facilitated from the runbook.\n`
    : `Demo scripts (private until taught, in ${d.demoDir}): ${J(scripts.map(s => ({ name:s.name, key:s.key, objective:s.objective, minutes:s.minutes })))}. Answer keys in ${d.keyDir}. Subtopics facilitated without a demo: ${J(facilitation)}.\n`
  const notes = () => gated(`${d.id} notes page`,
    (cr, pass) => agent(
      `You are the NOTES-PAGE author. ${dayHeader(d)}${demoCtx}` +
      `Read (1) ${TEMPLATE} — copy its FULL structure (head+meta tc-day, topbar, nav.toc, article.reading-col with .lede + section.step blocks + section.reading-sources, aside.side with diagram + ${d.noDemos ? 'NO demo card (demoFormat none)' : '.demo-card variant A (pending)'} + quiz card + side-nav, #quiz-modal, #goals-modal, optional #deep-modal, 0–2 #code-* popups, inline window.NEXT/DIAGRAM/QUIZ, the exact script tags). (2) ${d.researchFile} — your ONLY source of facts. (3) ${d.noDemos ? 'nothing else' : 'the demo scripts ' + J(scriptNames) + ' in ' + d.demoDir + ' and the answer keys in ' + d.keyDir}.\n` +
      `Write ${d.pageFile}:\n` +
      `- <meta name="tc-day" content="${d.id}">; title "<title> | ${CFG.siteTitle}"; topbar brand "${(CFG.brand||{}).bold}·${(CFG.brand||{}).rest}", Home ../../index.html, Demos ${CFG.repoUrl}/tree/main/demos, Exercises ${CFG.repoUrl}/tree/main/exercises.\n` +
      `- .lede meta: "Week ${A.week} · Day ${d.day}", "${d.dateLabel}", "${A.theme}", "~N min" where N = round(prose words / ${MN.readingWpm || 150}).\n` +
      `- ${MN.stepsMin}–${MN.stepsMax} section.step (data-step 0..n-1), prose ${WORD_MIN}–${WORD_MAX} words total; the page is the reference that deepens what the trainer types live — refer to a demo by its objective ("the Git local-loop demo"), never by a file path (the answer keys are not public until after class).\n` +
      (d.noDemos ? `- NO .demo-card and no "Demos today" list (demoFormat none).\n`
                 : `- .demo-card exactly as the template's variant A: data-demo="pending", text "Published after class", no links (D-0030; harness/publish_demos.py flips it after the session).\n`) +
      `- window.DIAGRAM with captions.length == step count, nodes {id,step,x,y,w,h,label,detail?}, edges referencing real ids; each step reveals something the section explains.\n` +
      `- window.QUIZ with exactly ${MN.quizQuestions} questions: ≥1 scq, ≥1 tf, ≥1 mcq or match, ≤1 open; every non-open question has explain; grounded in the brief and the demos.\n` +
      `- #goals-modal: ${MN.goalsMin}–${MN.goalsMax} "By the end of today you can" items; "Today's exercise" link ${exUrl}; ${d.noDemos ? 'no demo list' : '"Demos today" list: one item per script, its objective in order, no file names or links'}.\n` +
      `- Code popups: 0–2, each a SHORT excerpt of a real answer key in ${d.keyDir} (data-file = exact key filename, e.g. ${keyNames[0] || '01_<slug>.py'}; code HTML-escaped; never the whole file).\n` +
      `- Code in prose: single tokens (a command, a filename, an identifier) inline as <code>; any sequence of 2+ commands or lines the reader would type goes in a <pre><code> block (HTML-escaped, one command per line, no prompt characters) — never a run of commands inside a sentence.\n` +
      `- section.reading-sources with ≥${MN.sourcesMin} URLs from the brief.\n` +
      `- window.NEXT = { label: ${J(d.nextLabel)}, href: ${J(d.nextHref)} }.\n` +
      `- Scripts: theme.js in head; bottom exactly diagram, scrolly, modals, quiz, widgets, glossary, codeviewer${d.feedback ? ', survey (+ a #survey section with window.SURVEY and a link to ' + CFG.feedbackFormUrl + ')' : ''}; relative ../../assets/... paths. Widgets allowed: .ix-legend, .ix-predict, .ix-spot only.\n` +
      `- Prose voice (D-0029): write plainly, as a person explaining to a colleague. No "not X but Y" contrasts, no one-line closers that restate the paragraph, no forced triads, no em-dashes as the default joiner, no bold labels at the start of items, no stock AI words (delve, crucial, robust, seamless, leverage, landscape, navigate, journey, foster, testament, underscore). A humanizer pass runs after you; give it little to do.\n` +
      `- Count words with a Python one-liner before returning. Return wordCount, declaredMinutes, steps, quizCount, demoLinks, codePopups, summary.` + fix(cr),
      { schema: NOTES_SCHEMA, label:`${d.id}:notes`, phase:'Materials', ...tier('notes', pass) })
      .then(async (r) => { if (r) await humanize(d); return r }),
    (_r) => agent(
      `NOTES CRITIC. Read ${H}/critics/notes.md and apply it to ${d.pageFile} against ${d.researchFile} (allowed facts), ${TEMPLATE} (structure), ${d.noDemos ? 'no demos (demoFormat none: the page must carry NO demo card)' : 'demo scripts ' + J(scriptNames) + ' in ' + d.demoDir + ' and answer keys ' + J(keyNames) + ' in ' + d.keyDir + ' (the demo card must be data-demo="pending" with no links)'}. Word band ${WORD_MIN}–${WORD_MAX}. Item 12 against the week plan: the page teaches exactly this day's coverage rows (every subtopic row present, the step the row names covers it) and nothing the anti-spoiler rows defer. Run the verification snippet in the critic spec with Bash. Day context: ${dayHeader(d)}` +
      `Return pass, critiques (concrete fixes), one-sentence summary.`,
      { schema: VERDICT, label:`${d.id}:notes-crit`, phase:'Materials', ...tier('critic') }))

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
      `Return totalMinutes, demoSections (Demo + Facilitation blocks), solutionFiles (what exists under solutions/), summary.` + fix(cr),
      { schema: RUNBOOK_SCHEMA, label:`${d.id}:runbook`, phase:'Materials', ...tier('runbook', pass) }),
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
  `2. In ${H}/curriculum.json set "status": "live" for ${J(DAYS.map(d => d.id))} ONLY if that day's page ${'`'}docs/weeks/<rel>.html${'`'}, exercises/<rel>/README.md and (unless demoFormat is "none") ${TRAINER}/<rel>/demos/key/README.md all exist on disk. Never touch the "taught" field.\n` +
  `3. Run: python ${H}/build_index.py   (it also rebuilds tracker.html, the work tracker, D-0035)\n` +
  `4. For each shipped day whose previous day page exists, confirm the previous page's window.NEXT.href points at this day's filename; fix if not.\n` +
  `5. Publish step (D-0030): for each shipped day run "python ${H}/publish_demos.py <week> <day>" (${J(DAYS.map(d => `${A.week} ${d.day}`))}). It copies the answer keys to demos/<rel>/ and flips the notes demo card ONLY if curriculum.json carries taught:<date> for that day (set by the delivery-day close); otherwise it prints "not taught yet" and that is the expected outcome on an authoring run. Never copy demo files by hand.\n` +
  `6. Run ${ROOT}/docs/bump-css.sh --all if you changed glossary.js.\n` +
  `7. Last, run: python ${H}/build_tracker.py   so tracker.html matches the state you just changed (never edit tracker.html by hand).\n` +
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
  tests: null, resolved: false, note: A.noPlan ? 'run with the --no-plan escape' : '',
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
