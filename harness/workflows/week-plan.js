// week-plan.js — write one week's plan (harness/plans/week-WW.md) before any day of that week is authored (D-0034).
//
// Run ONCE per week, before the first day-fanout of the week:
//   python harness/args_for.py <week> --plan --today YYYY-MM-DD   -> paste as args (the ONLY source of these args)
//   Workflow({ scriptPath: "harness/workflows/week-plan.js", args: <that JSON> })
//
// One author agent + one critic (harness/critics/week-plan.md); one repass at most; then one Record agent that
// appends the run to harness/runs.jsonl and rebuilds tracker.html (D-0035). So <= 5 agents.
// The plan carries the Weekly Epic, the demo THREADS (one codebase growing rung by rung, D-0033), the ordered
// demo ladder with minutes and dependency guarantees, per-day AM/PM shape with stop points and squeeze
// priorities, the anti-spoiler and deliberate-deviation ledgers and the coverage map; args_for.py reads it to
// gate day args and to pass each day's rows into day-fanout.js.
//
// Model tiers (D-0032): `week-plan` (author) and `week-plan-critic` come from config.json models via args_for.py;
// tier() is copied from day-fanout.js, including the escalateOn repass rule. Every agent() call spreads a tier.
// Scripts cannot touch the filesystem or Date(); everything comes in through args.

export const meta = {
  name: 'week-plan',
  description: 'Week plan before any day: epic, demo threads and ladder, per-day shape, ledgers, coverage map (author + critic, one repass)',
  phases: [
    { title: 'Plan' },
    { title: 'Record' },
  ],
}

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
if (!A.root || !A.today || !A.week || !Array.isArray(A.days) || !A.days.length || !A.planFile || !A.template) throw new Error('args must come from `python harness/args_for.py <week> --plan` (root, today, week, days[], planFile, template required)')
if (!A.models || !A.models.stages || !A.models.stages['week-plan'] || !A.models.stages['week-plan-critic']) throw new Error('args.models.stages must carry week-plan and week-plan-critic (D-0032); regenerate args with args_for.py --plan')
const ROOT = A.root
const H = `${ROOT}/harness`
const M = A.metrics || {}
const CFG = A.config || {}
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
const TIER_LABELS = ['week-plan', 'week-plan-critic', 'wire'].map(tierLabel).join(' · ')
const J = (x) => JSON.stringify(x, null, 1)
const WW = String(A.week).padStart(2, '0')

