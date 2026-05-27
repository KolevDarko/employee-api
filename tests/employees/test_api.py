import csv
import io

import pytest

@pytest.fixture(autouse=True)
async def auto_seed(seed):
    pass


@pytest.mark.anyio
async def test_get_employees_returns_seeded_data(client):
    response = client.get("/employees/")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 20
    assert payload[0]["id"] == "emp-01"


@pytest.mark.anyio
async def test_get_employees_applies_filters_and_sorting(client):
    response = client.get(
        "/employees/",
        params={"country": "MK", "min_rating": 4.0, "sort_by": "rating", "sort_order": "desc"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["id"] == "emp-01"
    assert payload[1]["id"] == "emp-02"


@pytest.mark.anyio
async def test_get_employees_returns_csv_when_requested(client):
    response = client.get("/employees/", params={"country": "CA", "limit": 2, "format": "csv"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")

    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == 2
    assert rows[0]["id"] == "emp-14"
    assert rows[1]["id"] == "emp-15"


@pytest.mark.anyio
async def test_get_employee_returns_single_employee(client):
    response = client.get("/employees/emp-01")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "emp-01"
    assert payload["first_name"] == "Ana"


@pytest.mark.anyio
async def test_get_employee_returns_404_when_missing(client):
    response = client.get("/employees/missing-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}
