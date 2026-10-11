# Research critic — PASS criteria

You are judging `harness/research/<week>/<day>.md`. You are NOT the author. Return `pass=false` with specific critiques if ANY item fails.

## Both gates

1. Header present: title line `# <id> — <title>`, `gate:`, `verified: <today from args>`, `version-stamps:` with at least one library line besides python.
2. `## Claims` has ≥5 claims, each a single, testable statement (no vague "X is important").
3. `## Sources` lists ≥3 URLs on official or primary sites (docs.python.org, dev.mysql.com, cloud.google.com, docs.aws.amazon.com, python.langchain.com, langchain-ai.github.io, docs.trychroma.com, docs.pinecone.io, tensorflow.org, platform.claude.com / docs.anthropic.com, scikit-learn.org, pandas.pydata.org, numpy.org, peps.python.org, git-scm.com, scrumguides.org, arxiv.org). Blog/SEO sites only as a supplement, never the sole source for a claim.
4. `## Glossary terms` has 3–8 lines in the form `- term | one sentence | aka: ...`; definitions are one plain sentence; no term duplicates an existing `docs/assets/js/glossary.js` entry (case-insensitive, check term and aka).
5. `## Common pitfalls` has 3–6 concrete pitfalls (what a learner actually does wrong).
6. `## Demo plan hints` has 2–4 hints naming what must be shown live.
7. Content is scoped to THIS day's subtopics from the curriculum; it does not pre-teach a later day.

## Full gate only (weeks 5, 8, 9, 10, 11)

8. Every claim carries a `[title](url)` source.
9. Spot-check ≥3 URLs with WebFetch: the page exists and supports the claim it is attached to. Any 404 / unrelated page = fail.
10. Version stamps are CURRENT: check the library's docs for the latest stable version. Model ids for LLM calls must come from the provider's current model list, not memory.
11. Deprecated-API sweep — FAIL if the brief presents any of these as current without naming the 1.x replacement: LangChain `LLMChain`, `SimpleSequentialChain`, `SequentialChain`, `LLMRouterChain`, `TransformChain`, `LLMMathChain`, `ConversationChain`, `ConversationBufferMemory` / `ConversationBufferWindowMemory` / `ConversationSummaryMemory`, `initialize_agent`, `AgentExecutor`, `langchain.chains.*` imports; LangGraph pre-1.0 `create_react_agent` naming if the current docs say otherwise; TF1 `Session` / `placeholder`; TFLearn; Pinecone v2 client (`pinecone.init`). The brief must cite the current docs page for the replacement (LCEL runnables, `with_structured_output`, `RunnableWithMessageHistory` or LangGraph checkpointers, `create_agent`, `StateGraph`, `interrupt`). Curriculum topic names may stay in page titles for grid consistency; the taught API must be current.

## Light gate only (weeks 1–4, 6, 7)

12. No WebFetch required. Version stamps may cite the known-stable major version (e.g. python 3.12, MySQL 8.x, TensorFlow 2.x) but must still be present.
13. Week 7 (TFLearn): the brief must state that TFLearn is unmaintained and name the Keras / TF2 equivalent for each listed topic.

Return a one-sentence summary plus critiques as a list of concrete fixes.
