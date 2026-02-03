from __future__ import annotations

import re
import json
from dataclasses import dataclass
from typing import Any

from .llm_clients import (
    LLMRequest,
    call_anthropic,
    call_gemini,
    call_ollama_chat,
    call_openai_chat,
)


@dataclass
class EvalOutcome:
    score: float
    reason: str | None = None


class Evaluator:
    def score(self, *, expected: str, output: str, rule: dict[str, Any] | str) -> EvalOutcome:
        raise NotImplementedError


class RuleBasedEvaluator(Evaluator):
    def score(self, *, expected: str, output: str, rule: dict[str, Any] | str) -> EvalOutcome:
        if isinstance(rule, str):
            rule = {"type": rule}
        rule_type = rule.get("type", "exact")

        if rule_type == "exact":
            return EvalOutcome(score=1.0 if output == expected else 0.0)

        if rule_type == "regex":
            pattern = rule.get("pattern", "")
            return EvalOutcome(score=1.0 if re.search(pattern, output) else 0.0)

        if rule_type == "numeric":
            try:
                value = float(output)
            except ValueError:
                return EvalOutcome(score=0.0, reason="output_not_numeric")
            min_value = rule.get("min")
            max_value = rule.get("max")
            if min_value is not None and value < float(min_value):
                return EvalOutcome(score=0.0)
            if max_value is not None and value > float(max_value):
                return EvalOutcome(score=0.0)
            return EvalOutcome(score=1.0)

        return EvalOutcome(score=0.0, reason=f"unknown_rule:{rule_type}")


class LLMAsJudgeEvaluator(Evaluator):
    def __init__(
        self,
        *,
        provider: str,
        model: str,
        base_url: str | None,
        api_key_env: str | None,
        temperature: float,
        judge_prompt: str | None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.api_key_env = api_key_env
        self.temperature = temperature
        self.judge_prompt = judge_prompt

    def score(self, *, expected: str, output: str, rule: dict[str, Any] | str) -> EvalOutcome:
        if self.judge_prompt:
            prompt = (
                self.judge_prompt.replace("{{expected}}", expected).replace("{{output}}", output)
            )
        else:
            prompt = (
            "Compare expected vs output and return JSON only: "
            '{"score": 0.0-1.0, "reason": "short"}.\n'
            f"EXPECTED:\n{expected}\nOUTPUT:\n{output}"
            )
        request = LLMRequest(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            base_url=self.base_url,
            api_key_env=self.api_key_env,
            provider=self.provider,
        )

        if self.provider == "openai":
            content = call_openai_chat(request)
        elif self.provider == "anthropic":
            content = call_anthropic(request)
        elif self.provider == "gemini":
            content = call_gemini(request)
        elif self.provider == "ollama":
            content = call_ollama_chat(request)
        else:
            return EvalOutcome(score=0.0, reason=f"unknown_provider:{self.provider}")

        try:
            result = json.loads(content)
            score = float(result.get("score", 0.0))
            score = max(0.0, min(1.0, score))
            reason = str(result.get("reason", ""))
            return EvalOutcome(score=score, reason=reason)
        except (ValueError, json.JSONDecodeError) as exc:
            return EvalOutcome(score=0.0, reason=f"invalid_judge_json:{exc}")
