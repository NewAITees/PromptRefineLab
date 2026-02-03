from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMRequest:
    prompt: str
    model: str
    temperature: float
    base_url: str | None
    api_key_env: str | None
    provider: str


def _read_api_key(env_name: str | None) -> str | None:
    if not env_name:
        return None
    return os.environ.get(env_name)


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def call_openai_chat(req: LLMRequest) -> str:
    base = (req.base_url or "https://api.openai.com").rstrip("/")
    url = f"{base}/v1/chat/completions"
    api_key = _read_api_key(req.api_key_env) or ""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": req.model,
        "messages": [{"role": "user", "content": req.prompt}],
        "temperature": req.temperature,
    }
    response = _post_json(url, payload, headers)
    return response["choices"][0]["message"]["content"]


def call_ollama_chat(req: LLMRequest) -> str:
    base = (req.base_url or "http://localhost:11434").rstrip("/")
    url = f"{base}/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": req.model,
        "messages": [{"role": "user", "content": req.prompt}],
        "options": {"temperature": req.temperature},
        "stream": False,
    }
    response = _post_json(url, payload, headers)
    return response["message"]["content"]


def call_anthropic(req: LLMRequest) -> str:
    base = (req.base_url or "https://api.anthropic.com").rstrip("/")
    url = f"{base}/v1/messages"
    api_key = _read_api_key(req.api_key_env) or ""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": req.model,
        "max_tokens": 400,
        "temperature": req.temperature,
        "messages": [{"role": "user", "content": req.prompt}],
    }
    response = _post_json(url, payload, headers)
    return response["content"][0]["text"]


def call_gemini(req: LLMRequest) -> str:
    base = (req.base_url or "https://generativelanguage.googleapis.com").rstrip("/")
    api_key = _read_api_key(req.api_key_env) or ""
    url = f"{base}/v1beta/models/{req.model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": req.prompt}]}],
        "generationConfig": {"temperature": req.temperature},
    }
    response = _post_json(url, payload, headers)
    return response["candidates"][0]["content"]["parts"][0]["text"]
