from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: str
    content: str
    score: float | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    parent_id: str | None = None


class Task(BaseModel):
    input: str
    expected: str
    judge_rule: dict[str, Any] | str
    id: str | None = None


class RunResult(BaseModel):
    candidate_id: str
    task_id: str
    output: str
    score: float | None = None
    error: str | None = None
