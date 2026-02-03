"""
漫才プロンプト最適化スクリプト（自前APO実装）

シンプルなフィードバックループでプロンプトを自動改善する。
全てOllamaで動作するため、外部APIキー不要。

使用方法:
    uv run python scripts/train_manzai_apo.py

必要な環境:
    - Ollamaが起動していること (http://localhost:11434)
    - llama3.1:8b モデルがインストール済み
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

import ollama

# ============================================================
# 設定
# ============================================================

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen3-coder:30b"

# APO設定
NUM_ROUNDS = 10  # 改善ラウンド数（増加）
SAMPLES_PER_ROUND = 5  # 各ラウンドで評価するサンプル数
EARLY_STOP_PATIENCE = 3  # N回連続でベスト更新なしなら終了


# ============================================================
# データ型定義
# ============================================================


class DialogueTurn(TypedDict, total=False):
    speaker: int
    expression: str
    action_name: str
    text: str
    delay_ms: int


class ReferenceDialogue(TypedDict):
    turns: list[DialogueTurn]
    punchline: bool


class ManzaiTask(TypedDict):
    topic: str
    reference_dialogue: ReferenceDialogue


@dataclass
class EvaluationResult:
    """評価結果"""

    topic: str
    generated: str
    score: float
    reason: str


@dataclass
class RoundResult:
    """ラウンドの結果"""

    round_num: int
    prompt: str
    avg_score: float
    evaluations: list[EvaluationResult] = field(default_factory=list)


# ============================================================
# データ読み込み
# ============================================================


def load_manzai_tasks(path: str = "manzai_training_data.json") -> list[ManzaiTask]:
    """訓練データを読み込む"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# ユーティリティ
# ============================================================


def reference_to_text(ref: ReferenceDialogue) -> str:
    """参照ダイアログをテキスト形式に変換"""
    lines = []
    for turn in ref["turns"]:
        speaker = "boke" if turn["speaker"] == 0 else "tsukkomi"
        lines.append(f"{speaker}: [{turn['text']}]")
    return "\n".join(lines)


# ============================================================
# Ollama操作
# ============================================================


def generate_manzai(client: ollama.Client, prompt: str, topic: str) -> str:
    """プロンプトを使って漫才を生成"""
    user_message = prompt.replace("{topic}", topic)

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": user_message}],
            options={"temperature": 0.7, "num_predict": 1000},
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"  [ERROR] Generation error: {e}")
        return ""


def evaluate_manzai(
    client: ollama.Client,
    generated: str,
    reference: ReferenceDialogue,
) -> tuple[float, str]:
    """生成された漫才を評価してスコアと理由を返す"""
    reference_text = reference_to_text(reference)

    judge_prompt = f"""以下の2つの漫才を比較して、生成された漫才の品質を評価してください。

【参考(良い例)】:
{reference_text}

【生成された漫才】:
{generated}

評価基準:
- ボケとツッコミの自然さ（ボケが天然で、ツッコミが的確か）
- テンポの良さ（会話のリズム）
- 面白さ（オチがあるか）
- キャラクターの一貫性

必ず以下のJSON形式のみで回答:
{{"score": 0.0から1.0の数値, "reason": "具体的な評価理由"}}"""

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": judge_prompt}],
            format="json",
            options={"temperature": 0.0, "num_predict": 300},
        )
        content = response["message"]["content"]
        result = json.loads(content)
        score = max(0.0, min(1.0, float(result.get("score", 0.5))))
        reason = result.get("reason", "no reason")
        return score, reason
    except Exception as e:
        print(f"  [WARN] Evaluation parse error: {e}")
        return 0.5, "evaluation error"


def generate_feedback(
    client: ollama.Client,
    evaluations: list[EvaluationResult],
) -> str:
    """評価結果を分析してフィードバックを生成（テキスト勾配）"""
    eval_summary = []
    for e in evaluations:
        eval_summary.append(
            f"topic: {e.topic}\n"
            f"score: {e.score:.2f}\n"
            f"reason: {e.reason}\n"
            f"generated (excerpt): {e.generated[:200]}..."
        )

    feedback_prompt = f"""以下は漫才生成の評価結果です。これを分析して、
プロンプトの改善点を具体的に提案してください。

【評価結果】:
{chr(10).join(eval_summary)}

以下の観点で改善点を箇条書きで挙げてください:
1. ボケの質を上げるには？
2. ツッコミの切れ味を上げるには？
3. 会話のテンポを改善するには？
4. キャラクター性を強調するには？

改善提案:"""

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": feedback_prompt}],
            options={"temperature": 0.3, "num_predict": 500},
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"  [WARN] Feedback generation error: {e}")
        return ""


