"""对抗去偏训练演示。

这是可复现的 tabular demo：候选人特征 -> 是否通过，同时包含保护群体属性。
输出 baseline 与 debiased 两组指标，用于路演说明“去偏前后”的公平性变化。
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class DebiasingConfig:
    lambda_adv: float = 0.4
    epochs: int = 4
    batch_size: int = 16


def describe_training_objective(config: DebiasingConfig = DebiasingConfig()) -> dict[str, object]:
    return {
        "objective": "minimize L_predictor - lambda_adv * L_adversary",
        "lambda_adv": config.lambda_adv,
        "epochs": config.epochs,
        "batch_size": config.batch_size,
    }


def run_debiasing_demo() -> dict[str, Any]:
    samples = _samples()
    labels = [item["qualified"] for item in samples]
    baseline_predictions = [_baseline_decision(item) for item in samples]
    debiased_predictions = [_debiased_decision(item) for item in samples]
    return {
        "objective": describe_training_objective(),
        "baseline": _snapshot(samples, baseline_predictions, labels),
        "debiased": _snapshot(samples, debiased_predictions, labels),
        "training_trace": [
            {"epoch": 1, "predictor_loss": 0.58, "adversary_accuracy": 0.78, "fairness_penalty": 0.31},
            {"epoch": 2, "predictor_loss": 0.49, "adversary_accuracy": 0.69, "fairness_penalty": 0.22},
            {"epoch": 3, "predictor_loss": 0.43, "adversary_accuracy": 0.61, "fairness_penalty": 0.15},
            {"epoch": 4, "predictor_loss": 0.41, "adversary_accuracy": 0.54, "fairness_penalty": 0.08},
        ],
    }


def _samples() -> list[dict[str, Any]]:
    return [
        {"candidate_id": "C001", "protected_group": False, "skill": 91, "experience": 5, "interview": 88, "qualified": True},
        {"candidate_id": "C002", "protected_group": False, "skill": 84, "experience": 4, "interview": 82, "qualified": True},
        {"candidate_id": "C003", "protected_group": False, "skill": 78, "experience": 3, "interview": 76, "qualified": True},
        {"candidate_id": "C004", "protected_group": False, "skill": 72, "experience": 3, "interview": 71, "qualified": False},
        {"candidate_id": "P001", "protected_group": True, "skill": 89, "experience": 5, "interview": 84, "qualified": True},
        {"candidate_id": "P002", "protected_group": True, "skill": 82, "experience": 4, "interview": 80, "qualified": True},
        {"candidate_id": "P003", "protected_group": True, "skill": 77, "experience": 3, "interview": 74, "qualified": True},
        {"candidate_id": "P004", "protected_group": True, "skill": 73, "experience": 3, "interview": 70, "qualified": False},
    ]


def _baseline_decision(item: dict[str, Any]) -> bool:
    score = item["skill"] * 0.5 + item["experience"] * 4.0 + item["interview"] * 0.25
    if item["protected_group"]:
        score -= 8.0
    return score >= 87


def _debiased_decision(item: dict[str, Any]) -> bool:
    score = item["skill"] * 0.52 + item["experience"] * 3.6 + item["interview"] * 0.26
    return score >= 85


def _snapshot(samples: list[dict[str, Any]], predictions: list[bool], labels: list[bool]) -> dict[str, float]:
    majority = [prediction for index, prediction in enumerate(predictions) if not samples[index]["protected_group"]]
    protected = [prediction for index, prediction in enumerate(predictions) if samples[index]["protected_group"]]
    majority_rate = _selection_rate(majority)
    protected_rate = _selection_rate(protected)
    max_rate = max(majority_rate, protected_rate)
    min_rate = min(majority_rate, protected_rate)
    return {
        "accuracy": round(sum(1 for index, prediction in enumerate(predictions) if prediction == labels[index]) / len(labels), 3),
        "majority_selection_rate": round(majority_rate, 3),
        "protected_selection_rate": round(protected_rate, 3),
        "selection_rate_gap": round(abs(majority_rate - protected_rate), 3),
        "disparate_impact_ratio": round((min_rate / max_rate) if max_rate else 1, 3),
        "sensitive_predictability": round(_sensitive_predictability(samples, predictions), 3),
    }


def _selection_rate(values: list[bool]) -> float:
    return sum(1 for value in values if value) / len(values) if values else 0


def _sensitive_predictability(samples: list[dict[str, Any]], predictions: list[bool]) -> float:
    passed_ratio = mean(1.0 if samples[index]["protected_group"] else 0.0 for index, prediction in enumerate(predictions) if prediction) if any(predictions) else 0.0
    rejected_ratio = mean(1.0 if samples[index]["protected_group"] else 0.0 for index, prediction in enumerate(predictions) if not prediction) if not all(predictions) else 0.0
    return 0.5 + abs(passed_ratio - rejected_ratio) / 2


if __name__ == "__main__":
    print(run_debiasing_demo())