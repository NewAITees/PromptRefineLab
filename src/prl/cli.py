from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import typer

from .io import load_data, save_json
from .skill import evaluate as skill_evaluate
from .skill import optimize as skill_optimize
from .skill import validate_spec
from .spec import RunSpec

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _load_spec(path: Path) -> RunSpec:
    payload = load_data(path)
    return RunSpec.model_validate(payload)


def _make_run_dir() -> Path:
    run_id = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"
    run_dir = Path(".prl") / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _write_report(path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    lines = [f"# {title}", ""]
    for heading, body in sections:
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(body)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


@app.command()
def validate(config: Path) -> None:
    """Validate a run configuration file."""
    spec = _load_spec(config)
    errors = validate_spec(spec)
    if errors:
        for err in errors:
            typer.echo(f"error: {err}")
        raise typer.Exit(code=1)
    typer.echo("ok")


@app.command()
def evaluate(config: Path) -> None:
    """Evaluate candidates using precomputed outputs."""
    spec = _load_spec(config)
    errors = validate_spec(spec)
    if errors:
        for err in errors:
            typer.echo(f"error: {err}")
        raise typer.Exit(code=1)

    result = skill_evaluate(spec)
    run_dir = _make_run_dir()

    save_json(run_dir / "results.json", [r.model_dump() for r in result.run_results])
    save_json(run_dir / "leaderboard.json", result.leaderboard)

    report_sections = [
        ("Leaderboard", json.dumps(result.leaderboard, indent=2, ensure_ascii=False)),
        ("Notes", "This evaluation uses rule-based scoring only."),
    ]
    _write_report(run_dir / "report.md", "Evaluation Report", report_sections)

    typer.echo(str(run_dir))


@app.command()
def optimize(config: Path, steps: int = typer.Option(5, min=1)) -> None:
    """Optimize candidates (MVP: select best candidate by score)."""
    spec = _load_spec(config)
    _ = steps  # placeholder for future iterative optimization

    errors = validate_spec(spec)
    if errors:
        for err in errors:
            typer.echo(f"error: {err}")
        raise typer.Exit(code=1)

    result = skill_optimize(spec)
    run_dir = _make_run_dir()

    save_json(run_dir / "results.json", [r.model_dump() for r in result.run_results])
    save_json(run_dir / "leaderboard.json", result.leaderboard)

    best_candidate_json = json.dumps(
        result.best_candidate.model_dump(), indent=2, ensure_ascii=False
    )
    report_sections = [
        ("Best Candidate", best_candidate_json),
        ("Diff", result.diff or "(no diff)"),
    ]
    _write_report(run_dir / "report.md", "Optimization Report", report_sections)

    typer.echo(str(run_dir))
