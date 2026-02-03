from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from .models import Candidate, RunResult, Task


class EvalConfig(BaseModel):
    type: Literal["rule_based", "llm_judge"] = "rule_based"
    provider: Literal["openai", "anthropic", "gemini", "ollama"] | None = None
    model: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None
    temperature: float = 0.0
    judge_prompt: str | None = None


class RunSpec(BaseModel):
    version: str = "0.1"
    candidates: list[Candidate]
    tasks: list[Task]
    outputs: list[RunResult] = Field(default_factory=list)
    evaluator: EvalConfig = Field(default_factory=EvalConfig)
    model_config: dict[str, Any] = Field(default_factory=dict)
    optimize_config: dict[str, Any] = Field(default_factory=dict)
