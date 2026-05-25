from datetime import UTC, datetime
from logging import getLogger

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import get_token
from app.employees import repository
from app.employees.models import EmployeeRow
from app.employees.schemas import UpstreamEmployee
from app.settings import get_settings

logger = getLogger(__name__)

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
        upstream_employees = []
        for e in response.json():
            try:
                employee = UpstreamEmployee.model_validate(e)
                upstream_employees.append(employee)
                if employee.model_extra:
                    logger.warning(f"Extra fields from upstream: {employee.model_extra}")
            except ValidationError as e:
                logger.error(f"Invalid upstream employee: {e}", exc_info=True)
                continue
        return upstream_employees


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
        rating=upstream.rating,
        fetched_at=datetime.now(UTC),
    )
