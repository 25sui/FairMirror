from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import ResumeDB, UserDB
from app.models.schemas import (
    ResumeScanRequest,
    ResumeScanResponse,
)
from app.core.security import get_current_user, ensure_self_or_roles, get_accessible_job
from app.services import resume_shield

router = APIRouter(prefix="/resume", tags=["简历防御"])


@router.post("/scan", response_model=ResumeScanResponse)
async def scan_resume(
    request: ResumeScanRequest,
    current_user: UserDB = Depends(get_current_user)
):
    result = await resume_shield.scan_resume(request)
    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_resume(
    candidate_id: int,
    content: str,
    job_id: int = None,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ensure_self_or_roles(current_user, candidate_id, ["admin", "hr"])
    if job_id is not None:
        get_accessible_job(db, job_id, current_user)

    scan_result = await resume_shield.scan_resume(ResumeScanRequest(
        resume_text=content,
        job_id=job_id
    ))

    import json
    db_resume = ResumeDB(
        candidate_id=candidate_id,
        job_id=job_id,
        content=content,
        rewritten_resume=scan_result.rewritten_resume,
        sensitive_fields_json=json.dumps([s.model_dump() for s in scan_result.sensitive_fields]),
        ats_score=scan_result.ats_results[0].pass_probability if scan_result.ats_results else 0.0,
        risk_level=scan_result.overall_risk_level.value
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return {"id": db_resume.id, "scan_result": scan_result}


@router.get("/{resume_id}", response_model=dict)
async def get_resume(
    resume_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    ensure_self_or_roles(current_user, resume.candidate_id, ["admin", "hr"])
    if resume.job_id is not None:
        get_accessible_job(db, resume.job_id, current_user)

    import json
    return {
        "id": resume.id,
        "candidate_id": resume.candidate_id,
        "job_id": resume.job_id,
        "content": resume.content,
        "rewritten_resume": resume.rewritten_resume,
        "sensitive_fields": json.loads(resume.sensitive_fields_json) if resume.sensitive_fields_json else [],
        "ats_score": resume.ats_score,
        "risk_level": resume.risk_level,
        "created_at": resume.created_at
    }
