from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import warnings

warnings.filterwarnings("ignore")

from app.core.config import settings
from app.api.router import api_router
from app.models.database import init_db

print("Starting FairMirror in FULL MODE...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI反偏见招聘镜像 - 全链路招聘公平性审计平台",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
    init_db()
    print("Database initialized!")


@app.get("/")
async def root():
    return {
        "message": "Welcome to FairMirror API",
        "version": settings.VERSION,
        "mode": "full",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FairMirror API",
        "mode": "full"
    }
