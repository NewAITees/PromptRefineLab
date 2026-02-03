---
name: promptrefinelab
description: Build, run, and refine PromptRefineLab Skill workflows. Use when the user asks to optimize prompts/policies/agent skills, generate or validate run specs (candidates/tasks/outputs), execute prl CLI runs, interpret leaderboard/diff/results, or install/update PromptRefineLab as a Codex/Claude skill.
dependencies: python>=3.11
---

# PromptRefineLab Skill

## Core intent

- Treat this Skill as the "brain"; no UI or persistence logic here.
- Operate on explicit inputs: prompt template or script, target output, run parameters.
- Keep steps reproducible and traceable (candidates/tasks/outputs).

## Quick start workflow

1) Clarify the optimization target and desired output format.
2) Build or update a RunSpec (YAML/JSON) with:
   - candidates (prompt/policy text)
   - tasks (input/expected/judge_rule)
   - outputs (precomputed or generated)
   - evaluator config
3) Validate, then evaluate or optimize via CLI.
4) Summarize best candidate + diff + leaderboard.

## Use these resources

- `references/run-spec.md` for the canonical RunSpec layout and examples.
- `references/install.md` for Codex/Claude skill install/update commands.
- `scripts/run_prl.py` to execute `prl` with a config file.

## Output expectations

- Always show: best candidate, leaderboard, diff (if available), and run path.
- Keep reasoning concise; focus on actionable next steps.

## Dependencies

- `python` 3.11+ and `uv` are required to install the `prl` CLI.
- See `references/install.md` for the install command.
