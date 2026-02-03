from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import yaml


def ollama_running(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def model_available(base_url: str, model: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return any(m.get("name") == model for m in data.get("models", []))
    except Exception:
        return False


def main() -> int:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

    if not ollama_running(base_url):
        print("[SKIP] Ollama is not running.")
        return 0

    if not model_available(base_url, model):
        print(f"[SKIP] Model not available: {model}")
        return 0

    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = Path(tmp_dir) / "run.yaml"
        config = {
            "version": "0.1",
            "candidates": [
                {"id": "c1", "content": "Return the number only."},
            ],
            "tasks": [
                {
                    "id": "t1",
                    "input": "What is 2+2?",
                    "expected": "4",
                    "judge_rule": {"type": "exact"},
                }
            ],
            "outputs": [
                {"candidate_id": "c1", "task_id": "t1", "output": "4"},
            ],
            "evaluator": {
                "type": "llm_judge",
                "provider": "ollama",
                "model": model,
                "base_url": base_url,
                "temperature": 0.0,
                "judge_prompt": (
                    'Return JSON only: {"score": 0.0-1.0, "reason": "..."}\n'
                    "EXPECTED:\n{{expected}}\nOUTPUT:\n{{output}}"
                ),
            },
        }
        config_path.write_text(yaml.safe_dump(config, allow_unicode=True), encoding="utf-8")

        result = subprocess.run(
            ["prl", "evaluate", str(config_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("[FAIL] prl evaluate failed")
            print(result.stdout)
            print(result.stderr)
            return result.returncode

        run_dir = Path(result.stdout.strip())
        if not run_dir.exists():
            print(f"[FAIL] run dir not found: {run_dir}")
            return 1

        leaderboard = run_dir / "leaderboard.json"
        if not leaderboard.exists():
            print("[FAIL] leaderboard.json missing")
            return 1

        print(f"[OK] E2E completed: {run_dir}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
