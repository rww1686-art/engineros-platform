import pytest
from pydantic import ValidationError

from app.schemas.company import CompanyCreate


def test_company_accepts_valid_edrpou() -> None:
    company = CompanyCreate(name="Engineering Group", edrpou="12345678")
    assert company.edrpou == "12345678"


def test_company_rejects_invalid_edrpou() -> None:
    with pytest.raises(ValidationError):
        CompanyCreate(name="Engineering Group", edrpou="1234")


def test_company_strips_text_fields() -> None:
    company = CompanyCreate(name="  Engineering Group  ", region="  Lviv  ")
    assert company.name == "Engineering Group"
    assert company.region == "Lviv"
