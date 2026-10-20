# Research critic — PASS criteria

You are judging `harness/research/<week>/<day>.md`. You are NOT the author. Return `pass=false` with specific critiques if ANY item fails.

## Both gates

1. Header present: title line `# <id> — <title>`, `gate:`, `verified: <today from args>`, `version-stamps:` with at least one library line besides python.
2. `## Claims` has ≥ `metrics.research.claimsMin` (12) claims, each a single, testable statement (no vague "X is important").
3. `## Sources` lists ≥ `metrics.research.sourcesMin` (5) URLs on official or primary sites (docs.python.org, dev.mysql.com, cloud.google.com, docs.aws.amazon.com, python.langchain.com, langchain-ai.github.io, docs.trychroma.com, docs.pinecone.io, tensorflow.org, platform.claude.com / docs.anthropic.com, scikit-learn.org, pandas.pydata.org, numpy.org, peps.python.org, git-scm.com, scrumguides.org, arxiv.org). Blog/SEO sites only as a supplement, never the sole source for a claim.
4. `## Glossary terms` has 3–8 lines in the form `- term | one sentence | aka: ...`; definitions are one plain sentence; no term duplicates an existing `docs/assets/js/glossary.js` entry (case-insensitive, check term and aka).
5. `## Common pitfalls` has 3–6 concrete pitfalls (what a learner actually does wrong).
6. `## Demo plan hints` has 2–4 hints naming what must be shown live.
7. Content is scoped to THIS day's subtopics from the curriculum; it does not pre-teach a later day. When the prompt carries week-plan rows (D-0034), the brief covers exactly the day's coverage rows, its `## Demo plan hints` name the plan's demos for the day (the thread rows, in ladder order), and nothing the anti-spoiler rows defer to a later day appears as content.
7b. `## Notes depth` (D-0040; the notes page's study material) has one `### <subtopic>` block per curriculum subtopic of the day, spelled as the curriculum lists it, each with all five bullets: `Interview questions` (≥2 junior-level questions plus one follow-up a level beyond), `Adjacent concept` (the usual next question; it is NOT a subtopic of a later day), `Trade-off or limit` (sourced), `Recognise on sight` (a snippet or pattern name), `Claims` (3–6 testable statements, each with `[title](url)` on an official domain from item 3's list). On a full gate every URL in this section is fetched; on a light gate it must be an official-doc URL the author is confident exists. The item-11 deprecated-API sweep covers this section too.
7c. Exit criteria (D-0063): when the prompt carries EXIT CRITERIA rows, the `## Notes depth` block of the subtopic the row's Notes step teaches has an `Interview questions` bullet that answers the criterion, ending with its id in parentheses (`(qc2.sql.R07)`); every listed id appears at least once; an id the prompt does not list is a FAIL (a later week's criterion pre-taught).

## Full gate only (weeks 5, 8, 9, 10, 11)

8. Every claim carries a `[title](url)` source.
9. Spot-check ≥3 URLs with WebFetch: the page exists and supports the claim it is attached to. Any 404 / unrelated page = fail.
10. Version stamps are CURRENT: check the library's docs for the latest stable version. Model ids for LLM calls must come from the provider's current model list, not memory. Wheel rule (D-0058): for every third-party library the demos install, the stamp line names, after the version (inside the parenthetical or the trailing `#` comment, never before the version), the wheel pip will pick for the course Python (`config.json` `python`) on `win_amd64`: a `cpXYZ-cpXYZ-win_amd64` wheel or a pure-Python `py3-none-any` / `py2.py3-none-any` wheel, checked on PyPI (`https://pypi.org/pypi/<name>/json`, the `releases[<version>]` filenames). A library with neither for the course Python is a FAIL that names the newest Python every library of the week supports, so the pin (D-0041) can be revisited by a decision entry.
11. Deprecated-API sweep — FAIL if the brief presents any of these as current without naming the 1.x replacement: LangChain `LLMChain`, `SimpleSequentialChain`, `SequentialChain`, `LLMRouterChain`, `TransformChain`, `LLMMathChain`, `ConversationChain`, `ConversationBufferMemory` / `ConversationBufferWindowMemory` / `ConversationSummaryMemory`, `initialize_agent`, `AgentExecutor`, `langchain.chains.*` imports; LangGraph pre-1.0 `create_react_agent` naming if the current docs say otherwise; TF1 `Session` / `placeholder`; TFLearn; Pinecone v2 client (`pinecone.init`). The brief must cite the current docs page for the replacement (LCEL runnables, `with_structured_output`, `RunnableWithMessageHistory` or LangGraph checkpointers, `create_agent`, `StateGraph`, `interrupt`). Curriculum topic names may stay in page titles for grid consistency; the taught API must be current.

## Light gate only (weeks 1–4, 6, 7)

12. No WebFetch required for claims. Version stamps may cite the known-stable major version (e.g. python 3.15, MySQL 9.x, TensorFlow 2.x) but must still be present; the one fetch a light gate still makes is the PyPI wheel check of item 10 for each library the demos install.
13. Week 7 (TFLearn): the brief must state that TFLearn is unmaintained and name the Keras / TF2 equivalent for each listed topic.

Return a one-sentence summary plus critiques as a list of concrete fixes.
