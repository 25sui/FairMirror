from typing import List, Dict, Any
from app.models.schemas import ComplianceCheckItem, ComplianceReport
from datetime import datetime


class ComplianceChecker:
    def __init__(self):
        self.eu_ai_act_rules = self._load_eu_ai_act_rules()
        self.china_ai_ethics_rules = self._load_china_ai_ethics_rules()

    def _load_eu_ai_act_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "EU-001",
                "description": "系统是否为高风险AI系统（招聘属于高风险类别）",
                "category": "system_classification"
            },
            {
                "id": "EU-002",
                "description": "是否建立了风险管理系统",
                "category": "risk_management"
            },
            {
                "id": "EU-003",
                "description": "是否使用高质量、有代表性的训练数据",
                "category": "data_quality"
            },
            {
                "id": "EU-004",
                "description": "是否保留了技术文档（系统描述、能力、限制）",
                "category": "documentation"
            },
            {
                "id": "EU-005",
                "description": "是否提供人工监督机制",
                "category": "human_oversight"
            },
            {
                "id": "EU-006",
                "description": "是否提供透明度和信息提供义务",
                "category": "transparency"
            },
            {
                "id": "EU-007",
                "description": "是否建立了准确性、鲁棒性和网络安全措施",
                "category": "accuracy"
            },
            {
                "id": "EU-008",
                "description": "是否建立了事件报告机制",
                "category": "incident_reporting"
            },
            {
                "id": "EU-009",
                "description": "是否进行偏见检测和消除",
                "category": "bias_management"
            },
            {
                "id": "EU-010",
                "description": "是否为受影响方提供申诉机制",
                "category": "appeals"
            },
        ]

    def _load_china_ai_ethics_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "CN-001",
                "description": "是否遵循合法正当性原则",
                "category": "legitimacy"
            },
            {
                "id": "CN-002",
                "description": "是否遵循目的性原则（服务特定合法目的）",
                "category": "purpose"
            },
            {
                "id": "CN-003",
                "description": "是否遵循明确性原则（目的、方式明确）",
                "category": "clarity"
            },
            {
                "id": "CN-004",
                "description": "是否遵循最小必要原则（不必要信息不收集）",
                "category": "minimization"
            },
            {
                "id": "CN-005",
                "description": "是否遵循可问责原则（责任明确）",
                "category": "accountability"
            },
            {
                "id": "CN-006",
                "description": "是否遵循公平公正原则（无歧视）",
                "category": "fairness"
            },
            {
                "id": "CN-007",
                "description": "是否遵循权益保障原则（知情权、选择权）",
                "category": "rights_protection"
            },
            {
                "id": "CN-008",
                "description": "是否遵循透明性原则（决策可解释）",
                "category": "transparency"
            },
            {
                "id": "CN-009",
                "description": "是否遵循可控性原则（人类可干预）",
                "category": "controllability"
            },
            {
                "id": "CN-010",
                "description": "是否遵循质量保障原则（数据质量、系统稳定性）",
                "category": "quality"
            },
        ]

    def check_eu_ai_act(self, company_id: int, metrics: Dict[str, Any] = None) -> ComplianceReport:
        check_items = []

        for rule in self.eu_ai_act_rules:
            passed = self._evaluate_rule(rule, metrics)
            check_items.append(ComplianceCheckItem(
                item_id=rule["id"],
                description=rule["description"],
                regulation="EU AI Act",
                passed=passed,
                details=self._get_rule_details(rule["id"], passed)
            ))

        overall_passed = sum(1 for item in check_items if item.passed) / len(check_items) >= 0.8
        compliance_score = (sum(1 for item in check_items if item.passed) / len(check_items)) * 100

        return ComplianceReport(
            regulation_type="EU AI Act",
            company_id=company_id,
            check_items=check_items,
            overall_passed=overall_passed,
            compliance_score=round(compliance_score, 1),
            generated_at=datetime.utcnow()
        )

    def check_china_ai_ethics(self, company_id: int, metrics: Dict[str, Any] = None) -> ComplianceReport:
        check_items = []

        for rule in self.china_ai_ethics_rules:
            passed = self._evaluate_rule(rule, metrics)
            check_items.append(ComplianceCheckItem(
                item_id=rule["id"],
                description=rule["description"],
                regulation="China AI Ethics",
                passed=passed,
                details=self._get_rule_details(rule["id"], passed)
            ))

        overall_passed = sum(1 for item in check_items if item.passed) / len(check_items) >= 0.8
        compliance_score = (sum(1 for item in check_items if item.passed) / len(check_items)) * 100

        return ComplianceReport(
            regulation_type="China AI Ethics",
            company_id=company_id,
            check_items=check_items,
            overall_passed=overall_passed,
            compliance_score=round(compliance_score, 1),
            generated_at=datetime.utcnow()
        )

    def _evaluate_rule(self, rule: Dict[str, Any], metrics: Dict[str, Any] = None) -> bool:
        rule_id = rule["id"]
        category = rule["category"]

        if metrics:
            if category in metrics:
                return metrics[category] >= 0.8
            if rule_id in metrics:
                return bool(metrics[rule_id])

        return False

    def _get_rule_details(self, rule_id: str, passed: bool) -> str:
        details_map = {
            "EU-001": "招聘AI系统被分类为高风险系统，需要符合相应合规要求",
            "EU-002": "建议建立风险管理体系，定期评估系统风险",
            "EU-003": "使用代表性数据训练，定期审核数据质量",
            "EU-004": "保持完整技术文档，记录系统设计决策",
            "EU-005": "建立人工复核机制，人类保留最终决策权",
            "EU-006": "向用户提供清晰的使用说明和决策解释",
            "EU-007": "实施安全测试，确保系统稳定性",
            "EU-008": "建立事件日志记录和报告机制",
            "EU-009": "FairMirror提供偏见检测和消除功能",
            "EU-010": "FairMirror提供候选人申诉通道",
            "CN-001": "确保AI应用符合法律法规",
            "CN-002": "AI应用服务于合法招聘目的",
            "CN-003": "招聘流程和标准明确可查",
            "CN-004": "仅收集必要信息，避免过度收集",
            "CN-005": "明确责任人，建立问责机制",
            "CN-006": "FairMirror确保招聘无歧视",
            "CN-007": "候选人有权了解AI决策",
            "CN-008": "FairMirror提供可解释AI功能",
            "CN-009": "人类可随时干预AI决策",
            "CN-010": "确保数据和系统质量",
        }

        base = details_map.get(rule_id, "")
        return f"{'✓ ' if passed else '✗ '}{base}"


compliance_checker = ComplianceChecker()
