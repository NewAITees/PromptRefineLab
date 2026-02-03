from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def load_data(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("config_root_must_be_object")
    return data


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
