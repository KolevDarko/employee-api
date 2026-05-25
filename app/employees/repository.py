from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.employees.models import EmployeeRow
from app.employees.schemas import EmployeeFilters


async def get_filtered_employees(session: AsyncSession, filters: EmployeeFilters) -> list[EmployeeRow]:
    query = select(EmployeeRow)
    if filters.country:
        query = query.where(EmployeeRow.country == filters.country)
    if filters.min_rating is not None:
        query = query.where(EmployeeRow.rating >= filters.min_rating)
    if filters.limit is not None:
        query = query.limit(filters.limit)
    if filters.offset:
        query = query.offset(filters.offset)
    if filters.sort_by:
        sort_col = getattr(EmployeeRow, filters.sort_by)
        query = query.order_by(sort_col.desc() if filters.sort_order == "desc" else sort_col.asc())
    result = await session.scalars(query)
    return list(result.all())

async def get_by_id(session: AsyncSession, employee_id: str) -> EmployeeRow | None:
    result = await session.scalar(select(EmployeeRow).where(EmployeeRow.id == employee_id))
    return result

async def upsert_many(session: AsyncSession, employees: list[EmployeeRow]) -> None:
    if not employees:
        return
    rows = [
        {c.key: getattr(emp, c.key) for c in EmployeeRow.__table__.columns}
        for emp in employees
    ]
    columns_to_update = [c.key for c in EmployeeRow.__table__.columns if c.key != "id"]
    stmt = insert(EmployeeRow).values(rows).on_conflict_do_update(
        index_elements=["id"],
        set_={c: insert(EmployeeRow).excluded[c] for c in columns_to_update},
    )
    await session.execute(stmt)
    await session.commit()
