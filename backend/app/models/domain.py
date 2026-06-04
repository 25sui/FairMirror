from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    audits: Mapped[list["AuditJob"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(48), nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"))


class AuditJob(Base):
    __tablename__ = "audit_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(48), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    owner_role: Mapped[str] = mapped_column(String(48), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    result_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )
    organization: Mapped[Organization] = relationship(back_populates="audits")


class ComplianceReportRecord(Base):
    __tablename__ = "compliance_reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)