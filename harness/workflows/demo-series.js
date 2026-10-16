// demo-series.js — author one week's demo walkthroughs as a series (D-0055): one walkthrough per demo block
// (AM / PM slot), one commit per block on the demo repo's prep branch, authored strictly in ladder order.
//
// Run ONCE per week, after the week plan exists and every day's research brief is on disk:
//   python harness/args_for.py <week> --demos --today YYYY-MM-DD   -> paste as args (the ONLY source of these args)
//   Workflow({ scriptPath: "harness/workflows/demo-series.js", args: <that JSON> })
//
// Pipeline:  Blocks (serial, ladder order: author -> humanize -> critic, up to 3 passes, then flagged; a block that
// leaves no commit on the prep branch blocks the later blocks of its thread) -> Review (one series-review critic,
// flags only, D-0053; then harness/series_readme.py renders trainer/week-WW/demos/README.md) -> Record (run log +
// work tracker, D-0035) -> Verify (the demo, plan and README contract tests, <=2 fix loops).
// The walkthrough is trainer/week-WW/demos/NN-<slug>.md (template harness/templates/demo-script.md); its answer key
// is the demo repo at the block's commit on args.prepBranch (demo-repo/, config.json demoRepo). Nothing is published
// to the learner site: demos are disconnected from the notes pages (D-0055).
// A humanizer agent runs between author and critic (D-0039; prose only, guarded by harness/prose_guard.py).
// The push of the prep branch is a printed instruction for the session, never done by an agent.
//
// Scripts cannot touch the filesystem or Date(); everything comes in through args.

export const meta = {
  name: 'demo-series',
  description: 'One week of demo walkthroughs: per block author -> humanize -> critic in ladder order (commits on the prep branch), then one series review, the series README, run log and verify',
  phases: [
    { title: 'Blocks' },
    { title: 'Review' },
    { title: 'Record' },
    { title: 'Verify' },
  ],
}

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
if (!A.root || !A.today || !A.week || !Array.isArray(A.blocks) || !A.blocks.length || !A.demosDir || !A.prepBranch || !A.template || !A.critic || !A.seriesCritic) throw new Error('args must come from `python harness/args_for.py <week> --demos` (root, today, week, blocks[], demosDir, prepBranch, template, critic, seriesCritic required)')
if (!A.models || !A.models.stages || !A.models.stages.demos || !A.models.stages['demos-critic'] || !A.models.stages['series-review']) throw new Error('args.models.stages must carry demos, demos-critic and series-review (D-0055); regenerate args with args_for.py --demos')
const ROOT = A.root
const H = `${ROOT}/harness`
const M = A.metrics || {}
const MD = M.demos || {}
const CFG = A.config || {}
const LLM = A.llm || {}
const REPO = A.demoRepo || {}
const REPO_DIR = REPO.localPath || `${ROOT}/demo-repo`
const PREP = A.prepBranch
const WW = String(A.week).padStart(2, '0')
// Per-stage model/effort tiers (D-0026, D-0032). Copied from day-fanout.js: the stage's {model, effort}; on a
// repass numbered >= escalateOn, the escalate tier instead. A null model/effort is omitted (inherit the session).
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
const TIER_LABELS = ['demos', 'humanize', 'demos-critic', 'series-review', 'wire', 'verify', 'fix'].map(tierLabel).join(' · ')
const J = (x) => JSON.stringify(x, null, 1)
const BLOCKS = A.blocks.map(b => ({ ...b, file: `${A.demosDir}/${b.name}.md` }))

