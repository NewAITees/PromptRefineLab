# Development Plan Checklist

This checklist tracks what is implemented and what remains for the current phase.

## ✅ Done

- Project identity locked (PromptRefineLab, prl, tagline, stance)
- Python package + CLI scaffold (`prl`)
- Core data models (Candidate, Task, RunResult)
- Rule-based evaluator (exact/regex/numeric)
- LLM-as-judge evaluator (OpenAI/Anthropic/Gemini/Ollama)
- Skill API: validate / evaluate / optimize (baseline selection)
- CLI: validate / evaluate / optimize
- Encoding auto-detect (utf-8 / shift_jis / cp932)
- E2E inputs-driven test (Ollama default)
- Unit tests (evaluators, IO, skill basics)
- Codex/Claude skill folder + install scripts
- Pre-commit setup (ruff, ruff-format, basic hooks)

## 🔧 In Progress / Partial

- Optimization mutation logic (LLM-based candidate generation)
  - Current: selects best candidate only
  - Missing: generate new candidates per round

## ⛔ Required for Current Phase

- LLM-based mutation in `optimize`
  - Inputs: current best candidate, feedback, optional template
  - Outputs: N new candidates
- LLM-based scoring loop with Ollama in optimize path
  - Use evaluator output to rank candidates per round
- Deterministic run logs
  - Save mutation prompts and generated candidates per round
- E2E: verify mutation path (not just scoring)

## 📌 Recommended Next

- Add optimize config schema (rounds, samples, mutation count)
- Implement run log structure (.prl/runs/<id>/run_log.json)
- Add inputs structure for ideal outputs and judge prompt
- Provide minimal example for LLM mutation in `inputs/`

## 🔜 Later (Post-current phase)

- Multi-objective scoring
- Evaluator optimization
- Policy/YAML optimization
- Desktop UI (Tauri) integration

## 🧭 Gaps Found Across Docs

- Desktop app requirements are not specified (user flows, UX, data handling)
- Installer/packaging paths are not documented for Windows/macOS/Linux
- LLM provider selection and parity (OpenAI, Claude, Gemini, Ollama) is not documented
- Provider-specific limits, auth, and fallback behavior are not defined
- Config schemas lack formal versioning and validation rules
- Run log and artifact structure is not fully defined
- E2E scope is incomplete (full pipeline, generation+evaluation+mutation)
- CI/test matrix is not defined (unit + E2E, with/without Ollama)
- Release/versioning process is not documented
- Windows exe packaging flow is not documented
- Desktop UI design direction and visual system are not defined
- End-user usage guide is missing (quickstart, examples, troubleshooting)
