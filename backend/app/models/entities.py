from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"
    AUDITOR = "auditor"


class JDStatus(str, enum.Enum):
    DRAFT = "draft"
    AUDITING = "auditing"
    APPROVED = "approved"
    REJECTED = "rejected"


class AppealStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="hr")
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("CompanyDB", back_populates="users")
    job_descriptions = relationship("JobDescriptionDB", back_populates="creator")
    resumes = relationship("ResumeDB", back_populates="candidate")


class CompanyDB(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("UserDB", back_populates="company")
    job_descriptions = relationship("JobDescriptionDB", back_populates="company")
    bias_reports = relationship("BiasReportDB", back_populates="company")
    compliance_logs = relationship("ComplianceLogDB", back_populates="company")


class JobDescriptionDB(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    bias_score = Column(String(20), nullable=True)
    audit_status = Column(String(20), default="draft")
    audit_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("CompanyDB", back_populates="job_descriptions")
    creator = relationship("UserDB", back_populates="job_descriptions")
    resumes = relationship("ResumeDB", back_populates="job_description")


class ResumeDB(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    content = Column(Text, nullable=False)
    rewritten_resume = Column(Text, nullable=True)
    sensitive_fields_json = Column(Text, nullable=True)
    ats_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    candidate = relationship("UserDB", back_populates="resumes")
    job_description = relationship("JobDescriptionDB", back_populates="resumes")


class InterviewRecordDB(Base):
    __tablename__ = "interview_records"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scores_json = Column(Text, nullable=False)
    demographic_group = Column(String(100), nullable=False)
    analysis_result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BiasReportDB(Base):
    __tablename__ = "bias_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    report_type = Column(String(50), nullable=False)
    report_content = Column(Text, nullable=False)
    report_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("CompanyDB", back_populates="bias_reports")


class ComplianceLogDB(Base):
    __tablename__ = "compliance_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    regulation_type = Column(String(50), nullable=False)
    check_items_json = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False)
    compliance_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("CompanyDB", back_populates="compliance_logs")


class AppealDB(Base):
    __tablename__ = "appeals"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    appeal_reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


Base = Base
