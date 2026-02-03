# Environment Setup

This repo is documentation-first. Core stack decisions are locked for the current phase.

## Current prerequisites

- Git
- A POSIX shell (bash/zsh)
- Python 3.11+
- `uv` (Python package manager)

## Stack decisions (Current Phase)

- Skill + CLI language/runtime: Python 3.11+
- Package manager: `uv`
- AI providers: OpenAI, Anthropic, Gemini, local Ollama (selectable)
- Desktop: Tauri shell; integration with `prl` CLI is a choice (thin wrapper by default, optional later)
- Storage: local-only runs under `.prl/` (current phase)

## Suggested local tools (optional)

- `rg` (ripgrep) for fast search
- `jq` for JSON inspection

## Setup (once code exists)

This section will be filled after the first implementation lands:

- Exact version requirements
- Install commands
- Run/test commands
- Environment variables and `.env` usage

## E2E test (inputs -> outputs)

```bash
uv run python scripts/e2e_inputs_test.py
```

Ollama judge (set env vars if needed)

```bash
OLLAMA_MODEL=llama3.1:8b OLLAMA_BASE_URL=http://localhost:11434 uv run python scripts/e2e_inputs_test.py
```

## Unit tests

```bash
uv run pytest
```
