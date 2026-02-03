from prl.models import Candidate, RunResult, Task
from prl.skill import evaluate, validate_spec
from prl.spec import RunSpec


def test_validate_spec_detects_missing_candidate():
    spec = RunSpec(
        candidates=[Candidate(id="c1", content="x")],
        tasks=[Task(id="t1", input="q", expected="a", judge_rule={"type": "exact"})],
        outputs=[RunResult(candidate_id="c2", task_id="t1", output="a")],
    )
    errors = validate_spec(spec)
    assert "output_candidate_missing:c2" in errors


def test_evaluate_scores_candidate():
    spec = RunSpec(
        candidates=[Candidate(id="c1", content="x")],
        tasks=[Task(id="t1", input="q", expected="a", judge_rule={"type": "exact"})],
        outputs=[RunResult(candidate_id="c1", task_id="t1", output="a")],
    )
    result = evaluate(spec)
    assert result.leaderboard[0]["score"] == 1.0
