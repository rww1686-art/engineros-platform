import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.competency import Competency


class CompanyCompetency(Base):
    __tablename__ = "company_competencies"
    __table_args__ = (
        CheckConstraint(
            "experience_level BETWEEN 1 AND 5",
            name="ck_company_competencies_experience_level",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competencies.id", ondelete="CASCADE"), primary_key=True
    )
    experience_level: Mapped[int] = mapped_column(nullable=False, default=1)
    verification_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="unverified"
    )
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    competency: Mapped[Competency] = relationship(lazy="joined")
