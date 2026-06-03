from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import JobDescriptionDB, UserDB
from app.models.schemas import (
    JobDescriptionCreate,
    JobDescription,
    JDAuditRequest,
    JDAuditResponse,
)
from app.core.security import get_current_user, ensure_company_access, get_accessible_job, require_roles
from app.services import bias_detector

router = APIRouter(prefix="/jd", tags=["JD审计"])


@router.post("/analyze", response_model=JDAuditResponse)
async def analyze_jd(
    request: JDAuditRequest,
    current_user: UserDB = Depends(get_current_user)
):
    result = await bias_detector.analyze_jd(
        request.jd_text,
        request.job_title,
        use_deep_learning=True
    )
    return result


@router.post("/", response_model=JobDescription, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    job: JobDescriptionCreate,
    current_user: UserDB = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    ensure_company_access(current_user, job.company_id)
    db_job = JobDescriptionDB(
        company_id=job.company_id,
        creator_id=current_user.id,
        title=job.title,
        content=job.content
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/{job_id}", response_model=JobDescription)
async def get_job_description(
    job_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = get_accessible_job(db, job_id, current_user)
    return job


@router.get("/", response_model=List[JobDescription])
async def list_job_descriptions(
    company_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(JobDescriptionDB)
    if current_user.role == "admin":
        if company_id:
            query = query.filter(JobDescriptionDB.company_id == company_id)
    else:
        target_company_id = company_id or current_user.company_id
        ensure_company_access(current_user, target_company_id)
        query = query.filter(JobDescriptionDB.company_id == target_company_id)
    return query.offset(skip).limit(limit).all()
