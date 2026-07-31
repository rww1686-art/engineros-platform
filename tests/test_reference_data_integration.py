import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app.core.config import get_settings
from app.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="PostgreSQL integration tests are disabled",
)


@pytest.fixture(autouse=True)
def clean_reference_data() -> Iterator[None]:
    engine = create_engine(get_settings().database_url)
    statement = text(
        "TRUNCATE TABLE company_competencies, companies, competencies, regions "
        "RESTART IDENTITY CASCADE"
    )
    with engine.begin() as connection:
        connection.execute(statement)

    yield

    with engine.begin() as connection:
        connection.execute(statement)
    engine.dispose()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def create_region(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/regions",
        json={
            "code": "ua-lviv",
            "name": "Lviv Oblast",
            "macroregion": "West",
            "market_priority": 1,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_competency(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/competencies",
        json={
            "code": "industrial-hvac",
            "name": "Industrial HVAC",
            "category": "HVAC",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_company(client: TestClient, region_id: object) -> dict[str, object]:
    response = client.post(
        "/companies",
        json={
            "name": "West Engineering",
            "edrpou": "12345678",
            "region_id": region_id,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_list_regions(client: TestClient) -> None:
    region = create_region(client)

    response = client.get("/regions", params={"is_active": True})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [region["id"]]
    assert response.json()[0]["market_priority"] == 1


def test_reject_duplicate_region_code(client: TestClient) -> None:
    create_region(client)

    response = client.post(
        "/regions",
        json={
            "code": "ua-lviv",
            "name": "Another Lviv Region",
            "macroregion": "West",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Region code exists"


def test_create_and_filter_competencies(client: TestClient) -> None:
    competency = create_competency(client)

    response = client.get("/competencies", params={"category": "HVAC"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [competency["id"]]


def test_assign_and_remove_company_competency(client: TestClient) -> None:
    region = create_region(client)
    competency = create_competency(client)
    company = create_company(client, region["id"])

    company_response = client.get(f"/companies/{company['id']}")
    assert company_response.json()["region_id"] == region["id"]

    filtered = client.get("/companies", params={"region_id": region["id"]})
    assert filtered.json()["total"] == 1

    assigned = client.put(
        f"/companies/{company['id']}/competencies/{competency['id']}",
        json={
            "experience_level": 4,
            "verification_status": "verified",
            "source_url": "https://example.com/projects/hvac",
        },
    )
    assert assigned.status_code == 200
    assert assigned.json()["experience_level"] == 4
    assert assigned.json()["competency"]["code"] == "industrial-hvac"

    listed = client.get(f"/companies/{company['id']}/competencies")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(
        f"/companies/{company['id']}/competencies/{competency['id']}"
    )
    assert deleted.status_code == 204
    assert client.get(f"/companies/{company['id']}/competencies").json() == []


def test_reject_unknown_company_region(client: TestClient) -> None:
    response = client.post(
        "/companies",
        json={
            "name": "Unknown Region Engineering",
            "region_id": "d2d2e29f-5953-48cc-b09e-74951c96bf35",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Region not found"
