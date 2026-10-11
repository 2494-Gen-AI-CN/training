# {{title}} — code-along demos

Week {{week}} · Day {{day}} · `{{id}}`
Notes: [docs/weeks/{{rel}}.html](../../../docs/weeks/{{rel}}.html) · Exercise: [exercises/{{rel}}](../../../exercises/{{rel}})

## Prerequisites

- Python {{python}}
- `pip install -r requirements.txt` (only if this folder has one)
- Keys: copy `.env.example` → `.env` (only if this folder has one)

## Run order

| # | File | Shows | Run | Needs key? |
|---|---|---|---|---|
| 1 | `01_<slug>.py` | ... | `python 01_<slug>.py` | no |
| 2 | `02_<slug>.py` | ... | `python 02_<slug>.py` | no |

Each file is split into `# --- STEP n: ... ---` checkpoints. The trainer types STEP by STEP; trainees follow along. The top docstring states what the file demonstrates and the expected output.
