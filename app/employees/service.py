import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import get_token
from app.employees import repository
from app.employees.models import EmployeeRow
from app.employees.schemas import UpstreamEmployee
from app.settings import get_settings


async def fetch_and_store_employees(session: AsyncSession) -> None:
    upstream_employees = await _fetch_from_upstream()
    rows = [_to_row(upstream) for upstream in upstream_employees]
    await repository.upsert_many(session, rows)


async def _fetch_from_upstream() -> list[UpstreamEmployee]:
    settings = get_settings()
    token = await get_token()
    headers = {settings.auth_header_name: f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.employee_api_employees_url, headers=headers)
        response.raise_for_status()
        return [UpstreamEmployee.model_validate(e) for e in response.json()]


def _to_row(upstream: UpstreamEmployee) -> EmployeeRow:
    return EmployeeRow(
        id=upstream.id,
        date_of_birth=upstream.date_of_birth,
        image=upstream.image,
        email=upstream.email,
        first_name=upstream.first_name,
        last_name=upstream.last_name,
        title=upstream.title,
        address=upstream.address,
        country=upstream.country,
        bio=upstream.bio,
        rating=float(upstream.rating),
        fetched_at=datetime.now(timezone.utc),
    )
