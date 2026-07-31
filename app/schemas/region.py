import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

CODE_PATTERN = re.compile(r"^[a-z0-9-]+$")


class RegionCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=120)
    macroregion: str = Field(min_length=2, max_length=32)
    market_priority: int = Field(default=2, ge=1, le=2)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not CODE_PATTERN.fullmatch(normalized):
            raise ValueError("Region code must use lowercase letters, digits, and hyphens")
        return normalized

    @field_validator("name", "macroregion")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class RegionRead(RegionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
