# D-0106 — Week 8's four teaching days are notebook days; Chroma and Pinecone are both hands-on, each learner on a free Pinecone account

- Date: 2026-11-24
- Status: accepted
- Decision: Week 8's four teaching days are notebook days; Chroma and Pinecone are both hands-on, each learner on a free Pinecone account
- Why: Decided by the trainer in session 2026-11-24, before the week-8 plan is written. Weeks 6 and 7 run as Colab notebooks (D-0085) and W8D1 needs scikit-learn and Keras, which do not run on the course Python 3.15; the vector-database days stay in the same place and form so the room does not switch tools for three days. The trainer wants learners to have used a hosted vector database themselves, not only watched one.
- Affects: harness/curriculum.json (w08d1 to w08d4 demoFormat notebook, w08d2 day note), harness/plans/week-08.md, STATUS.md O-32
- Supersedes: —
- Superseded-by: —

## Notes

Install-ahead item O-32: a free Pinecone account and API key per learner, announced in week 7 and checked at the start of W8D2. The key is read from Colab Secrets, never typed into a cell: the demo repo and the learner repos are public. Key-gated cells are compile-checked only by critics (AGENTS.md); the trainer rehearses the Pinecone cells on a fresh Colab runtime before the day. Rejected: Chroma hands-on with Pinecone shown from the trainer's account; a typed walkthrough thread on local Python for the vector-database days.
