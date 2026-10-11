# D-0026 — Per-stage model and effort tiers for the day workflow in config.json models: cheap tiers (sonnet/haiku) for light-gate research, demos, exercise, runbook, wire and verify; session model at high effort for notes and full-gate research; session model for every critic; any repass from pass 2 escalates to the session model at high effort

- Date: 2026-10-11
- Status: accepted
- Decision: Per-stage model and effort tiers for the day workflow in config.json models: cheap tiers (sonnet/haiku) for light-gate research, demos, exercise, runbook, wire and verify; session model at high effort for notes and full-gate research; session model for every critic; any repass from pass 2 escalates to the session model at high effort
- Why: Both pilot runs spent ~1.5M subagent tokens with every one of 20 agents on the session model at session effort. Authors of structured artifacts and mechanical steps do not need the strongest tier; critics stay strong because they are the gate; the escalate rule bounds the cost of a cheap pass that fails to one extra pass.
- Affects: harness/config.json (models), harness/args_for.py (models passthrough), harness/workflows/day-fanout.js (tier(), gated() pass number, every agent() opts), AGENTS.md
- Supersedes: —
- Superseded-by: —

## Notes

Not yet measured: the first run under this map should be compared against wf_ce312ce5-ce9 (20 agents, 1.53M tokens, 0 flagged) on flag count, passes per artifact and tokens. If critic-fail rate on pass 1 rises sharply, raise the author tiers before raising escalateOn.
