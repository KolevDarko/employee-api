import pytest

from app.employees.repository import get_by_id, get_filtered_employees, upsert_many
from app.employees.schemas import EmployeeFilters
from tests.factories import make_employee


@pytest.mark.anyio
async def test_get_filtered_employees_by_country(session):
    employees = await get_filtered_employees(
        session,
        EmployeeFilters(country="MK"),
    )

    assert all(employee.country == "MK" for employee in employees)
    assert len(employees) == 6

@pytest.mark.anyio
async def test_get_filtered_employees_by_rating(session):
    employees = await get_filtered_employees(
        session,
        EmployeeFilters(min_rating=4.0),
    )

    assert all(employee.rating >= 4.0 for employee in employees)
    assert len(employees) == 7

@pytest.mark.anyio
async def test_get_filtered_employees_by_sort_by(session):
    employees = await get_filtered_employees(
        session,
        EmployeeFilters(sort_by="first_name"),
    )

    assert employees == sorted(employees, key=lambda x: x.first_name)

@pytest.mark.anyio
async def test_get_filtered_employees_by_sort_order(session):
    employees = await get_filtered_employees(
        session,
        EmployeeFilters(sort_by="rating", sort_order="desc"),
    )

    assert employees == sorted(employees, key=lambda x: x.rating, reverse=True)

@pytest.mark.anyio
async def test_get_filtered_employees_by_offset_and_limit(session):
    first_three = await get_filtered_employees(
        session,
        EmployeeFilters(limit=3, sort_by="rating"),
    )
    second_four = await get_filtered_employees(
        session,
        EmployeeFilters(limit=4, offset=3, sort_by="rating"),
    )

    assert len(first_three) == 3
    assert len(second_four) == 4
    assert first_three[0].rating < second_four[0].rating


@pytest.mark.anyio
async def test_get_by_id_returns_employee(session):
    employee = await get_by_id(session, "emp-01")

    assert employee is not None
    assert employee.id == "emp-01"
    assert employee.first_name == "Ana"


@pytest.mark.anyio
async def test_get_by_id_returns_none_when_employee_does_not_exist(session):
    employee = await get_by_id(session, "missing-employee")

    assert employee is None


@pytest.mark.anyio
async def test_upsert_many_inserts_new_employees(session):
    await upsert_many(
        session,
        [
            make_employee(id="emp-inserted-01", first_name="Inserted"),
            make_employee(id="emp-inserted-02", first_name="Also Inserted"),
        ],
    )

    first_employee = await get_by_id(session, "emp-inserted-01")
    second_employee = await get_by_id(session, "emp-inserted-02")

    assert first_employee is not None
    assert first_employee.first_name == "Inserted"
    assert second_employee is not None
    assert second_employee.first_name == "Also Inserted"


@pytest.mark.anyio
async def test_upsert_many_updates_existing_employees(session):
    await upsert_many(
        session,
        [
            make_employee(
                id="emp-01",
                first_name="Updated",
                last_name="Employee",
                country="DE",
                rating=1.1,
            ),
        ],
    )

    employee = await get_by_id(session, "emp-01")

    assert employee is not None
    assert employee.first_name == "Updated"
    assert employee.last_name == "Employee"
    assert employee.country == "DE"
    assert employee.rating == 1.1
