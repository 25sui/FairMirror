from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.entities import ComplianceLogDB, UserDB
from app.models.schemas import ComplianceReport, AppealCreate, Appeal
from app.core.security import get_current_user, ensure_company_access, require_roles
from app.services import compliance_checker

router = APIRouter(prefix="/compliance", tags=["合规报告"])


@router.get("/eu-ai-act/{company_id}", response_model=ComplianceReport)
async def get_eu_ai_act_report(
    company_id: int,
    current_user: UserDB = Depends(require_roles(["admin", "hr", "auditor"]))
):
    ensure_company_access(current_user, company_id)
    report = compliance_checker.check_eu_ai_act(company_id)
    return report


@router.get("/china-ai-ethics/{company_id}", response_model=ComplianceReport)
async def get_china_ai_ethics_report(
    company_id: int,
    current_user: UserDB = Depends(require_roles(["admin", "hr", "auditor"]))
):
    ensure_company_access(current_user, company_id)
    report = compliance_checker.check_china_ai_ethics(company_id)
    return report


@router.post("/report/export")
async def export_compliance_report(
    company_id: int,
    regulation_type: str,
    current_user: UserDB = Depends(require_roles(["admin", "hr", "auditor"])),
    db: Session = Depends(get_db)
):
    ensure_company_access(current_user, company_id)
    if regulation_type == "EU AI Act":
        report = compliance_checker.check_eu_ai_act(company_id)
    elif regulation_type == "China AI Ethics":
        report = compliance_checker.check_china_ai_ethics(company_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid regulation type")

    import json
    db_log = ComplianceLogDB(
        company_id=company_id,
        regulation_type=regulation_type,
        check_items_json=json.dumps([item.model_dump() for item in report.check_items], ensure_ascii=False),
        passed=report.overall_passed,
        compliance_score=report.compliance_score
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return {
        "report_id": db_log.id,
        "report": report,
        "message": "Compliance report exported successfully"
    }
