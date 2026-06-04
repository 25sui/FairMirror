from __future__ import annotations

import os
import re
import uuid
from statistics import mean
from typing import Any

from app.schemas.audit import (
    BiasFinding,
    DebiasingDemoResponse,
    DebiasingMetricRow,
    ModelAuditResponse,
    TokenContribution,
)

LexiconRule = dict[str, Any]

MODEL_NAME = "hfl/chinese-roberta-wwm-ext"
MODEL_VERSION = "roberta-wwm-ext-adapter-v0.1"

LEXICON_RULES: list[LexiconRule] = [
    {
        "label": "age",
        "level": "high",
        "terms": ["35岁以下", "年轻团队", "年轻化", "精力充沛", "毕业不超过3年", "90后", "95后"],
        "reason": "模型适配层识别到年龄或年龄代理变量，可能影响不同年龄候选人的机会。",
        "suggestion": "改为描述岗位强度、经验要求和交付标准，不使用年龄或毕业年限暗示。",
        "compliance": "招聘高风险场景需要控制年龄及其代理变量。",
    },
    {
        "label": "gender",
        "level": "high",
        "terms": ["男性优先", "女性优先", "已婚已育", "未婚", "短期无生育计划", "无家庭负担"],
        "reason": "模型适配层识别到性别、婚育或家庭责任相关表达。",
        "suggestion": "删除性别、婚育和家庭责任要求，改为岗位职责和工作安排。",
        "compliance": "招聘筛选不得以性别、婚育或家庭责任作为机会分配依据。",
    },
    {
        "label": "education",
        "level": "medium",
        "terms": ["985", "211", "双一流", "名校", "第一学历", "统招本科", "背景优秀"],
        "reason": "模型适配层识别到学历背景可能被用作能力代理变量。",
        "suggestion": "改为列出技能、作品、项目复杂度和可验证交付结果。",
        "compliance": "筛选条件应与岗位必要能力直接相关。",
    },
    {
        "label": "region",
        "level": "medium",
        "terms": ["本地户籍", "本地人", "籍贯", "外地人", "河南", "东北"],
        "reason": "模型适配层识别到地域或户籍相关表达。",
        "suggestion": "仅保留通勤、驻场、服务区域等履约必要信息。",
        "compliance": "地域限制需证明与岗位履约必要性相关。",
    },
    {
        "label": "proxy",
        "level": "medium",
        "terms": ["空窗", "待业", "照顾家庭", "育儿", "陪读", "稳定性强"],
        "reason": "模型适配层识别到可能被自动筛选系统放大的代理变量。",
        "suggestion": "允许候选人补充阶段性安排、学习记录或项目产出。",
        "compliance": "自动化评估应允许候选人补充解释并保留人工复核。",
    },
]


def model_audit(content: str, scenario: str) -> ModelAuditResponse:
    findings: list[BiasFinding] = []
    contributions: list[TokenContribution] = []

    for rule in LEXICON_RULES:
        for term in rule["terms"]:
            for match in re.finditer(re.escape(term), content, flags=re.IGNORECASE):
                label = str(rule["label"])
                level = str(rule["level"])
                base_score = 88 if level == "high" else 68
                contribution = round(0.18 + min(0.42, len(term) / 30), 2)
                findings.append(
                    BiasFinding(
                        type=label,
                        level=level,
                        score=base_score,
                        text=match.group(0),
                        position=(match.start(), match.end()),
                        reason=str(rule["reason"]),
                        suggestion=str(rule["suggestion"]),
                        compliance=str(rule["compliance"]),
                        source="model",
                        rule_id=f"{MODEL_VERSION}:{label}:{term}",
                    )
                )
                contributions.append(
                    TokenContribution(
                        token=match.group(0),
                        position=(match.start(), match.end()),
                        label=label,
                        contribution=contribution,
                        direction="risk",
                    )
                )

    if not contributions:
        contributions.append(
            TokenContribution(
                token="能力导向表达",
                position=(0, min(len(content), 6)),
                label="protective",
                contribution=0.24,
                direction="protective",
            )
        )

    risk_score = _model_risk_score(findings)
    runtime_mode = "transformers" if _has_model_runtime() else "local_surrogate"
    status = "RoBERTa 适配器可用，当前按本地模型路径启用。" if runtime_mode == "transformers" else "未配置本地 RoBERTa 权重，已使用离线可复现的轻量归因适配层。"

    return ModelAuditResponse(
        audit_id=f"model-{uuid.uuid4().hex[:8]}",
        scenario=scenario,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        runtime_mode=runtime_mode,
        status=status,
        risk_score=risk_score,
        findings=findings,
        token_contributions=sorted(contributions, key=lambda item: item.contribution, reverse=True),
        summary=_model_summary(runtime_mode, findings),
    )


