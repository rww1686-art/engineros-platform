import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

EDRPOU_PATTERN = re.compile(r"^\d{8}$")


class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    edrpou: str | None = None
    region: str | None = Field(default=None, max_length=120)
    region_id: uuid.UUID | None = None
    city: str | None = Field(default=None, max_length=120)
    website: HttpUrl | None = None
    status: str = Field(default="active", min_length=2, max_length=32)

    @field_validator("name", "region", "city", "status", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("edrpou")
    @classmethod
    def validate_edrpou(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not EDRPOU_PATTERN.fullmatch(normalized):
            raise ValueError("EDRPOU must contain exactly 8 digits")
        return normalized


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    edrpou: str | None = None
    region: str | None = Field(default=None, max_length=120)
    region_id: uuid.UUID | None = None
    city: str | None = Field(default=None, max_length=120)
    website: HttpUrl | None = None
    status: str | None = Field(default=None, min_length=2, max_length=32)

    @field_validator("name", "region", "city", "status", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("edrpou")
    @classmethod
    def validate_edrpou(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not EDRPOU_PATTERN.fullmatch(normalized):
            raise ValueError("EDRPOU must contain exactly 8 digits")
        return normalized


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CompanyList(BaseModel):
    items: list[CompanyRead]
    total: int
    limit: int
    offset: int
