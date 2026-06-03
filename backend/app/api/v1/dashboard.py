from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, ensure_company_access, require_roles
from app.models.database import get_db
from app.models.entities import (
    BiasReportDB,
    ComplianceLogDB,
    InterviewRecordDB,
    JobDescriptionDB,
    ResumeDB,
    UserDB,
)
from app.models.schemas import DashboardMetrics

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    company_id: Optional[int] = None,
    current_user: UserDB = Depends(require_roles(["admin", "hr", "auditor"])),
    db: Session = Depends(get_db),
):
    target_company_id = company_id or current_user.company_id
    if target_company_id is not None:
        ensure_company_access(current_user, target_company_id)

    jd_query = db.query(JobDescriptionDB)
    resume_query = db.query(ResumeDB)
    interview_query = db.query(InterviewRecordDB)
    compliance_query = db.query(ComplianceLogDB)

    if target_company_id is not None:
        jd_query = jd_query.filter(JobDescriptionDB.company_id == target_company_id)
        resume_query = resume_query.join(
            JobDescriptionDB,
            ResumeDB.job_id == JobDescriptionDB.id,
            isouter=True,
        ).filter(
            (JobDescriptionDB.company_id == target_company_id) | (ResumeDB.job_id.is_(None))
        )
        interview_query = interview_query.join(
            JobDescriptionDB,
            InterviewRecordDB.job_id == JobDescriptionDB.id,
        ).filter(JobDescriptionDB.company_id == target_company_id)
        compliance_query = compliance_query.filter(ComplianceLogDB.company_id == target_company_id)

    total_jds = jd_query.count()
    total_resumes = resume_query.count()
    total_interviews = interview_query.count()
    compliance_logs = compliance_query.all()

    scored_jds = [float(j.bias_score) for j in jd_query.all() if j.bias_score is not None]
    average_bias_score = round(sum(scored_jds) / len(scored_jds), 2) if scored_jds else 0.0
    compliance_rate = round(
        sum(1 for item in compliance_logs if item.passed) / len(compliance_logs) * 100,
        1,
    ) if compliance_logs else 0.0

    recent_alerts = []
    high_risk_resumes = resume_query.filter(ResumeDB.risk_level == "high").limit(5).all()
    for resume in high_risk_resumes:
        recent_alerts.append({
            "type": "warning",
            "message": f"简历 #{resume.id} 检测到高风险敏感信息",
            "time": str(resume.created_at),
        })

    low_compliance_logs = [item for item in compliance_logs if not item.passed][:5]
    for log in low_compliance_logs:
        recent_alerts.append({
            "type": "warning",
            "message": f"{log.regulation_type} 合规检查未通过",
            "time": str(log.created_at),
        })

    return DashboardMetrics(
        total_jds_audited=total_jds,
        total_resumes_scanned=total_resumes,
        total_interviews_analyzed=total_interviews,
        average_bias_score=average_bias_score,
        compliance_rate=compliance_rate,
        appeals_pending=0,
        recent_alerts=recent_alerts[:10],
    )