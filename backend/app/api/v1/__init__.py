from .auth import router as auth_router
from .jd import router as jd_router
from .resume import router as resume_router
from .interview import router as interview_router
from .compliance import router as compliance_router
from .dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "jd_router",
    "resume_router",
    "interview_router",
    "compliance_router",
    "dashboard_router",
]
