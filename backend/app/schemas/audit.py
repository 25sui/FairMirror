from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    enterprise_admin = "enterprise_admin"
    hr = "hr"
    candidate = "candidate"
    auditor = "auditor"


class RoleProfile(BaseModel):
    role: UserRole
    label: str
    scope: str
    permissions: list[str]
    default_view: str


class AuditJobSummary(BaseModel):
    audit_id: str
    kind: Literal["jd", "resume", "interview", "compliance"]
    title: str
    owner_role: UserRole
    status: Literal["completed", "warning", "failed"]
    risk_score: float = Field(ge=0, le=100)
    created_at: str


class AuditReportSummary(BaseModel):
    report_id: str
    title: str
    organization: str
    coverage: list[str]
    risk_score: float = Field(ge=0, le=100)
    key_findings: list[str]
    next_actions: list[str]


class BiasFinding(BaseModel):
    type: Literal["gender", "age", "education", "region", "appearance", "proxy", "workstyle", "identity"]
    level: Literal["high", "medium", "low"]
    score: float = Field(ge=0, le=100)
    text: str
    position: tuple[int, int]
    reason: str
    suggestion: str
    compliance: str
    source: Literal["rule", "semantic_review", "model"] = "rule"
    rule_id: Optional[str] = None


class ExplanationFactor(BaseModel):
    feature: str
    direction: Literal["risk", "protective"]
    impact: float = Field(ge=0, le=1)
    explanation: str


class TokenContribution(BaseModel):
    token: str
    position: tuple[int, int]
    label: str
    contribution: float = Field(ge=0, le=1)
    direction: Literal["risk", "protective"]


class ModelAuditRequest(BaseModel):
    scenario: Literal["jd", "resume"] = "jd"
    content: str


class ModelAuditResponse(BaseModel):
    audit_id: str
    scenario: Literal["jd", "resume"]
    model_name: str
    model_version: str
    runtime_mode: Literal["transformers", "local_surrogate"]
    status: str
    risk_score: float = Field(ge=0, le=100)
    findings: list[BiasFinding]
    token_contributions: list[TokenContribution]
    summary: str


class DebiasingMetricRow(BaseModel):
    metric: str
    label: str
    baseline: float
    debiased: float
    delta: float
    interpretation: str


class DebiasingDemoResponse(BaseModel):
    demo_id: str
    objective: str
    sensitive_attribute: str
    baseline: dict[str, float]
    debiased: dict[str, float]
    metrics: list[DebiasingMetricRow]
    training_trace: list[dict]
    sample_preview: list[dict]


class JDAuditRequest(BaseModel):
    title: str
    content: str
    role: UserRole = UserRole.hr


class JDAuditResponse(BaseModel):
    audit_id: str
    title: str
    risk_score: float
    inclusive_score: float
    summary: str
    findings: list[BiasFinding]
    explanations: list[ExplanationFactor]
    rewritten: str
    compliance_flags: list[str]


class ResumeAuditRequest(BaseModel):
    candidate_name: str = "候选人"
    content: str
    target_role: str = "产品经理"


class AtsScore(BaseModel):
    system: str
    pass_rate: float = Field(ge=0, le=100)
    reason: str


class ResumeAuditResponse(BaseModel):
    audit_id: str
    candidate_name: str
    risk_score: float
    ats_scores: list[AtsScore]
    findings: list[BiasFinding]
    rewritten: str
    anonymity_tips: list[str]
    explanations: list[ExplanationFactor]


class InterviewRecord(BaseModel):
    candidate_id: str
    group: str
    score: float = Field(ge=0, le=100)
    passed: bool
    question_depth: int = Field(ge=0)


class InterviewAuditRequest(BaseModel):
    batch_name: str
    records: list[InterviewRecord]


class GroupMetric(BaseModel):
    group: str
    total: int
    passed: int
    pass_rate: float
    average_score: float
    average_question_depth: float


class FairnessMetric(BaseModel):
    code: str
    label: str
    value: float
    threshold: str
    status: Literal["pass", "warning", "fail"]
    explanation: str


class InterviewAuditResponse(BaseModel):
    audit_id: str
    batch_name: str
    four_fifths_rule: bool
    disparate_impact_ratio: float
    risk_level: Literal["high", "medium", "low"]
    metrics: list[GroupMetric]
    fairness_metrics: list[FairnessMetric]
    calculation_notes: list[str]
    explanations: list[ExplanationFactor]
    recommendations: list[str]


class ComplianceItem(BaseModel):
    code: str
    title: str
    jurisdiction: Literal["EU AI Act", "中国AI伦理"]
    status: Literal["pass", "warning", "fail"]
    evidence: str
    remediation: str


class ComplianceReport(BaseModel):
    report_id: str
    organization: str
    readiness_score: float
    items: list[ComplianceItem]
    roadmap: list[str]


class DashboardSummary(BaseModel):
    fairness_index: float
    open_risks: int
    audits_completed: int
    compliance_readiness: float
    bias_heatmap: list[dict]
    pass_rate_trend: list[dict]
    role_distribution: list[dict]