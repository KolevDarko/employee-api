import pytest

from app.employees.repository import get_filtered_employees
from app.employees.schemas import EmployeeFilters


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