def improve_prompt(
    client: ollama.Client,
    current_prompt: str,
    feedback: str,
) -> str:
    """フィードバックを元にプロンプトを改善"""
    improve_prompt_text = f"""以下のプロンプトを改善してください。

【現在のプロンプト】:
{current_prompt}

【改善すべき点】:
{feedback}

改善のルール:
- {{topic}}プレースホルダーは必ず残す
- JSON出力形式の指示は維持する
- より具体的で効果的な指示に書き換える
- 余計な説明は加えず、改善したプロンプトのみを出力

改善後のプロンプト:"""

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": improve_prompt_text}],
            options={"temperature": 0.5, "num_predict": 800},
        )
        new_prompt = response["message"]["content"].strip()
        # {topic}が含まれているか確認
        if "{topic}" not in new_prompt:
            print("  [WARN] {topic} disappeared, keeping current prompt")
            return current_prompt
        return new_prompt
    except Exception as e:
        print(f"  [WARN] Prompt improvement error: {e}")
        return current_prompt


# ============================================================
# APOメインループ
# ============================================================


def run_evaluation_round(
    client: ollama.Client,
    prompt: str,
    tasks: list[ManzaiTask],
    num_samples: int,
) -> list[EvaluationResult]:
    """1ラウンドの評価を実行"""
    # ランダムにサンプルを選択
    samples = random.sample(tasks, min(num_samples, len(tasks)))
    results = []

    for task in samples:
        topic = task["topic"]
        print(f"    [GEN] {topic}...")

        # 生成
        generated = generate_manzai(client, prompt, topic)
        if not generated:
            continue

        # 評価
        score, reason = evaluate_manzai(client, generated, task["reference_dialogue"])
        results.append(
            EvaluationResult(
                topic=topic,
                generated=generated,
                score=score,
                reason=reason,
            )
        )
        print(f"       Score: {score:.2f}")

    return results


def train_apo(
    tasks: list[ManzaiTask],
    initial_prompt: str,
    initial_best_score: float = 0.0,
    num_rounds: int = NUM_ROUNDS,
    samples_per_round: int = SAMPLES_PER_ROUND,
    early_stop_patience: int = EARLY_STOP_PATIENCE,
) -> tuple[str, list[RoundResult]]:
    """APO訓練メインループ"""
    client = ollama.Client(host=OLLAMA_HOST)
    current_prompt = initial_prompt
    best_prompt = initial_prompt
    best_score = initial_best_score  # 前回の最高スコアを基準にする
    no_improvement_count = 0  # ベスト更新なしの連続回数
    history: list[RoundResult] = []

    print("\n=== APO Training Start ===")
    print(f"   Rounds: {num_rounds}")
    print(f"   Samples/Round: {samples_per_round}")
    print(f"   Early Stop Patience: {early_stop_patience}")
    print(f"   Model: {OLLAMA_MODEL}")
    print("=" * 50)

    for round_num in range(1, num_rounds + 1):
        print(f"\n>>> Round {round_num}/{num_rounds}")

        # 1. 評価
        print("  [EVAL] Evaluating...")
        evaluations = run_evaluation_round(client, current_prompt, tasks, samples_per_round)

        if not evaluations:
            print("  [ERROR] No evaluation results, skipping")
            continue

        avg_score = sum(e.score for e in evaluations) / len(evaluations)
        print(f"  [SCORE] Avg: {avg_score:.3f} (Best: {best_score:.3f})")

        # 結果を記録
        round_result = RoundResult(
            round_num=round_num,
            prompt=current_prompt,
            avg_score=avg_score,
            evaluations=evaluations,
        )
        history.append(round_result)

        # ベスト更新チェック
        if avg_score > best_score:
            best_score = avg_score
            best_prompt = current_prompt
            no_improvement_count = 0
            print("  [BEST] New best score!")
        else:
            no_improvement_count += 1
            print(f"  [--] No improvement ({no_improvement_count}/{early_stop_patience})")

        # Early stopping チェック
        if no_improvement_count >= early_stop_patience:
            print(f"\n  [STOP] Early stopping: no improvement for {early_stop_patience} rounds")
            break

        # 最終ラウンドなら改善しない
        if round_num == num_rounds:
            break

        # 2. フィードバック生成
        print("  [FEEDBACK] Generating feedback...")
        feedback = generate_feedback(client, evaluations)
        if feedback:
            print(f"  [FEEDBACK] {feedback[:150]}...")

        # 3. プロンプト改善
        print("  [IMPROVE] Improving prompt...")
        new_prompt = improve_prompt(client, current_prompt, feedback)
        if new_prompt != current_prompt:
            current_prompt = new_prompt
            print("  [OK] Prompt updated")
        else:
            print("  [SKIP] No prompt change")

    print("\n" + "=" * 50)
    print("=== Training Complete ===")
    print(f"   Final Best Score: {best_score:.3f}")

    return best_prompt, history


