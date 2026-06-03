from typing import List, Dict, Any
from collections import defaultdict
from app.models.schemas import (
    BiasLevel,
    InterviewAnalysisRequest,
    InterviewAnalysisResponse,
    FairnessMetrics,
    InterviewRecordBase,
)
from datetime import datetime


class InterviewMonitor:
    def __init__(self):
        self.four_fifths_threshold = 0.8

    def calculate_group_pass_rates(self, interviews: List[InterviewRecordBase]) -> Dict[str, float]:
        group_data = defaultdict(lambda: {"total": 0, "passed": 0})

        for interview in interviews:
            group = interview.demographic_group
            group_data[group]["total"] += 1

            avg_score = sum(interview.scores.values()) / len(interview.scores)
            if avg_score >= 3.0:
                group_data[group]["passed"] += 1

        return {
            group: (data["passed"] / data["total"] if data["total"] > 0 else 0.0)
            for group, data in group_data.items()
        }

    def check_four_fifths_rule(self, pass_rates: Dict[str, float]) -> bool:
        if len(pass_rates) < 2:
            return True

        rates = list(pass_rates.values())
        max_rate = max(rates)
        min_rate = min(rates)

        if max_rate == 0:
            return True

        ratio = min_rate / max_rate
        return ratio >= self.four_fifths_threshold

    def calculate_disparate_impact(self, pass_rates: Dict[str, float]) -> float:
        if len(pass_rates) < 2:
            return 1.0

        rates = list(pass_rates.values())
        max_rate = max(rates)
        min_rate = min(rates)

        if max_rate == 0:
            return 0.0

        return round(min_rate / max_rate, 3)

    def identify_high_risk_features(self, interviews: List[InterviewRecordBase]) -> List[str]:
        risk_features = []

        score_variance = self._calculate_score_variance(interviews)
        if score_variance > 2.0:
            risk_features.append("评分差异过大，可能存在评分标准不一致")

        group_sizes = self._get_group_sizes(interviews)
        if any(size < 5 for size in group_sizes.values()):
            risk_features.append("部分群体样本量过小，统计结果可能不可靠")

        demographic_bias = self._check_demographic_correlation(interviews)
        if demographic_bias > 0.3:
            risk_features.append("人口统计学特征与评分存在较强相关性")

        return risk_features

    def _calculate_score_variance(self, interviews: List[InterviewRecordBase]) -> float:
        if not interviews:
            return 0.0

        all_scores = []
        for interview in interviews:
            all_scores.extend(interview.scores.values())

        if len(all_scores) < 2:
            return 0.0

        mean = sum(all_scores) / len(all_scores)
        variance = sum((x - mean) ** 2 for x in all_scores) / len(all_scores)
        return round(variance, 2)

    def _get_group_sizes(self, interviews: List[InterviewRecordBase]) -> Dict[str, int]:
        sizes = defaultdict(int)
        for interview in interviews:
            sizes[interview.demographic_group] += 1
        return dict(sizes)

    def _check_demographic_correlation(self, interviews: List[InterviewRecordBase]) -> float:
        if len(interviews) < 10:
            return 0.0

        group_avg_scores = defaultdict(list)
        for interview in interviews:
            avg_score = sum(interview.scores.values()) / len(interview.scores)
            group_avg_scores[interview.demographic_group].append(avg_score)

        group_means = {
            group: sum(scores) / len(scores)
            for group, scores in group_avg_scores.items()
        }

        if len(group_means) < 2:
            return 0.0

        mean_of_means = sum(group_means.values()) / len(group_means)
        variance = sum((m - mean_of_means) ** 2 for m in group_means.values()) / len(group_means)

        return round(variance, 2)

    def generate_explanation_features(self, risk_features: List[str]) -> List[str]:
        return [f"启发式解释：{feature}" for feature in risk_features]

    def generate_recommendations(
        self,
        four_fifths_passed: bool,
        disparate_impact: float,
        risk_features: List[str]
    ) -> List[str]:
        recommendations = []

        if not four_fifths_passed:
            recommendations.append("【紧急】4/5法则未通过，部分群体通过率显著低于其他群体")
            recommendations.append("建议审查面试评分标准，确保对所有群体公平")

        if disparate_impact < 0.8:
            recommendations.append(f"【警告】差异影响比为 {disparate_impact}，存在潜在歧视风险")
            recommendations.append("建议检查是否有代理变量（如年龄、性别等）影响决策")

        if disparate_impact >= 0.8 and four_fifths_passed:
            recommendations.append("当前面试流程基本符合公平性要求")
            recommendations.append("建议持续监控各群体通过率，防止偏见累积")

        if not risk_features:
            recommendations.append("未检测到明显风险特征")
        else:
            for feature in risk_features:
                recommendations.append(f"【注意】{feature}")

        recommendations.append("建议定期进行公平性审计，确保招聘流程持续优化")

        return recommendations

    def determine_bias_risk_level(
        self,
        four_fifths_passed: bool,
        disparate_impact: float,
        risk_features: List[str]
    ) -> BiasLevel:
        risk_score = 0

        if not four_fifths_passed:
            risk_score += 3
        if disparate_impact < 0.8:
            risk_score += 2
        risk_score += len(risk_features)

        if risk_score >= 5:
            return BiasLevel.HIGH
        elif risk_score >= 2:
            return BiasLevel.MEDIUM
        else:
            return BiasLevel.LOW

    async def analyze_interviews(self, request: InterviewAnalysisRequest) -> InterviewAnalysisResponse:
        interviews = request.interview_data

        if not interviews:
            return InterviewAnalysisResponse(
                fairness_metrics=FairnessMetrics(
                    group_pass_rates={},
                    four_fifths_rule_passed=True,
                    disparate_impact_ratio=1.0,
                    shap_key_features=[],
                    bias_risk_level=BiasLevel.LOW,
                    recommendations=["暂无数据，请导入面试数据进行公平性分析"]
                ),
                analysis_timestamp=datetime.utcnow(),
                report_url=None
            )

        pass_rates = self.calculate_group_pass_rates(interviews)
        four_fifths_passed = self.check_four_fifths_rule(pass_rates)
        disparate_impact = self.calculate_disparate_impact(pass_rates)
        risk_features = self.identify_high_risk_features(interviews)
        recommendations = self.generate_recommendations(four_fifths_passed, disparate_impact, risk_features)
        explanation_features = self.generate_explanation_features(risk_features)
        bias_risk = self.determine_bias_risk_level(four_fifths_passed, disparate_impact, risk_features)

        return InterviewAnalysisResponse(
            fairness_metrics=FairnessMetrics(
                group_pass_rates={k: round(v, 3) for k, v in pass_rates.items()},
                four_fifths_rule_passed=four_fifths_passed,
                disparate_impact_ratio=disparate_impact,
                shap_key_features=explanation_features,
                bias_risk_level=bias_risk,
                recommendations=recommendations
            ),
            analysis_timestamp=datetime.utcnow(),
            report_url=None
        )


interview_monitor = InterviewMonitor()
