from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import yaml

from prl.io import read_text_any


def load_json(path: Path):
    return json.loads(read_text_any(path))


def ollama_running(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    inputs_dir = repo_root / "inputs"
    outputs_dir = repo_root / "outputs"

    candidates = load_json(inputs_dir / "candidates.json")
    tasks = load_json(inputs_dir / "tasks.json")
    outputs = load_json(inputs_dir / "outputs.json")
    prompt_path = inputs_dir / "prompt_before.txt"
    if prompt_path.exists():
        prompt_text = read_text_any(prompt_path).strip()
        if prompt_text:
            candidates[0]["content"] = prompt_text

    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    if not ollama_running(base_url):
        print("[FAIL] Ollama is not running.")
        return 2

    evaluator = {
        "type": "llm_judge",
        "provider": "ollama",
        "model": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
        "base_url": base_url,
        "temperature": 0.0,
        "judge_prompt": (
            'Return JSON only: {"score": 0.0-1.0, "reason": "..."}\n'
            "EXPECTED:\n{{expected}}\nOUTPUT:\n{{output}}"
        ),
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = Path(tmp_dir) / "run.yaml"
        config = {
            "version": "0.1",
            "candidates": candidates,
            "tasks": tasks,
            "outputs": outputs,
            "evaluator": evaluator,
        }
        config_path.write_text(yaml.safe_dump(config, allow_unicode=True), encoding="utf-8")

        result = subprocess.run(
            ["prl", "optimize", str(config_path), "--steps", "1"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("[FAIL] prl optimize failed")
            print(result.stdout)
            print(result.stderr)
            return result.returncode

        run_dir = Path(result.stdout.strip())
        if not run_dir.exists():
            print(f"[FAIL] run dir not found: {run_dir}")
            return 1

        outputs_dir.mkdir(parents=True, exist_ok=True)
        target = outputs_dir / "latest"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(run_dir, target)

        print(f"[OK] E2E completed: {target}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
