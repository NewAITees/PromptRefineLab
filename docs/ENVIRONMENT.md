# Environment Setup

This repo is documentation-first. Core stack decisions are now locked for the MVP.

## Current prerequisites

- Git
- A POSIX shell (bash/zsh)
- Python 3.11+
- `uv` (Python package manager)

## Stack decisions (MVP)

- Skill + CLI language/runtime: Python 3.11+
- Package manager: `uv`
- AI providers: OpenAI, Anthropic, Gemini, local Ollama (selectable)
- Desktop: Tauri shell; integration with `prl` CLI is a choice (thin wrapper by default, optional later)
- Storage: local-only runs under `.prl/` (MVP)

## Suggested local tools (optional)

- `rg` (ripgrep) for fast search
- `jq` for JSON inspection

## Setup (once code exists)

This section will be filled after the first implementation lands:

- Exact version requirements
- Install commands
- Run/test commands
- Environment variables and `.env` usage
