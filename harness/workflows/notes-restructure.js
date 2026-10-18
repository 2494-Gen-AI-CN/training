// notes-restructure.js — the readability pass over notes pages that are already written (D-0060).
//
// A live page keeps every fact, code block, heading, citation and number it has; this pass changes only the
// CONTAINERS of its prose: a paragraph over the cap is split at an idea boundary, a sentence that enumerates
// three or more parallel things becomes a list or a table, a sentence over the cap or with too many inline code
// spans is broken up or listed, every code block gets the sentence that states its output directly under it, and a
// "Takeaways" recap (div.recap, 2–4 one-line items drawn from the step) goes in front of each interview callout.
// Nothing is reworded (that is the humanizer's job, D-0029) and no output block is invented (pre.out is for pages
// authored from week 3 on, whose author runs the example).
//
// Run:
//   python harness/args_for.py --restructure [--today YYYY-MM-DD]        every authored or live page
//   python harness/args_for.py 1 2 --restructure                          one week, named day slots
//   Workflow({ scriptPath: "harness/workflows/notes-restructure.js", args: <that JSON> })
//
// Per page, in parallel: an author agent (tier `restructure`, sonnet first; the escalate tier from pass 2) edits one
// section.step per Edit call and verifies with harness/prose_guard.py check --restructure (the guard: code, headings,
// citations, numbers, scripts, section.practice, callouts frozen; per-step word delta bounded) and
// harness/notes_check.py --style (the bar). A gate agent (tier `verify`) re-runs both commands and reads
// `git status`: it judges nothing a script cannot; up to 3 passes, then the page is flagged (never blocks the others).
// Then Record (run log + work tracker, D-0035) and Verify (contract tests, ≤2 fix loops). Agents: 2–6 per page + 2.
//
// Scripts cannot touch the filesystem or Date(); everything comes in through args.

export const meta = {
  name: 'notes-restructure',
  description: 'Readability pass over written notes pages (D-0060): split paragraph walls, listify enumerations, add a Takeaways recap per step, keep output next to code; prose-guarded (--restructure) and gated by notes_check.py --style',
  phases: [
    { title: 'Restructure' },
    { title: 'Record' },
    { title: 'Verify' },
  ],
}

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
if (!A.root || !A.today || !Array.isArray(A.pages) || !A.pages.length || A.mode !== 'restructure') throw new Error('args must come from `python harness/args_for.py [week [day...]] --restructure` (root, today, pages[], mode required)')
if (!A.models || !A.models.stages || !A.models.stages.restructure) throw new Error('args.models.stages must carry restructure (D-0060); regenerate args with args_for.py')
const ROOT = A.root
const H = `${ROOT}/harness`
const M = A.metrics || {}
const MN = M.notes || {}
const MP = MN.prose || {}
const PAGES = A.pages
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
const TIER_LABELS = ['restructure', 'verify', 'wire'].map(tierLabel).join(' · ')
const J = (x) => JSON.stringify(x, null, 1)
const MAX_PASSES = 3

const RESULT = { type:'object', additionalProperties:false, properties:{
  snapshot:{type:'string'}, stepsEdited:{type:'number'}, paragraphsSplit:{type:'number'}, listsAdded:{type:'number'}, tablesAdded:{type:'number'},
  recapsAdded:{type:'number'}, declaredMinutes:{type:'number'}, guardLastLine:{type:'string'}, checkLastLine:{type:'string'}, summary:{type:'string'} },
  required:['snapshot','stepsEdited','paragraphsSplit','listsAdded','tablesAdded','recapsAdded','declaredMinutes','guardLastLine','checkLastLine','summary'] }
