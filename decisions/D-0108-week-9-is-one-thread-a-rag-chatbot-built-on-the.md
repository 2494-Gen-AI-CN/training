# D-0108 — Week 9 is one thread, a RAG chatbot built on the learners' own machines with Bedrock for chat and embeddings; no Colab and no hybrid

- Date: 2026-11-24
- Status: accepted
- Decision: Week 9 is one thread, a RAG chatbot built on the learners' own machines with Bedrock for chat and embeddings; no Colab and no hybrid
- Why: Decided by the trainer in session 2026-11-24. A RAG chatbot is a common industry use and the curriculum's week-9 topics already are its stages (a model call and prompt, retrieval over a vector store, structured output and logging, conversation memory, Streamlit). Learners may not use Anthropic API keys, so every model call goes through Bedrock. All local was chosen over Colab for Monday to Thursday with a local Friday: one environment, AWS credentials in a profile instead of pasted into a notebook, an app in files from the first day, no port on Friday, and the walkthrough machinery of weeks 1 to 4 instead of an untested mixed week.
- Affects: harness/curriculum.json (week 9 notes), harness/plans/week-09.md (to write), STATUS.md O-33, harness/config.json llm.byWeek.9 (already Bedrock), the future qc-5 file, projects/official/P2 (to write)
- Supersedes: —
- Superseded-by: —

## Notes

Runtime found the same day: chromadb, langchain-chroma and langchain-pinecone do not install on the course Python 3.15; the whole set resolves on Python 3.12 (dry run, nothing installed; 3.13 not tried). The trainer accepts another interpreter (it does not have to be 3.15). Proposed, to settle in the week-9 plan: embeddings from Bedrock too, so no PyTorch locally and week 8's collections are re-embedded by a script; Chroma as the store with a ten-minute swap to Pinecone; the RAG chatbot as a Project 2 option, which D-0101 then requires to be built end to end in the demos, as this thread does. Open with Revature: who provides AWS accounts, which Bedrock models are enabled, the spend cap. Rejected: the hybrid; pulling RAG into week 8 (D-0107 keeps it in week 9).