# ============================================================
# 初期プロンプト
# ============================================================

INITIAL_PROMPT = """あなたは二人のAITuberの掛け合いを生成します。
テーマ: {topic}

以下のルールに従ってください：
- speaker0はボケ担当の女性（一人称は「私」、おっとりした性格）
- speaker1はツッコミ担当のマスコットキャラ（ぼくっこ、ツンツンした性格）
- 3〜5往復の会話で構成
- 必ずJSONのみを返してください

出力形式:
{{"turns":[{{"speaker":0,"expression":"普通","text":"セリフ"}}],"punchline":true}}

expressionは: 普通, 笑顔, 驚き, 怒り, 悲しい, 恥ずかしい のいずれか"""


# ============================================================
# メイン
# ============================================================


def load_previous_best() -> tuple[str, float]:
    """前回の最良結果を読み込む（プロンプトとスコア）"""
    prev_prompt = Path("best_manzai_prompt.txt")
    prev_history = Path("apo_history.json")

    prompt = INITIAL_PROMPT
    score = 0.0

    # 前回のプロンプトを読み込み
    if prev_prompt.exists():
        loaded_prompt = prev_prompt.read_text(encoding="utf-8").strip()
        if "{topic}" in loaded_prompt:
            prompt = loaded_prompt
            print(f"[RESUME] Loading previous best prompt from {prev_prompt}")

    # 前回の最高スコアを読み込み
    if prev_history.exists():
        try:
            history_data = json.loads(prev_history.read_text(encoding="utf-8"))
            if history_data:
                score = max(r["avg_score"] for r in history_data)
                print(f"[RESUME] Previous best score: {score:.3f}")
        except (json.JSONDecodeError, KeyError):
            pass

    if score == 0.0:
        print("[START] Starting fresh (no previous score)")

    return prompt, score


def main() -> None:
    # データ読み込み
    tasks = load_manzai_tasks()
    print(f"[DATA] Training data: {len(tasks)} items")

    # 前回の結果を読み込み（プロンプトとスコア）
    initial_prompt, initial_score = load_previous_best()

    # APO訓練実行
    best_prompt, history = train_apo(
        tasks=tasks,
        initial_prompt=initial_prompt,
        initial_best_score=initial_score,
        num_rounds=NUM_ROUNDS,
        samples_per_round=SAMPLES_PER_ROUND,
    )

    # 結果保存
    output_path = Path("best_manzai_prompt.txt")
    output_path.write_text(best_prompt, encoding="utf-8")
    print(f"\n[SAVE] Best prompt saved to: {output_path}")

    # 履歴保存
    history_path = Path("apo_history.json")
    history_data = [
        {
            "round": r.round_num,
            "avg_score": r.avg_score,
            "prompt": r.prompt,
            "evaluations": [
                {"topic": e.topic, "score": e.score, "reason": e.reason} for e in r.evaluations
            ],
        }
        for r in history
    ]
    history_path.write_text(
        json.dumps(history_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[SAVE] Training history saved to: {history_path}")

    # 最終プロンプト表示
    print("\n" + "=" * 50)
    print("=== Optimized Prompt ===")
    print("=" * 50)
    print(best_prompt)


if __name__ == "__main__":
    main()
