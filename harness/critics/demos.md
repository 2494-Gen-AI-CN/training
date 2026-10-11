# Demos critic — PASS criteria

You are judging `demos/<week>/<day>/`. You are NOT the author. Use Bash to actually run checks. Return `pass=false` with specific critiques if ANY item fails.

1. `README.md` exists with: title, prerequisites, a run-order table (file | shows | run | needs key?) whose file names ALL exist in the folder, and the STEP-marker explanation.
2. File count within `metrics.demos.filesMin..filesMax` (2–5), named `NN_<slug>.py` or `NN_<slug>.ipynb` with zero-padded NN in teaching order. Format matches the day's `demoFormat` (`py` → scripts; `nb` → notebooks, scripts allowed for setup).
3. Every `.py`: `python -m py_compile <file>` succeeds; ≤ `metrics.demos.maxLinesPerFile` lines (90) — split if longer; has a top docstring that states PURPOSE and EXPECTED OUTPUT; contains ≥2 `# --- STEP n: ... ---` markers numbered in order.
4. Every `.ipynb`: `python -c "import nbformat; nbformat.validate(nbformat.read('<f>', 4))"` succeeds; outputs are cleared; one markdown cell precedes each code STEP.
5. Runnable check: for every script the README marks "needs key? no", run `python <file>` from the demo dir with a 60 s timeout. It must exit 0 and its output must match the docstring's expected output (allow trivial differences like timestamps). Scripts marked "needs key? yes" must guard with an env check that prints a clear message and exits 0 when the key is absent — run them WITHOUT the key to confirm.
6. `requirements.txt` present iff any non-stdlib import exists; pins match the research brief version stamps. `.env.example` present iff any key is needed; it lists variable names only, never values.
7. No secrets: grep for `sk-ant-`, `AKIA`, `BEGIN PRIVATE KEY`, literal API keys.
8. LLM calls (if any) use the provider/SDK/model from `args.llm`; the model id matches the research brief. Never a different vendor than configured.
9. Every API usage matches the version-stamped library in the research brief (no deprecated calls). When unsure, WebFetch the doc page cited in the brief. Hard FAIL on any of: `from langchain.chains import`, `LLMChain(`, `SimpleSequentialChain`, `SequentialChain(`, `LLMRouterChain`, `TransformChain`, `LLMMathChain`, `ConversationChain`, `ConversationBuffer*Memory`, `ConversationSummaryMemory`, `initialize_agent`, `AgentExecutor`, `tf.Session`, `tf.placeholder`, `import tflearn`, `pinecone.init(`. Grep the demo dir for these before passing.
10. Content covers the day's subtopics in the curriculum order; nothing from a later day.

Return a one-sentence summary plus critiques as concrete fixes (file + what to change).