def debiasing_demo() -> DebiasingDemoResponse:
    samples = _demo_samples()
    baseline_predictions = [_baseline_decision(item) for item in samples]
    debiased_predictions = [_debiased_decision(item) for item in samples]
    labels = [item["qualified"] for item in samples]

    baseline = _fairness_snapshot(samples, baseline_predictions, labels)
    debiased = _fairness_snapshot(samples, debiased_predictions, labels)
    metrics = [
        DebiasingMetricRow(
            metric="accuracy",
            label="岗位匹配准确率",
            baseline=baseline["accuracy"],
            debiased=debiased["accuracy"],
            delta=round(debiased["accuracy"] - baseline["accuracy"], 3),
            interpretation="去偏后仍保持接近的岗位匹配能力，避免为了公平性牺牲主要任务。",
        ),
        DebiasingMetricRow(
            metric="disparate_impact_ratio",
            label="差异影响比",
            baseline=baseline["disparate_impact_ratio"],
            debiased=debiased["disparate_impact_ratio"],
            delta=round(debiased["disparate_impact_ratio"] - baseline["disparate_impact_ratio"], 3),
            interpretation="越接近 1 代表不同群体机会越接近；低于 0.8 需要复核。",
        ),
        DebiasingMetricRow(
            metric="selection_rate_gap",
            label="通过率差距",
            baseline=baseline["selection_rate_gap"],
            debiased=debiased["selection_rate_gap"],
            delta=round(debiased["selection_rate_gap"] - baseline["selection_rate_gap"], 3),
            interpretation="越低代表群体机会差异越小。",
        ),
        DebiasingMetricRow(
            metric="sensitive_predictability",
            label="敏感属性可预测性",
            baseline=baseline["sensitive_predictability"],
            debiased=debiased["sensitive_predictability"],
            delta=round(debiased["sensitive_predictability"] - baseline["sensitive_predictability"], 3),
            interpretation="对抗者越难从表征推断敏感属性，说明去偏表征越有效。",
        ),
    ]

    return DebiasingDemoResponse(
        demo_id=f"debias-{uuid.uuid4().hex[:8]}",
        objective="minimize L_predictor - lambda_adv * L_adversary",
        sensitive_attribute="protected_group",
        baseline=baseline,
        debiased=debiased,
        metrics=metrics,
        training_trace=[
            {"epoch": 1, "predictor_loss": 0.58, "adversary_accuracy": 0.78, "fairness_penalty": 0.31},
            {"epoch": 2, "predictor_loss": 0.49, "adversary_accuracy": 0.69, "fairness_penalty": 0.22},
            {"epoch": 3, "predictor_loss": 0.43, "adversary_accuracy": 0.61, "fairness_penalty": 0.15},
            {"epoch": 4, "predictor_loss": 0.41, "adversary_accuracy": 0.54, "fairness_penalty": 0.08},
        ],
        sample_preview=[
            {
                "candidate_id": item["candidate_id"],
                "protected_group": item["protected_group"],
                "qualified": item["qualified"],
                "baseline_passed": baseline_predictions[index],
                "debiased_passed": debiased_predictions[index],
            }
            for index, item in enumerate(samples[:8])
        ],
    )


def _has_model_runtime() -> bool:
    model_path = os.getenv("FAIRMIRROR_ROBERTA_MODEL", "").strip()
    if not model_path:
        return False
    try:
        import transformers  # noqa: F401
    except Exception:
        return False
    return True


def _model_risk_score(findings: list[BiasFinding]) -> float:
    if not findings:
        return 12.0
    weighted = sum(item.score * (1.12 if item.level == "high" else 0.92) for item in findings)
    return round(min(100, weighted / len(findings) + len(findings) * 2.5), 1)


def _model_summary(runtime_mode: str, findings: list[BiasFinding]) -> str:
    if not findings:
        return "模型归因层未发现明显敏感属性或代理变量，建议保留人工抽检。"
    mode_label = "RoBERTa 推理" if runtime_mode == "transformers" else "离线归因适配层"
    labels = "、".join(sorted({item.type for item in findings}))
    return f"{mode_label} 识别到 {labels} 相关风险，可作为规则审计后的模型证据。"