// ---------- schemas ----------
const VERDICT = { type:'object', additionalProperties:false, properties:{ pass:{type:'boolean'}, critiques:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['pass','critiques','summary'] }
const BLOCK_SCHEMA = { type:'object', additionalProperties:false, properties:{
  name:{type:'string'}, minutes:{type:'number'}, steps:{type:'number'}, typedLines:{type:'number'}, commitSha:{type:'string'}, commitMessage:{type:'string'},
  filesTouched:{ type:'array', items:{type:'string'} }, summary:{type:'string'} },
  required:['name','minutes','steps','typedLines','commitSha','commitMessage','filesTouched','summary'] }
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

const header =
  `WEEK ${A.week} "${A.theme}" (phase ${A.phase}, project ${A.project}). Dates ${A.weekStart} to ${A.weekEnd} (${A.timezone}); today ${A.today}. Use these dates only; never invent one.\n` +
  (A.weekNotes ? `Week note (binding): ${A.weekNotes}\n` : '') +
  (CFG.audience ? `Audience: ${CFG.audience.summary} Assume known: ${(CFG.audience.assumeKnown || []).join('; ')}. Do NOT assume: ${(CFG.audience.assumeNotKnown || []).join('; ')}. ${CFG.audience.rule || ''} Emphasise: ${(CFG.audience.emphasise || []).join('; ')}.\n` : '') +
  `Week plan (binding): ${A.weekPlan}. Weekly Epic: ${A.epic}\n` +
  `Threads (config.json): ${J(A.threads || {})}\n` +
  `Conventions (from the plan, D-0057; binding: a block that breaks one is a critic FAIL, and a rule applies from the walkthrough its Applies from names): ${J(A.conventions || [])}\n` +
  `Demo repo (the answer key): ${REPO.url || ''}, cloned at ${REPO_DIR}; the trainer types live on ${REPO.branch || 'main'}; THIS run commits each block on branch ${PREP} (one commit per block, in ladder order). Never commit to ${REPO.branch || 'main'}; never push.\n` +
  `Walkthroughs go to ${A.demosDir}/NN-<slug>.md (private trainer repo; create the folder). Template ${A.template}; critic ${A.critic}.\n` +
  `Metrics: demos ${J(MD)}. Python ${CFG.python}. LLM config this week: ${J(LLM)}. Root: ${ROOT}.\n`

const blockCtx = (b) =>
  `BLOCK ${b.n} of ${BLOCKS.length}: ${b.name} — day ${b.dayId} "${b.title}" (${b.dateLabel}), ${b.slot} slot, ${b.minutes} min, thread ${b.thread}.\n` +
  `Starts from: ${b.startsFrom} (${b.startsFrom === 'cold' ? 'cold: the first block of the thread, or a cold restart; nothing on the prep branch before it' : 'the previous block; its commit on ' + PREP + ' is the start state: read it with git before typing a line'}).\n` +
  `Commit message (the block ends with exactly this, in a \`\`\`bash fence of the last step): ${b.commitMessage || '(standalone: no commit)'}\n` +
  `Adds (what the room types in this block, in this order; the (a), (b), (c) parts become step groups): ${b.adds}\n` +
  `End state (what runs when the block is done): ${b.endState}\n` +
  `Ladder: must follow ${b.mustFollow || '—'}; guarantees for later blocks: ${b.guarantees}\n` +
  `Stop point (the plan's clean stop for this block; it must be a step boundary that exists): ${b.stopPoint} — resume at: ${b.resumeAt}\n` +
  `Day subtopics (teach in this order; the coverage rows say which this block carries): ${J(b.subtopics)}; coverage rows ${J(b.coverageRows)}\n` +
  (b.dayNotes ? `Day note: ${b.dayNotes}\n` : '') +
  (b.spoilerRows && b.spoilerRows.length ? `Anti-spoiler rows touching this day: ${J(b.spoilerRows)}\n` : '') +
  `Research brief (the ONLY source of facts, versions and API shapes): ${b.researchBrief}\n`

// Humanizer pass on the walkthrough (D-0039): prose only, proven by harness/prose_guard.py against a snapshot.
const humanizeBlock = (b) => agent(
  `HUMANIZE pass on the trainer's delivery wording (D-0039) for walkthrough ${b.file}. This is the ONLY file you may change.\n` +
  `The trainer reads this file in front of the room and says the talking points aloud while typing. Wording that sounds machine-written has to be reworded live, which is clunky. Make it read like a person's own speaking notes and change nothing a demo depends on.\n` +
  `1. FIRST, from ${ROOT}, run: python harness/prose_guard.py snapshot ${b.file}   and keep the snapshot directory it prints.\n` +
  `2. Load the humanizer skill with the Skill tool ("humanizer:humanizer") and apply it in FILE MODE; read the whole file before editing it. Reference voice: a trainer's delivery notes, plain and technical. Lines said to the room are sentences a person can say without rephrasing them; instructions to the trainer stay short imperatives. Light touch: leave a sentence that already sounds spoken. The edits that usually help: split a run-on or a chain of clauses joined by semicolons or colons into short sentences, cut a stock phrase, give a clipped fragment its subject.\n` +
  `   Do NOT flatten good spoken wording: a contrast that corrects what the room really assumes ("review comments, not taste") stays, and so does a short line the trainer would say as it is. Add no joke, warmth, example or fact, and drop no fact. In a logistics sentence (a stop point, what is pasted from where, which commit waits) every fact survives in the same order; when unsure, leave the sentence.\n` +
  `3. FROZEN, byte for byte: everything above the first "## " heading (the title and the header blockquote: a checker parses it); every fenced block and the section it sits in; every inline code span (same spans, same count); every heading line, "### Talking points" lines included; every line starting with "cwd:"; the lines that introduce a block ("Check (expected output):"); the header row, the separator row and the number of rows of every table; every bold label such as **Pre-empt — "..."**; URLs, file names, paths, commit messages, branch names, numbers, minutes, dates and ids. One bullet in, one bullet out: never add, remove, merge, split or reorder bullets or numbered items, and never move text between sections. The "What we did NOT cover" bullets keep the format "- <topic>: <where it goes>. <reason>." (demo_check.py checks it).\n` +
  `4. Verify from ${ROOT}: python harness/prose_guard.py check <snapshot directory> ${b.file}   must print OK or UNCHANGED with no WARN line (a WARN means a number changed: restore it), and python ${H}/demo_check.py ${b.file}   must print OK. Fix and re-run until that holds. Use the Edit tool (no sed, no heredocs). Touch no other file and nothing in ${REPO_DIR}.\n` +
  `Return one short paragraph: sentences changed, humanizer sections found (by number), anything left alone on purpose.`,
  { label:`${b.name}:humanize`, phase:'Blocks', ...tier('humanize') })

async function blockStage(b, prev) {
  return gated(`${b.name}`,
    (cr, pass) => agent(
      `You are the DEMO author (D-0055: a demo IS the walkthrough the trainer performs live for one demo block; the demo repo at the block's commit is the answer key). ${header}${blockCtx(b)}` +
      `Read, in this order: (1) the research brief above; (2) ${A.template} — copy its shape exactly and follow every rule in its comments (title line, the five header fields, Hand-typed during demo, Stub manifest, Presenter cheat-sheet, "## Step n — title (M min)" steps with cwd: lines, typed fences, "### Talking points while typing", "> **Pre-empt — ..."" answers, "Check (expected output):" fences, Common pitfalls, What we did NOT cover (intentional), End-of-demo wrap-up, Sequence pointer); (3) ${A.critic} so you know what the critic runs; (4) the week plan ${A.weekPlan} (Threads row, ladder, stop points, squeeze priorities, scaffold bundle, anti-spoiler ledger for this block); ` +
      (prev ? `(5) the previous walkthrough ${prev.file} (its Sequence pointer names you; your opening frames what it left) and its commit on ${PREP}: from ${REPO_DIR} run "git log ${PREP} --format=%H%x09%s" and "git show <sha> --stat", and read the thread files at that commit (git show <sha>:<path>) — that is the state the room holds when this block starts; never re-type what it built.\n` : `(5) nothing before you: the thread starts cold in this block.\n`) +
      `Then, in ${REPO_DIR}: ${prev ? `check out the prep branch ("git switch ${PREP}"; it exists from the previous block)` : `create the prep branch from ${REPO.branch || 'main'} ("git switch ${REPO.branch || 'main'}", "git pull --ff-only", "git switch -c ${PREP}"; if it already exists, "git switch ${PREP}" and reset it to ${REPO.branch || 'main'} only when the session told you to re-author from block 1)`}. Make the block's code changes EXACTLY as the walkthrough types them (same files, same lines, in the thread folder ${J(Object.values(A.threads || {}).map(t => t.repoDir))}); run every command the walkthrough runs from the cwd: it names, with the real Python (${CFG.python}; use "py -${CFG.python}" where "python" is another version) and record the real output in the Check fences (timestamps, paths and hashes as they come). Then ONE commit: git add the files the walkthrough names and git commit -m "${b.commitMessage}" (the walkthrough's last step shows the same commands). Never commit to ${REPO.branch || 'main'}; never push; never commit files the walkthrough does not create (a .venv, PNGs, __pycache__ belong in the .gitignore the walkthrough writes). A standalone block makes no commit.\n` +
      `Write ${b.file}: Time ${b.minutes} min (${b.slot} block), ${MD.stepsPerBlockMin}–${MD.stepsPerBlockMax} steps whose minutes sum to it, a whiteboard framing step first, a break noted where the plan's per-day shape puts it, at most ${MD.maxTypedLinesPerBlock} typed lines, the plan's stop point at a real step boundary, every token introduced before first use (earlier blocks of the thread count as introduced; the first block that uses a tool carries its install, version and config commands proven by running them), every tool-output claim proven by the recorded output. "What we did NOT cover" sends each topic where the plan's anti-spoiler ledger or coverage map sends it. The Sequence pointer names ${prev ? prev.name : 'no previous block (first of the week)'} and ${b.n < BLOCKS.length ? BLOCKS[b.n].name : 'the next week (or the exercise briefing)'}.\n` +
      `LLM calls (if this block has any) use exactly ${J(LLM)}; model id from the brief. No secrets anywhere.\n` +
      `Before returning, with Bash from ${ROOT}: run "python ${H}/demo_check.py ${b.file}" until it prints OK; from ${REPO_DIR} confirm "git log ${PREP} -1 --format=%H%x09%s" shows your commit with the exact message and that "git status" is clean on the prep branch.\n` +
      `Wording (D-0039): the trainer says the talking points aloud while typing, so write sentences a person can say without rephrasing them (short, plain, one idea each). A humanizer pass runs after you (prose only); give it little to do.\n` +
      `Return name, minutes, steps, typedLines, commitSha (the full sha, or "" for a standalone block), commitMessage, filesTouched, summary.` + fix(cr),
      { schema: BLOCK_SCHEMA, label:`${b.name}:author`, phase:'Blocks', ...tier('demos', pass) })
      .then(async (r) => { if (r) await humanizeBlock(b); return r }),
    (_r) => agent(
      `DEMOS CRITIC. Read ${A.critic} and apply every item to ${b.file} and its commit on ${PREP} in ${REPO_DIR}. Use Bash: run "python ${H}/demo_check.py ${b.file}" and quote its output; find the block's commit by its message on the prep branch ("git -C ${REPO_DIR} log ${PREP} --format=%H%x09%s"), check it out in a scratch worktree, run what the walkthrough runs from the cwd: it names and compare with the Check fences; diff the commit against ${prev ? 'the previous block\'s commit' : 'the branch point'} and read the walkthrough's typed fences against it (item 3); walk the script as a learner (items 5–8); judge the teaching (items 9–11) against the brief and the plan; check the Thread line, the Adds, the End state and the stop point against the plan row (item 12). Remove the scratch worktree when done ("git worktree remove"). Context: ${header}${blockCtx(b)}` +
      `Return pass, critiques (step + concrete fix, or commit + file + line), one-sentence summary.`,
      { schema: VERDICT, label:`${b.name}:critic`, phase:'Blocks', ...tier('demos-critic') }))
}

// =====================================================================
// Run
// =====================================================================
log(`Model tiers: ${TIER_LABELS}; escalate on pass ≥ ${TIERS.escalateOn || '—'} → ${TIERS.escalate ? (TIERS.escalate.model || 'inherit') + '/' + (TIERS.escalate.effort || 'inherit') : 'off'}`)
log(`Week ${A.week}: ${BLOCKS.length} block(s) on ${PREP}; plan ${A.weekPlan}`)
phase('Blocks')
const done = []
let blockedBy = null
let prevOf = {}   // thread id -> the last block of that thread that left a commit
const blocked = (label, by) => ({ task: label, status:'flagged', passes:0, flags:[`blocked: ${by} left no commit on ${PREP}, so this block has no start state; re-run from ${by}`], summary:`not attempted (blocked by ${by})` })
for (const b of BLOCKS) {
  if (blockedBy && b.thread !== 'standalone') { done.push(blocked(b.name, blockedBy)); continue }
  const prev = b.startsFrom === 'cold' ? null : (BLOCKS.find(x => x.name === b.startsFrom) || null)
  let r = null
  try { r = await blockStage(b, prev) } catch (e) { log(`${b.name} threw: ${e && e.message}`) }
  done.push(r)
  const committed = r && r.result && (r.result.commitSha || b.thread === 'standalone')
  if (!committed) blockedBy = b.name
  else if (b.thread !== 'standalone') prevOf[b.thread] = b.name
}

phase('Review')
// Series review (D-0053): ONE critic reads the run's walkthroughs as a series, in ladder order, against the plan
// (story, Starts-from chain on the prep branch, Weekly Epic, anti-spoiler, minutes, handoffs). Flags only.
const written = BLOCKS.map((b, i) => ({ b, r: done[i] })).filter(x => x.r && x.r.result && x.r.result.steps)
let seriesReview = null
if (written.length >= 2) {
  try {
    seriesReview = await agent(
      `SERIES REVIEW (D-0053, D-0055). Read ${A.seriesCritic} and apply it to this run's walkthroughs as ONE series against the week plan ${A.weekPlan}, with the prep branch ${PREP} in ${REPO_DIR} beside them ("git log ${PREP} --format=%H%x09%s").\n` +
      `Walkthroughs of this run in ladder order: ${J(written.map(x => ({ n: x.b.n, day: x.b.dayId, slot: x.b.slot, file: x.b.file, commit: x.b.commitMessage })))}\n` +
      `Judge only what spans blocks; a problem inside one walkthrough belongs to the demos critic. Edit no file.\n` +
      `Return pass, critiques (walkthrough path + the series-level problem + a concrete fix), one-sentence summary.`,
      { schema: VERDICT, label:'series-review', phase:'Review', ...tier('series-review') })
  } catch (e) { log(`series review threw: ${e && e.message}`) }
  if (seriesReview) log(`Series review: ${seriesReview.pass ? 'PASS' : 'FLAGGED (' + (seriesReview.critiques || []).length + ' critique(s))'}; flags only, no block blocked`)
}
// The series README (D-0055) is generated from the plan; the Wire-tier agent renders it and rebuilds the tracker.
const wire = await agent(
  `WIRE step (D-0055). From ${ROOT}:\n` +
  `1. Run: python harness/series_readme.py ${A.week}   (renders ${A.demosDir}/README.md from the week plan; never edit that file by hand) and then python harness/series_readme.py ${A.week} --check, which must print OK.\n` +
  `2. Run: python harness/demo_check.py ${A.demosDir}   and quote its last line (fix nothing here; a problem is reported, the session resolves it).\n` +
  `3. From ${REPO_DIR} run: git log ${PREP} --oneline   and quote it: the session pushes the prep branch by hand ("git push -u origin ${PREP}"); you never push.\n` +
  `4. Run: python harness/build_tracker.py   so tracker.html matches the state you just changed.\n` +
  `Return a one-paragraph summary: the README state, the demo_check line, the prep branch log.`,
  { label:'wire', phase:'Review', ...tier('wire') })

// ---------- report ----------
const report = BLOCKS.map((b, i) => ({ block: b.name, day: b.dayId, ...compact(repairNull(done[i], b.name)) }))
const flagged = report.filter(r => r.status === 'flagged').map(r => ({ day: r.day, artifact: `demos:${r.block}`, flags: r.flags || [] }))
if (seriesReview && !seriesReview.pass) flagged.push({ day: BLOCKS[BLOCKS.length - 1].dayId, artifact:'series-review', flags:(seriesReview.critiques || []).map(c => `series-review: ${c}`) })

// ---------- RECORD (work tracker, D-0035) ----------
phase('Record')
const REPORT_FILE = `${H}/run-report.tmp.json`
const DAY_IDS = [...new Set(BLOCKS.map(b => b.dayId))]
const runRecord = {
  kind: 'demo-series', date: A.today, week: A.week, days: DAY_IDS, runId: null,
  agents: AGENTS + 1, minutes: null, tokens: null,
  tiers: { labels: TIER_LABELS, verified: null },
  artifacts: report.map(r => ({ day: r.day, name: `demos:${r.block}`, status: r.status || 'flagged', passes: r.passes || 0 })),
  flagged: flagged.length,
  flags: flagged.map(f => ({ day: f.day, artifact: f.artifact, flags: (f.flags || []).slice(0, 6).map(x => String(x).slice(0, 300)) })),
  tests: null, resolved: false, note: `prep branch ${PREP}; push it by hand after review`,
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
    `VERIFY step. From ${ROOT}: first run python harness/build_tracker.py, then run: python -m unittest discover -s tests -p "test_demos.py" -v ; python -m unittest discover -s tests -p "test_plans.py" -v ; python -m unittest discover -s tests -p "test_series_readme.py" -v   and python harness/series_readme.py ${A.week} --check. Report passed=true only if everything passes. List each failure as "<test>: <one-line cause>".\n` +
    (recorded
      ? `Then record the result: python harness/log_run.py amend --last --match-days ${DAY_IDS.join(',')} --agents ${AGENTS + 1} --tests pass   (use --tests fail when anything failed). If it refuses because the last record is not this run's, skip it and say so.`
      : `The Record step did not complete; do not amend the run log.`),
    { schema: VERIFY_SCHEMA, label:`verify:${attempt}`, phase:'Verify', ...tier('verify') })
  if (!verify || verify.passed || attempt === 3) break
  await agent(
    `FIX step (attempt ${attempt}). These contract tests failed: ${J(verify.failures)}. Fix the underlying walkthrough(s) under ${A.demosDir} or the plan's recorded rows — never weaken the tests or metrics, never touch ${REPO_DIR}'s ${REPO.branch || 'main'}. If a failure is the tracker staleness test, running python harness/build_tracker.py is the whole fix; if it is the README check, rerun python harness/series_readme.py ${A.week}. Re-run the failing tests with Bash until they pass. Return a short summary.`,
    { label:`fix:${attempt}`, phase:'Verify', ...tier('fix') })
}

log(`Run complete: ${BLOCKS.length} block(s), ${flagged.length} flagged item(s), tests ${verify && verify.passed ? 'PASS' : 'FAIL'}; run log ${recorded ? 'recorded' : 'NOT recorded'} (add the run id with: python harness/log_run.py amend --last --run-id <wf_...>). Push the prep branch by hand: git -C ${REPO_DIR} push -u origin ${PREP}`)
return { week: A.week, prepBranch: PREP, blocks: report, flaggedCount: flagged.length, flagged, seriesReview, wire, verify, recorded }
