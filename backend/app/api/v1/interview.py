from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.entities import InterviewRecordDB, UserDB
from app.models.schemas import (
    InterviewRecordBase,
    InterviewRecord,
    InterviewAnalysisRequest,
    InterviewAnalysisResponse,
)
from app.core.security import get_current_user, get_accessible_job, require_roles
from app.services import interview_monitor

router = APIRouter(prefix="/interview", tags=["面试监控"])


@router.post("/analyze", response_model=InterviewAnalysisResponse)
async def analyze_interviews(
    request: InterviewAnalysisRequest,
    current_user: UserDB = Depends(require_roles(["admin", "hr", "auditor"])),
    db: Session = Depends(get_db)
):
    for item in request.interview_data:
        get_accessible_job(db, item.job_id, current_user)
    result = await interview_monitor.analyze_interviews(request)
    return result


@router.post("/", response_model=InterviewRecord, status_code=status.HTTP_201_CREATED)
async def create_interview_record(
    record: InterviewRecordBase,
    current_user: UserDB = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    get_accessible_job(db, record.job_id, current_user)
    import json
    db_record = InterviewRecordDB(
        candidate_id=record.candidate_id,
        job_id=record.job_id,
        scores_json=json.dumps(record.scores),
        demographic_group=record.demographic_group
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_interview_records_batch(
    records: List[InterviewRecordBase],
    current_user: UserDB = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    import json
    db_records = []
    for record in records:
        get_accessible_job(db, record.job_id, current_user)
        db_record = InterviewRecordDB(
            candidate_id=record.candidate_id,
            job_id=record.job_id,
            scores_json=json.dumps(record.scores),
            demographic_group=record.demographic_group
        )
        db.add(db_record)
        db_records.append(db_record)

    db.commit()
    for record in db_records:
        db.refresh(record)

    return {"created": len(db_records), "ids": [r.id for r in db_records]}


@router.get("/job/{job_id}", response_model=List[dict])
async def get_interviews_by_job(
    job_id: int,
    current_user: UserDB = Depends(require_roles(["admin", "hr", "auditor"])),
    db: Session = Depends(get_db)
):
    get_accessible_job(db, job_id, current_user)
    records = db.query(InterviewRecordDB).filter(
        InterviewRecordDB.job_id == job_id
    ).all()

    import json
    return [
        {
            "id": r.id,
            "candidate_id": r.candidate_id,
            "job_id": r.job_id,
            "scores": json.loads(r.scores_json),
            "demographic_group": r.demographic_group,
            "created_at": r.created_at
        }
        for r in records
    ]
