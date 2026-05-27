import asyncio
from datetime import date

import httpx
import pytest

from app.employees import repository, service
from app.employees.schemas import EmployeeFilters

def make_upstream_employee_data(**overrides: object) -> dict[str, object]:
    defaults = {
        "id": "upstream-employee-01",
        "date_of_birth": date(1990, 1, 1),
        "image": "https://example.com/image.jpg",
        "email": "employee@example.com",
        "first_name": "Upstream",
        "last_name": "Employee",
        "title": "Engineer",
        "address": "123 Main St",
        "country": "MK",
        "bio": "A valid upstream employee.",
        "rating": 4.5,
    }
    return {**defaults, **overrides}


@pytest.mark.anyio
async def test_fetch_and_store_employees_stores_all_returned_employees(
    monkeypatch,
    session,
):

    async def mock_fetch_upstream_employee_data() -> list[dict[str, object]]:
        return [
        make_upstream_employee_data(id="service-happy-01", first_name="First"),
        make_upstream_employee_data(id="service-happy-02", first_name="Second"),
        ]

    monkeypatch.setattr(
        service,
        "_fetch_upstream_employee_data",
        mock_fetch_upstream_employee_data,
    )

    await service.fetch_and_store_employees(session)

    first_employee = await repository.get_by_id(session, "service-happy-01")
    second_employee = await repository.get_by_id(session, "service-happy-02")

    assert first_employee is not None
    assert first_employee.first_name == "First"
    assert second_employee is not None
    assert second_employee.first_name == "Second"


@pytest.mark.anyio
async def test_fetch_and_store_employees_skips_invalid_employee_data(
    monkeypatch,
    session,
):
    async def mock_fetch_upstream_employee_data() -> list[dict[str, object]]:
        return [
        make_upstream_employee_data(id="service-valid-01"),
        make_upstream_employee_data(id="service-invalid-01", email="not-an-email"),
        make_upstream_employee_data(id="service-invalid-02", date_of_birth="tomorrow"),
    ]

    monkeypatch.setattr(
        service,
        "_fetch_upstream_employee_data",
        mock_fetch_upstream_employee_data,
    )

    await service.fetch_and_store_employees(session)

    valid_employee = await repository.get_by_id(session, "service-valid-01")
    invalid_email_employee = await repository.get_by_id(session, "service-invalid-01")
    invalid_date_employee = await repository.get_by_id(session, "service-invalid-02")

    assert valid_employee is not None
    assert invalid_email_employee is None
    assert invalid_date_employee is None

@pytest.mark.anyio
async def test_fetch_and_store_employees_returns_empty_list_when_no_employees_are_returned(monkeypatch, session):
    async def mock_fetch_upstream_employee_data() -> list[dict[str, object]]:
        return []

    monkeypatch.setattr(
        service,
        "_fetch_upstream_employee_data",
        mock_fetch_upstream_employee_data,
    )

    await service.fetch_and_store_employees(session)
    employees = await repository.get_filtered_employees(session, EmployeeFilters())
    assert len(employees) == 0


@pytest.mark.anyio
async def test_fetch_upstream_employee_data_retries_with_exponential_backoff(
    monkeypatch,
):
    attempts = {"count": 0}
    backoff_seconds: list[float] = []

    class StubSettings:
        auth_header_name = "Access-Token"
        employee_api_employees_url = "http://example.test/api/employee/list"

    class StubAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url: str, headers: dict[str, str]) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise httpx.RequestError(
                    "temporary network issue",
                    request=httpx.Request("GET", url),
                )
            return httpx.Response(
                status_code=200,
                json=[
                    make_upstream_employee_data(
                        id="retry-success-01",
                        date_of_birth="1990-01-01",
                    )
                ],
                request=httpx.Request("GET", url, headers=headers),
            )

    async def record_backoff(seconds: float) -> None:
        backoff_seconds.append(seconds)

    async def mock_get_token() -> str:
        return "token-123"

    monkeypatch.setattr(asyncio, "sleep", record_backoff)
    monkeypatch.setattr(service, "get_token", mock_get_token)
    monkeypatch.setattr(service, "get_settings", lambda: StubSettings())
    monkeypatch.setattr(service.httpx, "AsyncClient", StubAsyncClient)

    employees = await service._fetch_upstream_employee_data()

    assert len(employees) == 1
    assert attempts["count"] == 2
    assert backoff_seconds == [1]