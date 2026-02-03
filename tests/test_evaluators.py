from prl.evaluators import RuleBasedEvaluator


def test_rule_based_exact():
    evaluator = RuleBasedEvaluator()
    outcome = evaluator.score(expected="4", output="4", rule={"type": "exact"})
    assert outcome.score == 1.0


def test_rule_based_regex():
    evaluator = RuleBasedEvaluator()
    outcome = evaluator.score(
        expected="", output="answer: 42", rule={"type": "regex", "pattern": "\\d+"}
    )
    assert outcome.score == 1.0


def test_rule_based_numeric():
    evaluator = RuleBasedEvaluator()
    outcome = evaluator.score(expected="", output="5", rule={"type": "numeric", "min": 3, "max": 7})
    assert outcome.score == 1.0