const GATE = { type:'object', additionalProperties:false, properties:{ pass:{type:'boolean'}, critiques:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['pass','critiques','summary'] }
const VERIFY_SCHEMA = { type:'object', additionalProperties:false, properties:{ passed:{type:'boolean'}, failures:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['passed','failures','summary'] }

const fix = (cr) => cr && cr.length ? ('\n\nThis is a REPASS. The gate found these problems — fix every one, keep what was good:\n- ' + cr.join('\n- ')) : ''
const repairNull = (x, label) => x || ({ task: label, status:'flagged', passes:0, flags:['agent hard-failed (structured return / terminal error)'], summary:'hard-fail' })
const compact = (x) => x ? ({ task:x.task, status:x.status, passes:x.passes, ...(x.flags ? {flags:x.flags} : {}), summary:x.summary }) : null

const bar = () =>
  `THE BAR (metrics.notes.prose, D-0060; python ${H}/notes_check.py <page> --style counts it, every "style:" line is a hard finding): inside the teaching steps (every section.step but the last "Check yourself" one) ` +
  `a paragraph has at most ${MP.paragraphWordsMax || 80} prose words; a sentence has at most ${MP.sentenceWordsMax || 40} words and at most ${MP.codeSpansPerSentenceMax || 5} inline <code> spans (interview callouts exempt); ` +
  `the page has at least ${MP.structuredBlocksMin || 3} <ul>/<ol>/<table> inside teaching steps (recap lists excluded); each teaching step ends with <div class="recap"><div class="k">${MP.recapLabel || 'Takeaways'}</div><ul>…</ul></div> ` +
  `(${MP.recapItemsMin || 2}–${MP.recapItemsMax || 4} <li>, each at most ${MP.recapItemWordsMax || 20} words) immediately before its <div class="callout interview">; every <pre> is followed by a <p> (or <pre class="out">).\n`

const author = (p, cr, pass, snapshot) => agent(
  `You are the RESTRUCTURE agent for the notes page ${p.pageFile} (${p.id} "${p.title}", D-0060). The page is live study material; every fact, code block, heading, citation and number it has stays exactly as it is. You change the CONTAINERS of its prose so it reads more easily. You do not reword sentences (that was the humanizer's pass) and you add no fact.\n` +
  bar() +
  (snapshot
    ? `1. The guard snapshot of the ORIGINAL page is ${snapshot} (taken before your first pass; never take another).\n`
    : `1. FIRST, before any edit, from ${ROOT} run: python harness/prose_guard.py snapshot ${p.pageFile}   and keep the directory it prints (return it as snapshot).\n`) +
  `2. Read the whole page. Run python harness/notes_check.py ${p.pageFile} --style   and treat every "style:" line as your to-do list. Read ${p.researchFile} only to make sure a recap item restates something the page already says.\n` +
  `3. Work ONE section.step per Edit call (never a whole-file Write). Allowed changes, inside teaching steps only:\n` +
  `   - split a paragraph over the cap into two or more <p> at an idea boundary (the words stay; only the split moves);\n` +
  `   - turn a sentence that enumerates three or more parallel things (file modes, exception types, dict keys, "how to X, how to Y and how to Z") into a <ul>, or a <table> (thead + tbody, one row per thing) when each thing carries two or more attributes; every word, inline <code> span and <sup class="cite"> marker of the sentence survives inside the items, in order;\n` +
  `   - break a sentence over the word cap at a clause boundary into shorter sentences (a comma or semicolon becomes a full stop and a capital; no other word changes), or list it when it is an enumeration;\n` +
  `   - move a sentence with too many inline <code> spans into a list or table the same way;\n` +
  `   - when a <pre> is followed by anything but a <p>, move the existing sentence that states its output to directly after it (invent no output, add no <pre class="out">);\n` +
  `   - add exactly one <div class="recap"><div class="k">${MP.recapLabel || 'Takeaways'}</div><ul><li>…</li></ul></div> immediately BEFORE the step's <div class="callout interview">: ${MP.recapItemsMin || 2}–${MP.recapItemsMax || 4} items (two when the page is within 150 words of ${MN.wordMax || 7000}), each one plain line of at most ${MP.recapItemWordsMax || 20} words that restates something this step's prose says, no code block, no bold, no new fact, no repeat of the h3 headings.\n` +
  `   Reach at least ${MP.structuredBlocksMin || 3} lists or tables on the page from the enumerations the page already has.\n` +
  `4. FROZEN (the guard fails the page otherwise): every word inside <pre> and <code>; every heading; the .tag, .k and .meta labels (except the "~N min" span); every <sup class="cite"> marker (they move with their sentence, never dropped, never renumbered); every number in step prose; URLs; the inline scripts; the lede, the "Check yourself" step, section.practice, section.reading-sources, every .callout, every details block and every .ix-* widget; the tag skeleton outside the teaching steps. Plain <p>/<ul>/<ol>/<li>/<table>/<thead>/<tbody>/<tr>/<th>/<td> carry no attributes (an attribute freezes them). Use the Edit tool only, never sed or a heredoc.\n` +
  `5. After every step: from ${ROOT} run python harness/prose_guard.py check --restructure <snapshot> ${p.pageFile}   (must print OK; a WARN about citation order is fine, a WARN about numbers outside steps means restore them) and python harness/notes_check.py ${p.pageFile} --counts --style --phrases --citations --stamps   (no finding except the "~N min" one until step 6).\n` +
  `6. Set the .meta "~N min" to round(prose words / ${MN.readingWpm || 150}) and re-run both commands until both print OK with no finding. Touch no other file.\n` +
  `Return snapshot, stepsEdited, paragraphsSplit, listsAdded, tablesAdded, recapsAdded, declaredMinutes, guardLastLine, checkLastLine (the last line each command printed), summary.` + fix(cr),
  { schema: RESULT, label:`${p.id}:restructure`, phase:'Restructure', ...tier('restructure', pass) })

const gate = (p, r) => agent(
  `GATE for the restructure pass on ${p.pageFile} (D-0060). You run three commands and report; you judge nothing a script cannot and you edit no file.\n` +
  `1. From ${ROOT}: python harness/prose_guard.py check --restructure ${r.snapshot} ${p.pageFile}   It must print "OK ${p.pageFile}" (or UNCHANGED is a FAIL: the pass did nothing). Every indented line under a FAIL is a critique, quoted. A "WARN citation order" line is fine; a "WARN numbers outside code changed" line is a critique.\n` +
  `2. From ${ROOT}: python harness/notes_check.py ${p.pageFile} --counts --phrases --stamps --citations --style   It must print "OK". Every finding line is a critique, quoted.\n` +
  `3. From ${ROOT}: git status --porcelain   Any changed or new file other than ${p.pageFile} (ignore other docs/weeks/*.html pages, which other agents are editing in parallel) is a critique naming the file.\n` +
  `Return pass (true only when all three are clean), critiques, one-sentence summary.`,
  { schema: GATE, label:`${p.id}:restructure-gate`, phase:'Restructure', ...tier('verify') })

async function restructure(p) {
  const label = `${p.id} restructure`
  let r = await author(p, null, 1, null)
  for (let pass = 1; pass <= MAX_PASSES; pass++) {
    if (!r) return { task: label, status:'flagged', passes: pass, flags:['author hard-failed (structured return / terminal error)'], summary:'hard-fail' }
    const v = await gate(p, r)
    if (v && v.pass) return { task: label, status:'done', passes: pass, summary: v.summary || r.summary, result: r }
    if (pass === MAX_PASSES) return { task: label, status:'flagged', passes: pass, flags: (v ? v.critiques : ['gate returned null']), summary: r.summary, result: r }
    const next = await author(p, v ? v.critiques : ['the gate hard-failed (returned null): re-run both checks yourself and fix what they print'], pass + 1, r.snapshot)
    r = next ? { ...next, snapshot: r.snapshot } : null
  }
}

phase('Restructure')
log(`Restructure pass over ${PAGES.length} page(s): ${PAGES.map(p => p.id).join(', ')} · tiers ${TIER_LABELS}`)
const results = await parallel(PAGES.map(p => () => restructure(p).catch(e => ({ task:`${p.id} restructure`, status:'flagged', passes:0, flags:[String(e).slice(0, 300)], summary:'threw' }))))
const report = results.map((x, i) => compact(repairNull(x, `${PAGES[i].id} restructure`)))
const flagged = report.filter(r => r.status === 'flagged').map((r, i) => ({ day: r.task.split(' ')[0], artifact:'notes', flags: r.flags || [] }))

// ---------- RECORD (work tracker, D-0035) ----------
phase('Record')
const REPORT_FILE = `${H}/run-report.tmp.json`
const DAY_IDS = PAGES.map(p => p.id).join(',')
const runRecord = {
  kind: 'notes-restructure', date: A.today, week: A.week, days: PAGES.map(p => p.id), runId: null,
  agents: AGENTS + 1, minutes: null, tokens: null,
  tiers: { labels: TIER_LABELS, verified: null },
  artifacts: report.map(r => ({ day: r.task.split(' ')[0], name: 'notes', status: r.status, passes: r.passes })),
  flagged: flagged.length,
  flags: flagged.map(f => ({ day: f.day, artifact: f.artifact, flags: (f.flags || []).slice(0, 6).map(x => String(x).slice(0, 300)) })),
  tests: null, resolved: false, note: 'readability restructure pass (D-0060): containers only, prose-guarded --restructure, gated by notes_check.py --style',
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
    `VERIFY step. From ${ROOT}: first run python harness/build_tracker.py (work tracker, D-0035), then run: python -m unittest discover -s tests -v   Report passed=true only if everything passes. List each failure as "<test>: <one-line cause>".\n` +
    (recorded
      ? `Then record the result: python harness/log_run.py amend --last --match-days ${DAY_IDS} --agents ${AGENTS + 1} --tests pass   (use --tests fail when anything failed). If it refuses because the last record is not this run's, skip it and say so.`
      : `The Record step did not complete; do not amend the run log.`),
    { schema: VERIFY_SCHEMA, label:`verify:${attempt}`, phase:'Verify', ...tier('verify') })
  if (!verify || verify.passed || attempt === 3) break
  await agent(
    `FIX step (attempt ${attempt}). These contract tests failed: ${J(verify.failures)}. Fix ONLY the page(s) of this run, ${J(PAGES.map(p => p.pageFile))}, within the restructure rules (containers only; code, headings, citations, numbers frozen) — never weaken the tests or metrics, never edit a page that is not in this run (a "style:" failure on another live page means that page still awaits its own pass: report it and leave it). If a failure is the tracker staleness test (tests/test_tracker.py, "stale"), running python harness/build_tracker.py is the whole fix. Re-run the failing tests with Bash until the ones about this run's pages pass. Return a short summary.`,
    { label:`fix:${attempt}`, phase:'Verify', ...tier('fix') })
}

log(`Restructure complete: ${PAGES.length} page(s), ${flagged.length} flagged, tests ${verify && verify.passed ? 'PASS' : 'FAIL'}; run log ${recorded ? 'recorded' : 'NOT recorded'} (add the run id with: python harness/log_run.py amend --last --run-id <wf_...>)`)
return { pages: PAGES.map(p => p.id), flaggedCount: flagged.length, flagged, verify, report, recorded }
