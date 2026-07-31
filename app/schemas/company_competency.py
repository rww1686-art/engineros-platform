import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.competency import CompetencyRead


class CompanyCompetencyUpsert(BaseModel):
    experience_level: int = Field(default=1, ge=1, le=5)
    verification_status: str = Field(default="unverified", min_length=2, max_length=32)
    source_url: HttpUrl | None = None
    verified_at: datetime | None = None


class CompanyCompetencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: uuid.UUID
    competency_id: uuid.UUID
    experience_level: int
    verification_status: str
    source_url: str | None
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
    competency: CompetencyRead