const VERDICT = { type:'object', additionalProperties:false, properties:{ pass:{type:'boolean'}, critiques:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['pass','critiques','summary'] }
const PLAN_SCHEMA = { type:'object', additionalProperties:false, properties:{
  rungs:{type:'number'}, standalone:{type:'number'},
  demoMinutesPerDay:{ type:'array', items:{ type:'object', additionalProperties:false, properties:{ day:{type:'string'}, minutes:{type:'number'} }, required:['day','minutes'] } },
  endStateKey:{type:'string'}, estimatedKeyLines:{type:'number'}, summary:{type:'string'} },
  required:['rungs','standalone','demoMinutesPerDay','endStateKey','estimatedKeyLines','summary'] }

const fix = (cr) => cr && cr.length ? ('\n\nThis is a REPASS. The critic flagged these issues — fix every one, keep what was good:\n- ' + cr.join('\n- ')) : ''

const header =
  `WEEK ${A.week} "${A.theme}" (phase ${A.phase}, project ${A.project}; projects: ${J(A.projects || {})}). Dates ${A.weekStart} to ${A.weekEnd} (${A.timezone}); today ${A.today}. Use these dates only; never invent one.\n` +
  (A.weekNotes ? `Week note (binding): ${A.weekNotes}\n` : '') +
  (CFG.audience ? `Audience: ${CFG.audience.summary} Assume known: ${(CFG.audience.assumeKnown || []).join('; ')}. Do NOT assume: ${(CFG.audience.assumeNotKnown || []).join('; ')}. ${CFG.audience.rule || ''} Emphasise: ${(CFG.audience.emphasise || []).join('; ')}.\n` : '') +
  `Teaching days (id, date, title, subtopics in curriculum order, day note, demoFormat, exerciseKind, status, scripts already on disk, research brief if any): ${J(A.days)}\n` +
  `Threads in scope this week (config.json threads; the thread id, domain and week range are fixed): ${J(A.threads || {})}\n` +
  `Previous week's plan: ${A.previousPlan || 'none (first week)'}; previous end state per thread: ${J(A.previousEndState || {})}.\n` +
  `Metrics: demos ${J(M.demos || {})}; runbook ${J(M.runbook || {})}; notes steps ${(M.notes || {}).stepsMin}–${(M.notes || {}).stepsMax}.\n` +
  `Python ${CFG.python}. LLM config this week: ${J(A.llm || {})}. Root: ${ROOT}.\n`

async function gated(gen, crit) {
  let result = await gen(null, 1)
  for (let pass = 1; pass <= 2; pass++) {
    const v = await crit(result, pass)
    if (v && v.pass) return { status:'done', passes: pass, summary: (v.summary || (result && result.summary) || ''), result }
    if (pass === 2) return { status:'flagged', passes: 2, flags: (v ? v.critiques : ['critic returned null']), summary: (result && result.summary) || (v && v.summary) || '', result }
    result = await gen(v ? v.critiques : ['prior critic hard-failed (returned null) — regenerate from scratch, full quality bar'], pass + 1)
  }
}

log(`Model tiers: ${TIER_LABELS}; escalate on pass ≥ ${TIERS.escalateOn || '—'} → ${TIERS.escalate ? (TIERS.escalate.model || 'inherit') + '/' + (TIERS.escalate.effort || 'inherit') : 'off'}`)
phase('Plan')
const plan = await gated(
  (cr, pass) => agent(
    `You are the WEEK-PLAN author (D-0034). ${header}` +
    `Read, in this order: (1) ${A.template} — copy EVERY heading in that order and follow every rule in its comments; the tables are parsed mechanically, so keep the column names exact and one row per line. (2) ${A.critic} — what the critic checks. (3) ${H}/plan_check.py (docstring) — the mechanical check you must pass. (4) ${A.demoTemplate} and ${A.demosCritic} — the demo-thread contract (D-0033): a rung is one demo script whose .py answer key is the thread's WHOLE runnable end state, typed on top of the previous rung's key; transcript (.md) keys for terminal demos; caps maxTypedLinesPerRung and maxLinesPerThreadKey. (5) ${H}/curriculum.json (this week's days, the week and day notes, projects). (6) ${A.previousPlan ? A.previousPlan + ' (its last rung is this week\'s start state)' : 'no previous plan: this is the first week'}. (7) For every day whose status is live: its scripts in ${ROOT}/trainer/<rel>/demos/ — a live day is RECORDED AS-IS (same names, minutes, Thread, Starts from, keys; never ask to change it). (8) Any research brief listed above.\n` +
    `Write ${A.planFile} (create harness/plans/). Decide and record:\n` +
    `- Weekly Epic: one paragraph, what the learner can DO by Friday in the thread's domain, naming the artifact built along the trainer; it must be something the learner project of this block will need (A24).\n` +
    `- Threads: one "### <thread-id>" per thread in scope (ids and domains from the args; do not invent a thread). Rung rows for every demo of every planned day plus the live days' rows as-is. A rung ADDS to the previous end state (never re-scaffolds; a rewrite names what it replaces in Adds), ends runnable, and ends in a commit whose message is the row's Commit message (imperative, <= 50 chars). Size each rung so Adds fits ${(M.demos || {}).maxTypedLinesPerRung} typed lines in its minutes and the week's end state stays under ${(M.demos || {}).maxLinesPerThreadKey} lines (state the estimate in "End state this week"). The Domain line says how the same records survive every week of the thread's scope.\n` +
    `- Standalone demos: only subtopics that fit no thread, each with its reason (A23); "none this week" rows are not needed, an empty table is fine but keep the heading.\n` +
    `- Demo ladder: every rung and standalone demo once, in teaching order, with minutes (${(M.demos || {}).minutesPerScriptMin}–${(M.demos || {}).minutesPerScriptMax} each, ${(M.demos || {}).scriptsMin}–${(M.demos || {}).scriptsMax} per day, numbered 01.. per day in that order), Must follow (cite the previous rung at least) and a concrete Guarantee.\n` +
    `- Per-day shape for EVERY teaching day (live ones too, matching their runbook): AM/PM blocks naming every demo, facilitation subtopic, notes handoff, exercise briefing and exercise; demo minutes; stop points naming a demo step and where the remainder lands; Cut first / Never cut (never cut a rung a later day starts from). The whole day must fit ${(M.runbook || {}).dayMinutesMin}–${(M.runbook || {}).dayMinutesMax} minutes with a 60-minute lunch and breaks.\n` +
    `- Anti-spoiler ledger: what each day defers and to which day/week, honouring the week note and the curriculum order.\n` +
    `- Real-world framing paragraph + deliberate-deviation table: every "nobody builds it this way" shape in the rungs gets a row (deviation / workplace reality / pedagogical reason).\n` +
    `- Coverage map: EVERY subtopic of EVERY teaching day, spelled exactly as the args list them, once; Demo = a demo of that day (fluency subtopics), "facilitation" (concept subtopics: a timed runbook block), or "notes" (with the reason in the per-day shape); Notes step = the page step (1-based, pages have ${(M.notes || {}).stepsMin}–${(M.notes || {}).stepsMax} steps).\n` +
    `Write plainly (D-0029): present tense, concrete names, no filler, no "not X but Y", no stock AI words.\n` +
    `Before returning, with Bash: run "python ${H}/plan_check.py ${A.planFile}" until it prints OK (fix the plan, never the checker).\n` +
    `Return rungs, standalone, demoMinutesPerDay (one entry per teaching day), endStateKey (the last rung's key path), estimatedKeyLines, summary (2 sentences).` + fix(cr),
    { schema: PLAN_SCHEMA, label:`week-${WW}:plan`, phase:'Plan', ...tier('week-plan', pass) }),
  (_r, pass) => agent(
    `WEEK-PLAN CRITIC (pass ${pass}). Read ${A.critic} and apply every item to ${A.planFile}. Use Bash: run "python ${H}/plan_check.py ${A.planFile}" and quote its output verbatim; open ${H}/curriculum.json, ${H}/metrics.json, ${A.demoTemplate}, ${A.demosCritic}${A.previousPlan ? ', ' + A.previousPlan : ''} and, for every live day, its scripts under ${ROOT}/trainer/<rel>/demos/. Context: ${header}` +
    `Return pass, critiques (section + row + concrete fix), one-sentence summary.`,
    { schema: VERDICT, label:`week-${WW}:plan-crit`, phase:'Plan', ...tier('week-plan-critic') }))

// ---------- RECORD (work tracker, D-0035) ----------
// The plan file changes what the tracker shows for the whole week, and the run itself is recorded in
// harness/runs.jsonl. Run id, tokens and minutes are invisible to a script: the session adds them afterwards
// with `python harness/log_run.py amend --last --run-id wf_... --minutes M --tokens T --tiers-verified yes`.
phase('Record')
const planFlags = plan && plan.flags ? plan.flags : []
const runRecord = {
  kind: 'week-plan', date: A.today, week: A.week, days: [], runId: null, agents: AGENTS + 1, minutes: null, tokens: null,
  tiers: { labels: TIER_LABELS, verified: null },
  artifacts: [{ day: null, name: 'plan', status: plan ? plan.status : 'flagged', passes: plan ? plan.passes : 0 }],
  flagged: (!plan || plan.status === 'flagged') ? 1 : 0,
  flags: (!plan || plan.status === 'flagged') ? [{ day: null, artifact: 'plan', flags: (planFlags.length ? planFlags : ['author or critic hard-failed']).slice(0, 6).map(x => String(x).slice(0, 300)) }] : [],
  tests: null, resolved: false, note: '',
}
const recorded = await agent(
  `RECORD step (work tracker, D-0035).\n` +
  `1. With the Write tool (not echo, not a heredoc) create ${H}/run-report.tmp.json containing EXACTLY this JSON:\n${JSON.stringify(runRecord)}\n` +
  `2. From ${ROOT} run: python harness/log_run.py add harness/run-report.tmp.json\n` +
  `   It validates the record, appends it to harness/runs.jsonl, deletes the temp file and rebuilds tracker.html. If it rejects the record, fix only what its message names in the temp file and retry. Never edit harness/runs.jsonl or tracker.html by hand.\n` +
  `3. Run: python harness/build_tracker.py --check   and return its one-line output.`,
  { label:`week-${WW}:record`, phase:'Record', ...tier('wire') })

log(`Week ${A.week} plan ${plan ? plan.status : 'hard-failed'} after ${plan ? plan.passes : 0} pass(es)${plan && plan.flags ? ': ' + plan.flags.length + ' open critique(s)' : ''}; run log ${recorded ? 'recorded' : 'NOT recorded'} (add the run id with: python harness/log_run.py amend --last --run-id <wf_...>)`)
return { week: A.week, recorded, planFile: A.planFile, status: plan ? plan.status : 'flagged', passes: plan ? plan.passes : 0, flags: plan && plan.flags ? plan.flags : [], summary: plan ? plan.summary : 'author hard-failed', result: plan ? plan.result : null }
