# RunSpec Reference

## Minimal structure (YAML)

```yaml
version: "0.1"

candidates:
  - id: c1
    content: "..."

tasks:
  - id: t1
    input: "..."
    expected: "..."
    judge_rule:
      type: exact

outputs:
  - candidate_id: c1
    task_id: t1
    output: "..."

evaluator:
  type: rule_based
```

## LLM judge (YAML)

```yaml
evaluator:
  type: llm_judge
  provider: openai | anthropic | gemini | ollama
  model: gpt-4o-mini
  base_url: https://api.openai.com
  api_key_env: OPENAI_API_KEY
  temperature: 0.0
  judge_prompt: |
    Return JSON only: {"score": 0.0-1.0, "reason": "..."}
    EXPECTED:
    {{expected}}
    OUTPUT:
    {{output}}
```
