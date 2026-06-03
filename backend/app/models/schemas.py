from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"
    AUDITOR = "auditor"


class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole


class UserCreate(UserBase):
    password: str
    company_id: Optional[int] = None


class User(UserBase):
    id: int
    company_id: Optional[int] = None
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class JDStatus(str, Enum):
    DRAFT = "draft"
    AUDITING = "auditing"
    APPROVED = "approved"
    REJECTED = "rejected"


class BiasType(str, Enum):
    GENDER = "gender"
    AGE = "age"
    EDUCATION = "education"
    REGION = "region"
    RACE = "race"
    APPEARANCE = "appearance"


class BiasLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class JobDescriptionBase(BaseModel):
    title: str
    content: str


class JobDescriptionCreate(JobDescriptionBase):
    company_id: int


class JobDescription(JobDescriptionBase):
    id: int
    company_id: int
    creator_id: int
    bias_score: Optional[float] = None
    audit_status: JDStatus = JDStatus.DRAFT
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BiasCheckResult(BaseModel):
    type: BiasType
    score: float = Field(ge=0.0, le=1.0)
    level: BiasLevel
    text: str
    position: List[int]
    suggestion: str
    severity: int = Field(ge=1, le=5)


class JDAuditRequest(BaseModel):
    jd_text: str
    job_title: Optional[str] = None
    language: Optional[str] = "zh"


class JDAuditResponse(BaseModel):
    bias_results: List[BiasCheckResult]
    overall_score: float
    overall_level: BiasLevel
    suggestions: List[str]
    report_url: Optional[str] = None
    audit_timestamp: datetime


class SensitiveField(BaseModel):
    field_name: str
    content: str
    risk_level: BiasLevel
    suggestion: str


class ResumeScanRequest(BaseModel):
    resume_text: str
    job_id: Optional[int] = None


class ATSResult(BaseModel):
    system_name: str
    pass_probability: float
    key_factors: List[str]


class ResumeScanResponse(BaseModel):
    sensitive_fields: List[SensitiveField]
    ats_results: List[ATSResult]
    overall_risk_level: BiasLevel
    rewritten_resume: Optional[str] = None
    scan_timestamp: datetime


class InterviewRecordBase(BaseModel):
    candidate_id: int
    job_id: int
    scores: Dict[str, float]
    demographic_group: str


class InterviewRecordCreate(InterviewRecordBase):
    pass


class InterviewRecord(InterviewRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FairnessMetrics(BaseModel):
    group_pass_rates: Dict[str, float]
    four_fifths_rule_passed: bool
    disparate_impact_ratio: float
    shap_key_features: List[str]
    bias_risk_level: BiasLevel
    recommendations: List[str]


class InterviewAnalysisRequest(BaseModel):
    interview_data: List[InterviewRecordBase]
    groups: Optional[List[str]] = None


class InterviewAnalysisResponse(BaseModel):
    fairness_metrics: FairnessMetrics
    analysis_timestamp: datetime
    report_url: Optional[str] = None


class ComplianceCheckItem(BaseModel):
    item_id: str
    description: str
    regulation: str
    passed: bool
    details: Optional[str] = None


class ComplianceReport(BaseModel):
    regulation_type: str
    company_id: int
    check_items: List[ComplianceCheckItem]
    overall_passed: bool
    compliance_score: float
    generated_at: datetime


class AppealStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class AppealBase(BaseModel):
    candidate_id: int
    job_id: int
    reason: str
    evidence: Optional[str] = None


class AppealCreate(AppealBase):
    pass


class Appeal(AppealBase):
    id: int
    status: AppealStatus = AppealStatus.PENDING
    reviewer_id: Optional[int] = None
    review_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BiasReportBase(BaseModel):
    report_type: str
    target_id: int
    results: Dict[str, Any]


class BiasReportCreate(BiasReportBase):
    pass


class BiasReport(BiasReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    total_jds_audited: int
    total_resumes_scanned: int
    total_interviews_analyzed: int
    average_bias_score: float
    compliance_rate: float
    appeals_pending: int
    recent_alerts: List[Dict[str, Any]]


class SystemHealth(BaseModel):
    status: str
    database: str
    ml_models: str
    api_responsetime_ms: float
    timestamp: datetime
