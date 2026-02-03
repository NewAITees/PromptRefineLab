from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Any

from .evaluators import LLMAsJudgeEvaluator, RuleBasedEvaluator
from .models import Candidate, RunResult, Task
from .spec import RunSpec


@dataclass
class EvaluateResult:
    run_results: list[RunResult]
    candidates: list[Candidate]
    leaderboard: list[dict[str, Any]]


@dataclass
class OptimizeResult:
    best_candidate: Candidate
    leaderboard: list[dict[str, Any]]
    diff: str | None
    run_results: list[RunResult]


def _ensure_task_ids(tasks: list[Task]) -> list[Task]:
    normalized: list[Task] = []
    for index, task in enumerate(tasks, start=1):
        if task.id is None:
            normalized.append(task.model_copy(update={"id": f"t{index}"}))
        else:
            normalized.append(task)
    return normalized


def validate_spec(spec: RunSpec) -> list[str]:
    errors: list[str] = []
    candidate_ids = {c.id for c in spec.candidates}
    task_ids = {t.id for t in _ensure_task_ids(spec.tasks)}

    if spec.evaluator.type not in {"rule_based", "llm_judge"}:
        errors.append(f"evaluator_unknown:{spec.evaluator.type}")
    if spec.evaluator.type == "llm_judge":
        if not spec.evaluator.provider:
            errors.append("evaluator_provider_missing")
        if not spec.evaluator.model:
            errors.append("evaluator_model_missing")
        if spec.evaluator.provider != "ollama" and not spec.evaluator.api_key_env:
            errors.append("evaluator_api_key_env_missing")

    for output in spec.outputs:
        if output.candidate_id not in candidate_ids:
            errors.append(f"output_candidate_missing:{output.candidate_id}")
        if output.task_id not in task_ids:
            errors.append(f"output_task_missing:{output.task_id}")
    return errors


def evaluate(spec: RunSpec) -> EvaluateResult:
    tasks = _ensure_task_ids(spec.tasks)
    if spec.evaluator.type == "rule_based":
        evaluator = RuleBasedEvaluator()
    else:
        evaluator = LLMAsJudgeEvaluator(
            provider=spec.evaluator.provider or "openai",
            model=spec.evaluator.model or "",
            base_url=spec.evaluator.base_url,
            api_key_env=spec.evaluator.api_key_env,
            temperature=spec.evaluator.temperature,
            judge_prompt=spec.evaluator.judge_prompt,
        )
    run_results: list[RunResult] = []

    task_index = {t.id: t for t in tasks if t.id is not None}

    for output in spec.outputs:
        task = task_index.get(output.task_id)
        if task is None:
            run_results.append(output.model_copy(update={"score": 0.0, "error": "task_not_found"}))
            continue
        outcome = evaluator.score(
            expected=task.expected, output=output.output, rule=task.judge_rule
        )
        run_results.append(output.model_copy(update={"score": outcome.score}))

    candidate_scores: dict[str, list[float]] = {c.id: [] for c in spec.candidates}
    for result in run_results:
        if result.score is not None:
            candidate_scores.setdefault(result.candidate_id, []).append(result.score)

    scored_candidates: list[Candidate] = []
    for candidate in spec.candidates:
        scores = candidate_scores.get(candidate.id, [])
        avg_score = sum(scores) / len(scores) if scores else 0.0
        scored_candidates.append(candidate.model_copy(update={"score": avg_score}))

    leaderboard = sorted(
        [{"candidate_id": c.id, "score": c.score or 0.0} for c in scored_candidates],
        key=lambda item: item["score"],
        reverse=True,
    )

    for rank, row in enumerate(leaderboard, start=1):
        row["rank"] = rank

    return EvaluateResult(
        run_results=run_results, candidates=scored_candidates, leaderboard=leaderboard
    )


def optimize(spec: RunSpec) -> OptimizeResult:
    eval_result = evaluate(spec)
    if not eval_result.leaderboard:
        raise ValueError("no_candidates")

    best_id = eval_result.leaderboard[0]["candidate_id"]
    best_candidate = next(c for c in eval_result.candidates if c.id == best_id)

    diff_text: str | None = None
    if best_candidate.parent_id:
        parent = next((c for c in eval_result.candidates if c.id == best_candidate.parent_id), None)
        if parent is not None:
            diff_text = "\n".join(
                difflib.unified_diff(
                    parent.content.splitlines(),
                    best_candidate.content.splitlines(),
                    fromfile=f"{parent.id}",
                    tofile=f"{best_candidate.id}",
                    lineterm="",
                )
            )

    return OptimizeResult(
        best_candidate=best_candidate,
        leaderboard=eval_result.leaderboard,
        diff=diff_text,
        run_results=eval_result.run_results,
    )
