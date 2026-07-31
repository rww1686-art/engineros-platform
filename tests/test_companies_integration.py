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
def clean_companies() -> Iterator[None]:
    engine = create_engine(get_settings().database_url)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE companies RESTART IDENTITY CASCADE"))

    yield

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE companies RESTART IDENTITY CASCADE"))
    engine.dispose()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def create_company(
    client: TestClient,
    *,
    name: str = "West Engineering",
    edrpou: str = "12345678",
    region: str = "Lviv",
    city: str = "Lviv",
) -> dict[str, object]:
    response = client.post(
        "/companies",
        json={
            "name": name,
            "edrpou": edrpou,
            "region": region,
            "city": city,
            "website": "https://example.com",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_get_company(client: TestClient) -> None:
    created = create_company(client)

    response = client.get(f"/companies/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "West Engineering"
    assert response.json()["edrpou"] == "12345678"


def test_list_and_filter_companies(client: TestClient) -> None:
    create_company(client)
    create_company(
        client,
        name="Central Automation",
        edrpou="87654321",
        region="Kyiv",
        city="Kyiv",
    )

    response = client.get("/companies", params={"region": "Lviv"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [company["name"] for company in payload["items"]] == ["West Engineering"]


def test_update_company(client: TestClient) -> None:
    created = create_company(client)

    response = client.patch(
        f"/companies/{created['id']}",
        json={"name": "West Engineering Group", "city": "Drohobych"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "West Engineering Group"
    assert response.json()["city"] == "Drohobych"


def test_delete_company(client: TestClient) -> None:
    created = create_company(client)

    response = client.delete(f"/companies/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/companies/{created['id']}").status_code == 404


def test_reject_duplicate_edrpou(client: TestClient) -> None:
    create_company(client)

    response = client.post(
        "/companies",
        json={"name": "Duplicate Engineering", "edrpou": "12345678"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "EDRPOU already exists"
