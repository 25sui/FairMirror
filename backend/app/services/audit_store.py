from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.domain import AuditJob, Organization
from app.schemas.audit import (
    AuditJobSummary,
    AuditReportSummary,
    DashboardSummary,
    UserRole,
)

OWNER_ROLE_BY_KIND = {
    "jd": UserRole.hr,
    "resume": UserRole.candidate,
    "interview": UserRole.auditor,
    "compliance": UserRole.enterprise_admin,
}

BIAS_LABELS = {
    "age": "年龄",
    "education": "学历",
    "region": "地域",
    "gender": "性别",
    "appearance": "外貌",
    "proxy": "代理变量",
    "workstyle": "工作风格",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_audit_record(
    db: Session,
    *,
    audit_id: str,
    kind: str,
    title: str,
    risk_score: float,
    input_payload: dict[str, Any],
    result_payload: dict[str, Any],
    organization_id: str = "fairmirror-demo",
    status: str | None = None,
) -> AuditJob:
    _ensure_organization(db, organization_id)
    record = AuditJob(
        id=audit_id,
        kind=kind,
        title=title,
        owner_role=OWNER_ROLE_BY_KIND.get(kind, UserRole.enterprise_admin).value,
        status=status or ("warning" if risk_score >= 50 else "completed"),
        risk_score=round(risk_score, 1),
        organization_id=organization_id,
        input_payload=input_payload,
        result_payload=result_payload,
        created_at=_utc_now(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _ensure_organization(db: Session, organization_id: str) -> None:
    if db.get(Organization, organization_id):
        return
    db.add(Organization(id=organization_id, name="FairMirror Demo Corp"))
    db.flush()


def list_audit_records(db: Session, limit: int = 20) -> list[AuditJob]:
    return list(db.scalars(select(AuditJob).order_by(desc(AuditJob.created_at)).limit(limit)).all())


def to_audit_job_summary(record: AuditJob) -> AuditJobSummary:
    return AuditJobSummary(
        audit_id=record.id,
        kind=record.kind,
        title=record.title,
        owner_role=UserRole(record.owner_role),
        status=record.status,
        risk_score=record.risk_score,
        created_at=record.created_at,
    )


def build_dashboard_summary(records: list[AuditJob]) -> DashboardSummary | None:
    if not records:
        return None

    risks = [record.risk_score for record in records]
    compliance_scores = [100 - record.risk_score for record in records if record.kind in {"jd", "resume", "interview"}]
    heatmap = _build_bias_heatmap(records)
    trend = _build_pass_rate_trend(records)
    distribution = _build_role_distribution(records)

    return DashboardSummary(
        fairness_index=round(max(0, 100 - mean(risks)), 1),
        open_risks=sum(1 for record in records if record.risk_score >= 50),
        audits_completed=len(records),
        compliance_readiness=round(mean(compliance_scores or [100 - mean(risks)]), 1),
        bias_heatmap=heatmap,
        pass_rate_trend=trend,
        role_distribution=distribution,
    )


def build_report_summary(records: list[AuditJob]) -> AuditReportSummary | None:
    if not records:
        return None

    coverage_map = {
        "jd": "JD 智能审计",
        "resume": "简历防御盾",
        "interview": "AI 面试公平监控",
        "compliance": "合规报告",
    }
    coverage = [label for kind, label in coverage_map.items() if any(record.kind == kind for record in records)]
    high_risk_records = sorted(records, key=lambda record: record.risk_score, reverse=True)[:3]

    return AuditReportSummary(
        report_id=f"report-{records[0].id}",
        title="FairMirror 全链路招聘公平性审计报告",
        organization="FairMirror Demo Corp",
        coverage=coverage or list(coverage_map.values()),
        risk_score=round(mean(record.risk_score for record in records), 1),
        key_findings=[_record_finding_summary(record) for record in high_risk_records],
        next_actions=[
            "优先复核高风险审计记录，确认是否需要人工修订。",
            "将已确认风险纳入整改闭环，并保留改写前后证据。",
            "按岗位、候选人和面试批次持续观察风险变化。",
        ],
    )


def _record_finding_summary(record: AuditJob) -> str:
    if record.kind == "interview":
        ratio = record.result_payload.get("disparate_impact_ratio", 1)
        return f"{record.title} 的差异影响比为 {ratio}，需要复核群体通过率。"

    findings = record.result_payload.get("findings") or []
    if findings:
        labels = sorted({BIAS_LABELS.get(item.get("type"), item.get("type", "风险")) for item in findings})
        return f"{record.title} 命中 {'、'.join(labels)} 等风险。"
    return f"{record.title} 当前风险分为 {record.risk_score}。"


def _build_bias_heatmap(records: list[AuditJob]) -> list[dict]:
    buckets: dict[str, dict[str, list[float]]] = {
        label: {"jd": [], "resume": [], "interview": []} for label in ["年龄", "学历", "地域", "性别"]
    }

    for record in records:
        if record.kind == "interview":
            ratio = float(record.result_payload.get("disparate_impact_ratio", 1))
            buckets["性别"]["interview"].append(round((1 - min(1, ratio)) * 100, 1))
            continue

        for finding in record.result_payload.get("findings", []):
            label = BIAS_LABELS.get(finding.get("type"))
            if label in buckets and record.kind in buckets[label]:
                buckets[label][record.kind].append(float(finding.get("score", record.risk_score)))

    rows = []
    for label, values in buckets.items():
        rows.append(
            {
                "type": label,
                "jd": round(mean(values["jd"] or [0]), 1),
                "resume": round(mean(values["resume"] or [0]), 1),
                "interview": round(mean(values["interview"] or [0]), 1),
            }
        )
    return rows


def _build_pass_rate_trend(records: list[AuditJob]) -> list[dict]:
    interview_records = [record for record in records if record.kind == "interview"][-4:]
    if not interview_records:
        return [{"month": "当前", "majority": 0.0, "protected": 0.0}]

    trend = []
    for index, record in enumerate(interview_records, start=1):
        rates = [float(item.get("pass_rate", 0)) for item in record.result_payload.get("metrics", [])]
        majority = max(rates) if rates else 0
        protected = min(rates) if rates else 0
        trend.append({"month": f"批次{index}", "majority": round(majority, 3), "protected": round(protected, 3)})
    return trend


def _build_role_distribution(records: list[AuditJob]) -> list[dict]:
    labels = {
        UserRole.enterprise_admin.value: "企业管理员",
        UserRole.hr.value: "HR",
        UserRole.candidate.value: "求职者",
        UserRole.auditor.value: "审计员",
    }
    return [
        {"role": label, "value": sum(1 for record in records if record.owner_role == role)}
        for role, label in labels.items()
    ]