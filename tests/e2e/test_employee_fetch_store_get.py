from datetime import UTC, datetime, timedelta

import httpx
import pytest
import respx

import app.auth.service as auth_service
from app.employees.service import fetch_and_store_employees
from app.settings import Settings, get_settings

FAKE_BASE_URL = "https://fake-upstream.test"

UPSTREAM_EMPLOYEES = [
    {
        "id": "e2e-01",
        "date_of_birth": "1990-05-15",
        "image": "https://example.com/img1.jpg",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Anderson",
        "title": "Engineer",
        "address": "123 Main St",
        "country": "US",
        "bio": "Bio one",
        "rating": 4.5,
    },
    {
        "id": "e2e-02",
        "date_of_birth": "1985-11-20",
        "image": "https://example.com/img2.jpg",
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Baker",
        "title": "Designer",
        "address": "456 Oak Ave",
        "country": "CA",
        "bio": "Bio two",
        "rating": 3.8,
    },
    {
        "id": "e2e-03",
        "date_of_birth": "1992-03-10",
        "image": "https://example.com/img3.jpg",
        "email": "carol@example.com",
        "first_name": "Carol",
        "last_name": "Chen",
        "title": "Manager",
        "address": "789 Pine Rd",
        "country": "US",
        "bio": "Bio three",
        "rating": 4.9,
    },
]


@pytest.fixture(autouse=True)
def _override_settings(monkeypatch):
    fake_settings = Settings(
        employee_api_base_url=FAKE_BASE_URL,
        employee_api_client_id="fake-id",
        employee_api_client_secret="fake-secret",
        employee_api_username="fake-user",
        employee_api_password="fake-pass",
        database_url="sqlite+aiosqlite:///:memory:",
    )
    monkeypatch.setattr("app.settings.get_settings", lambda: fake_settings)
    monkeypatch.setattr("app.employees.service.get_settings", lambda: fake_settings)
    monkeypatch.setattr("app.auth.service.get_settings", lambda: fake_settings)


@pytest.fixture(autouse=True)
def _reset_auth_token_cache():
    auth_service._cached_token = None
    yield
    auth_service._cached_token = None


@pytest.mark.anyio
async def test_fetch_store_and_get_employees(session, client, respx_mock):
    expires = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    respx_mock.post(f"{FAKE_BASE_URL}/api/token").mock(
        return_value=httpx.Response(200, json={"access_token": "fake-token", "expires_at": expires})
    )
    respx_mock.get(f"{FAKE_BASE_URL}/api/employee/list").mock(
        return_value=httpx.Response(200, json=UPSTREAM_EMPLOYEES)
    )
    no_employees_response = client.get("/employees/")
    assert no_employees_response.status_code == 200
    assert no_employees_response.json() == []
    
    await fetch_and_store_employees(session)

    response = client.get("/employees/")
    assert response.status_code == 200

    employees = response.json()
    assert len(employees) == len(UPSTREAM_EMPLOYEES)

    returned_ids = {e["id"] for e in employees}
    expected_ids = {e["id"] for e in UPSTREAM_EMPLOYEES}
    assert returned_ids == expected_ids
