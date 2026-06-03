from fastapi import APIRouter

from app.data.demo import SAMPLE_INTERVIEW_RECORDS, SAMPLE_JD, SAMPLE_RESUME
from app.schemas.audit import InterviewAuditRequest, InterviewRecord, JDAuditRequest, ResumeAuditRequest
from app.services.fairness_engine import (
    audit_interview,
    audit_jd,
    audit_job_summaries,
    audit_report_summary,
    audit_resume,
    compliance_report,
    dashboard_summary,
    role_profiles,
)

router = APIRouter()


@router.get("/roles")
def get_roles():
    return role_profiles()


@router.get("/audit-jobs")
def get_audit_jobs():
    return audit_job_summaries()


@router.get("/reports/summary")
def get_report_summary():
    return audit_report_summary()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fairmirror"}


@router.get("/demo")
def demo_payload() -> dict:
    return {
        "jd": SAMPLE_JD,
        "resume": SAMPLE_RESUME,
        "interview_records": SAMPLE_INTERVIEW_RECORDS,
    }


@router.post("/jd/audit")
def run_jd_audit(payload: JDAuditRequest):
    return audit_jd(payload.title, payload.content)


@router.post("/resume/audit")
def run_resume_audit(payload: ResumeAuditRequest):
    return audit_resume(payload.candidate_name, payload.content, payload.target_role)


@router.post("/interview/audit")
def run_interview_audit(payload: InterviewAuditRequest):
    return audit_interview(payload.batch_name, payload.records)


@router.get("/interview/demo")
def run_demo_interview_audit():
    records = [InterviewRecord(**item) for item in SAMPLE_INTERVIEW_RECORDS]
    return audit_interview("2026春招增长岗位批次", records)


@router.get("/compliance/report")
def get_compliance_report():
    return compliance_report()


@router.get("/dashboard/summary")
def get_dashboard_summary():
    return dashboard_summary()