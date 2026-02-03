# Skill Specification (MVP)

The Skill operates on *data only* and does not handle UI or persistence. The CLI is responsible for file I/O.

## Inputs

- `candidates`: list of Candidate
- `tasks`: list of Task
- `outputs`: list of RunResult (precomputed model outputs)
- `evaluator`: evaluator configuration
- `model_config`: stored but not executed in MVP
- `optimize_config`: stored but not executed in MVP

## Operations

- `validate`: schema + referential integrity checks
- `evaluate`: compute scores for each output and aggregate per candidate
- `optimize`: MVP selects best candidate by score (no mutation yet)

## Outputs

- `best_candidate`
- `leaderboard`
- `diff` (if parent exists)
- `run_results`

## Data Models

Candidate

```yaml
id
content
score
metrics
parent_id
```

Task

```yaml
input
expected
judge_rule
```

RunResult

```yaml
candidate_id
task_id
output
score
error
```

## Evaluators (MVP)

- Rule-based: implemented (exact/regex/numeric)
- LLM-as-judge: implemented (OpenAI, Anthropic, Gemini, Ollama)

LLM judge config (YAML):

```yaml
evaluator:
  type: llm_judge
  provider: openai | anthropic | gemini | ollama
  model: gpt-4o-mini
  base_url: https://api.openai.com   # optional
  api_key_env: OPENAI_API_KEY       # required except for ollama
  temperature: 0.0
  judge_prompt: |
    Return JSON only: {"score": 0.0-1.0, "reason": "..."}
    EXPECTED:
    {{expected}}
    OUTPUT:
    {{output}}
```
