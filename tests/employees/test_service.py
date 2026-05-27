from datetime import date

import pytest

from app.employees import repository, service


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
