# PromptRefineLab

A refinement laboratory for prompts, policies, and agent skills.

Independent prompt & policy optimization tool inspired by APO research. Not affiliated with Microsoft or Agent Lightning.

Short name (CLI/internal): `prl`

## Status

- Documentation-first: environment setup and project conventions only.
- Core Skill, CLI, and Desktop app are not implemented yet.

## Goals (Current Phase)

- Provide a minimal Skill that can validate, evaluate, and optimize candidates.
- Expose the Skill via a CLI that works without any Desktop app.
- Keep UI and persistence out of the Skill; treat them as separate layers.

## Stack (Current Phase)

- Language/runtime: Python 3.11+
- Package manager: `uv`
- AI providers: OpenAI, Anthropic, Gemini, local Ollama (selectable)
- Desktop: Tauri shell; use `prl` CLI by default, optional to embed later

## Non-goals (for now)

- Building a Desktop UI before the CLI is stable.
- Shipping a production-ready evaluator or hosted service.

## Environment setup

Start here: `docs/ENVIRONMENT.md`

## Project docs

- `docs/ENVIRONMENT.md`
- `docs/CONTRIBUTING.md`
- `docs/ROADMAP.md`
- `docs/SKILL_SPEC.md`
- `docs/examples/run.yaml`
- `docs/PLAN.md`
