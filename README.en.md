# Verification Guide

"검증 가이드" (Verification Guide) is a Claude Code / Codex plugin that frames software verification as four questions and walks an agent through four modes: plan, execute, interpret, report.

Korean is the primary language of the skill and docs. This file summarizes what the plugin does.

## Four questions

| ID | Question | Primary methods |
|---|---|---|
| Q1 Correctness | No crashes, hangs or misrendering on diverse, hostile or partial inputs | Shared fixture corpus, differential testing between implementations, seeded property-based fuzzing, pathological inputs |
| Q2 Performance | Latency, frame hitches, memory and size within thresholds on real devices, including low-end ones | Repeated real-device Release measurements, external thresholds, cross-checking tools with different principles |
| Q3 Security | Untrusted input cannot execute code, reach the network or exhaust resources; supply chain is pinned | Threat model → dynamic attack-input checks → static analysis, dependency audit, SBOM, sanitizers |
| Q4 Maintainability | Verification repeats automatically; code stays manageable | CI gates, coverage thresholds, complexity distribution, defect ledger |

## What you get

- `skills/verify/` — the agent-facing skill: `SKILL.md` (modes, ten principles, checklists), ten compact references (principles, Q1–Q4, defect ledger, report, tool map, iOS and Android commands), five templates, three stdlib-only Python scripts.
- `docs/` — human-facing guide: six chapters (principles and interpretation, correctness, performance with seven measurement pitfalls, security, maintainability, records and reports), five tool documents covering 26 tools (what, why, setup, usage, reading results, pitfalls), a glossary, and a case study with real numbers.
- `evals/` — four `claude plugin eval` cases, including a negative case.
- `tests/` — pytest for scripts and manifest/doc consistency.

## Install

```sh
claude plugin marketplace add Jimmy-Jung/verification-guide
claude plugin install verification-guide@verification-guide
# or try it for one session
claude --plugin-dir ./verification-guide
```

Codex users register `.agents/plugins/marketplace.json` as a local marketplace.

## Interpretation rules in one breath

Median plus range, never a single run. Real-device Release for absolute numbers, simulator Debug only for regression gates. External thresholds first; project-chosen values are "regression lines". Every "zero findings" carries the tool's field of view. Never compare metrics with different definitions on one axis. Cross-check key intervals with tools whose error modes differ.

## License

MIT
