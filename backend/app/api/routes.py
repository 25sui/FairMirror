from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.data.demo import SAMPLE_INTERVIEW_RECORDS, SAMPLE_JD, SAMPLE_RESUME
from app.db.session import get_db
from app.schemas.audit import InterviewAuditRequest, InterviewRecord, JDAuditRequest, ModelAuditRequest, ResumeAuditRequest
from app.services.ai_barrier import debiasing_demo, model_audit
from app.services.audit_store import (
    build_dashboard_summary,
    build_report_summary,
    create_audit_record,
    list_audit_records,
    to_audit_job_summary,
)
from app.services.document_parser import extract_document_text
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
def get_audit_jobs(db: Session = Depends(get_db)):
    records = list_audit_records(db)
    if records:
        return [to_audit_job_summary(record) for record in records]
    return audit_job_summaries()


@router.get("/reports/summary")
def get_report_summary(db: Session = Depends(get_db)):
    records = list_audit_records(db, limit=100)
    summary = build_report_summary(records)
    return summary or audit_report_summary()


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


@router.post("/documents/extract")
async def extract_uploaded_document(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = extract_document_text(file.filename or "upload.txt", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"filename": file.filename, "text": text, "characters": len(text)}


@router.post("/jd/audit")
def run_jd_audit(payload: JDAuditRequest, db: Session = Depends(get_db)):
    result = audit_jd(payload.title, payload.content)
    create_audit_record(
        db,
        audit_id=result.audit_id,
        kind="jd",
        title=f"{payload.title} JD 审计",
        risk_score=result.risk_score,
        input_payload=payload.model_dump(mode="json"),
        result_payload=result.model_dump(mode="json"),
    )
    return result


@router.post("/resume/audit")
def run_resume_audit(payload: ResumeAuditRequest, db: Session = Depends(get_db)):
    result = audit_resume(payload.candidate_name, payload.content, payload.target_role)
    create_audit_record(
        db,
        audit_id=result.audit_id,
        kind="resume",
        title=f"{payload.target_role} 简历防御盾",
        risk_score=result.risk_score,
        input_payload=payload.model_dump(mode="json"),
        result_payload=result.model_dump(mode="json"),
    )
    return result


@router.post("/interview/audit")
def run_interview_audit(payload: InterviewAuditRequest, db: Session = Depends(get_db)):
    result = audit_interview(payload.batch_name, payload.records)
    risk_score = round((1 - min(1, result.disparate_impact_ratio)) * 100, 1)
    create_audit_record(
        db,
        audit_id=result.audit_id,
        kind="interview",
        title=payload.batch_name,
        risk_score=risk_score,
        input_payload=payload.model_dump(mode="json"),
        result_payload=result.model_dump(mode="json"),
    )
    return result


@router.get("/interview/demo")
def run_demo_interview_audit():
    records = [InterviewRecord(**item) for item in SAMPLE_INTERVIEW_RECORDS]
    return audit_interview("2026春招增长岗位批次", records)


@router.get("/compliance/report")
def get_compliance_report():
    return compliance_report()


@router.post("/ai/model-audit")
def run_model_audit(payload: ModelAuditRequest):
    return model_audit(payload.content, payload.scenario)


@router.get("/ai/debiasing-demo")
def run_debiasing_demo():
    return debiasing_demo()


@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    records = list_audit_records(db, limit=100)
    summary = build_dashboard_summary(records)
    return summary or dashboard_summary()