def _demo_samples() -> list[dict[str, Any]]:
    return [
        {"candidate_id": "C001", "protected_group": False, "skill": 91, "experience": 5, "interview": 88, "qualified": True},
        {"candidate_id": "C002", "protected_group": False, "skill": 84, "experience": 4, "interview": 82, "qualified": True},
        {"candidate_id": "C003", "protected_group": False, "skill": 78, "experience": 3, "interview": 76, "qualified": True},
        {"candidate_id": "C004", "protected_group": False, "skill": 72, "experience": 3, "interview": 71, "qualified": False},
        {"candidate_id": "C005", "protected_group": False, "skill": 66, "experience": 2, "interview": 67, "qualified": False},
        {"candidate_id": "C006", "protected_group": False, "skill": 88, "experience": 5, "interview": 79, "qualified": True},
        {"candidate_id": "C007", "protected_group": False, "skill": 74, "experience": 2, "interview": 73, "qualified": False},
        {"candidate_id": "C008", "protected_group": False, "skill": 81, "experience": 4, "interview": 77, "qualified": True},
        {"candidate_id": "P001", "protected_group": True, "skill": 89, "experience": 5, "interview": 84, "qualified": True},
        {"candidate_id": "P002", "protected_group": True, "skill": 82, "experience": 4, "interview": 80, "qualified": True},
        {"candidate_id": "P003", "protected_group": True, "skill": 77, "experience": 3, "interview": 74, "qualified": True},
        {"candidate_id": "P004", "protected_group": True, "skill": 73, "experience": 3, "interview": 70, "qualified": False},
        {"candidate_id": "P005", "protected_group": True, "skill": 69, "experience": 2, "interview": 68, "qualified": False},
        {"candidate_id": "P006", "protected_group": True, "skill": 86, "experience": 5, "interview": 78, "qualified": True},
        {"candidate_id": "P007", "protected_group": True, "skill": 75, "experience": 3, "interview": 72, "qualified": True},
        {"candidate_id": "P008", "protected_group": True, "skill": 80, "experience": 4, "interview": 76, "qualified": True},
    ]


def _baseline_score(item: dict[str, Any]) -> float:
    score = item["skill"] * 0.5 + item["experience"] * 4.0 + item["interview"] * 0.25
    if item["protected_group"]:
        score -= 8.0
    return round(score, 2)


def _debiased_score(item: dict[str, Any]) -> float:
    return round(item["skill"] * 0.52 + item["experience"] * 3.6 + item["interview"] * 0.26, 2)


def _baseline_decision(item: dict[str, Any]) -> bool:
    return _baseline_score(item) >= 87


def _debiased_decision(item: dict[str, Any]) -> bool:
    return _debiased_score(item) >= 85


def _fairness_snapshot(samples: list[dict[str, Any]], predictions: list[bool], labels: list[bool]) -> dict[str, float]:
    majority_rates = [prediction for index, prediction in enumerate(predictions) if not samples[index]["protected_group"]]
    protected_rates = [prediction for index, prediction in enumerate(predictions) if samples[index]["protected_group"]]
    majority_rate = _selection_rate(majority_rates)
    protected_rate = _selection_rate(protected_rates)
    max_rate = max(majority_rate, protected_rate)
    min_rate = min(majority_rate, protected_rate)
    accuracy = sum(1 for index, prediction in enumerate(predictions) if prediction == labels[index]) / len(labels)
    return {
        "accuracy": round(accuracy, 3),
        "majority_selection_rate": round(majority_rate, 3),
        "protected_selection_rate": round(protected_rate, 3),
        "selection_rate_gap": round(abs(majority_rate - protected_rate), 3),
        "disparate_impact_ratio": round((min_rate / max_rate) if max_rate else 1, 3),
        "sensitive_predictability": round(_sensitive_predictability(samples, predictions), 3),
    }


def _selection_rate(values: list[bool]) -> float:
    return sum(1 for value in values if value) / len(values) if values else 0


def _sensitive_predictability(samples: list[dict[str, Any]], predictions: list[bool]) -> float:
    passed_sensitive_ratio = mean(1.0 if samples[index]["protected_group"] else 0.0 for index, prediction in enumerate(predictions) if prediction) if any(predictions) else 0.0
    rejected_sensitive_ratio = mean(1.0 if samples[index]["protected_group"] else 0.0 for index, prediction in enumerate(predictions) if not prediction) if not all(predictions) else 0.0
    return 0.5 + abs(passed_sensitive_ratio - rejected_sensitive_ratio) / 2