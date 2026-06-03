from fastapi import APIRouter

from app.api.v1 import (
    auth_router,
    jd_router,
    resume_router,
    interview_router,
    compliance_router,
    dashboard_router,
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(jd_router)
api_router.include_router(resume_router)
api_router.include_router(interview_router)
api_router.include_router(compliance_router)
api_router.include_router(dashboard_router)
